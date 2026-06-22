from pydantic import BaseModel
from typing import List


class FlightFeature(BaseModel):
    supplier: str
    airline: str
    price: float
    duration: int
    baggage: int
    refundability: float
    reliability: float
    meals: float
    timing_score: float
    journey_convenience: float


class PredictionResult(BaseModel):
    supplier: str
    expected_profit: float
    conversion_probability: float
    ranking_score: float


class RankedFlight(BaseModel):
    supplier: str
    flight_number: str
    final_score: float
    reasons: List[str]