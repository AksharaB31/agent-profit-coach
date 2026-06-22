import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sqlalchemy import func, case, create_engine
from sqlalchemy.orm import sessionmaker
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score
from datetime import datetime

from app.infra.mysql.models import (
    Booking, BookingFlight, BookingSegment, BookingProcess, BookingAdjustedFare
)
from app.core.config import settings
from app.domain.ai_engine.feature_validation_service import FeatureValidationService

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "conversion_model.pkl"


def build_training_dataset(session) -> pd.DataFrame:
    rows = session.query(
        Booking.id.label("booking_id"),
        Booking.total_amount,
        Booking.refundable,
        Booking.booking_date,
        Booking.passenger_count,
        BookingProcess.state,
        BookingSegment.duration_minutes,
        BookingSegment.departure_time,
        BookingSegment.arrival_airport,
        BookingSegment.departure_airport,
        func.count(BookingSegment.id).over(partition_by=BookingFlight.id).label("segment_count")
    ).join(
        BookingFlight, Booking.id == BookingFlight.booking_id
    ).join(
        BookingSegment, BookingFlight.id == BookingSegment.booking_flight_id
    ).join(
        BookingProcess,
        BookingProcess.provider_code == Booking.provider,
        isouter=True
    ).filter(
        Booking.total_amount.isnot(None),
        Booking.booking_date.isnot(None)
    ).all()

    records = []
    for r in rows:
        if r.departure_time is None:
            continue
        success = 1 if r.state and str(r.state).upper() in [
            "SUCCESS", "COMPLETED", "TICKETED", "CONFIRMED"
        ] else 0
        month = r.departure_time.month
        day_of_week = r.departure_time.weekday()
        advance_days = max(0, (r.departure_time - (r.booking_date or datetime.now())).days)
        records.append({
            "price": float(r.total_amount or 0),
            "duration_minutes": int(r.duration_minutes or 0),
            "stops": max(0, int((r.segment_count or 1)) - 1),
            "is_refundable": 1 if r.refundable else 0,
            "month": month,
            "day_of_week": day_of_week,
            "advance_purchase_days": advance_days,
            "is_successful": success
        })

    df = pd.DataFrame(records)
    logger.info(f"Built training dataset: {len(df)} rows, {df['is_successful'].sum()} successes")
    return df


def train_conversion_model(session=None):
    from app.infra.mysql.database import SessionLocal

    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        df = build_training_dataset(session)

        if len(df) < 50:
            logger.warning(f"Too few samples ({len(df)}) to train a meaningful model.")
            return "Insufficient training data"

        feature_cols = [
            "price", "duration_minutes", "stops", "is_refundable",
            "month", "day_of_week", "advance_purchase_days"
        ]
        FeatureValidationService.validate_features(feature_cols)
        X = df[feature_cols]
        y = df["is_successful"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_leaf=5,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        logger.info(
            "Conversion Model Metrics | Accuracy=%.4f | AUC=%.4f | Precision=%.4f | Recall=%.4f | F1=%.4f",
            accuracy_score(y_test, y_pred),
            roc_auc_score(y_test, y_proba),
            precision_score(y_test, y_pred),
            recall_score(y_test, y_pred),
            f1_score(y_test, y_pred)
        )

        joblib.dump(model, MODEL_PATH)
        logger.info(f"Conversion model saved to {MODEL_PATH}")
        return f"Model trained and saved. AUC: {roc_auc_score(y_test, y_proba):.4f}"

    finally:
        if close_session:
            session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(train_conversion_model())
