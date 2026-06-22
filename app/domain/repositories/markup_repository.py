import logging
from sqlalchemy.orm import Session
from app.infra.mysql.models import Markup

logger = logging.getLogger(__name__)

class MarkupRepository:
    """Enterprise repository for managing markup configurations."""

    def __init__(self, db: Session):
        self.db = db

    def get_active_markup_by_airline(self, airline_code: str) -> float:
        """Fetches the highest priority active global markup for an airline."""
        try:
            markup = self.db.query(Markup).filter(
                Markup.airline_code == airline_code,
                Markup.owner_type == 'global',
                Markup.status == 'active'
            ).order_by(Markup.priority.desc()).first()
            
            return float(markup.markup_value) if markup else 0.0
        except Exception as e:
            logger.error(f"Database error in get_active_markup_by_airline for {airline_code}: {e}")
            return 0.0
