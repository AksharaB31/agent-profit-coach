from pydantic import BaseModel


class Supplier(BaseModel):
    supplier_code: str
    supplier_name: str
    commission_percentage: float
    incentive_bonus: float
    reliability_score: float
    success_rate: float
    avg_ticketing_time: float
    cancellation_rate: float

    def estimated_margin(self, base_fare: float):

        commission = (
            base_fare *
            self.commission_percentage
        ) / 100

        total_margin = (
            commission +
            self.incentive_bonus
        )

        return round(total_margin, 2)

    def operational_score(self):

        score = (
            self.reliability_score * 0.5 +
            self.success_rate * 0.3 -
            self.cancellation_rate * 0.2
        )

        return round(score, 2)