# AI usage log — FlightHub assessment

## Progress log

### Session — project scaffold and backend run fix

**Goal I set:** Stand up the repo layout (FastAPI backend, Express frontend) and be able to run the API without import errors.

**Prompts I used (paraphrased where needed):**

1. *Create the folder structure for a fullstack project: FastAPI Python backend, Express Node frontend serving HTML; list specific files (`backend/main.py` with `GET /health`, placeholders, `frontend/app.js`, `public/index.html`, `package.json`, `.gitignore`, etc.).*

2. *Resolve error: `Could not import module "main"` when running `uvicorn main:app --reload` from the repo root (terminal snippet attached).*

**What the AI produced:**

- Backend/frontend files and `.gitignore` as specified; `backend/routes/__init__.py` (Python package convention) instead of a literal `init.py` name — I accepted that after confirming it matches normal Python layout.
- For the uvicorn error: a **root `main.py`** that re-exports `app` from `backend.main`, plus **`backend/__init__.py`** so `backend` is a package.

**Mistakes / risks I checked:**

- **Wrong working directory:** The failure was because `main.py` lived under `backend/` while uvicorn was started from the repository root. I did not treat the first AI answer as sufficient until I verified the fix matched how I want to run the server (from root).
- **Duplicate or confusing entrypoints:** I reviewed the shim so it only re-exports `app` and does not duplicate route logic.
- **Shell vs docs:** When the agent smoke-tested installs, its first command used `&&` (fails on older PowerShell). The agent retried with `;` — I noted that local shell syntax matters for my own CI/scripts later.

**How I directed the AI:**

- I supplied **exact file paths and acceptance criteria** (health JSON shape, port 3000, static `public/`, dependency lists).
- For the bug, I **pasted the real terminal output** so the fix targeted the actual error, not a generic “uvicorn tutorial.”
- I **kept scope tight** (scaffold + import path fix) and did not ask for refactors or extra features.

**Testing I did (or will do) after AI changes:**

- Run `uvicorn main:app --reload` from the repo root and confirm `/health` returns `{"status":"ok"}`.
- Run the frontend with `npm install` / `npm start` and load `index.html` in the browser when that part of the task needs verification.

---

*I will append new dated entries here as the assessment continues: prompts, AI outputs reviewed, mistakes caught, and corrections applied.*
