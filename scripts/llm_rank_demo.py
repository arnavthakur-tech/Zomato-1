"""Phase 3 demo: filter candidates, then Groq-rank (or force fallback)."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import get_settings
from src.filtering import filter_restaurants, load_processed_restaurants
from src.llm import rank_and_explain
from src.llm.rank import result_preview
from src.preferences import PreferenceValidationError, parse_preferences

SCENARIOS = {
    "italian_family": {
        "location": "Bangalore",
        "budget": "medium",
        "cuisine": "Italian",
        "min_rating": 4.0,
        "additional_preferences": "family-friendly, not too crowded",
    },
    "north_indian_low": {
        "location": "Bangalore",
        "budget": "low",
        "cuisine": "North Indian",
        "min_rating": 4.0,
        "additional_preferences": "quick service, casual",
    },
    "chinese_date": {
        "location": "Koramangala",
        "budget": "medium",
        "cuisine": "Chinese",
        "min_rating": 4.2,
        "additional_preferences": "good for a date night",
    },
    "cafe_high": {
        "location": "Bangalore",
        "budget": "high",
        "cuisine": "Cafe",
        "min_rating": 4.3,
        "additional_preferences": "quiet spot to work with coffee",
    },
    "empty": {
        "location": "Atlantis",
        "budget": "low",
        "cuisine": "Martian",
        "min_rating": 5.0,
        "additional_preferences": "",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank filtered restaurants with Groq.")
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS.keys()) + ["custom"],
        default="italian_family",
    )
    parser.add_argument("--location", default="Bangalore")
    parser.add_argument("--budget", default="medium")
    parser.add_argument("--cuisine", default="Italian")
    parser.add_argument("--min-rating", type=float, default=4.0)
    parser.add_argument("--additional", default="", dest="additional")
    parser.add_argument("--cap", type=int, default=None)
    parser.add_argument("--max-recommendations", type=int, default=5)
    parser.add_argument(
        "--fallback-only",
        action="store_true",
        help="Skip Groq and use rating-sorted fallback",
    )
    parser.add_argument("--json", action="store_true", help="Print full JSON result")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    if args.scenario == "custom":
        raw = {
            "location": args.location,
            "budget": args.budget,
            "cuisine": args.cuisine,
            "min_rating": args.min_rating,
            "additional_preferences": args.additional,
        }
    else:
        raw = SCENARIOS[args.scenario]

    try:
        prefs = parse_preferences(**raw)
    except PreferenceValidationError as exc:
        print("Validation failed:")
        for err in exc.errors:
            print(f"  - {err}")
        sys.exit(1)

    restaurants = load_processed_restaurants()
    filtered = filter_restaurants(restaurants, prefs, candidate_cap=args.cap)

    print("Preferences")
    for key, value in prefs.to_dict().items():
        print(f"  {key}: {value or '(none)'}")
    print(
        f"\nCandidates: {filtered.total_matches} total | "
        f"sending {len(filtered.candidates)} (cap={filtered.candidate_cap})"
    )

    if filtered.is_empty:
        print("No restaurants matched these filters. LLM was not called.")
        sys.exit(0)

    settings = get_settings()
    if not args.fallback_only and not settings.llm_api_key:
        print(
            "\nNo LLM_API_KEY/GROQ_API_KEY set — running fallback-only. "
            "Add your Groq key to .env for live ranking."
        )
        use_llm = False
    else:
        use_llm = not args.fallback_only

    result = rank_and_explain(
        prefs,
        filtered.candidates,
        max_recommendations=args.max_recommendations,
        use_llm=use_llm,
    )

    print(f"\nSource:  {result.source}")
    print(f"Summary: {result.summary}")
    if result.parse_notes:
        print(f"Notes:   {', '.join(result.parse_notes)}")
    print()

    if args.json:
        print(json.dumps(result_preview(result), indent=2, ensure_ascii=False))
        return

    for rec in result.recommendations:
        cost = "n/a" if rec.estimated_cost is None else f"{rec.estimated_cost:.0f}"
        rating = "n/a" if rec.rating is None else f"{rec.rating:.1f}"
        print(f"#{rec.rank}  {rec.name}  ({rec.id})")
        print(f"    cuisine={rec.cuisine}  rating={rating}  cost_for_two={cost}")
        print(f"    {rec.explanation}")
        print()


if __name__ == "__main__":
    main()
