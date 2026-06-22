from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum

class BookingStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    
    pnr = Column(String, index=True, nullable=True) # Passenger Name Record
    booking_reference = Column(String, index=True, nullable=True)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    
    total_price = Column(Float, nullable=False)
    currency = Column(String, default="USD")

    # Relationships
    agent = relationship("Agent", back_populates="bookings")
    supplier = relationship("Supplier", back_populates="bookings")
    processes = relationship("BookingProcess", back_populates="booking")
    booking_flights = relationship("BookingFlight", back_populates="booking")


class BookingProcess(Base, TimestampMixin):
    __tablename__ = "booking_processes"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    
    process_status = Column(String, nullable=False) # e.g. INITIATED, PAYMENT_PENDING, TICKETED
    details = Column(JSON, nullable=True) # Logs or metadata
    timestamp = Column(DateTime, nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="processes")


class BookingFlight(Base, TimestampMixin):
    __tablename__ = "booking_flights"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    
    departure_datetime = Column(DateTime, nullable=False)
    arrival_datetime = Column(DateTime, nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="booking_flights")
    flight = relationship("Flight", back_populates="booking_flights")
    segments = relationship("BookingSegment", back_populates="booking_flight")
    fares = relationship("BookingFare", back_populates="booking_flight")
    ancillaries = relationship("BookingAncillary", back_populates="booking_flight")


class BookingSegment(Base, TimestampMixin):
    __tablename__ = "booking_segments"

    id = Column(Integer, primary_key=True, index=True)
    booking_flight_id = Column(Integer, ForeignKey("booking_flights.id"), nullable=False)
    
    segment_number = Column(Integer, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    cabin_class = Column(String, nullable=False) # e.g. ECONOMY, BUSINESS
    duration_minutes = Column(Integer, nullable=True)

    # Relationships
    booking_flight = relationship("BookingFlight", back_populates="segments")


class BookingFare(Base, TimestampMixin):
    __tablename__ = "booking_fares"

    id = Column(Integer, primary_key=True, index=True)
    booking_flight_id = Column(Integer, ForeignKey("booking_flights.id"), nullable=False)
    
    base_fare = Column(Float, nullable=False)
    taxes = Column(Float, nullable=False)
    fees = Column(Float, nullable=False)
    total_fare = Column(Float, nullable=False)
    currency = Column(String, default="USD")

    # Relationships
    booking_flight = relationship("BookingFlight", back_populates="fares")
    adjusted_fares = relationship("BookingAdjustedFare", back_populates="booking_fare")


class BookingAdjustedFare(Base, TimestampMixin):
    __tablename__ = "booking_adjusted_fares"

    id = Column(Integer, primary_key=True, index=True)
    booking_fare_id = Column(Integer, ForeignKey("booking_fares.id"), nullable=False)
    
    supplier_commission_applied = Column(Float, default=0.0)
    markup_applied = Column(Float, default=0.0)
    agent_profit = Column(Float, default=0.0) # Core metric for the Coach
    final_selling_price = Column(Float, nullable=False)
    currency = Column(String, default="USD")

    # Relationships
    booking_fare = relationship("BookingFare", back_populates="adjusted_fares")


class BookingAncillary(Base, TimestampMixin):
    __tablename__ = "booking_ancillaries"

    id = Column(Integer, primary_key=True, index=True)
    booking_flight_id = Column(Integer, ForeignKey("booking_flights.id"), nullable=False)
    
    type = Column(String, nullable=False) # e.g. BAGGAGE, SEAT, MEAL
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")

    # Relationships
    booking_flight = relationship("BookingFlight", back_populates="ancillaries")
