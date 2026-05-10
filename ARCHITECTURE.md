# Architecture notes — FlightHub

## Data model

SQLite, one file under `backend/` (`flighthub.db`). SQLAlchemy models in `backend/models.py`.

### `flights`

Stores what you can sell a seat on.

| Column | Why it’s there |
|--------|----------------|
| `id` | Primary key; frontend and bookings reference this. |
| `origin` / `destination` | Human-readable route; search filters match these (case-insensitive). |
| `departure_datetime` | Actual departure instant; search by “date” uses the UTC calendar day containing this. |
| `duration_minutes` | Block time for the leg; shown in the UI as hours/minutes. |
| `price_per_seat` | What we quote per passenger. |
| `total_seats` | Aircraft/seat capacity (mostly informational next to available). |
| `available_seats` | **Source of truth for inventory.** Booking decrements it; cancel increments it. When it hits 0, new bookings get 409. |

### `bookings`

One row per reservation.

| Column | Why it’s there |
|--------|----------------|
| `id` | Internal PK. |
| `booking_reference` | Short public id (8 hex chars from UUID); staff/passengers use this for lookup and cancel. Unique. |
| `flight_id` | FK to `flights.id`; ties the booking to a route and schedule. |
| `passenger_name` | Searchable; displayed in UI. |
| `passport_number` | Required identity field from the brief. |
| `seat_number` | What the passenger picked (label only — we don’t model a full seat map). |
| `status` | `confirmed` vs `cancelled`; cancel is a soft update, not a hard delete. |
| `created_at` | Audit / sorting. |

Relationship: many bookings → one flight. Responses often embed the nested `flight` for convenience.

---

## API design

Base URL: **`http://localhost:8000`** (see also `/docs`).

| Method | Path | Purpose | Typical responses |
|--------|------|---------|-------------------|
| GET | `/health` | Liveness check | **200** `{"status":"ok"}` |
| GET | `/flights` | List all flights | **200** JSON array of flights |
| GET | `/flights/search` | Filter by `origin`, `destination`, `date` (query params, all optional) | **200** array; **404** no matches; **422** bad date string |
| GET | `/flights/{flight_id}` | Single flight | **200** flight; **404** not found |
| POST | `/bookings` | Create booking (JSON body: `flight_id`, `passenger_name`, `passport_number`, `seat_number`) | **201** booking + nested flight; **404** flight missing; **409** no seats; **422** validation |
| GET | `/bookings` | Search: need at least one of `passenger_name`, `booking_reference` (query) | **200** array; **400** if both empty |
| DELETE | `/bookings/{booking_reference}` | Cancel booking | **200** cancellation payload; **404** unknown ref; **409** already cancelled |

CORS allows the local UI on **`http://localhost:3000`** and **`http://127.0.0.1:3000`** so either hostname works in the browser.

---

## Ambiguity decisions (from the brief)

**Overbooking:** First-come-first-served using `available_seats`. When it would go below zero we reject instead — **409** *“No seats available on this flight”*. No waitlist: it’s a tiny internal tool and the brief leans toward something simple we can reason about and test.

**UI layout:** For agency staff the important thing is deciding *where* and *how much*, so the SPA foregrounds **route** and **price** on each card, with time/duration/seats secondary but still visible.
