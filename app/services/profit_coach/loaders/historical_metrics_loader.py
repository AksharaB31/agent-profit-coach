from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.infra.mysql.models import BookingProcess, Booking, BookingAdjustedFare, Supplier, Markup
from typing import Dict, Any

class HistoricalMetricsLoader:
    """Loads historical metrics from the database with caching to prevent N+1 queries."""

    def __init__(self, db: Session):
        self.db = db
        self._reliability_cache = None
        self._profitability_cache = None
        self._supplier_cache = None
        self._markup_cache = {}

    def get_supplier_health(self, supplier_code: str) -> str:
        if self._supplier_cache is None:
            suppliers = self.db.query(Supplier).all()
            self._supplier_cache = {s.code: s.health_status for s in suppliers}
        
        return self._supplier_cache.get(supplier_code, "unknown")

    def get_supplier_reliability(self, supplier_code: str) -> Dict[str, Any]:
        if self._reliability_cache is None:
            self._reliability_cache = {}
            process_stats = self.db.query(
                BookingProcess.provider_code,
                func.count(BookingProcess.id).label("total"),
                func.sum(case((BookingProcess.state.in_(["success", "completed", "ticketed"]), 1), else_=0)).label("success")
            ).group_by(BookingProcess.provider_code).all()

            for row in process_stats:
                if row.provider_code:
                    total = row.total or 0
                    success = row.success or 0
                    ratio = (success / total) if total > 0 else 0.5
                    self._reliability_cache[row.provider_code] = {
                        "total_bookings": total,
                        "successful_bookings": success,
                        "success_ratio": ratio
                    }
        
        return self._reliability_cache.get(supplier_code, {
            "total_bookings": 0,
            "successful_bookings": 0,
            "success_ratio": 0.5
        })

    def get_historical_profitability(self, supplier_code: str) -> Dict[str, float]:
        if self._profitability_cache is None:
            self._profitability_cache = {}
            profit_stats = self.db.query(
                Booking.provider,
                func.avg(BookingAdjustedFare.supplier_commission).label("avg_commission"),
                func.avg(BookingAdjustedFare.admin_profit + BookingAdjustedFare.agent_profit).label("avg_profit")
            ).join(
                BookingAdjustedFare, Booking.id == BookingAdjustedFare.booking_id
            ).group_by(Booking.provider).all()

            for row in profit_stats:
                if row.provider:
                    self._profitability_cache[row.provider] = {
                        "avg_commission": float(row.avg_commission or 0.0),
                        "avg_profit": float(row.avg_profit or 0.0)
                    }

        return self._profitability_cache.get(supplier_code, {
            "avg_commission": 0.0,
            "avg_profit": 0.0
        })

    def get_markup(self, agent_id: int | None, airline_code: str) -> float:
        cache_key = f"{agent_id}_{airline_code}"
        if cache_key not in self._markup_cache:
            query = self.db.query(Markup).filter(
                Markup.airline_code == airline_code,
                Markup.status == 'active'
            )
            
            if agent_id is not None:
                query = query.filter(Markup.owner_type == 'agent', Markup.owner_id == agent_id)
            else:
                query = query.filter(Markup.owner_type == 'global')
                
            markup = query.order_by(Markup.priority.desc()).first()
            self._markup_cache[cache_key] = markup.markup_value if markup else 0.0
            
        return self._markup_cache[cache_key]
