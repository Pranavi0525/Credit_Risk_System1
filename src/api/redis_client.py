import redis

redis_client = redis.Redis(
    host="redis",   # docker service name
    port=6379,
    decode_responses=True
)
