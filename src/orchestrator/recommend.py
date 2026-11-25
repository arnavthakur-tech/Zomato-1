"""End-to-end recommendation pipeline: validate → filter → Groq rank → normalize."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from src.config import get_settings
from src.filtering.filter_restaurants import filter_restaurants, load_processed_restaurants
from src.llm.parse_response import RecommendationResult
from src.llm.prompt_templates import DEFAULT_MAX_RECOMMENDATIONS
from src.llm.rank import rank_and_explain
from src.preferences.schema import PreferenceValidationError, UserPreferences, parse_preferences

logger = logging.getLogger(__name__)

_RESTAURANTS_CACHE: pd.DataFrame | None = None


@dataclass(frozen=True)
class RecommendResponse:
    """Structured pipeline result for UI / CLI consumers."""

    status: str  # ok | no_match | validation_error | error
    message: str
    preferences: UserPreferences | None = None
    total_matches: int = 0
    candidate_count: int = 0
    candidate_cap: int = 0
    result: RecommendationResult | None = None
    validation_errors: tuple[str, ...] = ()
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == "ok"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "message": self.message,
            "preferences": self.preferences.to_dict() if self.preferences else None,
            "total_matches": self.total_matches,
            "candidate_count": self.candidate_count,
            "candidate_cap": self.candidate_cap,
            "result": self.result.to_dict() if self.result else None,
            "validation_errors": list(self.validation_errors),
            "meta": self.meta,
        }


def clear_restaurant_cache() -> None:
    """Drop the in-memory processed dataset cache (mainly for tests)."""
    global _RESTAURANTS_CACHE
    _RESTAURANTS_CACHE = None


def get_restaurants(*, force_reload: bool = False, path: str | None = None) -> pd.DataFrame:
    """Load processed restaurants once and reuse across requests."""
    global _RESTAURANTS_CACHE
    if force_reload or _RESTAURANTS_CACHE is None or path is not None:
        frame = load_processed_restaurants(path)
        if frame.empty:
            raise FileNotFoundError("Processed restaurant dataset is empty")
        if path is None:
            _RESTAURANTS_CACHE = frame
            logger.info("Loaded processed restaurants rows=%s", len(frame))
            return _RESTAURANTS_CACHE
        return frame
    return _RESTAURANTS_CACHE


def recommend(
    *,
    location: object,
    budget: object,
    cuisine: object,
    min_rating: object,
    additional_preferences: object = "",
    candidate_cap: int | None = None,
    max_recommendations: int = DEFAULT_MAX_RECOMMENDATIONS,
    use_llm: bool | None = None,
    restaurants: pd.DataFrame | None = None,
) -> RecommendResponse:
    """
    Run the full hybrid recommendation pipeline.

    Hard filters run first. The LLM only ranks/explains the capped candidate set.
    """
    try:
        prefs = parse_preferences(
            location=location,
            budget=budget,
            cuisine=cuisine,
            min_rating=min_rating,
            additional_preferences=additional_preferences,
        )
    except PreferenceValidationError as exc:
        return RecommendResponse(
            status="validation_error",
            message="Please fix the highlighted preference fields.",
            validation_errors=tuple(exc.errors),
        )

    settings = get_settings()
    cap = candidate_cap if candidate_cap is not None else settings.candidate_cap
    llm_enabled = use_llm if use_llm is not None else bool(settings.llm_api_key)

    try:
        store = restaurants if restaurants is not None else get_restaurants()
        filtered = filter_restaurants(store, prefs, candidate_cap=cap)
    except FileNotFoundError as exc:
        logger.exception("Processed data missing")
        return RecommendResponse(
            status="error",
            message=(
                "Processed restaurant data not found. "
                "Run `python scripts/prepare_data.py` first."
            ),
            preferences=prefs,
            meta={"error": str(exc)},
        )
    except Exception as exc:  # noqa: BLE001 — surface as user-safe pipeline error
        logger.exception("Filter stage failed")
        return RecommendResponse(
            status="error",
            message="Something went wrong while filtering restaurants. Please try again.",
            preferences=prefs,
            meta={"error": f"{type(exc).__name__}: {exc}"},
        )

    if filtered.is_empty:
        return RecommendResponse(
            status="no_match",
            message=(
                "No restaurants matched these filters. "
                "Try relaxing location, budget, cuisine (if set), or minimum rating."
            ),
            preferences=prefs,
            total_matches=0,
            candidate_count=0,
            candidate_cap=filtered.candidate_cap,
            meta={"llm_called": False},
        )

    try:
        ranked = rank_and_explain(
            prefs,
            filtered.candidates,
            max_recommendations=max_recommendations,
            use_llm=llm_enabled,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Ranking stage failed unexpectedly")
        return RecommendResponse(
            status="error",
            message="Ranking failed unexpectedly. Please try again.",
            preferences=prefs,
            total_matches=filtered.total_matches,
            candidate_count=len(filtered.candidates),
            candidate_cap=filtered.candidate_cap,
            meta={"error": f"{type(exc).__name__}: {exc}"},
        )

    source_note = (
        "AI-ranked recommendations with explanations."
        if ranked.source == "llm"
        else "Showing filter matches ranked by rating (AI ranking unavailable)."
    )
    return RecommendResponse(
        status="ok",
        message=source_note,
        preferences=prefs,
        total_matches=filtered.total_matches,
        candidate_count=len(filtered.candidates),
        candidate_cap=filtered.candidate_cap,
        result=ranked,
        meta={
            "llm_called": llm_enabled,
            "source": ranked.source,
            "parse_notes": list(ranked.parse_notes),
        },
    )


def recommend_from_prefs(
    prefs: UserPreferences,
    **kwargs: Any,
) -> RecommendResponse:
    """Convenience wrapper when preferences are already validated."""
    return recommend(
        location=prefs.location,
        budget=prefs.budget,
        cuisine=prefs.cuisine,
        min_rating=prefs.min_rating,
        additional_preferences=prefs.additional_preferences,
        **kwargs,
    )
