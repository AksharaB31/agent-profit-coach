from typing import Dict, Any

class SupplierReliabilityService:
    def calculate_score(self, reliability_data: Dict[str, Any], health_status: str) -> float:
        """
        Calculates a reliability score between 0.0 and 1.0 based on historical booking success 
        ratio and current supplier health status.
        """
        base_score = reliability_data.get("success_ratio", 0.5)
        
        # Penalize if health status is poor
        if health_status:
            status = health_status.lower()
            if status in ["down", "offline", "critical"]:
                base_score *= 0.2
            elif status in ["degraded", "warning"]:
                base_score *= 0.7
            elif status in ["excellent", "optimal"]:
                base_score = min(1.0, base_score * 1.1)
                
        return min(1.0, max(0.0, base_score))
