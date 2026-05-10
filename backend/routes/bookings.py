from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

if __package__:
    from ..database import get_db
    from ..models import Booking, Flight
    from ..schemas import BookingCreate, BookingResponse, CancellationResponse
else:
    from database import get_db
    from models import Booking, Flight
    from schemas import BookingCreate, BookingResponse, CancellationResponse

router = APIRouter(prefix="/bookings", tags=["bookings"])


def _new_booking_reference() -> str:
    return uuid.uuid4().hex[:8].upper()


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    flight = db.get(Flight, payload.flight_id)
    if flight is None:
        raise HTTPException(status_code=404, detail="Flight not found")

    if flight.available_seats <= 0:
        raise HTTPException(
            status_code=409,
            detail="No seats available on this flight",
        )

    booking_reference = _new_booking_reference()
    booking = Booking(
        booking_reference=booking_reference,
        flight_id=payload.flight_id,
        passenger_name=payload.passenger_name,
        passport_number=payload.passport_number,
        seat_number=payload.seat_number,
        status="confirmed",
    )
    db.add(booking)
    flight.available_seats -= 1
    db.commit()
    db.refresh(booking)
    _ = booking.flight  # ensure relationship loaded for response
    return booking


@router.get("", response_model=list[BookingResponse])
def list_bookings(
    db: Session = Depends(get_db),
    passenger_name: Annotated[Optional[str], Query()] = None,
    booking_reference: Annotated[Optional[str], Query()] = None,
):
    has_name = passenger_name is not None and passenger_name.strip() != ""
    has_ref = booking_reference is not None and booking_reference.strip() != ""

    if not has_name and not has_ref:
        raise HTTPException(
            status_code=400,
            detail="Provide passenger_name or booking_reference to search",
        )

    stmt = select(Booking).options(selectinload(Booking.flight))

    filters = []
    if has_name:
        needle = passenger_name.strip().lower()
        filters.append(
            func.instr(func.lower(Booking.passenger_name), needle) > 0,
        )
    if has_ref:
        ref = booking_reference.strip()
        filters.append(Booking.booking_reference == ref)

    if len(filters) == 1:
        stmt = stmt.where(filters[0])
    else:
        stmt = stmt.where(or_(*filters))

    stmt = stmt.order_by(Booking.id)
    rows = list(db.scalars(stmt).all())
    return rows


@router.delete("/{booking_reference}", response_model=CancellationResponse)
def cancel_booking(booking_reference: str, db: Session = Depends(get_db)):
    stmt = (
        select(Booking)
        .options(selectinload(Booking.flight))
        .where(Booking.booking_reference == booking_reference)
    )
    booking = db.scalars(stmt).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="Booking is already cancelled",
        )

    flight = booking.flight
    booking.status = "cancelled"
    flight.available_seats += 1
    db.commit()

    return CancellationResponse(
        booking_reference=booking.booking_reference,
        status="cancelled",
        message="Booking cancelled successfully",
    )
