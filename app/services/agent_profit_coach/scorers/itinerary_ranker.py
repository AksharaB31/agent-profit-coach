import logging
from typing import List, Dict, Any
from app.services.agent_profit_coach.core.logger import setup_logger
from app.services.agent_profit_coach.core.exceptions import MissingItineraryDataException
from app.services.agent_profit_coach.explainability.enhanced_explainability_service import EnhancedExplainabilityService

logger = setup_logger(__name__)

class ItineraryRanker:
    """Ranks all scored itineraries based on overall_score."""
    
    def __init__(self):
        pass

    def validate_itinerary(self, itinerary: Dict[str, Any]):
        """Enterprise validation to ensure no missing critical data before ranking"""
        required_keys = ["supplier", "itinerary", "scores", "pricing"]
        
        for key in required_keys:
            if key not in itinerary:
                logger.error(f"Validation failed: missing '{key}' in itinerary.")
                raise MissingItineraryDataException(f"Missing required key: {key}")
                
        pricing = itinerary.get("pricing", {})
        if "expected_agent_profit" not in pricing:
            logger.error("Validation failed: missing 'expected_agent_profit' in pricing.")
            raise MissingItineraryDataException("Missing 'expected_agent_profit' in pricing.")
                
        scores = itinerary.get("scores", {})
        if "overall_score" not in scores:
            logger.error("Validation failed: missing 'overall_score' in scores.")
            raise MissingItineraryDataException("Missing 'overall_score' in itinerary scores.")

    def rank(self, scored_itineraries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid_itineraries = []
        
        for itinerary in scored_itineraries:
            try:
                # 1. Enterprise Validation
                self.validate_itinerary(itinerary)
                
                # 2. Use the dynamically calculated overall score from the engine
                scores = itinerary.get("scores", {})
                recalculated_overall_score = scores.get("overall_score", 0.0)
                
                supplier_code = itinerary.get("supplier", {}).get("code", "UNKNOWN")
                expected_profit = itinerary.get("pricing", {}).get("expected_agent_profit", 0.0)
                
                logger.info(
                    "Validated & Scored itinerary | supplier=%s | overall_score=%s | expected_agent_profit=%s",
                    supplier_code,
                    recalculated_overall_score,
                    expected_profit
                )
                
                valid_itineraries.append(itinerary)
                
            except MissingItineraryDataException as e:
                logger.warning(f"Skipping invalid itinerary: {e}")
                # We skip or we could raise, but skipping ensures the rest of valid results return
                continue
                
        if not valid_itineraries:
            return []

        # Calculate true cohort maximums and averages
        max_expected_revenue = max((it.get("pricing", {}).get("expected_revenue", 0.0) for it in valid_itineraries), default=0.0)
        max_profit_score = max((it.get("scores", {}).get("profit_score", 0.0) for it in valid_itineraries), default=0.0)
        max_reliability = max((it.get("scores", {}).get("reliability_score", 0.0) for it in valid_itineraries), default=0.0)
        avg_success_prob = sum(it.get("scores", {}).get("conversion_probability", 0.0) for it in valid_itineraries) / len(valid_itineraries)
        avg_overall_score = sum(it.get("scores", {}).get("overall_score", 0.0) for it in valid_itineraries) / len(valid_itineraries)
        avg_reliability = sum(it.get("scores", {}).get("reliability_score", 0.0) for it in valid_itineraries) / len(valid_itineraries)

        # Sort itineraries
        sorted_itineraries = sorted(
            valid_itineraries, 
            key=lambda x: x.get("scores", {}).get("overall_score", 0), 
            reverse=True
        )

        # Apply dynamic explainability reasons based on cohort leaders
        for idx, itinerary in enumerate(sorted_itineraries):
            reasons = []
            pricing = itinerary.get("pricing", {})
            scores = itinerary.get("scores", {})
            
            exp_rev = pricing.get("expected_revenue", 0.0)
            p_score = scores.get("profit_score", 0.0)
            conv_prob = scores.get("conversion_probability", 0.0)
            
            explainability = EnhancedExplainabilityService
            
            # Rank 1 gets the top value reason, comparing against market average
            if idx == 0 and scores.get("overall_score", 0) > 0:
                reasons.append(explainability.generate_reason("Best value supplier on route", scores.get("overall_score", 0), avg_overall_score))
                
            # Highest expected revenue dynamically
            if exp_rev >= max_expected_revenue and max_expected_revenue > 0:
                reasons.append(explainability.generate_reason("Highest expected revenue", exp_rev, max_expected_revenue))
                
            # Highest profit score dynamically
            if p_score >= max_profit_score and max_profit_score > 0:
                reasons.append(explainability.generate_reason("Highest profitability score", p_score, max_profit_score))
                
            # Above average success dynamically
            if conv_prob > avg_success_prob and conv_prob > 0.5:
                reasons.append(explainability.generate_reason("Strong booking success history", conv_prob * 100, avg_success_prob * 100))
                
            # Best reliability dynamically compared strictly to average
            rel_score = scores.get("reliability_score", 0.0)
            if rel_score > avg_reliability and avg_reliability > 0:
                reasons.append(explainability.generate_reason("Supplier reliability above average", rel_score * 100, avg_reliability * 100))
                
            itinerary["reasons"] = reasons

        return sorted_itineraries
