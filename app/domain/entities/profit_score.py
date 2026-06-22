from pydantic import BaseModel
from typing import List


class ProfitScore(BaseModel):
    supplier: str
    expected_profit: float
    conversion_probability: float
    reliability_score: float
    risk_score: float
    final_score: float
    reasons: List[str]

    @staticmethod
    def calculate(
        expected_profit,
        conversion_probability,
        reliability_score,
        risk_score
    ):

        normalized_profit = expected_profit / 2000

        score = (
            normalized_profit * 0.40 +
            conversion_probability * 0.30 +
            reliability_score * 0.20 -
            risk_score * 0.10
        )

        return round(score, 2)