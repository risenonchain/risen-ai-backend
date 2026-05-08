import os
import time
from typing import Tuple, Optional
import redis
from core.config import settings

# In-memory fallback if Redis is not configured
_usage_cache = {}

def get_redis_client():
    if settings.REDIS_URL and settings.REDIS_TOKEN:
        # Assuming Upstash format or standard redis://
        try:
            return redis.from_url(settings.REDIS_URL, decode_responses=True)
        except:
            return None
    return None

def check_usage(user_id: str, is_premium: bool, action_type: str = "prompt") -> Tuple[bool, Optional[int]]:
    """
    Returns (allowed, remaining)
    action_type: "prompt" or "image"
    """
    if is_premium:
        return True, None # Unlimited

    limit = 10 if action_type == "prompt" else 1
    key = f"usage:{user_id}:{action_type}"

    client = get_redis_client()
    if client:
        try:
            count = int(client.get(key) or 0)
            if count >= limit:
                return False, 0

            # Increment and set expiry to end of day or 24h
            new_count = client.incr(key)
            if new_count == 1:
                client.expire(key, 86400) # 24 hours

            return True, limit - new_count
        except Exception as e:
            print(f"🔥 Redis usage error: {e}")
            # Fallback to in-memory on redis failure
            pass

    # In-memory fallback
    now = time.time()
    user_data = _usage_cache.get(user_id, {"prompts": 0, "images": 0, "reset": now + 86400})

    if now > user_data["reset"]:
        user_data = {"prompts": 0, "images": 0, "reset": now + 86400}

    field = "prompts" if action_type == "prompt" else "images"
    if user_data[field] >= limit:
        return False, 0

    user_data[field] += 1
    _usage_cache[user_id] = user_data
    return True, limit - user_data[field]
