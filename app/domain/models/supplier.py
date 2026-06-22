from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    health_status = Column(String, nullable=True)

    last_checked_at = Column(DateTime, nullable=True)

    # Relationships
    commissions = relationship(
        "SupplierCommission",
        back_populates="supplier"
    )

    bookings = relationship(
        "Booking",
        back_populates="supplier"
    )