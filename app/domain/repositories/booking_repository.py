import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.infra.mysql.models import Booking, BookingProcess, BookingFlight, BookingSegment

logger = logging.getLogger(__name__)    

class BookingRepository:
    """Enterprise repository for managing Booking and BookingProcess database queries."""

    def __init__(self, db: Session):
        self.db = db

    def get_process_success_stats(self) -> List[Any]:
        """Fetches total processes and successful processes grouped by provider code."""
        try:
            return self.db.query(
                BookingProcess.provider_code,
                func.count(BookingProcess.id).label("total"),
                func.sum(case((func.upper(BookingProcess.state).in_(["SUCCESS", "COMPLETED", "TICKETED", "CONFIRMED"]), 1), else_=0)).label("success"),
                func.sum(case((func.upper(BookingProcess.state) == "TICKETED", 1), else_=0)).label("ticketed"),
                func.sum(case((func.upper(BookingProcess.state).in_(["REFUNDED", "REFUND_SUCCESS"]), 1), else_=0)).label("refunded")
            ).group_by(BookingProcess.provider_code).all()
        except Exception as e:
            logger.error(f"Database error in get_process_success_stats: {e}")
            return []

    def get_booking_cancellation_stats(self) -> List[Any]:
        """Fetches total bookings and cancelled bookings grouped by provider."""
        try:
            return self.db.query(
                Booking.provider,
                func.count(Booking.id).label("total"),
                func.sum(case((func.upper(Booking.status).in_(["CANCELLED", "VOID"]), 1), else_=0)).label("cancelled"),
                func.sum(case((func.upper(Booking.status).in_(["REFUNDED", "PARTIAL_REFUND"]), 1), else_=0)).label("refunded")
            ).group_by(Booking.provider).all()
        except Exception as e:
            logger.error(f"Database error in get_booking_cancellation_stats: {e}")
            return []

    def get_route_conversion_stats(self, supplier_code: str, origin: str, destination: str) -> Dict[str, int]:
        """Fetches booking conversion probability for a specific route."""
        try:
            result = self.db.query(
                func.count(Booking.id).label("total_bookings"),
                func.sum(case((func.upper(Booking.status).in_(['CONFIRMED', 'COMPLETED', 'TICKETED', 'SUCCESS']), 1), else_=0)).label("successful_bookings")
            ).join(
                BookingFlight, Booking.id == BookingFlight.booking_id
            ).join(
                BookingSegment, BookingFlight.id == BookingSegment.booking_flight_id
            ).filter(
                Booking.provider == supplier_code,
                BookingSegment.departure_airport == origin,
                BookingSegment.arrival_airport == destination
            ).first()
            
            if result:
                return {
                    "total": int(result.total_bookings or 0),
                    "successful": int(result.successful_bookings or 0)
                }
        except Exception as e:
            logger.error(f"Database error in get_route_conversion_stats: {e}")
            
        return {"total": 0, "successful": 0}
