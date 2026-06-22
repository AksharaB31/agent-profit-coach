import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AIFeedbackRepository:
    """
    Repository for storing continuous learning feedback from real-world bookings.
    Since we cannot create new DB tables/migrations per constraints, we persist 
    the outcomes in a local structured JSON datastore that the model_trainer 
    can ingest in the future.
    """
    
    def __init__(self):
        self.data_dir = Path(__file__).resolve().parents[3] / "data" / "ai_training"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.data_dir / "feedback_loop.json"
        
        if not self.feedback_file.exists():
            with open(self.feedback_file, "w", encoding="utf-8") as f:
                json.dump([], f)
                
    def record_outcome(self, recommendation_id: str, booked: bool, cancelled: bool, profit_earned: float, features: Optional[Dict[str, Any]] = None) -> bool:
        """Records the final outcome of an AI recommendation for future retraining."""
        try:
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            outcome = {
                "recommendation_id": recommendation_id,
                "booked": booked,
                "cancelled": cancelled,
                "profit_earned": profit_earned,
                "is_successful": booked and not cancelled,
                "features": features or {}
            }
            
            data.append(outcome)
            
            with open(self.feedback_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Recorded AI feedback outcome for recommendation: {recommendation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record AI feedback: {e}")
            return False
