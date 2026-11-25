"""Clean and normalize raw Zomato rows into a recommendation-ready table."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import DATA_PROCESSED_DIR

PROCESSED_NAME = "restaurants.parquet"
REQUIRED_OUTPUT_COLUMNS = [
    "id",
    "name",
    "location",
    "locality",
    "cuisines",
    "cuisine_tokens",
    "cost_for_two",
    "budget_band",
    "rating",
]

# Flexible source-column aliases across common HF Zomato mirrors.
COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "name": ("name", "restaurant name", "restaurant_name"),
    "locality": ("location", "locality", "area", "local address"),
    "city": ("city", "City"),
    "cuisines": ("cuisines", "cuisines type", "cuisine", "cuisines_type"),
    "cost": (
        "approx_cost(for two people)",
        "avg cost (two people)",
        "average_cost_for_two",
        "cost_for_two",
        "approx_cost_for_two_people",
    ),
    "rating": ("rate", "rate (out of 5)", "rating", "aggregate_rating"),
}

# Bangalore HF mirrors often put area names in listed_in(city), not the city.
KNOWN_CITIES = {
    "bangalore",
    "bengaluru",
    "mumbai",
    "delhi",
    "new delhi",
    "hyderabad",
    "chennai",
    "kolkata",
    "pune",
    "gurgaon",
    "noida",
    "jaipur",
    "ahmedabad",
}


def processed_path(output_dir: Path | None = None) -> Path:
    return (output_dir or DATA_PROCESSED_DIR) / PROCESSED_NAME


def _pick_column(df: pd.DataFrame, logical_name: str) -> str | None:
    for alias in COLUMN_ALIASES[logical_name]:
        if alias in df.columns:
            return alias
    # case-insensitive fallback
    lower_map = {c.lower(): c for c in df.columns}
    for alias in COLUMN_ALIASES[logical_name]:
        if alias.lower() in lower_map:
            return lower_map[alias.lower()]
    return None


def _parse_rating(value: object) -> float | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, (int, float)):
        rating = float(value)
        return rating if 0.0 <= rating <= 5.0 else None

    text = str(value).strip()
    if not text or text in {"-", "NEW", "nan", "None"}:
        return None
    # Forms like "4.1/5"
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    rating = float(match.group(1))
    return rating if 0.0 <= rating <= 5.0 else None


def _parse_cost(value: object) -> float | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, (int, float)):
        cost = float(value)
        return cost if cost >= 0 else None

    text = str(value).strip().replace(",", "")
    if not text or text in {"-", "nan", "None"}:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    return float(match.group(1))


def budget_band_from_cost(cost: float | None) -> str | None:
    """Map cost-for-two into low / medium / high bands."""
    if cost is None or (isinstance(cost, float) and np.isnan(cost)):
        return None
    if cost < 500:
        return "low"
    if cost <= 1500:
        return "medium"
    return "high"


def _normalize_cuisines(value: object) -> tuple[str, list[str]]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "", []
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "-"}:
        return "", []
    tokens = [part.strip().lower() for part in text.split(",") if part.strip()]
    # Preserve a readable original-ish display string
    display = ", ".join(part.strip() for part in text.split(",") if part.strip())
    return display, tokens


def _stable_id(name: str, locality: str, city: str) -> str:
    key = f"{name.strip().lower()}|{locality.strip().lower()}|{city.strip().lower()}"
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
    return f"rest_{digest}"


def preprocess_restaurants(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Transform a raw HF Zomato frame into the cleaned restaurant store."""
    name_col = _pick_column(raw_df, "name")
    if name_col is None:
        raise ValueError(
            f"Could not find a restaurant name column. Available: {list(raw_df.columns)}"
        )

    locality_col = _pick_column(raw_df, "locality")
    city_col = _pick_column(raw_df, "city")
    cuisines_col = _pick_column(raw_df, "cuisines")
    cost_col = _pick_column(raw_df, "cost")
    rating_col = _pick_column(raw_df, "rating")

    working = pd.DataFrame(
        {
            "name": raw_df[name_col].astype("string").str.strip(),
            "locality": (
                raw_df[locality_col].astype("string").str.strip()
                if locality_col
                else pd.Series([pd.NA] * len(raw_df), dtype="string")
            ),
            "city_raw": (
                raw_df[city_col].astype("string").str.strip()
                if city_col
                else pd.Series([pd.NA] * len(raw_df), dtype="string")
            ),
            "cuisines_raw": (
                raw_df[cuisines_col]
                if cuisines_col
                else pd.Series([pd.NA] * len(raw_df))
            ),
            "cost_raw": raw_df[cost_col] if cost_col else pd.Series([pd.NA] * len(raw_df)),
            "rating_raw": (
                raw_df[rating_col] if rating_col else pd.Series([pd.NA] * len(raw_df))
            ),
        }
    )

    working = working[working["name"].notna() & (working["name"] != "")].copy()
    working["locality"] = working["locality"].fillna("").astype(str)

    def _resolve_city(value: object) -> str:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return "Bangalore"
        text = str(value).strip()
        if not text or text.lower() in {"", "nan", "none", "<na>"}:
            return "Bangalore"
        if text.lower() in KNOWN_CITIES:
            return "Bengaluru" if text.lower() == "bengaluru" else text.title()
        # Non-city area labels (common in Bangalore mirrors) → default city.
        return "Bangalore"

    working["location"] = working["city_raw"].map(_resolve_city)

    cuisine_parsed = working["cuisines_raw"].map(_normalize_cuisines)
    working["cuisines"] = cuisine_parsed.map(lambda x: x[0])
    working["cuisine_tokens"] = cuisine_parsed.map(lambda x: x[1])

    working["cost_for_two"] = working["cost_raw"].map(_parse_cost)
    working["rating"] = working["rating_raw"].map(_parse_rating)
    working["budget_band"] = working["cost_for_two"].map(budget_band_from_cost)

    working["id"] = [
        _stable_id(name, locality, city)
        for name, locality, city in zip(
            working["name"], working["locality"], working["location"], strict=True
        )
    ]

    # Deduplicate identical venues; keep the highest rating when available.
    working["_rating_sort"] = working["rating"].fillna(-1.0)
    working = (
        working.sort_values("_rating_sort", ascending=False)
        .drop_duplicates(subset=["id"], keep="first")
        .drop(columns=["_rating_sort"])
    )

    cleaned = working[REQUIRED_OUTPUT_COLUMNS].reset_index(drop=True)
    return cleaned


def save_processed(
    df: pd.DataFrame,
    output_dir: Path | None = None,
    *,
    also_csv: bool = True,
) -> Path:
    path = processed_path(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    if also_csv:
        df.to_csv(path.with_suffix(".csv"), index=False)
    return path


def summarize_quality(df: pd.DataFrame) -> dict[str, object]:
    """Return a compact data-quality summary for logging/printing."""
    total = len(df)
    return {
        "rows": total,
        "unique_ids": int(df["id"].nunique()) if total else 0,
        "unique_locations": int(df["location"].nunique()) if total else 0,
        "unique_localities": int(df["locality"].replace("", pd.NA).nunique(dropna=True))
        if total
        else 0,
        "null_rating_pct": round(float(df["rating"].isna().mean() * 100), 2) if total else 0.0,
        "null_cost_pct": round(float(df["cost_for_two"].isna().mean() * 100), 2)
        if total
        else 0.0,
        "null_cuisines_pct": round(float((df["cuisines"] == "").mean() * 100), 2)
        if total
        else 0.0,
        "budget_distribution": (
            df["budget_band"].fillna("unknown").value_counts(dropna=False).to_dict()
            if total
            else {}
        ),
        "rating_describe": (
            df["rating"].describe()[["count", "mean", "min", "max"]].to_dict()
            if total and df["rating"].notna().any()
            else {}
        ),
    }


def print_quality_summary(df: pd.DataFrame) -> None:
    summary = summarize_quality(df)
    print("Data quality summary")
    print(f"  rows:              {summary['rows']}")
    print(f"  unique ids:        {summary['unique_ids']}")
    print(f"  unique locations:  {summary['unique_locations']}")
    print(f"  unique localities: {summary['unique_localities']}")
    print(f"  null rating %:     {summary['null_rating_pct']}")
    print(f"  null cost %:       {summary['null_cost_pct']}")
    print(f"  empty cuisines %:  {summary['null_cuisines_pct']}")
    print(f"  budget bands:      {summary['budget_distribution']}")
    if summary["rating_describe"]:
        print(f"  rating stats:      {summary['rating_describe']}")
