# Zomato Restaurant Recommendation System

LLM-powered restaurant recommendations over the Zomato dataset (Hugging Face): deterministic preference filters first, then LLM ranking and explanations.

See `Docs/` for the problem statement, architecture, implementation plan, and edge cases.

## Project layout

```text
Zomato/
├── Docs/                  # Project documentation
├── data/
│   ├── raw/               # Optional HF extract cache
│   └── processed/         # Cleaned restaurant table (Phase 1+)
├── src/
│   ├── config.py          # Env-based settings
│   ├── ingestion/         # Dataset load + preprocess
│   ├── preferences/       # Preference schema + validation
│   ├── filtering/         # Hard constraint filters
│   ├── llm/               # Prompt, client, response parser
│   ├── orchestrator/      # End-to-end recommend pipeline
│   ├── api/               # FastAPI for Next.js frontend
│   └── ui/                # Streamlit fallback demo
├── web/                   # Next.js BiteRank UI (primary)
├── prompts/               # Prompt templates (Phase 3)
├── scripts/               # Utility / smoke scripts
├── .env.example
├── requirements.txt
└── README.md
```

## Setup (Phase 0)

### 1. Create a virtual environment

```powershell
cd C:\Users\LENOVO\Downloads\Zomato
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set at least:

- `LLM_API_KEY` — your [Groq](https://console.groq.com/keys) API key (needed from Phase 3; `GROQ_API_KEY` also works)
- `LLM_MODEL` — Groq model name (default `openai/gpt-oss-20b`)
- `HF_DATASET_ID` — Hugging Face dataset id

Never commit `.env`.

### 4. Verify the skeleton

```powershell
python scripts\hello_world.py
```

You should see `Phase 0 hello-world OK` plus path/import checks.

## Prepare data (Phase 1)

Download the Hugging Face Zomato dataset, clean it, and write `data/processed/restaurants.parquet`:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\prepare_data.py
```

Re-run safely (uses `data/raw/zomato_raw.parquet` cache). Force a fresh HF download with:

```powershell
python scripts\prepare_data.py --force-download
```

## Filter candidates (Phase 2)

Validate preferences and print a deterministic shortlist (no LLM):

```powershell
python scripts\filter_demo.py --scenario good
python scripts\filter_demo.py --scenario empty
python scripts\filter_demo.py --scenario invalid
python scripts\filter_demo.py --location Bangalore --budget medium --cuisine Italian --min-rating 4.0
python scripts\test_phase2.py
```

## LLM ranking (Phase 3)

Uses **Groq** to rank filtered candidates and write explanations. Hallucinated restaurants are dropped; if Groq/parse fails, results fall back to rating order.

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and set LLM_API_KEY to your Groq key

python scripts\test_phase3.py
python scripts\llm_rank_demo.py --scenario italian_family
python scripts\llm_rank_demo.py --scenario north_indian_low
python scripts\llm_rank_demo.py --scenario chinese_date
python scripts\llm_rank_demo.py --fallback-only
```

## Run the app (Phase 4+)

End-to-end pipeline: validate preferences → hard filters → Groq rank/explain → display.

### Primary UI — Next.js + FastAPI (BiteRank)

Two terminals:

```powershell
# Terminal 1 — API (port 8000)
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8000
```

```powershell
# Terminal 2 — frontend (port 3000)
cd web
npm install
npm run dev
```

Open **http://localhost:3000**. The UI calls `GET /api/meta` and `POST /api/recommend` on the FastAPI backend (`NEXT_PUBLIC_API_URL` defaults to `http://localhost:8000` via `web/.env.local`).

Screens: Recommend (preference rail + AI shortlist) and About. Loading, empty, validation, and fallback states are handled in the UI. If Groq is unavailable, results fall back to rating-sorted filter matches.

### Optional — Streamlit fallback

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\test_phase4.py
streamlit run src\ui\app.py
```

## Deploy (free): Railway + Vercel

Stack: **FastAPI on Railway**, **Next.js on Vercel**, **Groq** for LLM.

Ensure `data/processed/restaurants.parquet` exists locally (from `python scripts/prepare_data.py`) and is committed — it is allowlisted in `.gitignore` so the API can boot without downloading Hugging Face data on Railway.

### 1. Backend — Railway

1. Push this repo to GitHub/GitLab.
2. In [Railway](https://railway.app): **New Project → Deploy from GitHub** → select this repo.
3. Railway should pick up `nixpacks.toml` / `Procfile` and start:
   `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
4. In the service **Variables**, set at least:

| Variable | Example |
|---|---|
| `LLM_API_KEY` | your Groq key |
| `LLM_MODEL` | `openai/gpt-oss-20b` |
| `CORS_ORIGINS` | `http://localhost:3000,https://YOUR_APP.vercel.app` |
| `CORS_ORIGIN_REGEX` | `https://.*\.vercel\.app` (optional; covers preview URLs) |

5. Generate a public domain (**Settings → Networking → Generate Domain**).
6. Smoke-test: `https://YOUR_RAILWAY_URL/api/health` → `{"status":"ok"}`.

Lean install file for the API: `requirements-api.txt` (full local install remains `requirements.txt`).

### 2. Frontend — Vercel

1. In [Vercel](https://vercel.com): **Add New Project** → import the same repo.
2. Set **Root Directory** to `web`.
3. Framework preset: **Next.js** (default build/start is fine).
4. Environment variable:

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://YOUR_RAILWAY_URL` (no trailing slash) |

5. Deploy. Copy the Vercel URL into Railway `CORS_ORIGINS`, then redeploy the API if needed.

### 3. Local ↔ production env files

| File | Purpose |
|---|---|
| `.env` / `.env.example` | API secrets + `CORS_*` |
| `web/.env.local` / `web/.env.example` | `NEXT_PUBLIC_API_URL` for the UI |

Never commit real `.env` or `.env.local` files.

## Documentation

| Doc | Description |
|---|---|
| `Docs/problemStatement.md` | Product goals and workflow |
| `Docs/architecture.md` | System design |
| `Docs/implementation-plan.md` | Phase-wise build plan |
| `Docs/edge-case.md` | Edge cases and fallbacks |
| `Docs/deployment-plan.md` | Vercel + Railway free deploy plan |
