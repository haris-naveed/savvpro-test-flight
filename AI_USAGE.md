# AI usage log (required)

This file is the **AI usage log** for this repository, as required by the assessment. It records **specific prompts**, **mistakes the AI made**, **how I corrected them**, and **how I directed the work** so it is clear I steered the AI—not the other way around.

---

## Session 1 — Fullstack scaffold and fixing `uvicorn` import

### Specific prompts I used

1. “Create the folder structure for a fullstack project: backend is FastAPI Python, frontend is Express Node serving HTML. I need: `backend/main.py` with GET `/health` returning `{"status": "ok"}`, `backend/models.py` / `database.py` / `schemas.py` as commented placeholders, `backend/routes/` with empty `__init__.py`, `backend/requirements.txt` with fastapi uvicorn sqlalchemy pydantic pytest httpx, `frontend/app.js` Express on port 3000 serving `public/`, `frontend/public/index.html` with title FlightHub and h1 FlightHub, `frontend/package.json` name `flighthub-frontend` with express, `.gitignore` for Python/Node/`*.db`/`.env`.”

2. “Resolve error:” + pasted terminal output showing `uvicorn main:app --reload` from repo root and `Could not import module "main"`.

### Mistakes the AI made and how I corrected them

| Mistake | How I corrected it |
|--------|----------------------|
| The AI assumed imports like `from database import …` inside `backend/` would work when the app is loaded as `backend.main` from the repo root. That would raise `ModuleNotFoundError` once we added real modules. | I caught this when we moved beyond the empty placeholders: I had the AI use **package-relative imports** with a **`__package__` fallback** so both `from backend.main import app` (root) and `uvicorn main:app` from inside `backend/` keep working. |
| During an automated smoke test, the AI used `&&` between commands, which **fails on older PowerShell**. | I treated that as a bad pattern for my machine: I run or rewrite commands using **`;`** (or separate lines) and do not copy shell one-liners blindly. |
| N/A for “wrong fix” on the first import error: the **root cause** was my **cwd** (repo root) vs where `main.py` lived. | I **pasted the real error** and constrained the fix to “works when I start uvicorn from the repo root,” then **verified** by running the server myself. |

### How I directed the AI (I led; the AI did not lead)

- I gave a **fixed file list** and **exact behaviors** (health JSON, port 3000, static `public/`, dependency names).
- For the bug, I supplied **evidence** (terminal snippet) and **success criteria** (import path / run location), instead of asking for a generic tutorial.
- I **rejected scope creep**: scaffold + import fix only—no extra routes or refactors in that step.
- I **reviewed** the shim (`root/main.py` re-export) so it stays a thin entrypoint and does not duplicate app logic.

---

## Session 2 — SQLAlchemy SQLite schema, models, startup seed

### Specific prompts I used

1. “Set up the database. In `backend/database.py` use SQLAlchemy with SQLite file `flighthub.db`: create engine, `SessionLocal`, `Base`, and a `get_db` dependency for FastAPI. In `backend/models.py` create `Flight` and `Booking` with [full column list…]. Add relationship on `Booking` named `flight`. In `backend/main.py` import `Base` and `engine`, call `Base.metadata.create_all` on startup, add startup event that seeds 8 sample flights if the flights table is empty—real city names, mixed prices/durations/availability, **2 flights with only 1 available seat**. Do not touch routes yet.”

### Mistakes the AI made and how I corrected them

| Mistake | How I corrected it |
|--------|----------------------|
| First version used **non-package imports** (`from database import …`) in `main.py` / `models.py`, which **breaks** when the app is imported as `backend.main` from the repo root (`ModuleNotFoundError: No module named 'database'`). | I required **relative imports** (`from .database`, `from .models`) **plus** the same **`__package__` / flat fallback** pattern as above so both entry styles work. |
| (Risk, not a committed bug) Seeding or paths could silently target the **wrong cwd** for `flighthub.db`. | I kept the DB path **anchored to `Path(__file__).resolve().parent`** so the file lands next to `database.py` regardless of where I start the process, and I **verified** with a local import / `TestClient` run. |

### How I directed the AI (I led; the AI did not lead)

- I specified **storage** (SQLite filename), **ORM surface** (`engine`, session, `get_db`, `Base`), **exact tables/columns/constraints**, and **seed rules** (8 rows, diversity, **two flights with `available_seats == 1`**).
- I explicitly said **do not touch routes yet** to avoid unsolicited API surface.
- After the AI produced code, I **validated behavior** (metadata created, eight flights present) instead of assuming correctness.

---

## Commands I ran to verify (optional trace)

- `uvicorn main:app --reload` from repo root — confirm server starts after import fixes.
- `python -c` / `TestClient` against `backend.main` — confirm startup, `create_all`, and seed insert **8** flights.
- `npm install` / `npm start` — confirm the Express scaffold serves `public/` when I exercise the frontend.

---

*For new work: add a new dated/session section with the same three subsections—**Specific prompts**, **Mistakes & corrections**, **How I directed the AI**.*
