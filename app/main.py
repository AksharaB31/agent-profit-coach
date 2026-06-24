from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings
from app.api.middlewares.rate_limiter import RateLimiterMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import logging
from pythonjsonlogger import jsonlogger

from contextlib import asynccontextmanager

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    from app.infra.mysql.database import engine
    logger.info("Disposing MySQL engine...")
    engine.dispose()
    
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimiterMiddleware, limit=100, window=60)

# Instrumentator().instrument(app).expose(app)  # Temporarily disabled due to FastAPI 0.138.0 incompatibility

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import uuid
    request_id = str(uuid.uuid4())
    logger.error(f"Request {request_id} failed: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "request_id": request_id}
    )

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Agent Profit Coach API Running"
    }
