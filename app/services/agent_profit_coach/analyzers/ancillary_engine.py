class AncillaryEngine:
    """Scores ancillary availability."""
    
    def score_baggage(self, baggage: str) -> float:
        if not baggage or baggage in ["0KG", "None", "false"]:
            return 0.0
        if "20" in baggage or "23" in baggage:
            return 80.0
        if "30" in baggage or "40" in baggage:
            return 100.0
        return 50.0

    def score_meals(self, meals: bool) -> float:
        return 100.0 if meals else 0.0
