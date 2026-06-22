from pydantic import BaseModel
from datetime import date


class Route(BaseModel):
    origin: str
    destination: str
    departure_date: date
    return_date: date | None = None
    trip_type: str = "oneway"

    def route_key(self):

        return f"{self.origin}-{self.destination}"

    def is_domestic(self):

        return self.origin[:2] == self.destination[:2]