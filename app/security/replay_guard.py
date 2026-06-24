from app.infra.redis_provider import RedisProvider

redis_client = RedisProvider()

def validate_nonce(nonce: str):
    # Check if nonce exists in Redis
    if redis_client.get(f"nonce:{nonce}"):
        return False

    # Store nonce in Redis with a 5-minute TTL (300 seconds)
    redis_client.set(f"nonce:{nonce}", "1", ttl=300)

    return True