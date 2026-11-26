"""Dataset loading and preprocessing.

Heavy Hugging Face `datasets` imports are lazy so the Railway API can load
processed parquet without installing the `datasets` package.
"""

from __future__ import annotations

from typing import Any

from src.ingestion.preprocess import (
    preprocess_restaurants,
    print_quality_summary,
    processed_path,
    save_processed,
    summarize_quality,
)

__all__ = [
    "load_raw_dataframe",
    "raw_cache_path",
    "preprocess_restaurants",
    "print_quality_summary",
    "processed_path",
    "save_processed",
    "summarize_quality",
]


def __getattr__(name: str) -> Any:
    if name in {"load_raw_dataframe", "raw_cache_path"}:
        from src.ingestion.load_dataset import load_raw_dataframe, raw_cache_path

        exports = {
            "load_raw_dataframe": load_raw_dataframe,
            "raw_cache_path": raw_cache_path,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
