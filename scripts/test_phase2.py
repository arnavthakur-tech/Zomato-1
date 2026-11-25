"""Lightweight Phase 2 checks (validation, good match, empty set, cap)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.filtering import filter_restaurants, load_processed_restaurants
from src.preferences import PreferenceValidationError, parse_preferences


def assert_true(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> None:
    # Invalid preferences
    try:
        parse_preferences(
            location=" ",
            budget="cheap",
            cuisine="",
            min_rating=11,
        )
        raise AssertionError("Expected PreferenceValidationError")
    except PreferenceValidationError as exc:
        assert_true(len(exc.errors) >= 3, f"Expected multiple errors, got {exc.errors}")

    # Cuisine is optional
    prefs_any_cuisine = parse_preferences(
        location="Bangalore",
        budget="medium",
        cuisine="",
        min_rating=4.0,
    )
    assert_true(prefs_any_cuisine.cuisine == "", "Blank cuisine should be allowed")

    prefs_good = parse_preferences(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_preferences="family-friendly",
    )
    prefs_empty = parse_preferences(
        location="Atlantis",
        budget="low",
        cuisine="Martian",
        min_rating=5.0,
    )

    restaurants = load_processed_restaurants()
    good = filter_restaurants(restaurants, prefs_good, candidate_cap=20)
    empty = filter_restaurants(restaurants, prefs_empty, candidate_cap=20)
    any_cuisine = filter_restaurants(restaurants, prefs_any_cuisine, candidate_cap=20)

    assert_true(good.total_matches > 0, "Expected non-empty matches for good prefs")
    assert_true(
        any_cuisine.total_matches >= good.total_matches,
        "Optional blank cuisine should match at least as many as a cuisine filter",
    )
    assert_true(len(good.candidates) > 0, "Expected candidates for good prefs")
    assert_true(
        len(good.candidates) <= good.candidate_cap,
        "Candidate count exceeded cap",
    )
    assert_true(empty.is_empty, "Expected empty result for over-constrained prefs")
    assert_true(len(empty.candidates) == 0, "Empty path should return 0 candidates")

    # Bengaluru alias should behave like Bangalore
    prefs_alias = parse_preferences(
        location="Bengaluru",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
    )
    alias = filter_restaurants(restaurants, prefs_alias, candidate_cap=20)
    assert_true(alias.total_matches > 0, "Bengaluru alias should match Bangalore rows")

    # Cap enforcement even when many matches exist
    prefs_broad = parse_preferences(
        location="Bangalore",
        budget="low",
        cuisine="Indian",
        min_rating=3.0,
    )
    capped = filter_restaurants(restaurants, prefs_broad, candidate_cap=5)
    assert_true(capped.total_matches >= len(capped.candidates), "total_matches >= capped size")
    assert_true(len(capped.candidates) <= 5, "Hard cap of 5 violated")

    print("Phase 2 checks passed")
    print(f"  good matches:     {good.total_matches} (showing {len(good.candidates)})")
    print(f"  empty matches:    {empty.total_matches}")
    print(f"  alias matches:    {alias.total_matches}")
    print(f"  broad total/cap:  {capped.total_matches}/{len(capped.candidates)}")


if __name__ == "__main__":
    main()
