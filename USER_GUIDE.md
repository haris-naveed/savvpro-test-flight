# User guide — FlightHub API & UI

Assume the API is running at **`http://localhost:8000`**. Swap in **127.0.0.1** if that’s what you use.

Interactive docs (try requests in the browser): **http://localhost:8000/docs**

The **web app** is served by Express at **`http://localhost:3000`** (or **`http://127.0.0.1:3000`**). Start the backend first, then run **`node app.js`** from the **`frontend/`** folder — see **`README.md`**.

---

### Search flights

Optional query params: **`origin`**, **`destination`**, **`date`** (date must look like **`YYYY-MM-DD`**).

Example — filter by origin:

```bash
curl "http://localhost:8000/flights/search?origin=Paris"
```

Example — origin + destination:

```bash
curl "http://localhost:8000/flights/search?origin=New%20York&destination=London"
```

You’ll get **404** with a JSON `detail` if nothing matches. **422** if `date` is garbage.

---

### Book a flight

#### In the FlightHub UI

1. Open the **Book a flight** tab.
2. **Flight** is a **dropdown** loaded from **`GET /flights`**. Each option shows the flight id, route (origin → destination), price per seat, and how many seats are left. The **first** flight in the list is **selected automatically** when data loads.
3. The preview card on the left updates when you change the selection (it loads details with **`GET /flights/{id}`**).
4. You can also click **Select & Book** on any card under **All Flights** or **Search**; that switches to this tab and selects that flight in the dropdown.
5. Fill in **full name**, **passport number**, and **seat**, then **Confirm booking**. On success you’ll see a **booking reference**; the dropdown **refreshes** so seat counts stay accurate (your flight stays selected when it still exists). **409** means no seats left; **422** means validation failed (shown inline).

#### With curl (API)

**POST** JSON body with **`flight_id`**, **`passenger_name`**, **`passport_number`**, **`seat_number`**:

```bash
curl -X POST "http://localhost:8000/bookings" ^
  -H "Content-Type: application/json" ^
  -d "{\"flight_id\": 1, \"passenger_name\": \"Jane Doe\", \"passport_number\": \"AB12345\", \"seat_number\": \"12A\"}"
```

(On macOS/Linux use single quotes around the `-d` string instead of escaping quotes.)

**201** → response includes **`booking_reference`** (save it). **409** if the flight is full. **422** if validation fails (short name, etc.).

---

### View bookings

You need at least one of **`passenger_name`** or **`booking_reference`** as query params.

By **name** (substring match, case-insensitive):

```bash
curl "http://localhost:8000/bookings?passenger_name=Jane"
```

By **reference** (exact):

```bash
curl "http://localhost:8000/bookings?booking_reference=AB12CD34"
```

The UI sometimes sends **both** with the same search box text so either path matches — the API is fine with that.

---

### Cancel a booking

**DELETE** using the booking reference from the booking response:

```bash
curl -X DELETE "http://localhost:8000/bookings/AB12CD34"
```

**200** → cancelled, seat goes back on the flight. **404** if the reference doesn’t exist. **409** if it was already cancelled.

---

### List all flights (no filter)

```bash
curl "http://localhost:8000/flights"
```

### One flight by id

```bash
curl "http://localhost:8000/flights/1"
```
