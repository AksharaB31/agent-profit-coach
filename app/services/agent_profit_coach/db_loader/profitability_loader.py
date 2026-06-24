from sqlalchemy.orm import Session
from app.domain.repositories.commission_repository import CommissionRepository
import threading
from app.domain.repositories.markup_repository import MarkupRepository
from typing import Dict, Any

class ProfitabilityLoader:
    """Loads historical agent profitability and markup rules."""
    
    def __init__(self, db: Session):
        self.db = db
        self.commission_repo = CommissionRepository(db)
        self.markup_repo = MarkupRepository(db)
        self._profit_cache = {}
        self._markup_cache = {}
        self._lock = threading.Lock()
        
    def get_historical_agent_profit(self, supplier_code: str, origin: str, destination: str) -> float:
        cache_key = f"{supplier_code}_{origin}_{destination}"
        
        with self._lock:
            if cache_key in self._profit_cache:
                return self._profit_cache[cache_key]
                
        profit = self.commission_repo.get_average_profit_by_supplier(supplier_code, origin, destination)
        
        with self._lock:
            self._profit_cache[cache_key] = profit
            
        return profit

    def get_supplier_avg_profit(self, supplier_code: str) -> float:
        return self.commission_repo.get_average_profit_by_supplier(supplier_code)

    def get_airline_avg_profit(self, airline_code: str) -> float:
        return self.commission_repo.get_average_profit_by_airline(airline_code)

    def get_recommended_agent_markup(self, airline_code: str) -> float:
        # Fetch global recommended agent markup since agent_id is not provided
        if airline_code not in self._markup_cache:
            markup = self.markup_repo.get_active_markup_by_airline(airline_code)
            self._markup_cache[airline_code] = markup
            
        return self._markup_cache[airline_code]

    def get_supplier_incentive(self, supplier_code: str) -> float:
        """
        Returns simulated B2B incentives (e.g. Campaign Bonus, Override Commission)
        In a real production environment, this would query a SupplierIncentives table.
        """
        import hashlib
        
        # Simulated Seasonal Promotion logic based on supplier code
        incentives = {
            "sup_k2m7": 25.0,  # Preferred Partner Bonus
            "sup_f8a1": 15.0,  # Q2 Volume Target Met
            "sup_x9p4": 5.0    # Standard Override
        }
        
        if supplier_code in incentives:
            return incentives[supplier_code]
            
        # Fallback for unknown suppliers in JSON to ensure they get a non-zero incentive
        hash_val = int(hashlib.md5(supplier_code.encode()).hexdigest(), 16)
        # Give a stable random value between 5.0 and 25.0
        return 5.0 + (hash_val % 21)
