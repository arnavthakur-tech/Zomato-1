"""Central configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
PROMPTS_DIR = ROOT_DIR / "prompts"

load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    llm_api_key: str
    llm_model: str
    llm_timeout_seconds: float
    llm_max_retries: int
    hf_dataset_id: str
    hf_dataset_revision: str
    candidate_cap: int


def _resolve_llm_api_key() -> str:
    """Prefer LLM_API_KEY; accept GROQ_API_KEY as an alias."""
    for name in ("LLM_API_KEY", "GROQ_API_KEY"):
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def get_settings() -> Settings:
    return Settings(
        llm_api_key=_resolve_llm_api_key(),
        llm_model=os.getenv("LLM_MODEL", "openai/gpt-oss-20b").strip()
        or "openai/gpt-oss-20b",
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "45")),
        llm_max_retries=int(os.getenv("LLM_MAX_RETRIES", "3")),
        hf_dataset_id=os.getenv(
            "HF_DATASET_ID", "jason1966/absin7_zomato-bangalore-dataset"
        ),
        hf_dataset_revision=os.getenv("HF_DATASET_REVISION", "main"),
        candidate_cap=int(os.getenv("CANDIDATE_CAP", "20")),
    )
