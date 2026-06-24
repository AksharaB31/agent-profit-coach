import redis
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisProvider:

    def __init__(self):
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            self.client = None

    def get(self, key):
        if not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error for {key}: {e}")
            return None

    def set(self, key, value, ttl=300):
        if not self.client:
            return
        try:
            self.client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Redis set error for {key}: {e}")

    def delete(self, key):
        if not self.client:
            return
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error for {key}: {e}")

    def close(self):
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logger.error(f"Redis close error: {e}")