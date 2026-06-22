from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.schemas import ProfitCoachRequest
from app.services.profit_coach.recommendation_engine.profit_coach_engine import ProfitCoachEngine
from app.infra.mysql.database import get_db

router = APIRouter()

@router.post("/route-profit")
def route_profit(payload: ProfitCoachRequest, db: Session = Depends(get_db)):
    service = ProfitCoachEngine(db)

    result = service.execute(payload)

    return {
        "route": f"{payload.origin}-{payload.destination}",
        "recommended_supplier": result["recommended_supplier"],
        "expected_profit": result["expected_profit"],
        "profit_score": result["profit_score"]
    }