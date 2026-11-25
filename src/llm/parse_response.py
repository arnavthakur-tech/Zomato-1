"""Parse LLM ranking JSON and ground recommendations against candidates."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from src.preferences.schema import UserPreferences

FALLBACK_EXPLANATION = (
    "Matched your filters; ranked by rating because the AI ranking step was unavailable."
)
FALLBACK_SUMMARY = (
    "Showing the top matches from your filters, sorted by rating "
    "(AI ranking/explanation unavailable)."
)

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


@dataclass(frozen=True)
class Recommendation:
    id: str
    name: str
    cuisine: str
    rating: float | None
    estimated_cost: float | None
    rank: int
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RecommendationResult:
    summary: str
    recommendations: list[Recommendation]
    source: str  # "llm" | "fallback"
    raw_response: str | None = None
    parse_notes: tuple[str, ...] = ()

    @property
    def is_fallback(self) -> bool:
        return self.source == "fallback"

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "source": self.source,
            "raw_response": self.raw_response,
            "parse_notes": list(self.parse_notes),
        }


class ParseError(ValueError):
    """Raised when the LLM response cannot be turned into grounded recommendations."""


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract a JSON object from raw model output (plain or fenced)."""
    if text is None:
        raise ParseError("Empty LLM response")

    cleaned = text.strip()
    if not cleaned:
        raise ParseError("Empty LLM response")

    fence = _JSON_FENCE_RE.search(cleaned)
    if fence:
        cleaned = fence.group(1).strip()

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ParseError("No JSON object found in LLM response") from None
        try:
            payload = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ParseError(f"Invalid JSON in LLM response: {exc}") from exc

    if not isinstance(payload, dict):
        raise ParseError("LLM JSON root must be an object")
    return payload


def _as_str(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def _cuisine_display(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(v).strip() for v in value if str(v).strip())
    return _as_str(value)


def _optional_float(value: object) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _candidate_indexes(candidates: pd.DataFrame) -> tuple[dict[str, int], dict[str, int]]:
    by_id: dict[str, int] = {}
    by_name: dict[str, int] = {}
    for idx, row in candidates.reset_index(drop=True).iterrows():
        rid = _as_str(row.get("id"))
        name = _as_str(row.get("name")).lower()
        if rid and rid not in by_id:
            by_id[rid] = int(idx)
        if name and name not in by_name:
            by_name[name] = int(idx)
    return by_id, by_name


def _row_to_recommendation(
    row: pd.Series,
    *,
    rank: int,
    explanation: str,
) -> Recommendation:
    return Recommendation(
        id=_as_str(row.get("id")),
        name=_as_str(row.get("name")),
        cuisine=_cuisine_display(row.get("cuisines")),
        rating=_optional_float(row.get("rating")),
        estimated_cost=_optional_float(row.get("cost_for_two")),
        rank=rank,
        explanation=explanation.strip() or FALLBACK_EXPLANATION,
    )


def fallback_rank(
    candidates: pd.DataFrame,
    prefs: UserPreferences | None = None,
    *,
    limit: int | None = None,
    reason: str | None = None,
) -> RecommendationResult:
    """
    Deterministic fallback: rating-sorted candidates with a generic explanation.

    Assumes ``candidates`` are already filtered/sorted (rating desc).
    """
    if candidates.empty:
        summary = "No matching restaurants to rank."
        if prefs is not None:
            summary = (
                f"No restaurants matched location={prefs.location}, "
                f"budget={prefs.budget}, cuisine={prefs.cuisine}, "
                f"min_rating>={prefs.min_rating}."
            )
        return RecommendationResult(
            summary=summary,
            recommendations=[],
            source="fallback",
            parse_notes=(reason or "empty_candidates",),
        )

    frame = candidates.reset_index(drop=True)
    if limit is not None:
        frame = frame.head(max(0, limit))

    notes = [reason] if reason else []
    recommendations = [
        _row_to_recommendation(row, rank=i + 1, explanation=FALLBACK_EXPLANATION)
        for i, (_, row) in enumerate(frame.iterrows())
    ]
    return RecommendationResult(
        summary=FALLBACK_SUMMARY,
        recommendations=recommendations,
        source="fallback",
        parse_notes=tuple(notes),
    )


def parse_rank_response(
    raw_text: str,
    candidates: pd.DataFrame,
    prefs: UserPreferences | None = None,
    *,
    max_items: int | None = None,
) -> RecommendationResult:
    """
    Parse LLM JSON, map items to candidate id/name, drop hallucinations,
    and normalize recommendation fields from the dataset.
    """
    if candidates.empty:
        raise ParseError("Cannot parse recommendations against an empty candidate set")

    payload = extract_json_object(raw_text)
    items = payload.get("recommendations")
    if items is None:
        raise ParseError("Missing 'recommendations' array")
    if not isinstance(items, list):
        raise ParseError("'recommendations' must be an array")
    if not items:
        raise ParseError("Empty 'recommendations' array")

    by_id, by_name = _candidate_indexes(candidates)
    frame = candidates.reset_index(drop=True)
    notes: list[str] = []
    seen_ids: set[str] = set()
    grounded: list[Recommendation] = []

    for raw_item in items:
        if not isinstance(raw_item, dict):
            notes.append("skipped_non_object_item")
            continue

        item_id = _as_str(raw_item.get("id"))
        item_name = _as_str(raw_item.get("name"))
        explanation = _as_str(raw_item.get("explanation")) or FALLBACK_EXPLANATION

        row_idx: int | None = None
        if item_id and item_id in by_id:
            row_idx = by_id[item_id]
        elif item_name and item_name.lower() in by_name:
            row_idx = by_name[item_name.lower()]
            notes.append(f"matched_by_name:{item_name}")
        else:
            notes.append(f"hallucination_dropped:{item_id or item_name or '?'}")
            continue

        row = frame.iloc[row_idx]
        rid = _as_str(row.get("id"))
        if rid in seen_ids:
            notes.append(f"duplicate_dropped:{rid}")
            continue
        seen_ids.add(rid)

        grounded.append(
            _row_to_recommendation(
                row,
                rank=len(grounded) + 1,
                explanation=explanation,
            )
        )
        if max_items is not None and len(grounded) >= max_items:
            break

    if not grounded:
        raise ParseError("No grounded recommendations remained after validation")

    summary = _as_str(payload.get("summary"))
    if not summary:
        if prefs is not None:
            cuisine_bit = f" for {prefs.cuisine}" if prefs.cuisine else ""
            summary = (
                f"Top picks{cuisine_bit} in {prefs.location} "
                f"on a {prefs.budget} budget."
            )
        else:
            summary = "Top restaurant matches for your preferences."
        notes.append("summary_generated")

    return RecommendationResult(
        summary=summary,
        recommendations=grounded,
        source="llm",
        raw_response=raw_text,
        parse_notes=tuple(notes),
    )
