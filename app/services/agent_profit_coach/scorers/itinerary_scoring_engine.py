from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings
from app.services.agent_profit_coach.analytics.reliability_engine import ReliabilityEngine
from app.services.agent_profit_coach.analytics.conversion_engine import ConversionEngine
from app.services.agent_profit_coach.analyzers.profitability_engine import ProfitabilityEngine
from app.services.agent_profit_coach.analyzers.convenience_engine import ConvenienceEngine
from app.services.agent_profit_coach.analyzers.ancillary_engine import AncillaryEngine
from app.services.agent_profit_coach.analyzers.refundability_engine import RefundabilityEngine
from app.services.agent_profit_coach.analyzers.timing_engine import TimingEngine
from app.services.agent_profit_coach.analyzers.score_normalization_service import ScoreNormalizationService
from app.domain.ai_engine.inference_engine import AIInferenceEngine

class ItineraryScoringEngine:
    """Orchestrates all analyzers to score a single itinerary."""
    
    def __init__(self):
        self.reliability = ReliabilityEngine()
        self.conversion = ConversionEngine()
        self.profitability = ProfitabilityEngine()
        self.convenience = ConvenienceEngine()
        self.ai_engine = AIInferenceEngine()
        self.ancillary = AncillaryEngine()
        self.refundability = RefundabilityEngine()
        self.timing = TimingEngine()

    def score_itinerary(
        self, 
        flight: Dict[str, Any], 
        supplier_data: Dict[str, Any],
        rel_data: Dict[str, Any],
        historical_agent_profit: float,
        recommended_markup: float,
        min_price: float, max_price: float,
        avg_price: float,
        min_duration: int, max_duration: int,
        conversion_data: Dict[str, int],
        max_revenue_cohort: float,
        min_revenue_cohort: float,
        departure_date: str = "",
        agent_profile: Dict[str, Any] = None,
        profit_model_features: Dict[str, Any] = None,
        trip_type: str = "oneway",
        supplier_incentive: float = 0.0
    ) -> Dict[str, Any]:
        
        # 1. Reliability Engine
        p_total = float(rel_data.get("process_total", 0))
        p_success = float(rel_data.get("process_success", 0))
        p_ticketed = float(rel_data.get("process_ticketed", 0))
        p_refunded = float(rel_data.get("process_refunded", 0))
        
        b_total = float(rel_data.get("booking_total", 0))
        b_cancelled = float(rel_data.get("booking_cancelled", 0))
        b_refunded = float(rel_data.get("booking_refunded", 0))
        
        success_prob = float(self.reliability.calculate_booking_success_probability(p_success, p_total))
        cancel_risk = float(self.reliability.calculate_cancellation_risk(b_cancelled, b_total))
        ticketing_rate = float(self.reliability.calculate_ticketing_success_rate(p_ticketed, p_total))
        refund_rate = float(self.reliability.calculate_refund_success_rate(p_refunded, p_total))
        
        health_status = supplier_data.get("health_status", "unknown")
        reliability_score = float(self.reliability.calculate_supplier_reliability(
            success_prob, cancel_risk, ticketing_rate, refund_rate, health_status
        ))
        
        rel_metrics = {
            "reliability_score": round(reliability_score, 2),
            "booking_success_probability": round(success_prob, 2),
            "cancellation_risk": round(cancel_risk, 2),
            "metrics_source": "database_only"
        }
        
        # 2. Profitability
        profit_data = self.profitability.calculate_profitability(
            base_price=flight.get("price", 0.0), 
            historical_profit=historical_agent_profit, 
            markup=recommended_markup,
            incentive=supplier_incentive
        )
        
        sell_price = profit_data.get("sell_price", flight.get("price", 0.0))
        heuristic_agent_profit = profit_data.get("expected_agent_profit", 0.0)

        # ML Profit Model Integration: blend heuristic with ML prediction
        ml_predicted_profit = self.ai_engine.predict_expected_profit(
            profit_model_features or {}, trip_type, fallback_profit=-1.0
        )
        if ml_predicted_profit >= 0:
            ml_weight = settings.ML_PROFIT_WEIGHT
            agent_profit = ml_predicted_profit * ml_weight + heuristic_agent_profit * (1.0 - ml_weight)
            profit_prediction_source = "ml_blended"
        else:
            agent_profit = heuristic_agent_profit
            ml_predicted_profit = heuristic_agent_profit
            profit_prediction_source = "heuristic_only"

        profit_score = profit_data.get("profit_score", 0.0)
        profit_margin_percent = profit_data.get("profit_margin_percent", 0.0)
        
        # 3. Convenience & Factors
        stops = flight.get("stops", flight.get("stop_count", flight.get("segment_count", 1) - 1))
        duration = flight.get("duration_minutes", 999999)
        refundable = flight.get("refundable", False)
        
        conv_score = self.convenience.calculate_score(duration, stops, min_duration, max_duration)
        
        bag_score = self.ancillary.score_baggage(flight.get("baggage", "0KG"))
        meal_score = self.ancillary.score_meals(flight.get("meals", False))
        ref_score = self.conversion.calculate_refundability_score(refundable)
        time_score = self.timing.calculate_score(flight.get("departure_hour", 12))
        
        stop_score = self.conversion.calculate_stop_score(stops)
        price_score = self.conversion.calculate_price_score(sell_price, avg_price)
        
        # 4. Dynamic Conversion Score (using AI Inference)
        # AI Feature Extraction for Conversion Model
        # Dynamic fallback if departure date is missing
        month = datetime.now().month
        day_of_week = datetime.now().weekday()
        advance_purchase_days = 0
        
        if departure_date:
            try:
                dt = datetime.strptime(departure_date, "%Y-%m-%d")
                month = dt.month
                day_of_week = dt.weekday()
                advance_purchase_days = max(0, (dt - datetime.now()).days)
            except Exception:
                pass
                
        conv_features = {
            "price": flight.get("price", 0.0),
            "duration_minutes": flight.get("duration_minutes", 0),
            "stops": flight.get("stops", 0),
            "is_refundable": flight.get("refundable", False),
            "month": month,
            "day_of_week": day_of_week,
            "advance_purchase_days": advance_purchase_days
        }
        
        # We strictly rely on the AI model for conversion probability. Default is 0.0 if missing.
        conv_prob = self.ai_engine.predict_conversion_probability(conv_features, settings.DEFAULT_BOOKING_SUCCESS_PROBABILITY)
        conversion_score = conv_prob * 100.0
            
        conv_metrics_source = "ai_enhanced"
        
        # A. Expected Revenue Calculation (Uses both conversion and booking success probability)
        expected_revenue = agent_profit * conv_prob * success_prob if (conv_prob > 0 and success_prob > 0) else 0.0
        
        # Normalize all inputs
        norm = ScoreNormalizationService
        
        # Max profit dynamically based on cohort's maximum expected revenue. No hardcoded caps.
        # Fallback to 1.0 to avoid division by zero if cohort has 0 revenue across the board
        revenue_score = norm.normalize_value(expected_revenue, min_val=min_revenue_cohort, max_val=max(max_revenue_cohort, 1.0))
        
        booking_score = norm.normalize_probability(conv_prob)
        reliability_score_norm = norm.normalize_reliability(reliability_score)
        convenience_score_norm = norm.normalize_convenience(conv_score)
        
        # Agent-specific preference adjustments
        preference_boost = 0.0
        if agent_profile:
            sup_code = supplier_data.get("code", "")
            if agent_profile.get("preferred_supplier") == sup_code:
                preference_boost += 0.05
            if agent_profile.get("preferred_airline") == flight.get("airline", ""):
                preference_boost += 0.03
            if agent_profile.get("refund_preference") == "high" and flight.get("refundable", False):
                preference_boost += 0.04
            if agent_profile.get("refund_preference") == "low" and not flight.get("refundable", False):
                preference_boost += 0.02
            if agent_profile.get("profile_type") == "premium":
                profit_weight = settings.PROFIT_WEIGHT + 0.05
                convenience_weight = settings.CONVENIENCE_WEIGHT - 0.05
            else:
                profit_weight = settings.PROFIT_WEIGHT - 0.05
                convenience_weight = settings.CONVENIENCE_WEIGHT + 0.05
            rel_weight = settings.RELIABILITY_WEIGHT
            price_weight = settings.PRICE_WEIGHT
            conv_weight = settings.CONVERSION_WEIGHT
        else:
            profit_weight = settings.PROFIT_WEIGHT
            rel_weight = settings.RELIABILITY_WEIGHT
            convenience_weight = settings.CONVENIENCE_WEIGHT
            price_weight = settings.PRICE_WEIGHT
            conv_weight = settings.CONVERSION_WEIGHT

        remaining = 1.0 - profit_weight - rel_weight - convenience_weight - price_weight - conv_weight
        profit_weight += remaining * 0.5
        convenience_weight += remaining * 0.5

        # Normalize price score if available (assuming price_score is 0-100)
        price_score_norm = price_score

        # B. Profit Opportunity Score (Deterministic, Transparent Math - 0-100 Scale)
        profit_opportunity_score_100 = (
            revenue_score * profit_weight +
            reliability_score_norm * rel_weight +
            convenience_score_norm * convenience_weight +
            price_score_norm * price_weight +
            conversion_score * conv_weight
        ) + (preference_boost * 100.0)
        
        profit_opportunity_score_100 = max(0.0, min(profit_opportunity_score_100, 100.0))
        
        score_breakdown = {
            "expected_revenue_score": round(revenue_score, 2),
            "booking_score": round(conversion_score, 2),
            "convenience_score": round(convenience_score_norm, 2),
            "price_score": round(price_score_norm, 2),
            "final_profit_opportunity_score": round(profit_opportunity_score_100, 2)
        }
        
        # 5. Build Output
        scores_dict = {
            "profit_score": round(profit_score, 2),
            "reliability_score": round(reliability_score, 2),
            "price_score": round(price_score, 2),
            "convenience_score": round(conv_score, 2),
            "conversion_score": round(conv_prob, 2),
            "conversion_probability": round(conv_prob, 2),
            "journey_convenience_score": round(conv_score, 2),
            "baggage_score": round(bag_score, 2),
            "meal_score": round(meal_score, 2),
            "timing_score": round(time_score, 2),
            "refundability_score": round(ref_score, 2),
            "overall_score": round(profit_opportunity_score_100, 2),
            "profit_opportunity_score": round(profit_opportunity_score_100, 2)
        }
        
        # Reason generation moved to ItineraryRanker for dynamic cohort-level assignment
        reasons = []
            
        return {
            "supplier": supplier_data,
            "itinerary": flight,
            "pricing": {
                "supplier_price": flight.get("price", 0.0),
                "expected_agent_profit": round(agent_profit, 2),
                "historical_agent_profit": round(historical_agent_profit, 2),
                "profit_margin_percent": round(profit_margin_percent, 2),
                "currency": flight.get("currency", "EUR"),
                "expected_revenue": round(expected_revenue, 2),
                "ai_predicted_profit": round(ml_predicted_profit, 2),
                "profit_prediction_source": profit_prediction_source
            },
            "reliability_metrics": rel_metrics,
            "conversion_metrics_source": conv_metrics_source,
            "scores": scores_dict,
            "score_breakdown": score_breakdown,
            "reasons": reasons
        }
