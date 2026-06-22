class AncillaryScoringService:
    def score_baggage(self, baggage_weight: int) -> float:
        # 30kg+ is excellent, 20kg+ is good, 0kg is poor
        if baggage_weight >= 30: return 1.0
        elif baggage_weight >= 20: return 0.8
        elif baggage_weight >= 10: return 0.5
        else: return 0.0

    def score_refundability(self, is_refundable: bool) -> float:
        return 1.0 if is_refundable else 0.0

    def score_meals(self, meals_included: bool) -> float:
        return 1.0 if meals_included else 0.0
