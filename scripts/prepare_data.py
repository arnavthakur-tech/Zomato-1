"""Phase 1: download, preprocess, and summarize the Zomato restaurant store."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import get_settings
from src.ingestion import (
    load_raw_dataframe,
    preprocess_restaurants,
    print_quality_summary,
    save_processed,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare processed Zomato restaurant data.")
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Ignore local raw cache and reload from Hugging Face.",
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Skip writing the CSV companion file.",
    )
    args = parser.parse_args()

    settings = get_settings()
    print(f"Dataset: {settings.hf_dataset_id} @ {settings.hf_dataset_revision}")

    raw_df = load_raw_dataframe(force_download=args.force_download)
    print(f"Loaded raw rows: {len(raw_df)} | columns: {list(raw_df.columns)}")

    cleaned = preprocess_restaurants(raw_df)
    out_path = save_processed(cleaned, also_csv=not args.no_csv)

    print_quality_summary(cleaned)
    print(f"Wrote processed store: {out_path}")
    if not args.no_csv:
        print(f"Also wrote CSV:       {out_path.with_suffix('.csv')}")


if __name__ == "__main__":
    main()
