"""FastAPI app exposing meta + recommend endpoints for the Next.js UI."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import get_settings
from src.orchestrator import get_restaurants, recommend

ANY_CUISINE = "Any cuisine"

DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000,"
    "http://127.0.0.1:3000"
)
# Matches Vercel production + preview hosts (https://*.vercel.app).
DEFAULT_VERCEL_ORIGIN_REGEX = r"https://.*\.vercel\.app"


def _running_on_railway() -> bool:
    return bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_PROJECT_ID")
        or os.getenv("RAILWAY_SERVICE_ID")
    )


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
    origins: list[str] = []
    for part in raw.split(","):
        origin = part.strip().rstrip("/")
        if origin:
            origins.append(origin)
    return origins


def _cors_origin_regex() -> str | None:
    """Optional regex for preview URLs (e.g. https://.*\\.vercel\\.app).

    On Railway, default to allowing Vercel hosts when CORS_ORIGIN_REGEX is unset.
    Set CORS_ORIGIN_REGEX= (empty) to disable the default.
    """
    if "CORS_ORIGIN_REGEX" in os.environ:
        value = os.environ["CORS_ORIGIN_REGEX"].strip()
        return value or None
    if _running_on_railway():
        return DEFAULT_VERCEL_ORIGIN_REGEX
    return None


app = FastAPI(
    title="BiteRank API",
    version="1.4.0",
    description="Hybrid Zomato filter + LLM ranking API",
)

_cors_kwargs: dict[str, Any] = {
    "allow_origins": _cors_origins(),
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
_origin_regex = _cors_origin_regex()
if _origin_regex:
    # Validate at startup so a bad regex fails loudly in deploy logs.
    re.compile(_origin_regex)
    _cors_kwargs["allow_origin_regex"] = _origin_regex

app.add_middleware(CORSMiddleware, **_cors_kwargs)


class RecommendRequest(BaseModel):
    location: str = Field(..., min_length=1)
    budget: str = Field(..., description="low | medium | high")
    cuisine: str = ""
    min_rating: float = Field(4.0, ge=0.0, le=5.0)
    additional_preferences: str = ""
    max_recommendations: int = Field(5, ge=1, le=10)
    use_llm: bool = True


def _build_meta() -> dict[str, Any]:
    frame = get_restaurants()
    settings = get_settings()

    cities = (
        frame["location"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .value_counts()
        .index.tolist()
    )
    localities = (
        frame["locality"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .value_counts()
        .index.tolist()
    )

    location_options: list[str] = []
    for city in cities:
        if city not in location_options:
            location_options.append(city)
    for locality in localities:
        if locality not in location_options:
            location_options.append(locality)

    cuisine_counts: dict[str, int] = {}
    for value in frame["cuisines"].dropna().astype(str):
        for part in value.split(","):
            name = part.strip()
            if name:
                cuisine_counts[name] = cuisine_counts.get(name, 0) + 1
    cuisines = sorted(
        cuisine_counts.keys(),
        key=lambda c: (-cuisine_counts[c], c.lower()),
    )

    return {
        "rows": len(frame),
        "location_options": location_options,
        "cuisine_options": [ANY_CUISINE] + cuisines,
        "default_location": cities[0]
        if cities
        else (location_options[0] if location_options else "Bangalore"),
        "llm_model": settings.llm_model,
        "llm_configured": bool(settings.llm_api_key),
        "any_cuisine_label": ANY_CUISINE,
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    """Liveness probe for Railway healthchecks."""
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    """Convenience root for platform URL smoke tests."""
    return {"service": "biterank-api", "docs": "/docs", "health": "/api/health"}


@app.get("/api/meta")
def meta() -> dict[str, Any]:
    try:
        return _build_meta()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Processed restaurant data not found. "
                "Run `python scripts/prepare_data.py` first."
            ),
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/recommend")
def recommend_endpoint(body: RecommendRequest) -> dict[str, Any]:
    settings = get_settings()
    cuisine = body.cuisine.strip()
    if cuisine == ANY_CUISINE:
        cuisine = ""

    response = recommend(
        location=body.location,
        budget=body.budget,
        cuisine=cuisine,
        min_rating=body.min_rating,
        additional_preferences=body.additional_preferences,
        max_recommendations=body.max_recommendations,
        use_llm=body.use_llm and bool(settings.llm_api_key),
    )
    return response.to_dict()
