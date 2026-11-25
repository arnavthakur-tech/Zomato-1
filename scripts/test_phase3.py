"""Phase 3 checks: prompts, grounding, hallucination drop, fallback path."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.filtering import filter_restaurants, load_processed_restaurants
from src.llm import (
    build_rank_prompt,
    fallback_rank,
    parse_rank_response,
    ParseError,
)
from src.preferences import parse_preferences


def assert_true(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> None:
    prefs = parse_preferences(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_preferences="family-friendly, not too crowded",
    )
    restaurants = load_processed_restaurants()
    filtered = filter_restaurants(restaurants, prefs, candidate_cap=8)
    assert_true(not filtered.is_empty, "Need non-empty candidates for Phase 3 checks")

    candidates = filtered.candidates
    prompt = build_rank_prompt(prefs, candidates, max_recommendations=5)
    assert_true("family-friendly" in prompt.user, "Preferences missing from user prompt")
    assert_true(candidates.iloc[0]["id"] in prompt.user, "Candidate id missing from prompt")
    assert_true("Only recommend from the provided candidate list" in prompt.system.lower()
                or "only from the provided candidate list" in prompt.system.lower()
                or "ONLY from the provided candidate list" in prompt.system,
                "System prompt missing grounding rule")

    top = candidates.iloc[0]
    second = candidates.iloc[1] if len(candidates) > 1 else candidates.iloc[0]

    good_payload = {
        "summary": "Family-friendly Italian picks in Bangalore on a medium budget.",
        "recommendations": [
            {
                "id": str(top["id"]),
                "rank": 1,
                "explanation": "High rating and Italian options that fit a medium budget.",
            },
            {
                "id": "rest_DOES_NOT_EXIST",
                "name": "Totally Fake Trattoria",
                "rank": 2,
                "explanation": "Should be dropped as a hallucination.",
            },
            {
                "id": str(second["id"]),
                "rank": 3,
                "explanation": "Solid match for family-friendly dining.",
            },
        ],
    }
    parsed = parse_rank_response(json.dumps(good_payload), candidates, prefs)
    assert_true(parsed.source == "llm", "Expected llm source")
    assert_true(len(parsed.recommendations) >= 1, "Expected grounded recommendations")
    grounded_ids = {r.id for r in parsed.recommendations}
    assert_true("rest_DOES_NOT_EXIST" not in grounded_ids, "Hallucinated id was not dropped")
    assert_true(str(top["id"]) in grounded_ids, "Valid candidate id missing after parse")
    assert_true(
        any("hallucination_dropped" in note for note in parsed.parse_notes),
        "Expected hallucination note",
    )
    # Dataset facts should win over any invented values
    first = parsed.recommendations[0]
    assert_true(first.name == str(top["name"]), "Name should come from dataset")
    assert_true(first.rank == 1, "Ranks should be reassigned in order")

    # Markdown-fenced JSON should still parse
    fenced = "```json\n" + json.dumps(good_payload) + "\n```"
    fenced_parsed = parse_rank_response(fenced, candidates, prefs, max_items=1)
    assert_true(len(fenced_parsed.recommendations) == 1, "max_items should truncate")

    # All-hallucination response must fail parse (caller falls back)
    bad_payload = {
        "summary": "Invented places",
        "recommendations": [
            {"id": "rest_fake", "name": "No Such Place", "explanation": "Nope"},
        ],
    }
    try:
        parse_rank_response(json.dumps(bad_payload), candidates, prefs)
        raise AssertionError("Expected ParseError for all-hallucination response")
    except ParseError:
        pass

    fallback = fallback_rank(candidates, prefs, limit=3, reason="simulated_llm_failure")
    assert_true(fallback.is_fallback, "Expected fallback source")
    assert_true(len(fallback.recommendations) == 3, "Fallback limit not applied")
    assert_true(
        "ranked by rating" in fallback.recommendations[0].explanation.lower(),
        "Fallback explanation missing",
    )

    print("Phase 3 checks passed")
    print(f"  candidates:           {len(candidates)}")
    print(f"  grounded after parse: {len(parsed.recommendations)}")
    print(f"  parse notes:          {list(parsed.parse_notes)}")
    print(f"  fallback count:       {len(fallback.recommendations)}")


if __name__ == "__main__":
    main()
