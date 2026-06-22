from typing import Dict, Any

class EnhancedExplainabilityService:
    """Generates quantified, numerical explainability for AI decisions."""

    @staticmethod
    def generate_reason(reason_text: str, value: float, benchmark: float) -> Dict[str, Any]:
        """
        Creates a structured reason object.
        Example: {"reason": "Highest expected revenue", "value": 620, "benchmark": 410}
        """
        return {
            "reason": reason_text,
            "value": round(value, 2),
            "benchmark": round(benchmark, 2)
        }
