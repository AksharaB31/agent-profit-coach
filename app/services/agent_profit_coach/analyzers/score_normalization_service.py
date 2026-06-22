class ScoreNormalizationService:
    """Normalizes raw scoring inputs to a standard 0-100 scale."""

    @staticmethod
    def normalize_value(value: float, min_val: float, max_val: float) -> float:
        if max_val <= min_val:
            return 0.0
        normalized = ((value - min_val) / (max_val - min_val)) * 100.0
        return max(0.0, min(normalized, 100.0))

    @staticmethod
    def normalize_probability(probability: float) -> float:
        """Probabilities are 0.0 to 1.0. Scale to 0-100."""
        return max(0.0, min(probability * 100.0, 100.0))

    @staticmethod
    def normalize_reliability(reliability: float) -> float:
        """Reliability is 0.0 to 1.0. Scale to 0-100."""
        return max(0.0, min(reliability * 100.0, 100.0))

    @staticmethod
    def normalize_convenience(convenience_score: float) -> float:
        """Convenience score is typically 0.0 to 100.0, ensure it stays clamped."""
        return max(0.0, min(convenience_score, 100.0))
