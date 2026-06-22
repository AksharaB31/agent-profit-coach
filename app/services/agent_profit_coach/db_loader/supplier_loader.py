from sqlalchemy.orm import Session
from app.domain.repositories.supplier_repository import SupplierRepository
from typing import Dict, Any

class SupplierLoader:
    """Loads supplier configuration and health status."""
    
    def __init__(self, db: Session):
        self.db = db
        self.supplier_repo = SupplierRepository(db)
        self._cache = {}
        
    def get_supplier_details(self, supplier_code: str) -> Dict[str, Any]:
        if supplier_code not in self._cache:
            s = self.supplier_repo.get_supplier_by_code(supplier_code)
            if s:
                self._cache[supplier_code] = {"name": s.name, "health_status": s.health_status, "is_active": s.is_active}
            else:
                self._cache[supplier_code] = {"name": supplier_code, "health_status": "unknown", "is_active": False}
            
        return self._cache[supplier_code]
