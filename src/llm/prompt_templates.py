"""Build grounded ranking prompts from preferences and candidates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import PROMPTS_DIR
from src.preferences.schema import UserPreferences

SYSTEM_PROMPT_FILE = "recommend_system.txt"
USER_PROMPT_FILE = "recommend_user.txt"
DEFAULT_MAX_RECOMMENDATIONS = 10

# Compact fields sent to the model (facts stay authoritative in the dataset).
CANDIDATE_FIELDS = (
    "id",
    "name",
    "location",
    "locality",
    "cuisines",
    "cost_for_two",
    "budget_band",
    "rating",
)


@dataclass(frozen=True)
class RankPrompt:
    system: str
    user: str
    preferences: dict[str, Any]
    candidates: list[dict[str, Any]]
    max_recommendations: int


def _load_template(name: str, prompts_dir: Path | None = None) -> str:
    base = prompts_dir or PROMPTS_DIR
    path = base / name
    if not path.is_file():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def _render(template: str, **values: object) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", str(value))
    return rendered


def candidates_to_compact_records(candidates: pd.DataFrame) -> list[dict[str, Any]]:
    """Serialize candidates into a compact JSON-friendly list for the prompt."""
    if candidates.empty:
        return []

    missing = {"id", "name"} - set(candidates.columns)
    if missing:
        raise ValueError(f"Candidates missing required columns: {sorted(missing)}")

    records: list[dict[str, Any]] = []
    for _, row in candidates.iterrows():
        item: dict[str, Any] = {}
        for field in CANDIDATE_FIELDS:
            if field not in candidates.columns:
                continue
            value = row[field]
            if field == "cuisines":
                if isinstance(value, list):
                    item[field] = ", ".join(str(v) for v in value)
                elif value is None or (isinstance(value, float) and pd.isna(value)):
                    item[field] = ""
                else:
                    item[field] = str(value)
            elif field in {"cost_for_two", "rating"}:
                if value is None or (isinstance(value, float) and pd.isna(value)):
                    item[field] = None
                else:
                    item[field] = float(value) if field == "rating" else (
                        int(value) if float(value).is_integer() else float(value)
                    )
            else:
                if value is None or (isinstance(value, float) and pd.isna(value)):
                    item[field] = ""
                else:
                    item[field] = str(value)
        records.append(item)
    return records


def build_rank_prompt(
    prefs: UserPreferences,
    candidates: pd.DataFrame,
    *,
    max_recommendations: int = DEFAULT_MAX_RECOMMENDATIONS,
    prompts_dir: Path | None = None,
) -> RankPrompt:
    """
    Inject structured preferences + compact candidate JSON into prompt templates.

    Raises ValueError if candidates are empty (caller should use the no-match path).
    """
    if candidates.empty:
        raise ValueError("Cannot build ranking prompt with an empty candidate set")
    if max_recommendations < 1:
        raise ValueError("max_recommendations must be >= 1")

    compact = candidates_to_compact_records(candidates)
    prefs_payload = prefs.to_dict()

    system = _load_template(SYSTEM_PROMPT_FILE, prompts_dir)
    user_template = _load_template(USER_PROMPT_FILE, prompts_dir)
    user = _render(
        user_template,
        preferences_json=json.dumps(prefs_payload, ensure_ascii=False, indent=2),
        candidates_json=json.dumps(compact, ensure_ascii=False, indent=2),
        max_recommendations=min(max_recommendations, len(compact)),
    )

    return RankPrompt(
        system=system,
        user=user,
        preferences=prefs_payload,
        candidates=compact,
        max_recommendations=min(max_recommendations, len(compact)),
    )
