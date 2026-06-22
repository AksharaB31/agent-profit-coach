from fastapi import APIRouter, Depends, HTTPException  
from sqlalchemy.orm import Session
from app.api.schemas import ProfitCoachRequest, EnterpriseProfitCoachResponse
from app.services.agent_profit_coach.response_builder.enterprise_response_builder import EnterpriseResponseBuilder
from app.infra.mysql.database import get_db
                            
router = APIRouter()         

@router.post("/agent-profit-coach", response_model=EnterpriseProfitCoachResponse)
def agent_profit_coach(payload: ProfitCoachRequest, db: Session = Depends(get_db)):  
    builder = EnterpriseResponseBuilder(db)   
    return builder.build(payload) 






