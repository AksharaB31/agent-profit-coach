import logging
from typing import Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.infra.mysql.models import Booking, BookingFlight, BookingAdjustedFare

logger = logging.getLogger(__name__)

class CommissionRepository:
    """Enterprise repository for managing agent commissions and profitability data."""

    def __init__(self, db: Session):
        self.db = db

    def get_average_profit_by_airline(self, airline_code: str) -> float:
        """Fetches the historical average agent profit for flights on a given airline."""
        try:
            result = self.db.query(
                func.avg(BookingAdjustedFare.agent_profit).label("avg_agent_profit")
            ).join(
                BookingFlight, BookingFlight.booking_id == BookingAdjustedFare.booking_id
            ).join(
                Booking, Booking.id == BookingFlight.booking_id
            ).filter(
                BookingFlight.validating_airline == airline_code
            ).first()

            if result and result.avg_agent_profit and float(result.avg_agent_profit) > 0:
                return float(result.avg_agent_profit)
            return 0.0
        except Exception as e:
            logger.error(f"Database error in get_average_profit_by_airline for {airline_code}: {e}")
            raise e

    def get_average_profit_by_supplier(self, supplier_code: str, origin: str = None, destination: str = None) -> float:
        """Fetches the historical average agent profit for a given supplier, optionally filtered by route."""
        from app.infra.mysql.models import BookingFlight, BookingSegment
        
        try:
            # Base query
            query = self.db.query(
                func.avg(BookingAdjustedFare.agent_profit).label("avg_agent_profit"),
                func.avg(BookingAdjustedFare.agent_markup).label("avg_agent_markup"),
                func.avg(BookingAdjustedFare.final_price - BookingAdjustedFare.total_base).label("avg_derived_profit")
            ).join(
                Booking, Booking.id == BookingAdjustedFare.booking_id
            )
            
            # Add route filtering if provided
            if origin and destination:
                query = query.join(
                    BookingFlight, BookingFlight.booking_id == Booking.id
                ).join(
                    BookingSegment, BookingSegment.booking_flight_id == BookingFlight.id
                ).filter(
                    BookingSegment.departure_airport == origin,
                    BookingSegment.arrival_airport == destination
                )
                
            query = query.filter(Booking.provider == supplier_code)
            result = query.first()
            
            # If route-specific data fails to yield profit, fallback to generic supplier average
            if not result or (not result.avg_agent_profit and not result.avg_agent_markup and not result.avg_derived_profit):
                if origin and destination:
                    return self.get_average_profit_by_supplier(supplier_code) # Fallback without route
                return 0.0
            
            if result.avg_agent_profit and float(result.avg_agent_profit) > 0:
                return float(result.avg_agent_profit)
            elif result.avg_agent_markup and float(result.avg_agent_markup) > 0:
                return float(result.avg_agent_markup)
            elif result.avg_derived_profit and float(result.avg_derived_profit) > 0:
                return float(result.avg_derived_profit)
                
            return 0.0
        except Exception as e:
            logger.error(f"Database error in get_average_profit_by_supplier for {supplier_code}: {e}")
            raise e
