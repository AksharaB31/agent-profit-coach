import logging
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)   

try:
    import pandas as pd
    import numpy as np
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

class AIInferenceEngine:
    """Loads saved models and generates AI-driven profit and conversion predictions.""" 

    def __init__(self):
        self.conversion_model_path = (
            Path(__file__).resolve().parents[3] / settings.CONVERSION_MODEL_PATH
        )
        self.profit_model_oneway_path = (
            Path(__file__).resolve().parents[3] / settings.PROFIT_MODEL_PATH
        )
        self.profit_model_roundtrip_path = (
            Path(__file__).resolve().parents[3] / settings.ROUNDTRIP_PROFIT_MODEL_PATH
        )

        self.conversion_model = self._load_model(self.conversion_model_path)
        self.profit_model_oneway = self._load_model(self.profit_model_oneway_path)
        self.profit_model_roundtrip = self._load_model(self.profit_model_roundtrip_path)

    def _load_model(self, path: Path) -> Any:
        if ML_AVAILABLE and path.exists():
            try:
                return joblib.load(path)
            except Exception as e:
                logger.error(f"Failed to load AI model at {path}: {e}")
        return None

    def predict_conversion_probability(self, features: Dict[str, Any], fallback_prob: float) -> float:
        """Predicts the exact booking success probability using the Random Forest model."""
        if not self.conversion_model or not ML_AVAILABLE:
            return fallback_prob
            
        try:
            # Features: price, duration_minutes, stops, is_refundable, month, day_of_week, advance_purchase_days
            feature_array = np.array([[
                features.get("price", 0.0),
                features.get("duration_minutes", 0),
                features.get("stops", 0),
                1 if features.get("is_refundable") else 0,
                features.get("month", 1),
                features.get("day_of_week", 0),
                features.get("advance_purchase_days", 30)
            ]])
            # Probability of class 1 (success)
            prob = self.conversion_model.predict_proba(feature_array)[0][1]
            return float(prob)
        except Exception as e:
            logger.warning(f"AI Conversion prediction failed: {e}")
            return fallback_prob

    def predict_expected_profit(
        self, features: Dict[str, Any], trip_type: str = "oneway", fallback_profit: float = 0.0
    ) -> float:
        """Predicts expected agent profit using the trained GradientBoosting model."""
        model = self.profit_model_oneway if trip_type.lower() == "oneway" else self.profit_model_roundtrip
        if not model or not ML_AVAILABLE:
            return fallback_profit

        try:
            feature_array = np.array([[
                features.get("total_amount", 0.0),
                features.get("passenger_count", 1),
                features.get("markup_amount", 0.0),
                features.get("supplier_commission", 0.0),
                features.get("agent_markup", 0.0),
                features.get("duration_minutes", 0),
                features.get("stops", 0),
                features.get("total_base", 0.0),
                features.get("total_tax", 0.0),
                features.get("supplier_avg_profit", 0.0),
                features.get("airline_avg_profit", 0.0)
            ]])
            predicted = model.predict(feature_array)[0]
            return float(max(predicted, 0.0))
        except Exception as e:
            logger.warning(f"AI Profit prediction failed: {e}")
            return fallback_profit
