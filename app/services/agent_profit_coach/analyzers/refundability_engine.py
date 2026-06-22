class RefundabilityEngine:
    """Scores flexible booking terms."""
    
    def calculate_score(self, refundable: bool) -> float:
        return 100.0 if refundable else 0.0
