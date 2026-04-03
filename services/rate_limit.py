import requests
import os

BASE_URL = os.getenv("REDIS_URL")
TOKEN = os.getenv("REDIS_TOKEN")


def rate_limit_check(user_id: str, limit: int = 20):
    key = f"rate_limit:{user_id}"

    res = requests.get(
        f"{BASE_URL}/get/{key}",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    data = res.json()
    count = int(data.get("result") or 0)

    if count >= limit:
        return False

    requests.post(
        f"{BASE_URL}/set/{key}",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "value": count + 1,
            "ex": 60
        }
    )

    return True