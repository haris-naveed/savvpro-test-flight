from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FlightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    origin: str
    destination: str
    departure_datetime: datetime
    duration_minutes: int
    price_per_seat: float
    total_seats: int
    available_seats: int


class BookingCreate(BaseModel):
    flight_id: int
    passenger_name: str = Field(..., min_length=2)
    passport_number: str = Field(..., min_length=5)
    seat_number: str

    @field_validator("passenger_name", "passport_number", mode="before")
    @classmethod
    def strip_and_reject_blank(cls, v):
        if not isinstance(v, str):
            return v
        stripped = v.strip()
        if stripped == "":
            raise ValueError("must not be blank")
        return stripped


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_reference: str
    flight_id: int
    passenger_name: str
    passport_number: str
    seat_number: str
    status: str
    created_at: datetime
    flight: FlightResponse


class CancellationResponse(BaseModel):
    booking_reference: str
    status: str
    message: str
