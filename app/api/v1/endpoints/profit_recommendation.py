from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.schemas import ProfitCoachRequest
from app.services.profit_coach.recommendation_engine.profit_coach_engine import ProfitCoachEngine
from app.infra.mysql.database import get_db

router = APIRouter()

@router.post("/profit-recommendation")
def profit_recommendation(payload: ProfitCoachRequest, db: Session = Depends(get_db)):
    service = ProfitCoachEngine(db)

    result = service.execute(payload)

    return {
        "recommended_flight": result["recommended_flight"],
        "recommended_supplier": result["recommended_supplier"],
        "reasons": result["reasons"]
    }  