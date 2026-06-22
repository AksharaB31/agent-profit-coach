from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.schemas import ProfitCoachRequest
from app.services.profit_coach.recommendation_engine.profit_coach_engine import ProfitCoachEngine
from app.infra.mysql.database import get_db

router = APIRouter()

@router.post("/supplier-profit")
def supplier_profit(payload: ProfitCoachRequest, db: Session = Depends(get_db)):
    service = ProfitCoachEngine(db)

    result = service.execute(payload) 

    return {
        "recommended_supplier": result["recommended_supplier"],
        "alternative_suppliers": result["alternative_suppliers"]
    }