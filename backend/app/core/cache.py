import redis
import json
from app.core.config import settings

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
PREFIX = "marketly"


class CacheManager:
    @staticmethod
    def make_key(namespace: str, identifier: str) -> str:
        return f"{PREFIX}:{namespace}:{identifier}"

    @staticmethod
    def get(key: str):
        value = r.get(key)

        if value:
            return value
        else:
            return None

    def set(key: str, value: str, ttl: int = 3600):
        r.set(key, value, ex=ttl)
        
    @staticmethod
    def delete(pattern: str):
        for key in r.scan_iter(f"{PREFIX}:{pattern}*"):
            r.delete(key)
