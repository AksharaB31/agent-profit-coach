from fastapi import APIRouter

from app.api.v1.endpoints.agent_profit_coach import router as agent_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.version import router as version_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(agent_router, tags=["Agent Profit Coach"])
v1_router.include_router(health_router, tags=["Health"])
v1_router.include_router(version_router, tags=["Version"])

api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)
