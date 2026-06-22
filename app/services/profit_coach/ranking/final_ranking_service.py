from app.core.config import settings

class FinalRankingService:
    def rank_flights(self, scored_flights: list) -> list:
        for flight in scored_flights:
            scores = flight.get("scores", {})

            final_score = (
                scores.get("price_score", 0) * settings.PRICE_WEIGHT +
                scores.get("profit_score", 0) * settings.PROFIT_WEIGHT +
                scores.get("reliability_score", 0) * settings.RELIABILITY_WEIGHT +
                scores.get("convenience_score", 0) * settings.CONVENIENCE_WEIGHT +
                scores.get("baggage_score", 0) * settings.CONVERSION_WEIGHT * 0.4 +
                scores.get("refundability_score", 0) * settings.CONVERSION_WEIGHT * 0.3 +
                scores.get("meals_score", 0) * settings.CONVERSION_WEIGHT * 0.3
            )
            flight["final_score"] = round(final_score, 2)

        return sorted(scored_flights, key=lambda x: x["final_score"], reverse=True)
