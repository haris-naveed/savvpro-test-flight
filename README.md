# FlightHub

Small full-stack app for a fake travel agency: FastAPI + SQLite in the back, Express serving a vanilla HTML/JS UI on port 3000. Staff can list/search flights, book seats, look up bookings, and cancel.

**Prerequisites:** Python **3.10+**, Node **18+**.

### Backend

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix:   source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn main:app --reload --app-dir backend
```

API listens on **http://localhost:8000** (or use **127.0.0.1** — same thing for local dev).

### Frontend

```bash
cd frontend
npm install
node app.js
```

UI is at **http://localhost:3000**. **Start the backend first**, then the frontend — the page calls the API on port 8000 and will look broken if nothing is listening there.

### Tests

```bash
cd backend && pytest ../tests/ -v
```

If that complains it can’t import `backend`, run from the project root instead: `python -m pytest tests/ -v` (same venv, `pip install -r backend/requirements.txt` already done).
