from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class MissedProfitRequest(BaseModel):
    selected_profit: float
    available_profits: List[float]

@router.post("/missed-profit")
def missed_profit(payload: MissedProfitRequest):
    if not payload.available_profits:
        return {"missed_profit": 0.0, "currency": "PLN", "message": "No alternatives available"}
        
    optimal_profit = max(payload.available_profits)
    missed = max(0.0, optimal_profit - payload.selected_profit)
    
    if missed > 0:
        return {
            "missed_profit": round(missed, 2),
            "currency": "PLN",
            "message": f"Higher margin suppliers were available. You missed out on {round(missed, 2)} PLN."
        }
        
    return {
        "missed_profit": 0.0,
        "currency": "PLN",
        "message": "You selected the optimal profit margin."
    }