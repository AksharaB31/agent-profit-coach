from sqlalchemy.orm import Session
from sqlalchemy import func
from app.infra.mysql.models import Booking, BookingAdjustedFare, BookingFlight, Agent
from typing import Dict, Any

class AgentLoader:
    """Dynamically calculates an agent's behavioral profile from historical bookings."""
    
    def __init__(self, db: Session):
        self.db = db
        self._cache = {}
        
    def get_agent_profile(self, agent_id: int) -> Dict[str, Any]:
        if not agent_id:
            return None
            
        if agent_id in self._cache:
            return self._cache[agent_id]
            
        try:
            # Check if agent exists
            agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                self._cache[agent_id] = None
                return None
                
            agent_type = agent.agent_type or "UNKNOWN"
            
            # Aggregate queries
            # 1. Preferred Supplier
            pref_supplier_row = self.db.query(
                Booking.provider, func.count(Booking.id).label('cnt')
            ).filter(Booking.agent_id == agent_id).group_by(Booking.provider).order_by(func.count(Booking.id).desc()).first()
            preferred_supplier = pref_supplier_row.provider if pref_supplier_row else None
            
            # 2. Preferred Airline
            pref_airline_row = self.db.query(
                BookingFlight.validating_airline, func.count(BookingFlight.id).label('cnt')
            ).join(Booking, Booking.id == BookingFlight.booking_id).filter(
                Booking.agent_id == agent_id
            ).group_by(BookingFlight.validating_airline).order_by(func.count(BookingFlight.id).desc()).first()
            preferred_airline = pref_airline_row.validating_airline if pref_airline_row else None
            
            # 3. Average Booking Value & Refunds
            agg_row = self.db.query(
                func.avg(Booking.total_amount).label('avg_val'),
                func.count(Booking.id).label('total_bookings'),
                func.sum(func.cast(Booking.refundable, type_=func.integer)).label('refund_count')
            ).filter(Booking.agent_id == agent_id).first()
            
            avg_val = float(agg_row.avg_val) if agg_row and agg_row.avg_val else 0.0
            total_bookings = int(agg_row.total_bookings) if agg_row and agg_row.total_bookings else 0
            refund_count = int(agg_row.refund_count) if agg_row and agg_row.refund_count else 0
            
            refund_preference = "low"
            if total_bookings > 0:
                if (refund_count / total_bookings) > 0.5:
                    refund_preference = "high"
                elif (refund_count / total_bookings) > 0.2:
                    refund_preference = "medium"
                    
            profile_type = "premium" if avg_val > 500 else "budget"
            
            profile = {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "preferred_supplier": preferred_supplier,
                "preferred_airline": preferred_airline,
                "average_booking_value": round(avg_val, 2),
                "refund_preference": refund_preference,
                "profile_type": profile_type
            }
            
            self._cache[agent_id] = profile
            return profile
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to load agent profile for agent {agent_id}: {e}")
            self._cache[agent_id] = None
            return None
