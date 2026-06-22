from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/version")
def version():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }