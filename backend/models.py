from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

if __package__:
    from .database import Base
else:
    from database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_datetime = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    price_per_seat = Column(Float, nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)

    bookings = relationship("Booking", back_populates="flight")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_reference = Column(String, unique=True, nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    passenger_name = Column(String, nullable=False)
    passport_number = Column(String, nullable=False)
    seat_number = Column(String, nullable=False)
    status = Column(String, nullable=False, default="confirmed")
    created_at = Column(DateTime(timezone=True), default=utcnow)

    flight = relationship("Flight", back_populates="bookings")
