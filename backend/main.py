from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

if __package__:
    from .database import Base, SessionLocal, engine
    from .models import Flight
    from .routes.bookings import router as bookings_router
    from .routes.flights import router as flights_router
else:
    from database import Base, SessionLocal, engine
    from models import Flight
    from routes.bookings import router as bookings_router
    from routes.flights import router as flights_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flights_router)
app.include_router(bookings_router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    _seed_sample_flights_if_empty()


def _seed_sample_flights_if_empty() -> None:
    utc = timezone.utc
    with SessionLocal() as db:
        count = db.scalar(select(func.count()).select_from(Flight))
        if count and count > 0:
            return
        sample_flights = [
            Flight(
                origin="New York",
                destination="London",
                departure_datetime=datetime(2026, 6, 10, 9, 0, tzinfo=utc),
                duration_minutes=420,
                price_per_seat=649.99,
                total_seats=280,
                available_seats=45,
            ),
            Flight(
                origin="Tokyo",
                destination="Sydney",
                departure_datetime=datetime(2026, 6, 12, 22, 30, tzinfo=utc),
                duration_minutes=580,
                price_per_seat=1199.0,
                total_seats=332,
                available_seats=12,
            ),
            Flight(
                origin="Paris",
                destination="Berlin",
                departure_datetime=datetime(2026, 6, 14, 7, 15, tzinfo=utc),
                duration_minutes=105,
                price_per_seat=88.5,
                total_seats=189,
                available_seats=1,
            ),
            Flight(
                origin="Dubai",
                destination="Singapore",
                departure_datetime=datetime(2026, 6, 18, 2, 45, tzinfo=utc),
                duration_minutes=465,
                price_per_seat=515.25,
                total_seats=312,
                available_seats=6,
            ),
            Flight(
                origin="Los Angeles",
                destination="Seattle",
                departure_datetime=datetime(2026, 6, 20, 14, 0, tzinfo=utc),
                duration_minutes=175,
                price_per_seat=139.0,
                total_seats=178,
                available_seats=1,
            ),
            Flight(
                origin="Chicago",
                destination="Miami",
                departure_datetime=datetime(2026, 6, 22, 11, 20, tzinfo=utc),
                duration_minutes=205,
                price_per_seat=178.75,
                total_seats=192,
                available_seats=28,
            ),
            Flight(
                origin="San Francisco",
                destination="Tokyo",
                departure_datetime=datetime(2026, 6, 25, 16, 10, tzinfo=utc),
                duration_minutes=650,
                price_per_seat=975.0,
                total_seats=316,
                available_seats=4,
            ),
            Flight(
                origin="Amsterdam",
                destination="Rome",
                departure_datetime=datetime(2026, 6, 28, 8, 40, tzinfo=utc),
                duration_minutes=125,
                price_per_seat=105.5,
                total_seats=205,
                available_seats=71,
            ),
        ]
        db.add_all(sample_flights)
        db.commit()


@app.get("/health")
def health():
    return {"status": "ok"}
