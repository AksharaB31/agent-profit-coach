from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    agency_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    tier = Column(String, default="Bronze") # e.g., Bronze, Silver, Gold
    status = Column(Boolean, default=True)

    # Relationships
    bookings = relationship("Booking", back_populates="agent")
    markups = relationship("Markup", back_populates="agent")
