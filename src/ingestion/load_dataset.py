"""Load the Zomato dataset from Hugging Face with optional local caching."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from datasets import load_dataset

from src.config import DATA_RAW_DIR, get_settings

RAW_CACHE_NAME = "zomato_raw.parquet"

# Drop bulky text blobs that are unused by the recommendation pipeline.
DROP_COLUMNS = {
    "reviews_list",
    "menu_item",
    "dish_liked",
    "url",
    "address",
    "phone",
}


def raw_cache_path(cache_dir: Path | None = None) -> Path:
    return (cache_dir or DATA_RAW_DIR) / RAW_CACHE_NAME


def _slim_raw_frame(df: pd.DataFrame) -> pd.DataFrame:
    keep = [c for c in df.columns if c not in DROP_COLUMNS]
    return df.loc[:, keep].copy()


def load_raw_dataframe(
    *,
    dataset_id: str | None = None,
    revision: str | None = None,
    split: str = "train",
    cache_dir: Path | None = None,
    use_cache: bool = True,
    force_download: bool = False,
) -> pd.DataFrame:
    """
    Load the configured Hugging Face dataset as a pandas DataFrame.

    If ``use_cache`` is True and a raw parquet cache exists, load from disk
    unless ``force_download`` is set.
    """
    settings = get_settings()
    dataset_id = dataset_id or settings.hf_dataset_id
    revision = revision or settings.hf_dataset_revision
    cache_path = raw_cache_path(cache_dir)

    if use_cache and not force_download and cache_path.exists():
        return pd.read_parquet(cache_path)

    ds = load_dataset(dataset_id, split=split, revision=revision)
    df = _slim_raw_frame(ds.to_pandas())

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path, index=False)
    return df
