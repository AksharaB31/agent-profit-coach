from sqlalchemy.orm import Session
from app.domain.repositories.booking_repository import BookingRepository
import threading
from typing import Dict, Any

class ConversionLoader:
    """Loads conversion analytics from historical bookings."""
    
    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self._cache = {}
        self._lock = threading.Lock()
        
    def get_route_conversion_probability(self, supplier_code: str, origin: str, destination: str) -> dict:
        cache_key = f"{supplier_code}_{origin}_{destination}"
        
        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        stats = self.booking_repo.get_route_conversion_stats(supplier_code, origin, destination)
        total = stats.get("total", 0)
        successful = stats.get("successful", 0)
        
        with self._lock:
            if total > 0:
                self._cache[cache_key] = {"total": int(total), "successful": int(successful)}
            else:
                self._cache[cache_key] = {"total": 0, "successful": 0}
            
        return self._cache[cache_key]
