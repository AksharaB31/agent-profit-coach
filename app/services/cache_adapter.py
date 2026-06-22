import json
from app.infra.redis_provider import RedisProvider


class CacheAdapter:

    def __init__(self):
        self.redis = RedisProvider()

    def get(self, key):

        data = self.redis.get(key)

        if not data:
            return None

        return json.loads(data)

    def set(
        self,
        key,
        value,
        ttl=300
    ):

        self.redis.set(
            key,
            json.dumps(value),
            ttl
        )

    def delete(self, key):

        self.redis.delete(key)