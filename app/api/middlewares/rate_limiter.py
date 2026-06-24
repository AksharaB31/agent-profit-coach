import time
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.infra.redis_provider import RedisProvider
import logging

logger = logging.getLogger(__name__)
redis_provider = RedisProvider()

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        api_key = request.headers.get("X-API-Key", "anonymous")
        
        # Use API key for rate limiting if available, else IP
        key = f"rate_limit:{api_key if api_key != 'anonymous' else client_ip}"
        
        current_time = int(time.time())
        window_key = f"{key}:{current_time // self.window}"
        
        try:
            r = redis_provider.client
            requests = r.incr(window_key)
            if requests == 1:
                r.expire(window_key, self.window + 1)
                
            if requests > self.limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too Many Requests"}
                )
        except Exception as e:
            # If Redis fails, fail open so we don't block legitimate traffic
            logger.error(f"Rate Limiter Redis Error: {e}")
            pass
            
        response = await call_next(request)
        return response
