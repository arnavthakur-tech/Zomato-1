"""Phase 0 smoke check: verify core imports and project paths."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    import pandas as pd
    from dotenv import dotenv_values

    from src.config import (
        DATA_PROCESSED_DIR,
        DATA_RAW_DIR,
        PROMPTS_DIR,
        ROOT_DIR,
        get_settings,
    )

    settings = get_settings()
    env_example = ROOT_DIR / ".env.example"

    print("Phase 0 hello-world OK")
    print(f"  root:            {ROOT_DIR}")
    print(f"  data/raw:        {DATA_RAW_DIR.exists()}")
    print(f"  data/processed:  {DATA_PROCESSED_DIR.exists()}")
    print(f"  prompts:         {PROMPTS_DIR.exists()}")
    print(f"  .env.example:    {env_example.exists()}")
    print(f"  pandas:          {pd.__version__}")
    print(f"  HF dataset id:   {settings.hf_dataset_id}")
    print(f"  LLM model:       {settings.llm_model}")
    print(f"  candidate cap:   {settings.candidate_cap}")
    print(f"  API key set:     {bool(settings.llm_api_key)}")
    print(f"  env example keys:{list(dotenv_values(env_example).keys())}")


if __name__ == "__main__":
    main()
