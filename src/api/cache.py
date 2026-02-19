import redis
import json
import hashlib

# Connect to Redis container
redis_client = redis.Redis(
    host="redis",   # Docker service name
    port=6379,
    decode_responses=True
)

# Generate unique cache key
def generate_key(data: dict):
    return hashlib.md5(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()

# Get cached result
def get_cache(key: str):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

# Save result to Redis
def set_cache(key: str, value: dict, ttl=3600):
    redis_client.setex(key, ttl, json.dumps(value))
