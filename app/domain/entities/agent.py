from pydantic import BaseModel
from typing import Optional


class Agent(BaseModel):
    agent_id: int
    agency_name: str
    preferred_supplier: Optional[str] = None
    markup_percentage: float = 0.0
    total_bookings: int = 0
    total_profit: float = 0.0
    tier: str = "standard"

    def average_profit_per_booking(self):

        if self.total_bookings == 0:
            return 0

        return round(
            self.total_profit / self.total_bookings,
            2
        )