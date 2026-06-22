import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.infra.mysql.models import Supplier

logger = logging.getLogger(__name__)

class SupplierRepository:
    """Enterprise repository for managing supplier data and health metrics."""

    def __init__(self, db: Session):
        self.db = db

    def get_supplier_by_code(self, supplier_code: str) -> Optional[Supplier]:
        """Fetches the supplier ORM object by its unique code."""
        try:
            return self.db.query(Supplier).filter(Supplier.code == supplier_code).first()
        except Exception as e:
            logger.error(f"Database error in get_supplier_by_code for {supplier_code}: {e}")
            return None
