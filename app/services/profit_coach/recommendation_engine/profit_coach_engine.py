import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.api.schemas import ProfitCoachRequest
from app.services.profit_coach.loaders.historical_metrics_loader import HistoricalMetricsLoader
from app.services.profit_coach.loaders.search_results_loader import SearchResultsLoader
from app.services.profit_coach.analyzers.supplier_reliability_service import SupplierReliabilityService
from app.services.profit_coach.analyzers.profitability_service import ProfitabilityService
from app.services.profit_coach.scorers.price_scoring_service import PriceScoringService
from app.services.profit_coach.scorers.journey_scoring_service import JourneyScoringService
from app.services.profit_coach.scorers.ancillary_scoring_service import AncillaryScoringService
from app.services.profit_coach.ranking.final_ranking_service import FinalRankingService

logger = logging.getLogger(__name__)

class ProfitCoachEngine:
    """
    Enterprise-grade engine to orchestrate the scoring, ranking, and recommendation 
    of flights based on historical profitability, supplier reliability, and real-time search features.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.metrics_loader = HistoricalMetricsLoader(db)
        self.search_loader = SearchResultsLoader()
        
        self.reliability_analyzer = SupplierReliabilityService()
        self.profitability_analyzer = ProfitabilityService()
        
        self.price_scorer = PriceScoringService()
        self.journey_scorer = JourneyScoringService()
        self.ancillary_scorer = AncillaryScoringService()
        self.ranking_service = FinalRankingService()

    def execute(self, payload: ProfitCoachRequest) -> Dict[str, Any]:
        """
        Executes the profit coach pipeline to recommend the optimal flight and supplier.
        
        Args:
            payload (ProfitCoachRequest): The request payload containing search criteria.
            
        Returns:
            Dict[str, Any]: A dictionary containing the recommendation response.
        """
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

        # 1. Load Real-Time Search Results
        file_name = "roundtrip.json" if payload.trip_type.lower() == "roundtrip" else "oneway.json"
        file_path = BASE_DIR / "data" / file_name

        if not file_path.exists():
            logger.error(f"Search results file not found: {file_path}")
            return {"error": f"JSON file not found: {file_path}"}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
        except json.JSONDecodeError as e:
            logger.exception(f"Failed to decode JSON from {file_path}")
            return {"error": "Invalid search results data format"}
        except Exception as e:
            logger.exception(f"Unexpected error reading {file_path}")
            return {"error": "Failed to read search results"}

        if payload.trip_type.lower() == "roundtrip":
            flight_features = self.search_loader.load_roundtrip(json_data)
        else:
            flight_features = self.search_loader.load_oneway(json_data)

        logger.info(f"Loaded {len(flight_features)} raw itineraries")

        # Filter flights by requested route
        filtered_flights = [
            f for f in flight_features 
            if f.get("origin") == payload.origin and f.get("destination") == payload.destination
        ]
        
        if not filtered_flights:
            logger.warning(f"No flights found for route: {payload.origin}-{payload.destination}")
            return {"error": "No flights found for given route"}

        # 2. Extract cohort metrics for normalization
        prices = [f.get("price", 0.0) for f in filtered_flights]
        durations = [f.get("duration", 0) for f in filtered_flights]
        
        min_price, max_price = min(prices), max(prices)
        min_duration, max_duration = min(durations), max(durations)

        scored_results: List[Dict[str, Any]] = []

        # 3. Analyze & Score Each Option
        for flight in filtered_flights:
            try:
                supplier_code = flight.get("supplier", "")
                airline_code = flight.get("airline", "")
                flight_price = flight.get("price", 0.0)
                
                # Fetch historical DB intelligence
                health_status = self.metrics_loader.get_supplier_health(supplier_code)
                reliability_data = self.metrics_loader.get_supplier_reliability(supplier_code)
                profit_data = self.metrics_loader.get_historical_profitability(supplier_code)
                markup = self.metrics_loader.get_markup(None, airline_code)
                
                # Analyzers
                reliability_score = self.reliability_analyzer.calculate_score(reliability_data, health_status)
                expected_profit = self.profitability_analyzer.calculate_expected_profit(flight_price, profit_data, markup)
                
                # Simple normalization for score
                profit_score = 1.0 if expected_profit > 100 else (expected_profit / 100.0)
                
                # Scorers
                price_score = self.price_scorer.score(flight_price, min_price, max_price)
                duration_score = self.journey_scorer.score_duration(flight.get("duration", 0), min_duration, max_duration)
                convenience_score = self.journey_scorer.score_convenience(flight.get("stops", 0))
                timing_score = self.journey_scorer.score_timing(flight.get("departure_hour", 12))
                
                # Average convenience & timing for combined convenience score
                final_convenience = (convenience_score + timing_score) / 2.0
                
                baggage_score = self.ancillary_scorer.score_baggage(flight.get("baggage", 0))
                refundability_score = self.ancillary_scorer.score_refundability(flight.get("refundability", False))
                meals_score = self.ancillary_scorer.score_meals(flight.get("meals", False))

                flight_entry = {
                    "supplier_name": supplier_code, # Fallback to code if name not in JSON
                    "supplier_code": supplier_code,
                    "airline": airline_code,
                    "route": f"{payload.origin}-{payload.destination}",
                    "total_price": flight_price,
                    "expected_profit": expected_profit,
                    "duration": flight.get("duration", 0),
                    "stops": flight.get("stops", 0),
                    "baggage": flight.get("baggage", 0),
                    "refundable": flight.get("refundability", False),
                    "meals": flight.get("meals", False),
                    
                    # Store scores
                    "scores": {
                        "price_score": price_score,
                        "profit_score": profit_score,
                        "reliability_score": reliability_score,
                        "duration_score": duration_score,
                        "convenience_score": final_convenience,
                        "baggage_score": baggage_score,
                        "refundability_score": refundability_score,
                        "meals_score": meals_score
                    },
                    
                    # Extra metadata for UI
                    "cancellation_risk": 1.0 - reliability_score,
                    "booking_success_probability": reliability_score,
                    "historical_profit_margin": profit_data.get("avg_profit", 0.0)
                }
                
                scored_results.append(flight_entry)
                
            except Exception as e:
                logger.exception(f"Error scoring flight for supplier {flight.get('supplier', 'UNKNOWN')}")

        if not scored_results:
            logger.error("Failed to score any flights in the cohort.")
            return {"error": "Failed to score flights."}

        # 4. Final Ranking
        ranked_results = self.ranking_service.rank_flights(scored_results)
        best = ranked_results[0]
        
        # Format reasons
        reasons = []
        if best["scores"]["profit_score"] > 0.8: reasons.append("Highly profitable option")
        if best["scores"]["reliability_score"] > 0.8: reasons.append("Very reliable supplier")
        if best["scores"]["price_score"] > 0.8: reasons.append("Excellent pricing")
        if not reasons: reasons.append("Best overall balance")

        # 5. Deduplicate and select Alternative Suppliers
        alternative_suppliers: List[Dict[str, Any]] = []
        seen_suppliers = {best["supplier_code"]}
        
        for flight in ranked_results[1:]:
            sup_code = flight["supplier_code"]
            if sup_code not in seen_suppliers:
                alternative_suppliers.append({
                    "supplier": sup_code,
                    "profit": round(flight["expected_profit"], 2)
                })
                seen_suppliers.add(sup_code)
                
            if len(alternative_suppliers) >= 3:
                break

        # 6. Output Response (Rounded to 2 decimal places)
        return {
            "recommended_supplier": best["supplier_code"],
            "recommended_flight": best["airline"],
            "expected_profit": round(best["expected_profit"], 2),
            "profit_score": round(best["scores"]["profit_score"], 2),
            "conversion_probability": round(best["scores"]["price_score"], 2),
            "reliability_score": round(best["scores"]["reliability_score"], 2),
            "cancellation_risk": round(best["cancellation_risk"], 2),
            "booking_success_probability": round(best["booking_success_probability"], 2),
            "historical_profit_margin": round(best["historical_profit_margin"], 2),
            "reasons": reasons,
            "alternative_suppliers": alternative_suppliers
        }
