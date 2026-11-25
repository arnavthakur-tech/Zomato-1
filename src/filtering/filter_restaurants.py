"""Deterministic preference filters over the processed restaurant store."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.config import get_settings
from src.preferences.schema import UserPreferences

# City synonyms so "Bengaluru" matches stored "Bangalore" and vice versa.
LOCATION_ALIASES: dict[str, set[str]] = {
    "bangalore": {"bangalore", "bengaluru"},
    "bengaluru": {"bangalore", "bengaluru"},
}


@dataclass(frozen=True)
class FilterResult:
    candidates: pd.DataFrame
    total_matches: int
    candidate_cap: int
    prefs: UserPreferences

    @property
    def is_empty(self) -> bool:
        return self.total_matches == 0


def _normalize(text: object) -> str:
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    return str(text).strip().lower()


def _location_terms(location_query: str) -> set[str]:
    query = _normalize(location_query)
    return LOCATION_ALIASES.get(query, {query})


def _cuisine_queries(cuisine: str) -> list[str]:
    """Split comma-separated cuisines; match policy is ANY."""
    return [part.strip().lower() for part in cuisine.split(",") if part.strip()]


def _matches_cuisine(row_tokens: object, row_cuisines: object, queries: list[str]) -> bool:
    if not queries:
        return False

    tokens: list[str] = []
    if isinstance(row_tokens, list):
        tokens = [_normalize(t) for t in row_tokens]
    elif row_tokens is not None and not (isinstance(row_tokens, float) and pd.isna(row_tokens)):
        # parquet may restore list-like values differently
        try:
            tokens = [_normalize(t) for t in list(row_tokens)]
        except TypeError:
            tokens = []

    joined = _normalize(row_cuisines)
    for query in queries:
        if any(query == token or query in token or token in query for token in tokens if token):
            return True
        if query and query in joined:
            return True
    return False


def _matches_location(location: object, locality: object, terms: set[str]) -> bool:
    loc = _normalize(location)
    area = _normalize(locality)
    for term in terms:
        if not term:
            continue
        if term == loc or term in loc or term == area or term in area:
            return True
    return False


def filter_restaurants(
    restaurants: pd.DataFrame,
    prefs: UserPreferences,
    *,
    candidate_cap: int | None = None,
) -> FilterResult:
    """
    Apply hard filters and return at most ``candidate_cap`` rows.

    Sort order: rating descending, then name ascending for stability.
    Rows with null ratings are excluded when ``min_rating`` filtering applies.
    """
    settings = get_settings()
    cap = candidate_cap if candidate_cap is not None else settings.candidate_cap
    if cap < 1:
        raise ValueError("candidate_cap must be >= 1")

    required = {"id", "name", "location", "locality", "cuisines", "budget_band", "rating"}
    missing = required - set(restaurants.columns)
    if missing:
        raise ValueError(f"Restaurant frame missing columns: {sorted(missing)}")

    location_terms = _location_terms(prefs.location)
    cuisine_queries = _cuisine_queries(prefs.cuisine)

    mask_location = restaurants.apply(
        lambda row: _matches_location(row["location"], row["locality"], location_terms),
        axis=1,
    )
    mask_budget = restaurants["budget_band"].fillna("").astype(str).str.lower() == prefs.budget
    if cuisine_queries:
        mask_cuisine = restaurants.apply(
            lambda row: _matches_cuisine(
                row["cuisine_tokens"] if "cuisine_tokens" in restaurants.columns else None,
                row["cuisines"],
                cuisine_queries,
            ),
            axis=1,
        )
    else:
        # Optional cuisine: do not hard-filter by cuisine.
        mask_cuisine = pd.Series(True, index=restaurants.index)
    mask_rating = restaurants["rating"].notna() & (restaurants["rating"] >= prefs.min_rating)

    filtered = restaurants.loc[
        mask_location & mask_budget & mask_cuisine & mask_rating
    ].copy()

    filtered = filtered.sort_values(
        by=["rating", "name"],
        ascending=[False, True],
        kind="mergesort",
    )
    total_matches = len(filtered)
    capped = filtered.head(cap).reset_index(drop=True)

    return FilterResult(
        candidates=capped,
        total_matches=total_matches,
        candidate_cap=cap,
        prefs=prefs,
    )


def load_processed_restaurants(path: str | None = None) -> pd.DataFrame:
    """Load the Phase 1 processed restaurant store."""
    from src.ingestion.preprocess import processed_path

    file_path = path or str(processed_path())
    return pd.read_parquet(file_path)
