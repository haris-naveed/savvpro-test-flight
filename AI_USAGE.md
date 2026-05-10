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

## Session 3 — Pydantic v2 API schemas (`backend/schemas.py`)

### Specific prompts I used

1. “Write Pydantic v2 schemas in `backend/schemas.py`. **FlightResponse:** `id`, `origin`, `destination`, `departure_datetime`, `duration_minutes`, `price_per_seat`, `total_seats`, `available_seats`; use `model_config = ConfigDict(from_attributes=True)`. **BookingCreate:** `flight_id` int, `passenger_name` str (min 2 chars, strip whitespace), `passport_number` str (min 5 chars), `seat_number` str; add a `field_validator` that rejects blank strings for `passenger_name` and `passport_number`. **BookingResponse:** `booking_reference`, `flight_id`, `passenger_name`, `passport_number`, `seat_number`, `status`, `created_at` datetime; nested field `flight` of type `FlightResponse`; use `ConfigDict(from_attributes=True)`. **CancellationResponse:** `booking_reference` str, `status` str, `message` str. No routes yet, just schemas.”

### Mistakes the AI made and how I corrected them

| Mistake | How I corrected it |
|--------|----------------------|
| None in the final merged code that I kept. | I still **spot-checked** edge cases myself: whitespace-only names must fail after strip, stripped values must satisfy `min_length`, and imports must load under `from backend.schemas import …` from the repo root. |
| (Common pitfall I watched for) **Validator vs constraint order** for “strip → not blank → min length” can be easy to get wrong in Pydantic v2. | I had the AI use a **`mode="before"`** validator that strips and rejects empty strings, then rely on **`Field(..., min_length=…)`** on the stripped values; I confirmed with short `python -c` runs (e.g. `"  Jo  "` → `"Jo"`, `"   "` → validation error). |

### How I directed the AI (I led; the AI did not lead)

- I pinned the **Pydantic major version** (v2) and required **`ConfigDict(from_attributes=True)`** only where specified, so responses stay ORM-friendly without extra guessing.
- I spelled out **every model, field, nesting rule, and validation rule** (including **which fields** get the blank-string validator) instead of asking for “generic DTOs.”
- I explicitly said **no routes yet, just schemas** to block unsolicited FastAPI endpoints.
- After the AI edited the file, I **ran small validation checks** rather than assuming the validators behaved as intended.

---

## Session 4 — Flight routes (`backend/routes/flights.py`) + app wiring

### Specific prompts I used

1. “Create `backend/routes/flights.py` with an `APIRouter` prefix `/flights`. **GET `/flights`** — return all flights as a list, status **200**. **GET `/flights/search`** — query params: `origin` optional str, `destination` optional str, `date` optional str format **YYYY-MM-DD**; filter **case insensitive**; if no results return **404** with detail **`No flights found matching your criteria`**; if results return **200** with list. **GET `/flights/{flight_id}`** — return single flight or **404** **`Flight not found`**. In `backend/main.py` import and register this router. Also add **CORS** middleware allowing **`http://localhost:3000`**. Use **`get_db`** dependency injection for **all** endpoints.”

### Mistakes the AI made and how I corrected them

| Mistake | How I corrected it |
|--------|----------------------|
| The first cut named the search query parameter `date`, which **shadowed** Python’s `datetime.date` type, so `date.fromisoformat(...)` would have called the **wrong object** at runtime. | I renamed the function argument (e.g. `date_value`) and kept the **public query name** `date` using **`Query(alias="date")`**, so the URL stays `?date=` and parsing uses **`date.fromisoformat`** correctly. |
| (Pitfall I enforced in the same change) **`/search` must be registered before** **`/{flight_id}`** or FastAPI may treat `"search"` as an ID. | I kept **`/search`** **above** the dynamic route in the router module and **smoke-tested** with `TestClient` so search and detail behave independently. |
| The prompt did not specify behavior for a **malformed** `date` string. | I kept a **`422`** response with a clear detail for bad `YYYY-MM-DD` input so invalid params are not confused with “no matching flights” (**404**). |

### How I directed the AI (I led; the AI did not lead)

- I specified **exact paths**, **HTTP statuses**, and **exact `detail` strings** for the two 404 cases so the API matches the task wording.
- I required **`Depends(get_db)` on every handler**, **`FlightResponse`** for list/detail payloads, and **`prefix="/flights"`** on the router—no extra booking endpoints in that step.
- I called out **CORS** explicitly (**`http://localhost:3000` only**) and **router registration** in **`main.py`** next to existing app setup.
- After the code landed, I **ran automated requests** (list, detail 404, search match / no match, invalid date) instead of assuming routing and filters were correct.

---

## Session 5 — Booking routes (`backend/routes/bookings.py`) + router registration

### Specific prompts I used

1. “Create `backend/routes/bookings.py` with `APIRouter` prefix `/bookings`. **POST `/bookings`** — accepts `BookingCreate` body. Rules in order: check flight exists (**404** if not); check **`available_seats > 0`**, if zero return **409** with detail **`No seats available on this flight`**; generate **`booking_reference`**: take **`uuid4`**, uppercase first **8** chars; decrement **`available_seats`** by 1; save booking status **confirmed**; commit and return **`BookingResponse`** with **201**. **GET `/bookings`** — query params **`passenger_name`** optional or **`booking_reference`** optional; if neither provided return **400** **`Provide passenger_name or booking_reference to search`**; search **`passenger_name`** case insensitive **contains** match, **`booking_reference`** **exact** match; return list of **`BookingResponse`** with nested **`flight`**. **DELETE `/bookings/{booking_reference}`** — find booking, **404** if not found; if status already cancelled return **409** **`Booking is already cancelled`**; set status to **cancelled**, increment **`flight.available_seats`** by 1, commit; return **`CancellationResponse`**. Register this router in **`main.py`.”

### Mistakes the AI made and how I corrected them

| Mistake | How I corrected it |
|--------|----------------------|
| The first draft used **`func.instr`** for passenger substring search but **forgot to import `func`** from SQLAlchemy, which would **fail at import time**. | I added **`from sqlalchemy import func, or_, select`** and re-ran **`TestClient`** checks. |
| The prompt did not spell out **combining both** search fields when a user sends **`passenger_name` and `booking_reference` together**. | I chose **`OR`** (match name contains **or** reference equals) so results align with “lookup by name **or** reference” in `TASK.md` rather than over-narrow **AND**. |
| Risk: **`BookingResponse`** requires a nested **`flight`**; lazy loading can surprise you if the session is configured oddly. | After **`commit`**, I **refresh** the booking and touch **`booking.flight`** (or rely on **`selectinload`** on **GET**) so serialization always sees the related **`Flight`**. |

### How I directed the AI (I led; the AI did not lead)

- I specified a **strict ordering** of checks (**existence → capacity → reference → inventory mutation → commit**) and **exact HTTP status / `detail` strings** for **409/400/404** cases.
- I required **`uuid4`-derived references** (8-char uppercase hex from **`hex[:8]`**, equivalent to “first 8” of the hyphen-free form) and **`status="confirmed"`** on create.
- I scoped work to **`bookings.py` + `main.py` router include**—no unrelated refactors.
- I **verified** create/search/cancel flows against a **single-seat** seeded flight (second booking → **409**; after cancel → book again succeeds).

---

## Session 6 — Pytest API tests (`tests/test_api.py`, `tests/conftest.py`)

### Specific prompts I used

1. “Write tests in **`tests/test_api.py`** using **pytest** and FastAPI **`TestClient`**. **Setup:** use an **in-memory SQLite** database for tests, **override the `get_db` dependency** so tests **never touch `flighthub.db`**, **`create_all` tables fresh before each test**, seed **two flights**: one with **`available_seats=1`**, one with **`available_seats=5`**. Write these **6 tests**: **`test_get_flights`** — `GET /flights` returns **200** and a non-empty list; **`test_search_by_origin`** — search by a seeded origin returns **200** and matching results; **`test_book_flight_success`** — `POST /bookings` with valid data returns **201**, response has **`booking_reference`**, status **confirmed**; **`test_overbooking_blocked`** — book the single-seat flight twice, first **201**, second **409**; **`test_cancel_booking`** — book then cancel, cancel **200** and status cancelled, then check **`available_seats`** went back up by **1**; **`test_cancel_twice`** — cancel same booking twice, second **409**. **No mocking** — use **real SQLAlchemy** against in-memory DB.”

### Mistakes the AI made and how I corrected them

| Mistake | How I corrected it |
|--------|----------------------|
| The first implementation used **`sqlite:///:memory:`** with the default pool; **each new DB connection gets its own empty in-memory database**, so **`create_all` + seed** on one connection did not match **`TestClient`** / **`get_db`** on another → **`no such table: flights`**. | I switched the test engine to use **`sqlalchemy.pool.StaticPool`** so **all sessions share one connection** and one in-memory database. |
| **`Startup`** still imports **`engine`** into **`main`** by value; tests must **monkeypatch both** **`backend.database.engine`** and **`backend.main.engine`** (and **`SessionLocal`** in both modules) so **`create_all` on startup** hits the test engine, not **`flighthub.db`**. | I patched **`main.engine`**, **`main.SessionLocal`**, and disabled production **`_seed_sample_flights_if_empty`** in tests so only the **two** fixture flights exist. |

### How I directed the AI (I led; the AI did not lead)

- I required **isolation** from disk **`flighthub.db`** via **`dependency_overrides[get_db]`** plus engine/session **monkeypatches**, and **fresh schema + seed per test** (`drop_all` / `create_all` in an **autouse** fixture).
- I listed **exact test names** and **assertions** (status codes, overbooking **409**, double-cancel **409**, inventory **±1** after cancel).
- I insisted on **no mocks** for the ORM—only **real** SQLAlchemy + **`TestClient`** HTTP calls.
- I **ran `pytest tests/test_api.py -v`** and iterated until all **six** tests passed.

---

## Session 7 — Single-page UI (`frontend/public/index.html`)

### Specific prompts I used

1. “Build a **complete single page app** in **`frontend/public/index.html`**. **Vanilla HTML, CSS, JavaScript only**, no frameworks. Backend at **`http://localhost:8000`**. **Top navigation** with **4 tabs**: All Flights, Search, My Bookings, Book a Flight. **All Flights** (default): on load **`GET /flights`**, cards with route **ORIGIN → DESTINATION**, date/time, duration **Xh Ym**, price **$XX.XX per seat**, seats available, **Select & Book** → Book tab + pre-fill flight id. **Search**: origin, destination, date picker, **`GET /flights/search`**, same cards, **404** → ‘No flights found’. **Book**: **`POST /bookings`**, success green + reference, **409** red ‘fully booked’, **422** validation. **My Bookings**: one field name or reference, **`GET /bookings`**, badges, **Cancel** → **`DELETE`** + refresh. **Design**: clean blue, mobile, **loading** while fetching, **inline errors** (no `alert` except **`confirm`** for cancel).”

### Mistakes the AI made and how I corrected them

| Mistake | How I corrected it |
|--------|----------------------|
| Follow-up: UI stuck **loading** or **blank** with **no `fetch`** in DevTools—looked like the app never called the API. | I traced **two classes of issues**: (1) **HTML default** `#all-loading` had class **`visible`** so the spinner showed even when JS died; **`DOMContentLoaded`-only** init could miss running; **`loadAllFlights`** had work **outside** `try` so **`finally`** did not always hide the overlay. I had the AI **remove default `visible`**, call **`initApp()` immediately** at end of `<body>`, wrap startup in **`try/catch`**, and keep **`setLoading` in `finally`**. (2) **Fatal syntax error** in **`renderFlightCard`**: the last string literal ended with **`</button>";`** (wrong quote) instead of **`</button>';`**, so the **entire script failed to parse**—**no API calls**, Console error. I had the AI **fix the closing delimiter** and I verified with **`node --check`** on the extracted script. |
| Browsing the UI at **`http://127.0.0.1:3000`** while CORS only allowed **`http://localhost:3000`** would **block** cross-origin **`fetch`** (different browser **Origin**). | I had the AI add **`http://127.0.0.1:3000`** to **`CORSMiddleware`** **`allow_origins`** in **`backend/main.py`** alongside **`localhost`**, then **restart uvicorn**. |

### How I directed the AI (I led; the AI did not lead)

- I specified **stack constraints** (no frameworks), **exact tab names**, **endpoints**, **status handling**, and **UX** (loading, inline errors, `confirm` only for cancel).
- When integration broke, I supplied **DevTools evidence** (no XHR, JS error badge) and asked for **root-cause fixes**, not guesses.
- I required **proof** the script is valid (**`node --check`**) after the quote bug so the failure mode could not repeat silently.
- I connected **localhost vs 127.0.0.1** for **Origin** to **CORS allowlist** myself and had the backend updated accordingly.

---

## Session 8 — Book a flight: dropdown instead of flight ID

### Specific prompts I used

1. “In **book a flight** tab instead of manually enter the flight id replace it with the **dropdown** which shows all **available** flights, user can select any option **by default first flight is auto selected**.”

2. “**Continue** the booking dropdown work from the handoff: replace the number input with a `<select>` fed by **`GET /flights`**, default the **first** flight, keep **Select & Book** in sync, **re-fetch** after a **201** so seat labels update and **preserve** the booked **`flight_id`** when possible, don’t leave the control stuck on **Loading…** when **`loadAllFlights`** errors, **prefetch** options on startup if needed, style the **select** like the other book fields, and **verify** the inline script with **`node --check`**.”

### Mistakes the AI made and how I corrected them

| Mistake | How I corrected them |
|--------|----------------------|
| Early **`return`** paths inside **`loadAllFlights`** (bad HTTP response, bad JSON shape, missing container) **skipped** **`populateBookFlightSelect`**, so the Book tab could stay on **“Loading flights…”** forever. | I had the AI call **`populateBookFlightSelect([])`** (or the successful list on the happy path) on **every** exit from that flow, including **error** returns, so the select always reflects reality. |
| Only **`loadAllFlights`** filled the dropdown; if I opened **Book** before the all-flights request finished—or **`loadAllFlights` failed**—**Select & Book** could set a **value** on options that were not built yet. | I had the AI call **`loadBookFlightOptionsFromApi()`** at **app init** (parallel with **`loadAllFlights`**) so the dropdown populates sooner; I accepted an **extra **`GET /flights`** on cold start** as a tradeoff for simpler UX. |
| **`form.reset()`** after **201** clears the form; without an immediate **re-fetch**, the select could be wrong or empty until the next manual reload. | I had the AI **`await loadBookFlightOptionsFromApi(body.flight_id)`** after success so options and **seat counts** refresh and the **same flight** stays selected when it still exists. |

### How I directed the AI (I led; the AI did not lead)

- I constrained the change to the **Book** tab: **`<select>`** bound to **`GET /flights`**, **first option selected** when there is no prior choice, **`change`** drives the preview (no **number-input** debounce).
- I required **behavior after booking** (**201** / **409**): refresh from the API so **available seats** in the dropdown stay honest.
- I insisted on **guarding** submit when **no flight** is selected and on **re-running **`node --check`** on the extracted `<script>`** after edits.
- I kept scope **frontend-only** for this step (**`frontend/public/index.html`** + existing backend contract).

---

## Session 9 — AI usage log update (`AI_USAGE.md`)

### Specific prompts I used

1. “**Add last 2 prompts work** in **`@AI_USAGE.md`** file **according to rules**.”

### Mistakes the AI made and how I corrected them

| Mistake | How I corrected them |
|--------|----------------------|
| Risk: treating the log as a **third-person changelog** instead of the required **first-person** “I prompted / I corrected / I directed” voice. | I required **Session 8** and **Session 9** entries to **match** the same headings and tables as **Sessions 1–7**, with **verbatim-style** prompt quotes and concrete **mistake → correction** rows. |
| Risk: **vague** “we improved the UI” without tying rows to **files**, **endpoints**, and **verification** steps. | I had the AI tie Session 8 to **`populateBookFlightSelect`**, **`loadBookFlightOptionsFromApi`**, **`loadAllFlights`**, **`node --check`**, and this file for Session 9. |

### How I directed the AI (I led; the AI did not lead)

- I pointed at **`AI_USAGE.md`** as the **single source** for log structure and asked for the **last two** conversation prompts to be recorded **explicitly**.
- I required **no scope creep**: update **documentation only** for Session 9; implementation details belong under **Session 8**.

---

## Commands I ran to verify (optional trace)

- `uvicorn main:app --reload` from repo root — confirm server starts after import fixes.
- `node --check` on script extracted from `index.html` — confirm **no syntax errors** after fixes (including **book-flight `<select>`** changes).
- `python -m pytest tests/test_api.py -v` — **6** API tests against in-memory SQLite.
- `python -c` / `TestClient` against `backend.main` — confirm startup, `create_all`, and seed insert **8** flights.
- `python -c` / `TestClient` — **`GET /flights`**, **`GET /flights/{id}`**, **`GET /flights/search`** (match / no match / invalid date).
- `python -c` / `TestClient` — **`POST /bookings`**, **`GET /bookings`**, **`DELETE /bookings/{ref}`** (capacity, search, double-cancel **409**, **400** with no query params).
- `python -c` imports / `BookingCreate(...)` cases — confirm strip, blank rejection, and `min_length` after strip for `backend/schemas.py`.
- `npm install` / `npm start` — confirm the Express scaffold serves `public/` when I exercise the frontend.


