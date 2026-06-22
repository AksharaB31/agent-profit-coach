from sqlalchemy.orm import Session
from app.domain.repositories.booking_repository import BookingRepository
from typing import Dict, Any

class ReliabilityLoader:
    """Loads supplier reliability and booking success rates."""
    
    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self._cache = None
        
    def get_supplier_reliability(self, supplier_code: str) -> Dict[str, Any]:
        if self._cache is None:
            self._cache = {}
            
            # 1. Booking Success Probability via BookingProcess
            process_stats = self.booking_repo.get_process_success_stats()
            for row in process_stats:
                if row.provider_code:
                    total = row.total or 0
                    success = row.success or 0
                    ticketed = getattr(row, "ticketed", 0) or 0
                    refunded_process = getattr(row, "refunded", 0) or 0
                    
                    if row.provider_code not in self._cache:
                        self._cache[row.provider_code] = {}
                    self._cache[row.provider_code]["process_success"] = success
                    self._cache[row.provider_code]["process_ticketed"] = ticketed
                    self._cache[row.provider_code]["process_refunded"] = refunded_process
                    self._cache[row.provider_code]["process_total"] = total
            
            # 2. Cancellation Risk via Booking
            booking_stats = self.booking_repo.get_booking_cancellation_stats()
            for row in booking_stats:
                if row.provider:
                    total = row.total or 0
                    cancelled = row.cancelled or 0
                    refunded_booking = getattr(row, "refunded", 0) or 0
                    
                    if row.provider not in self._cache:
                        self._cache[row.provider] = {}
                    self._cache[row.provider]["booking_cancelled"] = cancelled
                    self._cache[row.provider]["booking_refunded"] = refunded_booking
                    self._cache[row.provider]["booking_total"] = total
                
        # Extract specific supplier data
        sup_data = self._cache.get(supplier_code, {})
        
        # Check if we have enough historical data
        has_history = sup_data.get("process_total", 0) > 0 or sup_data.get("booking_total", 0) > 0
        
        return {
            "process_total": sup_data.get("process_total", 0),
            "process_success": sup_data.get("process_success", 0),
            "process_ticketed": sup_data.get("process_ticketed", 0),
            "process_refunded": sup_data.get("process_refunded", 0),
            "booking_total": sup_data.get("booking_total", 0),
            "booking_cancelled": sup_data.get("booking_cancelled", 0),
            "booking_refunded": sup_data.get("booking_refunded", 0),
            "has_historical_data": has_history
        }
