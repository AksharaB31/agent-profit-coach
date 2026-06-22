class ConversionEngine:
    """
    Calculates predictive conversion probability using a 6-factor enterprise algorithm.
    """
    def __init__(self):
        pass

    def calculate_refundability_score(self, refundable: bool) -> float:
        return 1.0 if refundable else 0.5

    def calculate_stop_score(self, stops: int) -> float:
        if stops == 0:
            return 1.0
        elif stops == 1:
            return 0.7
        else:
            return 0.4

    def calculate_price_score(self, price: float, average_route_price: float) -> float:
        if average_route_price <= 0 or price <= 0:
            return 0.0
        
        ratio = price / average_route_price
        score = 1.0 - ((ratio - 0.5) / 1.5)
        return max(0.0, min(score, 1.0))

    def calculate_route_conversion_rate(self, successful_route_bookings: int, total_route_searches: int) -> float:
        if total_route_searches == 0:
            return 0.0
        return max(0.0, min(successful_route_bookings / total_route_searches, 1.0))

    def calculate_conversion_probability(self, 
                                         reliability_score: float, 
                                         price_score: float, 
                                         convenience_score: float, 
                                         refundability_score: float, 
                                         stop_score: float, 
                                         supplier_route_performance: float,
                                         has_historical_data: bool = True) -> float:
        
        import logging
        logger = logging.getLogger(__name__)

        if not has_historical_data:
            logger.warning("Conversion probability calculation bypassed: No historical conversion analytics found in DB.")
            return 0.0
            
        probability = (
            (reliability_score * 0.30) +
            (price_score * 0.20) +
            (convenience_score * 0.20) +
            (refundability_score * 0.10) +
            (stop_score * 0.10) +
            (supplier_route_performance * 0.10)
        )
        
        final_probability = max(0.0, min(probability, 1.0))
        logger.info(f"Dynamically calculated conversion_probability: {final_probability:.2f} (rel={reliability_score:.2f}, price={price_score:.2f}, conv={convenience_score:.2f}, ref={refundability_score:.2f}, stops={stop_score:.2f}, perf={supplier_route_performance:.2f})")
        return final_probability
