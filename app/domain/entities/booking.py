from pydantic import BaseModel
from datetime import datetime


class Booking(BaseModel):
    booking_id: str
    agent_id: int
    supplier_code: str
    airline: str
    origin: str
    destination: str
    fare: float
    markup: float
    commission: float
    booking_status: str
    created_at: datetime

    def calculate_profit(self):

        return round(
            self.markup + self.commission,
            2
        )