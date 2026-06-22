from fastapi import APIRouter

router = APIRouter()

@router.get("/missed-profit")
def missed_profit():
    return {
        "missed_profit": 12500,
        "currency": "INR",
        "message": "Higher margin suppliers were available"
    }