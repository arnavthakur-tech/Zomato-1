"""Phase 4 smoke checks: orchestrator happy path, no-match, validation, localities."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestrator import recommend


def assert_true(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> None:
    # Validation errors stay user-safe (no crash)
    invalid = recommend(
        location=" ",
        budget="cheap",
        cuisine="",
        min_rating=11,
    )
    assert_true(invalid.status == "validation_error", "Expected validation_error")
    assert_true(len(invalid.validation_errors) >= 3, "Expected multiple validation errors")

    # Optional cuisine path
    any_cuisine = recommend(
        location="Bangalore",
        budget="medium",
        cuisine="",
        min_rating=4.0,
        max_recommendations=3,
        use_llm=False,
    )
    assert_true(any_cuisine.status == "ok", f"Optional cuisine failed: {any_cuisine.message}")
    assert_true(any_cuisine.total_matches > 0, "Optional cuisine should still find matches")

    # No-match path does not call LLM / returns empty guidance
    empty = recommend(
        location="Atlantis",
        budget="low",
        cuisine="Martian",
        min_rating=5.0,
        use_llm=False,
    )
    assert_true(empty.status == "no_match", "Expected no_match")
    assert_true(empty.result is None, "No-match should not include recommendations")

    # Happy path: Bangalore + Italian (fallback mode keeps test offline-fast)
    italian = recommend(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_preferences="family-friendly",
        max_recommendations=3,
        use_llm=False,
    )
    assert_true(italian.status == "ok", f"Italian path failed: {italian.message}")
    assert_true(italian.result is not None, "Missing result")
    assert_true(len(italian.result.recommendations) > 0, "Expected recommendations")
    first = italian.result.recommendations[0]
    for attr in ("name", "cuisine", "rating", "estimated_cost", "explanation"):
        assert_true(hasattr(first, attr), f"Missing field {attr}")
    assert_true(bool(first.name), "Name should be present")
    assert_true(bool(first.explanation), "Explanation should be present")

    # Second locality/cuisine smoke: Koramangala + Chinese
    chinese = recommend(
        location="Koramangala",
        budget="medium",
        cuisine="Chinese",
        min_rating=4.0,
        additional_preferences="good for a date night",
        max_recommendations=3,
        use_llm=False,
    )
    assert_true(chinese.status == "ok", f"Chinese/Koramangala path failed: {chinese.message}")
    assert_true(chinese.total_matches > 0, "Expected Koramangala Chinese matches")
    assert_true(len(chinese.result.recommendations) > 0, "Expected Chinese recommendations")

    # Optional live Groq path when key is present
    live = recommend(
        location="Bangalore",
        budget="low",
        cuisine="North Indian",
        min_rating=4.0,
        additional_preferences="quick service",
        max_recommendations=2,
        use_llm=True,
    )
    assert_true(live.status in {"ok", "no_match", "error"}, f"Unexpected status {live.status}")
    if live.status == "ok":
        assert_true(live.result is not None, "Live ok response missing result")
        assert_true(live.result.source in {"llm", "fallback"}, "Unexpected source")

    print("Phase 4 checks passed")
    print(f"  validation errors: {len(invalid.validation_errors)}")
    print(f"  empty status:      {empty.status}")
    print(
        f"  italian:           {italian.status} "
        f"matches={italian.total_matches} recs={len(italian.result.recommendations)} "
        f"source={italian.result.source}"
    )
    print(
        f"  chinese locality:  {chinese.status} "
        f"matches={chinese.total_matches} recs={len(chinese.result.recommendations)}"
    )
    if live.status == "ok" and live.result is not None:
        print(
            f"  live north indian: {live.status} "
            f"source={live.result.source} recs={len(live.result.recommendations)}"
        )
    else:
        print(f"  live north indian: {live.status} ({live.message})")


if __name__ == "__main__":
    main()
