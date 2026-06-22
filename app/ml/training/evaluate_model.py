import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score

from app.infra.mysql.database import SessionLocal
from app.ml.training.train_conversion_model import build_training_dataset, MODEL_PATH as CONV_MODEL_PATH
from app.ml.training.train_profit_model import build_profit_dataset, ONEWAY_MODEL_PATH, ROUNDTRIP_MODEL_PATH

logger = logging.getLogger(__name__)


def evaluate_conversion_model():
    model_path = Path(CONV_MODEL_PATH)
    if not model_path.exists():
        return {"error": "Conversion model not found"}

    model = joblib.load(model_path)
    session = SessionLocal()
    try:
        df = build_training_dataset(session)
        if df.empty:
            return {"error": "No evaluation data"}

        feature_cols = [
            "price", "duration_minutes", "stops", "is_refundable",
            "month", "day_of_week", "advance_purchase_days"
        ]
        X = df[feature_cols]
        y = df["is_successful"]

        y_pred = model.predict(X)
        y_proba = model.predict_proba(X)[:, 1]

        return {
            "accuracy": round(accuracy_score(y, y_pred), 4),
            "auc": round(roc_auc_score(y, y_proba), 4),
            "precision": round(precision_score(y, y_pred), 4),
            "recall": round(recall_score(y, y_pred), 4),
            "f1": round(f1_score(y, y_pred), 4),
            "samples": len(df),
            "success_rate": float(y.mean())
        }
    finally:
        session.close()


def evaluate_profit_models():
    results = {}
    for label, path in [("OneWay", ONEWAY_MODEL_PATH), ("RoundTrip", ROUNDTRIP_MODEL_PATH)]:
        model_path = Path(path)
        if not model_path.exists():
            results[label] = {"error": "Model not found"}
            continue

        model = joblib.load(model_path)
        session = SessionLocal()
        try:
            df = build_profit_dataset(session)
            if df.empty:
                results[label] = {"error": "No evaluation data"}
                continue

            for col in [
                "total_amount", "passenger_count", "markup_amount", "supplier_commission",
                "agent_markup", "duration_minutes", "stops", "total_base", "total_tax",
                "supplier_avg_profit", "airline_avg_profit"
            ]:
                df[col] = df[col].fillna(0)

            df = df[df["agent_profit"].notna() & (df["agent_profit"] >= 0)]
            if df.empty:
                results[label] = {"error": "No valid profit rows"}
                continue

            feature_cols = [
                "total_amount", "passenger_count", "markup_amount", "supplier_commission",
                "agent_markup", "duration_minutes", "stops", "total_base", "total_tax",
                "supplier_avg_profit", "airline_avg_profit"
            ]
            X = df[feature_cols]
            y = df["agent_profit"]
            y_pred = model.predict(X)

            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            results[label] = {
                "mae": round(mean_absolute_error(y, y_pred), 2),
                "rmse": round(mean_squared_error(y, y_pred) ** 0.5, 2),
                "r2": round(r2_score(y, y_pred), 4),
                "samples": len(df),
                "avg_profit": float(y.mean())
            }
        finally:
            session.close()

    return results


def evaluate_all():
    return {
        "conversion_model": evaluate_conversion_model(),
        "profit_models": evaluate_profit_models()
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import json
    print(json.dumps(evaluate_all(), indent=2))
