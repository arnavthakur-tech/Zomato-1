"""Rank filtered candidates with Groq, falling back to rating order on failure."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from src.llm.client import ChatMessage, GroqLLMClient, LLMClientError, get_llm_client
from src.llm.parse_response import (
    ParseError,
    RecommendationResult,
    fallback_rank,
    parse_rank_response,
)
from src.llm.prompt_templates import DEFAULT_MAX_RECOMMENDATIONS, build_rank_prompt
from src.preferences.schema import UserPreferences

logger = logging.getLogger(__name__)


def rank_and_explain(
    prefs: UserPreferences,
    candidates: pd.DataFrame,
    *,
    client: GroqLLMClient | None = None,
    max_recommendations: int = DEFAULT_MAX_RECOMMENDATIONS,
    use_llm: bool = True,
) -> RecommendationResult:
    """
    Build a prompt, call Groq, parse/ground the response.

    On LLM or parse failure, return rating-sorted fallback recommendations.
    """
    if candidates.empty:
        return fallback_rank(candidates, prefs, reason="empty_candidates")

    if not use_llm:
        return fallback_rank(
            candidates,
            prefs,
            limit=max_recommendations,
            reason="llm_disabled",
        )

    try:
        prompt = build_rank_prompt(
            prefs,
            candidates,
            max_recommendations=max_recommendations,
        )
        llm = client or get_llm_client()
        completion = llm.chat(
            [
                ChatMessage(role="system", content=prompt.system),
                ChatMessage(role="user", content=prompt.user),
            ]
        )
        result = parse_rank_response(
            completion.content,
            candidates,
            prefs,
            max_items=max_recommendations,
        )
        logger.info(
            "LLM ranking ok model=%s latency_ms=%.0f attempts=%s items=%s",
            completion.model,
            completion.latency_ms,
            completion.attempts,
            len(result.recommendations),
        )
        return result
    except (LLMClientError, ParseError, ValueError, OSError) as exc:
        logger.warning("LLM ranking failed; using fallback: %s", exc)
        return fallback_rank(
            candidates,
            prefs,
            limit=max_recommendations,
            reason=f"fallback:{type(exc).__name__}:{exc}",
        )


def result_preview(result: RecommendationResult) -> dict[str, Any]:
    """Compact dict useful for CLI demos."""
    return {
        "source": result.source,
        "summary": result.summary,
        "count": len(result.recommendations),
        "parse_notes": list(result.parse_notes),
        "recommendations": [r.to_dict() for r in result.recommendations],
    }
