from pydantic import BaseModel
from typing import List


class FlightSegment(BaseModel):
    origin: str
    destination: str
    airline: str
    departure_time: str
    arrival_time: str
    duration_minutes: int


class Itinerary(BaseModel):
    trip_type: str
    segments: List[FlightSegment]
    total_duration: int
    total_stops: int
    baggage_allowance: int
    refundable: bool

    def journey_convenience_score(self):

        score = 1.0

        if self.total_stops > 1:
            score -= 0.3

        if self.total_duration > 600:
            score -= 0.2

        return round(max(score, 0), 2)