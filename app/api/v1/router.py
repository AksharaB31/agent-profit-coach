from fastapi import APIRouter
from app.api.v1.endpoints.agent_profit_coach import router as agent_router

router = APIRouter(prefix="/v1")
router.include_router(agent_router)