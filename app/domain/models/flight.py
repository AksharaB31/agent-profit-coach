from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Flight(Base, TimestampMixin):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    flight_number = Column(String, nullable=False)
    origin = Column(String, index=True, nullable=False) # IATA code
    destination = Column(String, index=True, nullable=False) # IATA code

    # Relationships
    airline = relationship("Airline", back_populates="flights")
    booking_flights = relationship("BookingFlight", back_populates="flight")
