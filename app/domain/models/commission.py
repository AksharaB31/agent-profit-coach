from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum

class CommissionType(enum.Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"

class SupplierCommission(Base, TimestampMixin):
    __tablename__ = "supplier_commissions"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=True) # Nullable for generic commissions
    
    commission_type = Column(Enum(CommissionType), nullable=False)
    commission_value = Column(Float, nullable=False)
    
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)

    # Relationships
    supplier = relationship("Supplier", back_populates="commissions")
    airline = relationship("Airline", back_populates="commissions")


class Markup(Base, TimestampMixin):
    __tablename__ = "markups"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True) # Nullable for global markups
    
    markup_type = Column(Enum(CommissionType), nullable=False)
    markup_value = Column(Float, nullable=False)
    
    flight_route = Column(String, nullable=True) # Optional specific route e.g. "JFK-LHR"
    
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="markups")
