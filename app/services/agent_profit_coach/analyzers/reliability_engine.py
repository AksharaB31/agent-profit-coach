from typing import Dict, Any
from app.core.config import settings
from app.services.agent_profit_coach.core.logger import setup_logger

logger = setup_logger(__name__)

class ReliabilityEngine:
    """Engine responsible for calculating reliability and risk metrics based on historical DB data"""
    
    def analyze(self, supplier_code: str, historical_metrics: Dict[str, Any] = None) -> Dict[str, float]:
        """
        Calculates reliability_score, booking_success_probability, cancellation_risk.
        Uses environment-configured defaults if historical DB data is missing or insufficient.
        """
        if not historical_metrics:
            historical_metrics = {}
            
        total_bookings = historical_metrics.get("total_bookings", 0)
        
        # If DB data is insufficient, use defaults from settings
        if total_bookings < settings.MIN_BOOKING_THRESHOLD:
            logger.info(f"Insufficient historical data for {supplier_code}. Using fallback defaults.")
            return {
                "reliability_score": settings.DEFAULT_RELIABILITY_SCORE,
                "booking_success_probability": settings.DEFAULT_BOOKING_SUCCESS_PROBABILITY,
                "cancellation_risk": settings.DEFAULT_CANCELLATION_RISK
            }
            
        # Real calculation from DB data (simplified for example)
        successful_bookings = historical_metrics.get("successful_bookings", 0)
        cancelled_bookings = historical_metrics.get("cancelled_bookings", 0)
        
        success_prob = successful_bookings / total_bookings if total_bookings > 0 else 0
        cancel_risk = cancelled_bookings / total_bookings if total_bookings > 0 else 0
        
        # Reliability score could be a weighted mix
        reliability_score = success_prob * 0.8 + (1 - cancel_risk) * 0.2
        
        logger.debug(f"Reliability analyzed for {supplier_code}: score={reliability_score}")
        
        return {
            "reliability_score": round(reliability_score, 4),
            "booking_success_probability": round(success_prob, 4),
            "cancellation_risk": round(cancel_risk, 4)
        }
