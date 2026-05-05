import requests
from fastapi import Header, HTTPException
from core.config import settings

def get_user_status(authorization: str = Header(None)):
    if not authorization:
        # Allow anonymous for now but with very low limits?
        # Or force login?
        # User said "uses rush login", so likely required.
        return {"id": "anonymous", "is_premium": False}

    try:
        # Pass the token to Rush backend to verify
        # Token is usually "Bearer <token>"
        res = requests.get(
            f"{settings.RUSH_API_URL}/auth/me",
            headers={"Authorization": authorization},
            timeout=5
        )
        if res.ok:
            user_data = res.json()
            return {
                "id": str(user_data.get("id")),
                "is_premium": user_data.get("is_premium", False)
            }
        else:
            return {"id": "anonymous", "is_premium": False}
    except Exception as e:
        print(f"🔥 Auth verification failed: {e}")
        return {"id": "anonymous", "is_premium": False}
