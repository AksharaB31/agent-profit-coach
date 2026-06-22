from typing import Dict, Any

class SupplierReliabilityAnalyzer:
    """Combines DB health status and empirical success rate into a reliability score (0-100)."""
    
    def calculate_score(self, success_rate: float, health_status: str) -> float:
        # Base score from empirical success rate
        base_score = success_rate * 100.0
        
        # Penalties based on hard health_status
        if health_status == "down":
            return 0.0
        elif health_status == "degraded":
            return base_score * 0.5
        elif health_status == "unknown":
            return base_score * 0.8
            
        return base_score
