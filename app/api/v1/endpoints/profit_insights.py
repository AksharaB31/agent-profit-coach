from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.schemas import ProfitCoachRequest
from app.services.profit_coach.recommendation_engine.profit_coach_engine import ProfitCoachEngine
from app.infra.mysql.database import get_db

router = APIRouter()

@router.post("/profit-insights")
def profit_insights(payload: ProfitCoachRequest, db: Session = Depends(get_db)):
    service = ProfitCoachEngine(db)

    result = service.execute(payload)

    return {
        "expected_profit": result["expected_profit"],
        "conversion_probability": result["conversion_probability"],
        "reliability_score": result["reliability_score"],
        "profit_score": result["profit_score"]
    }