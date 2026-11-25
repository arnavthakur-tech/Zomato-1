"""Phase 2 demo: validate preferences and print a filtered candidate shortlist."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.filtering import filter_restaurants, load_processed_restaurants
from src.preferences import PreferenceValidationError, parse_preferences


def _print_candidates(result) -> None:
    prefs = result.prefs
    print("Preferences")
    print(f"  location:                 {prefs.location}")
    print(f"  budget:                   {prefs.budget}")
    print(f"  cuisine:                  {prefs.cuisine}")
    print(f"  min_rating:               {prefs.min_rating}")
    print(f"  additional_preferences:   {prefs.additional_preferences or '(none)'}")
    print()
    print(
        f"Matches: {result.total_matches} total | "
        f"showing {len(result.candidates)} (cap={result.candidate_cap})"
    )

    if result.is_empty:
        print("No restaurants matched these filters. Try relaxing location/budget/cuisine/rating.")
        return

    display_cols = ["id", "name", "locality", "cuisines", "rating", "cost_for_two", "budget_band"]
    print(result.candidates[display_cols].to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter restaurants by preferences (no LLM).")
    parser.add_argument("--location", default="Bangalore")
    parser.add_argument("--budget", default="medium")
    parser.add_argument("--cuisine", default="Italian")
    parser.add_argument("--min-rating", type=float, default=4.0)
    parser.add_argument("--additional", default="family-friendly", dest="additional")
    parser.add_argument("--cap", type=int, default=None, help="Override CANDIDATE_CAP")
    parser.add_argument(
        "--scenario",
        choices=["good", "empty", "invalid", "custom"],
        default="custom",
        help="Preset scenarios for quick checks",
    )
    args = parser.parse_args()

    if args.scenario == "good":
        location, budget, cuisine, min_rating, additional = (
            "Bangalore",
            "medium",
            "Italian",
            4.0,
            "family-friendly",
        )
    elif args.scenario == "empty":
        location, budget, cuisine, min_rating, additional = (
            "Atlantis",
            "low",
            "Martian",
            5.0,
            "",
        )
    elif args.scenario == "invalid":
        location, budget, cuisine, min_rating, additional = (
            "  ",
            "cheap",
            "",
            11,
            "",
        )
    else:
        location, budget, cuisine, min_rating, additional = (
            args.location,
            args.budget,
            args.cuisine,
            args.min_rating,
            args.additional,
        )

    try:
        prefs = parse_preferences(
            location=location,
            budget=budget,
            cuisine=cuisine,
            min_rating=min_rating,
            additional_preferences=additional,
        )
    except PreferenceValidationError as exc:
        print("Validation failed:")
        for err in exc.errors:
            print(f"  - {err}")
        sys.exit(1)

    restaurants = load_processed_restaurants()
    result = filter_restaurants(restaurants, prefs, candidate_cap=args.cap)
    _print_candidates(result)

    if len(result.candidates) > result.candidate_cap:
        print("ERROR: candidate count exceeded cap", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
