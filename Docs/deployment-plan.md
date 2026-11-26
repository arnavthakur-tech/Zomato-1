# BiteRank Deployment Plan

Deploy the Zomato / BiteRank recommendation system for free using:

| Layer | Platform | Role |
|---|---|---|
| Frontend | **Vercel** | Next.js UI (`web/`) |
| Backend | **Railway** | FastAPI API (`src/api/`) |
| LLM | **Groq** | Ranking + explanations |

Local Streamlit (`src/ui/`) is **not** part of this production path.

---

## 1. Architecture (production)

```text
Browser
   │
   ▼
Vercel (Next.js)
   │  NEXT_PUBLIC_API_URL
   ▼
Railway (FastAPI / uvicorn)
   ├── data/processed/restaurants.parquet
   └── Groq API (LLM_API_KEY)
```

**Request flow**

1. UI loads options via `GET /api/meta`
2. User submits preferences → `POST /api/recommend`
3. API filters candidates → ranks/explains with Groq (or rating fallback)
4. JSON results render in the BiteRank UI

**Health check:** `GET /api/health` → `{"status":"ok"}`

---

## 2. Prerequisites

Before deploying:

- [ ] GitHub (or GitLab) account
- [ ] [Railway](https://railway.app) account
- [ ] [Vercel](https://vercel.com) account
- [ ] [Groq](https://console.groq.com/keys) API key
- [ ] Local processed data present:
  ```powershell
  python scripts\prepare_data.py
  ```
  Confirm `data/processed/restaurants.parquet` exists (~0.4 MB).  
  This file is allowlisted in `.gitignore` so it can be committed and shipped with the API.

- [ ] Repo initialized and pushed (this project may start without git):
  ```powershell
  cd C:\Users\LENOVO\Downloads\Zomato
  git init
  git add .
  git commit -m "Prepare BiteRank for Railway + Vercel deploy"
  # create remote on GitHub, then:
  git branch -M main
  git remote add origin https://github.com/<you>/<repo>.git
  git push -u origin main
  ```

Do **not** commit `.env`, `web/.env.local`, or any real API keys.

---

## 3. Repo deploy artifacts (already in project)

| File | Purpose |
|---|---|
| `requirements-api.txt` | Lean Python deps for Railway (no Streamlit / HF datasets) |
| `Procfile` | `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT` |
| `Dockerfile` | Reliable Railway image: Python 3.12 + `requirements-api.txt` |
| `railway.toml` | `DOCKERFILE` builder + `/api/health` healthcheck |
| `nixpacks.toml` | Fallback only (Railway uses Dockerfile now) |
| `runtime.txt` | Python 3.12 pin |
| `.env.example` | API + CORS variable template |
| `web/.env.example` | `NEXT_PUBLIC_API_URL` template |
| `web/vercel.json` | Next.js framework hint for Vercel |
| `src/api/main.py` | CORS from `CORS_ORIGINS` / `CORS_ORIGIN_REGEX` (Vercel regex default on Railway) |
| `web/src/lib/api.ts` | Calls Railway via `NEXT_PUBLIC_API_URL` (trailing slash stripped) |

---

## 4. Environment variables

### 4.1 Railway (backend)

| Variable | Required | Example / notes |
|---|---|---|
| `LLM_API_KEY` | Yes (for LLM ranking) | Groq key; `GROQ_API_KEY` also accepted |
| `LLM_MODEL` | No | Default `openai/gpt-oss-20b` |
| `LLM_TIMEOUT_SECONDS` | No | Default `45` |
| `LLM_MAX_RETRIES` | No | Default `3` |
| `CANDIDATE_CAP` | No | Default `20` |
| `CORS_ORIGINS` | Yes (prod) | Comma-separated origins, e.g. `http://localhost:3000,https://biterank.vercel.app` |
| `CORS_ORIGIN_REGEX` | Optional | Defaults to `https://.*\.vercel\.app` on Railway when unset; set empty to disable |
| `PORT` | Auto | Set by Railway; do not hardcode |

`HF_DATASET_*` is only needed if you re-run data prep on the server (not required when parquet is committed).

### 4.2 Vercel (frontend)

| Variable | Required | Example / notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Yes | Railway public URL, **no trailing slash** — e.g. `https://biterank-api-production.up.railway.app` |

Used by `web/src/lib/api.ts` for `/api/meta` and `/api/recommend`.

---

## 5. Deployment sequence

Deploy **backend first**, then frontend, then lock CORS.

### Phase A — Railway (API)

1. Open Railway → **New Project** → **Deploy from GitHub** → select this repo.
2. Confirm root is the repo root (not `web/`).
3. Wait for first build. Start command should be:
   ```text
   uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
   ```
4. **Variables** → add `LLM_API_KEY`, `LLM_MODEL`, and a temporary CORS value:
   ```text
   CORS_ORIGINS=http://localhost:3000
   ```
   (`CORS_ORIGIN_REGEX` defaults to Vercel hosts on Railway; override only if needed.)
5. **Settings → Networking → Generate Domain** → copy the HTTPS URL.
6. Verify:
   ```text
   GET https://<railway-url>/api/health
   GET https://<railway-url>/api/meta
   ```
   Expect health `ok` and meta with location/cuisine lists.

**Rollback:** Redeploy a previous successful deployment from Railway’s deployment history.

### Phase B — Vercel (UI)

1. Open Vercel → **Add New Project** → import the same repo.
2. Set **Root Directory** to `web`.
3. Framework: **Next.js** (default `npm run build` / `next start`).
4. Environment Variables → Production (and Preview if desired):
   ```text
   NEXT_PUBLIC_API_URL=https://<railway-url>
   ```
5. Deploy. Copy the production URL (e.g. `https://<app>.vercel.app`).

**Note:** `NEXT_PUBLIC_*` is baked in at build time. Changing the Railway URL later requires a Vercel redeploy.

### Phase C — Wire CORS

1. On Railway, update:
   ```text
   CORS_ORIGINS=http://localhost:3000,https://<app>.vercel.app
   CORS_ORIGIN_REGEX=https://.*\.vercel\.app
   ```
2. Redeploy the API (or restart) so CORS picks up the new values.
3. Open the Vercel URL → run a recommendation → confirm no browser CORS errors.

---

## 6. Post-deploy verification checklist

| Check | How | Pass |
|---|---|---|
| API up | `/api/health` | `{"status":"ok"}` |
| Data loaded | `/api/meta` | `rows` > 0, location/cuisine options present |
| LLM configured | `/api/meta` | `llm_configured: true` |
| UI loads | Open Vercel URL | Recommend + About screens render |
| Happy path | Submit prefs with matches | Shortlist + explanations |
| Empty path | Impossible filters | No-matches / empty state |
| Fallback | Invalid/missing Groq key | Rating-sorted results still return |
| CORS | Browser Network tab | No blocked cross-origin errors |
| Mobile | Phone / DevTools | Layout usable |

---

## 7. Operational notes

### Cold starts & free tiers
- Railway free/trial usage is limited by monthly credits; services may sleep or need spend caps watched.
- First request after idle can be slower — healthcheck helps catch dead deploys.

### Secrets
- Store keys only in Railway / Vercel dashboards.
- Rotate Groq key if it was ever committed or shared.

### Data updates
1. Re-run `python scripts/prepare_data.py` locally (or `--force-download`).
2. Commit updated `data/processed/restaurants.parquet`.
3. Push → Railway redeploys automatically.

### CORS changes
Any new production frontend host must be added to `CORS_ORIGINS` (or covered by `CORS_ORIGIN_REGEX`).

### Local development (unchanged)

```powershell
# Terminal 1 — API
uvicorn src.api.main:app --reload --port 8000

# Terminal 2 — UI
cd web
npm run dev
```

`web/.env.local`:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 8. Failure playbook

| Symptom | Likely cause | Fix |
|---|---|---|
| Railway build fails on pip | Wrong requirements / Python | Confirm `nixpacks.toml` installs `requirements-api.txt`; check Python 3.12 |
| `/api/meta` → 503 | Missing parquet | Commit `data/processed/restaurants.parquet` and redeploy |
| UI “Failed to fetch” | Wrong `NEXT_PUBLIC_API_URL` or CORS | Fix Vercel env (redeploy UI); fix Railway `CORS_ORIGINS` |
| CORS error in browser | Origin not allowed | Add Vercel URL to `CORS_ORIGINS` or set regex |
| Recommendations without AI copy | Groq key missing/invalid | Set `LLM_API_KEY`; check Railway logs |
| Slow / timeout on recommend | Groq latency or cold start | Raise `LLM_TIMEOUT_SECONDS`; retry; check Groq status |
| Vercel build fails | `web/` deps / Node | Ensure Root Directory is `web`; clear cache & redeploy |

---

## 9. Out of scope (this plan)

- Custom domains / DNS
- CI (GitHub Actions) beyond platform auto-deploy on push
- Auth, rate limiting, or paid Railway/Vercel upgrades
- Deploying Streamlit Community Cloud
- Running Hugging Face download inside Railway at boot

---

## 10. Suggested order of work (summary)

1. Prepare & commit parquet + push repo  
2. Deploy API on Railway + set Groq key + temp CORS  
3. Smoke-test `/api/health` and `/api/meta`  
4. Deploy UI on Vercel with `NEXT_PUBLIC_API_URL`  
5. Finalize `CORS_ORIGINS` with the Vercel URL  
6. Run the verification checklist  

When all checklist rows pass, the free Vercel + Railway deployment is complete.
