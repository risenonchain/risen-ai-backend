import requests
import json
from core.config import settings

BASE_URL = settings.REDIS_URL
HEADERS = {
    "Authorization": f"Bearer {settings.REDIS_TOKEN}"
}

MAX_HISTORY = 10


def get_key(session_id: str):
    return f"risen:memory:{session_id}"


def get_history(session_id: str):
    if not BASE_URL or not settings.REDIS_TOKEN:
        return []

    try:
        key = get_key(session_id)
        res = requests.get(f"{BASE_URL}/get/{key}", headers=HEADERS, timeout=5)
        if not res.ok:
            return []

        data = res.json()
        if not data.get("result"):
            return []

        return json.loads(data["result"])
    except Exception as e:
        print(f"🔥 Memory Retrieval Error: {e}")
        return []


def add_message(session_id: str, role: str, content: str):
    if not BASE_URL or not settings.REDIS_TOKEN:
        return

    try:
        key = get_key(session_id)
        history = get_history(session_id)

        history.append({
            "role": role,
            "content": content
        })

        history = history[-MAX_HISTORY:]

        requests.post(
            f"{BASE_URL}/set/{key}",
            headers=HEADERS,
            json={
                "value": json.dumps(history),
                "ex": 3600
            },
            timeout=5
        )
    except Exception as e:
        print(f"🔥 Memory Store Error: {e}")
