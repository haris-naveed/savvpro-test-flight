from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

if __package__:
    from ..database import get_db
    from ..models import Flight
    from ..schemas import FlightResponse
else:
    from database import get_db
    from models import Flight
    from schemas import FlightResponse

router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("", response_model=list[FlightResponse])
def list_flights(db: Session = Depends(get_db)):
    stmt = select(Flight).order_by(Flight.id)
    return list(db.scalars(stmt).all())


@router.get("/search", response_model=list[FlightResponse])
def search_flights(
    db: Session = Depends(get_db),
    origin: Annotated[Optional[str], Query()] = None,
    destination: Annotated[Optional[str], Query()] = None,
    date_value: Annotated[Optional[str], Query(alias="date")] = None,
):
    stmt = select(Flight)

    if origin is not None and origin.strip():
        o = origin.strip().lower()
        stmt = stmt.where(func.lower(Flight.origin) == o)
    if destination is not None and destination.strip():
        d = destination.strip().lower()
        stmt = stmt.where(func.lower(Flight.destination) == d)
    if date_value is not None and date_value.strip():
        try:
            day = date.fromisoformat(date_value.strip())
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid date format, expected YYYY-MM-DD",
            ) from None
        start = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        stmt = stmt.where(
            Flight.departure_datetime >= start,
            Flight.departure_datetime < end,
        )

    stmt = stmt.order_by(Flight.id)
    rows = list(db.scalars(stmt).all())
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No flights found matching your criteria",
        )
    return rows


@router.get("/{flight_id}", response_model=FlightResponse)
def get_flight(flight_id: int, db: Session = Depends(get_db)):
    flight = db.get(Flight, flight_id)
    if flight is None:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight
