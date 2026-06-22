import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sqlalchemy import func
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.infra.mysql.models import Booking, BookingFlight, BookingSegment, BookingAdjustedFare
from app.core.config import settings
from app.domain.ai_engine.feature_validation_service import FeatureValidationService

logger = logging.getLogger(__name__)

ONEWAY_MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "ml_profit_model_oneway_v1.pkl"
ROUNDTRIP_MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "ml_profit_model_roundtrip_v1.pkl"


def build_profit_dataset(session) -> pd.DataFrame:
    rows = session.query(
        Booking.provider.label("supplier_code"),
        BookingFlight.validating_airline.label("airline_code"),
        BookingSegment.departure_airport.label("origin"),
        BookingSegment.arrival_airport.label("destination"),
        Booking.total_amount,
        Booking.passenger_count,
        BookingAdjustedFare.agent_profit,
        BookingAdjustedFare.markup_amount,
        BookingAdjustedFare.supplier_commission,
        BookingAdjustedFare.agent_markup,
        BookingSegment.duration_minutes,
        func.count(BookingSegment.id).over(partition_by=BookingFlight.id).label("segment_count"),
        BookingAdjustedFare.total_base,
        BookingAdjustedFare.total_tax,
        func.count(func.distinct(BookingFlight.id)).over(partition_by=Booking.id).label("flight_count")
    ).join(
        BookingFlight, Booking.id == BookingFlight.booking_id
    ).join(
        BookingSegment, BookingFlight.id == BookingSegment.booking_flight_id
    ).join(
        BookingAdjustedFare, Booking.id == BookingAdjustedFare.booking_id
    ).filter(
        BookingAdjustedFare.agent_profit.isnot(None),
        Booking.total_amount.isnot(None),
        Booking.total_amount > 0
    ).all()

    records = []
    for r in rows:
        records.append({
            "supplier_code": str(r.supplier_code or ""),
            "airline_code": str(r.airline_code or ""),
            "origin": str(r.origin or ""),
            "destination": str(r.destination or ""),
            "total_amount": float(r.total_amount or 0),
            "passenger_count": int(r.passenger_count or 1),
            "agent_profit": float(r.agent_profit or 0),
            "markup_amount": float(r.markup_amount or 0),
            "supplier_commission": float(r.supplier_commission or 0),
            "agent_markup": float(r.agent_markup or 0),
            "duration_minutes": int(r.duration_minutes or 0),
            "stops": max(0, int((r.segment_count or 1)) - 1),
            "total_base": float(r.total_base or 0),
            "total_tax": float(r.total_tax or 0),
            "booking_flight_count": int(r.flight_count or 1)
        })

    df = pd.DataFrame(records)

    supplier_mean_profit = df.groupby("supplier_code")["agent_profit"].transform("mean")
    df["supplier_avg_profit"] = supplier_mean_profit.fillna(0)

    airline_mean_profit = df.groupby("airline_code")["agent_profit"].transform("mean")
    df["airline_avg_profit"] = airline_mean_profit.fillna(0)

    logger.info(f"Built profit dataset: {len(df)} rows")
    return df


def _train_model(df: pd.DataFrame, model_path: Path, label: str) -> str:
    feature_cols = [
        "total_amount", "passenger_count", "markup_amount", "supplier_commission",
        "agent_markup", "duration_minutes", "stops", "total_base", "total_tax",
        "supplier_avg_profit", "airline_avg_profit"
    ]

    FeatureValidationService.validate_features(feature_cols)

    df = df[df["agent_profit"].notna() & (df["agent_profit"] >= 0)].copy()

    for col in feature_cols:
        df[col] = df[col].fillna(0)

    X = df[feature_cols]
    y = df["agent_profit"]

    if len(df) < 30:
        logger.warning(f"Too few samples ({len(df)}) to train {label} model.")
        return f"Insufficient data for {label}"

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = GradientBoostingRegressor(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        min_samples_leaf=5,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2 = r2_score(y_test, y_pred)

    logger.info(
        f"{label} Model Metrics | MAE={mae:.2f} | RMSE={rmse:.2f} | R2={r2:.4f}"
    )

    joblib.dump(model, model_path)
    logger.info(f"{label} model saved to {model_path}")
    return f"{label} trained. MAE: {mae:.2f}, R2: {r2:.4f}"


def train_profit_models(session=None):
    from app.infra.mysql.database import SessionLocal

    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        df = build_profit_dataset(session)

        if df.empty:
            return "No profit data available for training."

        oneway_df = df[df["booking_flight_count"] == 1].copy()
        roundtrip_df = df[df["booking_flight_count"] > 1].copy()

        result_oneway = _train_model(oneway_df, ONEWAY_MODEL_PATH, "OneWay")
        result_roundtrip = _train_model(roundtrip_df, ROUNDTRIP_MODEL_PATH, "RoundTrip")

        return f"{result_oneway} | {result_roundtrip}"

    finally:
        if close_session:
            session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(train_profit_models())
