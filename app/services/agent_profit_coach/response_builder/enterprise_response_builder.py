import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from sqlalchemy.orm import Session 

from app.core.config import settings
from app.api.schemas import ProfitCoachRequest
from app.services.agent_profit_coach.search_loader.json_search_loader import JsonSearchLoader
from app.services.agent_profit_coach.db_loader.supplier_loader import SupplierLoader
from app.services.agent_profit_coach.db_loader.reliability_loader import ReliabilityLoader
from app.services.agent_profit_coach.db_loader.profitability_loader import ProfitabilityLoader
from app.services.agent_profit_coach.db_loader.conversion_loader import ConversionLoader
from app.services.agent_profit_coach.db_loader.agent_loader import AgentLoader
from app.services.agent_profit_coach.scorers.itinerary_scoring_engine import ItineraryScoringEngine
from app.services.agent_profit_coach.scorers.itinerary_ranker import ItineraryRanker

from fastapi import HTTPException 

logger = logging.getLogger(__name__)

class EnterpriseResponseBuilder:
    """Orchestrates the entire Agent Profit Coach pipeline and builds the Pydantic-compatible response."""
    
    def __init__(self, db: Session):
        self.search_loader = JsonSearchLoader()
        self.supplier_loader = SupplierLoader(db)
        self.reliability_loader = ReliabilityLoader(db)
        self.profitability_loader = ProfitabilityLoader(db)
        self.conversion_loader = ConversionLoader(db)
        self.agent_loader = AgentLoader(db)
        self.scoring_engine = ItineraryScoringEngine()
        self.ranker = ItineraryRanker()

    def _map_itinerary(self, item: Dict) -> Dict:
        sup_code = item["supplier"].get("code", "UNKNOWN")
        return {
            "supplier": sup_code,
            "airline": item["itinerary"].get("airline", "UNKNOWN"),
            "flight_numbers": item["itinerary"].get("flight_numbers", []),
            "price": item["pricing"].get("supplier_price", 0.0),
            "currency": item["pricing"].get("currency", "EUR"),
            "expected_agent_profit": item["pricing"].get("expected_agent_profit", 0.0),
            "historical_agent_profit": item["pricing"].get("historical_agent_profit", 0.0),
            "profit_score": item["scores"].get("profit_score", 0.0),
            "duration_minutes": item["itinerary"].get("duration_minutes", 0),
            "stops": item["itinerary"].get("stops", 0),
            "baggage": item["itinerary"].get("baggage", "0KG"),
            "refundable": item["itinerary"].get("refundable", False),
            "meals": item["itinerary"].get("meals", False),
            "reliability_score": item.get("reliability_metrics", {}).get("reliability_score", 0.0),
            "conversion_probability": item["scores"].get("conversion_probability", item["scores"].get("conversion_score", 0.0)),
            "booking_success_probability": item.get("reliability_metrics", {}).get("booking_success_probability", 0.0),
            "cancellation_risk": item.get("reliability_metrics", {}).get("cancellation_risk", 0.0),
            "journey_convenience_score": item["scores"].get("journey_convenience_score", 0.0),
            "expected_revenue": item["pricing"].get("expected_revenue", 0.0),
            "ai_predicted_profit": item["pricing"].get("ai_predicted_profit", 0.0),
            "profit_prediction_source": item["pricing"].get("profit_prediction_source", "heuristic_only"),
            "profit_opportunity_score": item["scores"].get("profit_opportunity_score", 0.0),
            "recommendation_reasons": item.get("reasons", []),
            "score_breakdown": item.get("score_breakdown", {})
        }

    def _build_empty_response(self, payload: ProfitCoachRequest, reason: str, metrics: dict = None) -> Dict[str, Any]:
        """Returns a safe enterprise fallback response when itineraries cannot be processed."""
        if metrics is None:
            metrics = {
                "raw_itineraries": 0,
                "normalized_itineraries": 0,
                "scored_itineraries": 0,
                "failed_itineraries": 0,
                "ranked_itineraries": 0,
                "skipped_itineraries": 0,
                "normalization_failures": []
            }
            
        file_name = "roundtrip.json" if payload.trip_type.lower() == "roundtrip" else "oneway.json"
            
        return {
            "route_analysis": {
                "origin": payload.origin,
                "destination": payload.destination,
                "trip_type": payload.trip_type,
                "departure_date": payload.departure_date
            },
            "best_overall_itinerary": None,
            "supplier_route_profitability": [],
            "market_insights": {
                "cheapest_supplier": None,
                "fastest_supplier": None,
                "most_reliable_supplier": None,
                "best_value_supplier": None,
                "highest_profit_supplier": None
            },
            "alternative_recommendations": [],
            "engine_metadata": {
                "search_source": file_name,
                "database_analysis_enabled": True,
                "live_search_analysis_enabled": True,
                "total_itineraries_analyzed": metrics.get("raw_itineraries", 0),
                "total_suppliers_analyzed": 0,
                "ranking_engine_version": "enterprise_v2",
                "metrics_source": "database_only",
                "status": "no_itineraries_found",
                "reason": reason
            }
        }

    def build(self, payload: ProfitCoachRequest) -> Dict[str, Any]:
        BASE_DIR = Path(__file__).resolve().parents[3]
        DATA_DIR = BASE_DIR / "data"

        # Pipeline Metrics
        metrics = {
            "raw_itineraries": 0,
            "normalized_itineraries": 0,
            "scored_itineraries": 0,
            "failed_itineraries": 0,
            "ranked_itineraries": 0
        }

        # 1. Load Live Search Data
        file_name = "roundtrip.json" if payload.trip_type.lower() == "roundtrip" else "oneway.json"
        file_path = DATA_DIR / file_name

        logger.info(f"Selected search result file path: {file_path}")

        if not file_path.exists():
            logger.error(f"File exists check failed for: {file_path}")
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "search_results_not_found",
                        "message": "Search result dataset missing"
                    }
                }
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
        except Exception as e:
            logger.exception("Failed to load JSON data")
            raise HTTPException(status_code=500, detail="Internal server error while parsing search results")

        if payload.trip_type.lower() == "roundtrip":
            raw_flights = self.search_loader.load_roundtrip(json_data)
        else:
            raw_flights = self.search_loader.load_oneway(json_data)

        metrics["raw_itineraries"] = len(raw_flights)
        logger.info(f"Raw flight count: {metrics['raw_itineraries']}")

        flights = self.search_loader.normalize_itineraries(raw_flights, payload.origin, payload.destination, payload.trip_type)
        
        if not flights or not isinstance(flights, list):
            logger.warning("No normalized itineraries generated for route %s-%s", payload.origin, payload.destination)
            return self._build_empty_response(payload, "No normalized itineraries generated", metrics=metrics)

        # 1.5 Defensive Validation
        valid_flights = []
        normalization_failures = []
        
        for f in flights:
            if not isinstance(f, dict):
                normalization_failures.append("Malformed itinerary payload")
                continue
            if f.get("price") is None or float(f.get("price", 0)) <= 0:
                normalization_failures.append("Missing or invalid price")
                continue
            if not f.get("supplier_code"):
                normalization_failures.append("Missing supplier")
                continue
            if not f.get("airline"):
                normalization_failures.append("Missing airline")
                continue
            if f.get("duration_minutes") is None or f.get("duration_minutes", 0) <= 0:
                normalization_failures.append("Invalid duration")
                continue
            valid_flights.append(f)

        metrics["normalized_itineraries"] = len(flights)
        metrics["skipped_itineraries"] = len(flights) - len(valid_flights)
        metrics["normalization_failures"] = list(set(normalization_failures))
        
        logger.info(f"Normalized itinerary count: {metrics['normalized_itineraries']} (Skipped: {metrics['skipped_itineraries']})")

        flights = valid_flights
        
        if not flights:
            logger.warning("All normalized itineraries were skipped due to validation failures for route %s-%s", payload.origin, payload.destination)
            return self._build_empty_response(payload, "All itineraries failed normalization validation", metrics)

        # Cohort metrics for normalization
        prices = [f.get("price", 999999) for f in flights]
        durations = [f.get("duration_minutes", 999999) for f in flights]
        min_price, max_price = min(prices), max(prices)
        avg_price = sum(prices) / len(prices) if prices else 0.0
        min_duration, max_duration = min(durations), max(durations)

        scored_results = []
        suppliers_seen = set()
        max_expected_revenue_cohort = 0.0
        
        from datetime import datetime

        # 1.5 Pre-computation (Pass 1)
        pass_1_errors = []
        for f in flights:
            try:
                sup_code = f.get("supplier_code", "UNKNOWN")
                air_code = f.get("airline", "UNKNOWN")
                
                sup_details = self.supplier_loader.get_supplier_details(sup_code)
                sup_details["code"] = sup_code
                
                rel_data = self.reliability_loader.get_supplier_reliability(sup_code)
                hist_profit = self.profitability_loader.get_historical_agent_profit(sup_code, payload.origin, payload.destination)
                rec_markup = self.profitability_loader.get_recommended_agent_markup(air_code)
                conv_prob_db = self.conversion_loader.get_route_conversion_probability(sup_code, payload.origin, payload.destination)
                supplier_incentive = self.profitability_loader.get_supplier_incentive(sup_code)
                
                # Pass 1: Pre-calculate raw expected revenue
                base_price = f.get("price", 0.0)
                expected_agent_profit = hist_profit + (rec_markup if rec_markup else 0.0) + (supplier_incentive if supplier_incentive else 0.0)
                
                # We need raw conversion probability for expected revenue
                dt = payload.departure_date
                month = datetime.now().month
                day_of_week = datetime.now().weekday()
                adv_days = 0
                if dt:
                    try:
                        parsed = datetime.strptime(dt, "%Y-%m-%d")
                        month = parsed.month
                        day_of_week = parsed.weekday()
                        adv_days = max(0, (parsed - datetime.now()).days)
                    except Exception:
                        pass
                        
                features = {
                    "price": base_price,
                    "duration_minutes": f.get("duration_minutes", 0),
                    "stops": f.get("stops", 0),
                    "is_refundable": f.get("refundable", False),
                    "month": month,
                    "day_of_week": day_of_week,
                    "advance_purchase_days": adv_days
                }
                
                raw_conv_prob = self.scoring_engine.ai_engine.predict_conversion_probability(features, settings.DEFAULT_BOOKING_SUCCESS_PROBABILITY)
                
                p_total = float(rel_data.get("process_total", 0))
                p_success = float(rel_data.get("process_success", 0))
                raw_success_prob = float(self.scoring_engine.reliability.calculate_booking_success_probability(p_success, p_total))
                
                raw_expected_revenue = expected_agent_profit * raw_conv_prob * raw_success_prob if (raw_conv_prob > 0 and raw_success_prob > 0) else 0.0
                max_expected_revenue_cohort = max(max_expected_revenue_cohort, raw_expected_revenue)
                
                # Pre-fetch aggregate profit features for ML profit model
                sup_avg_profit = self.profitability_loader.get_supplier_avg_profit(sup_code)
                air_avg_profit = self.profitability_loader.get_airline_avg_profit(air_code)

                # Cache these so we don't fetch from DB twice
                f["_cached_rel"] = rel_data
                f["_cached_profit"] = hist_profit
                f["_cached_markup"] = rec_markup
                f["_cached_conv"] = conv_prob_db
                f["_cached_sup_avg_profit"] = sup_avg_profit
                f["_cached_air_avg_profit"] = air_avg_profit
                f["_cached_incentive"] = supplier_incentive
            except Exception as e:
                import traceback
                pass_1_errors.append(f"{type(e).__name__}: {str(e)} - {traceback.format_exc()}")
                logger.warning(f"Pass 1 prep failed: {e}")
                
        # Agent personalization
        agent_profile = self.agent_loader.get_agent_profile(payload.agent_id)

        # 2. Score Each Itinerary (Pass 2)
        for f in flights:
            try:
                sup_code = f.get("supplier_code", "UNKNOWN")
                
                sup_details = self.supplier_loader.get_supplier_details(sup_code)
                sup_details["code"] = sup_code
                
                profit_model_features = {
                    "total_amount": f.get("price", 0.0),
                    "passenger_count": 1,
                    "markup_amount": f.get("_cached_markup", 0.0),
                    "supplier_commission": 0.0,
                    "agent_markup": f.get("_cached_markup", 0.0),
                    "duration_minutes": f.get("duration_minutes", 0),
                    "stops": f.get("stops", 0),
                    "total_base": 0.0,
                    "total_tax": 0.0,
                    "supplier_avg_profit": f.get("_cached_sup_avg_profit", 0.0),
                    "airline_avg_profit": f.get("_cached_air_avg_profit", 0.0)
                }

                scored_itinerary = self.scoring_engine.score_itinerary(
                    flight=f, 
                    supplier_data=sup_details, 
                    rel_data=f.get("_cached_rel", {}), 
                    historical_agent_profit=f.get("_cached_profit", 0.0), 
                    recommended_markup=f.get("_cached_markup", 0.0),
                    supplier_incentive=f.get("_cached_incentive", 0.0),
                    min_price=min_price, 
                    max_price=max_price, 
                    avg_price=avg_price,
                    min_duration=min_duration, 
                    max_duration=max_duration,
                    conversion_data=f.get("_cached_conv", {}),
                    max_revenue_cohort=max_expected_revenue_cohort,
                    departure_date=payload.departure_date,
                    agent_profile=agent_profile,
                    profit_model_features=profit_model_features,
                    trip_type=payload.trip_type
                )
                scored_results.append(scored_itinerary)
                suppliers_seen.add(sup_code)
                metrics["scored_itineraries"] += 1
            except Exception as e:
                logger.warning(f"Failed to score itinerary: {e}")
                metrics["failed_itineraries"] += 1
                continue

        logger.info(f"Successfully scored itinerary count: {metrics['scored_itineraries']}, Failed: {metrics['failed_itineraries']}")

        if not scored_results:
            logger.warning("No itineraries successfully scored.")

        # 3. Rank Itineraries
        ranked = self.ranker.rank(scored_results)
        
        if not ranked:
            logger.warning("No itineraries successfully ranked. Returning empty results.")
            best = {}
            alternatives = []
        else:
            best = ranked[0]
            
            # 4. Generate Alternative Recommendations (Deduplicated)
            alternatives = []
            seen_suppliers = {best.get("supplier", {}).get("code", "UNKNOWN")}
            
            for item in ranked[1:]:
                sup_code = item.get("supplier", {}).get("code", "UNKNOWN")
                if sup_code not in seen_suppliers:
                    alternatives.append(item)
                    seen_suppliers.add(sup_code)
                if len(alternatives) >= 3:
                    break



        # 5. Aggregate Supplier Route Profitability
        supplier_stats = {}
        for item in scored_results:
            sup_code = item["supplier"].get("code", "UNKNOWN")
            sup_name = item["supplier"].get("name", "UNKNOWN")
            if sup_code not in supplier_stats:
                supplier_stats[sup_code] = {
                    "supplier": sup_code,
                    "supplier_name": sup_name,
                    "count": 0,
                    "best_profit": -999999.0,
                    "total_profit": 0.0,
                    "total_reliability": 0.0,
                    "best_conversion": 0.0
                }
            
            stats = supplier_stats[sup_code]
            stats["count"] += 1
            expected_profit = item["pricing"].get("expected_agent_profit", 0.0)
            stats["best_profit"] = max(stats["best_profit"], expected_profit)
            stats["total_profit"] += expected_profit
            stats["total_reliability"] += item.get("reliability_metrics", {}).get("reliability_score", 0.0)
            
            conversion_prob = item["scores"].get("conversion_probability", 0.0)
            stats["best_conversion"] = max(stats["best_conversion"], conversion_prob)
            
            logger.debug(f"Aggregating supplier {sup_code} - conversion_probability: {conversion_prob}, new best_conversion: {stats['best_conversion']}")
            
        supplier_route_profitability = []
        best_supplier_code = best.get("supplier", {}).get("code", "UNKNOWN") if best else "UNKNOWN"
        
        for code, stats in supplier_stats.items():
            supplier_route_profitability.append({
                "supplier": code,
                "supplier_name": stats["supplier_name"],
                "total_itineraries": stats["count"],
                "best_itinerary_profit": round(stats["best_profit"], 2),
                "average_agent_profit": round(stats["total_profit"] / stats["count"], 2),
                "average_reliability": round(stats["total_reliability"] / stats["count"], 2),
                "best_conversion_probability": round(stats["best_conversion"], 2),
                "recommended": (code == best_supplier_code)
            })

        # 6. Market Analysis
        if scored_results:
            market_insights = {
                "cheapest_supplier": min(scored_results, key=lambda x: x["pricing"].get("supplier_price", 999999))["supplier"].get("code", "UNKNOWN"),
                "fastest_supplier": min(scored_results, key=lambda x: x["itinerary"].get("duration_minutes", 999999))["supplier"].get("code", "UNKNOWN"),
                "most_reliable_supplier": max(scored_results, key=lambda x: x.get("reliability_metrics", {}).get("reliability_score", 0))["supplier"].get("code", "UNKNOWN"),
                "best_value_supplier": max(scored_results, key=lambda x: x["scores"].get("overall_score", 0))["supplier"].get("code", "UNKNOWN"),
                "highest_profit_supplier": max(scored_results, key=lambda x: x["pricing"].get("expected_agent_profit", 0))["supplier"].get("code", "UNKNOWN")
            }
        else:
            market_insights = {
                "cheapest_supplier": None,
                "fastest_supplier": None,
                "most_reliable_supplier": None,
                "best_value_supplier": None,
                "highest_profit_supplier": None
            }

        # 7. Engine Metadata
        metrics_source = "database_only"

        engine_metadata = {
            "search_source": file_name,
            "database_analysis_enabled": True,
            "live_search_analysis_enabled": True,
            "total_itineraries_analyzed": len(flights),
            "total_suppliers_analyzed": len(suppliers_seen),
            "ranking_engine_version": "enterprise_v2",
            "metrics_source": metrics_source,
            "pass_1_errors": pass_1_errors
        }

        # 8. Assemble Final Dict (matching Pydantic EnterpriseProfitCoachResponse structure)
        return {
            "route_analysis": {
                "origin": payload.origin,
                "destination": payload.destination,
                "departure_date": payload.departure_date,
                "trip_type": payload.trip_type
            },
            "best_overall_itinerary": self._map_itinerary(best) if best else None,
            "supplier_route_profitability": supplier_route_profitability,
            "market_insights": market_insights,
            "alternative_recommendations": [self._map_itinerary(alt) for alt in alternatives] if alternatives else [],
            "engine_metadata": engine_metadata
        }
