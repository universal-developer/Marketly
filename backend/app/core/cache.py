import redis
import json
from app.core.config import settings

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
PREFIX = "marketly"

TTL_PRESETS = {
    "macro": 86400 * 7,     # 7 days
    "stocks": 86400,        # 1 day
    "news": 3600 * 3,       # 3 hours
    "analyst": 86400 * 2,   # 2 days
}


class CacheManager:
    @staticmethod
    def make_key(namespace: str, identifier: str) -> str:
        return f"{PREFIX}:{namespace}:{identifier}"

    @staticmethod
    def get(key: str):
        value = r.get(key)
        return value if value else None

    @staticmethod
    def set(key: str, value: str, ttl: int | None = None):
        # Determine namespace from key
        namespace = key.split(":")[1] if ":" in key else None
        ttl = ttl or TTL_PRESETS.get(namespace, 3600)  # default 1 h fallback
        r.set(key, value, ex=ttl)

    @staticmethod
    def delete(pattern: str):
        for key in r.scan_iter(f"{PREFIX}:{pattern}*"):
            r.delete(key)
