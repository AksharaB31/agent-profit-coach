import redis
from app.infra.settings import infra_settings


class RedisProvider:

    def __init__(self):
        self.client = redis.Redis(
            host=infra_settings.REDIS_HOST,
            port=infra_settings.REDIS_PORT,
            decode_responses=True
        )

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value, ttl=300):
        self.client.setex(key, ttl, value)

    def delete(self, key):
        self.client.delete(key)