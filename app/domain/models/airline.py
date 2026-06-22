from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Airline(Base, TimestampMixin):
    __tablename__ = "airlines"

    id = Column(Integer, primary_key=True, index=True)
    iata_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    # Relationships
    flights = relationship("Flight", back_populates="airline")
    commissions = relationship("SupplierCommission", back_populates="airline")
