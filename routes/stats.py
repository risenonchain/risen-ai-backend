
from fastapi import APIRouter, HTTPException
import httpx


router = APIRouter()

# Set this to your Rush backend base URL or deployed URL
RUSH_BACKEND_URL = "http://risen-rush-backend:8000"

@router.get("/stats/overview")
def get_stats_overview():
    try:
        resp = httpx.get(f"{RUSH_BACKEND_URL}/stats/overview", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch stats overview: {e}")

@router.get("/stats/engagement")
def get_stats_engagement():
    try:
        resp = httpx.get(f"{RUSH_BACKEND_URL}/stats/engagement", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch stats engagement: {e}")


# Endpoint to log a website visit
@router.post("/log-visit")
def log_website_visit(request: dict):
    try:
        resp = httpx.post(f"{RUSH_BACKEND_URL}/log-visit", json=request, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to log website visit: {e}")

# Endpoint to log AI usage
@router.post("/log-ai-usage")
def log_ai_usage(request: dict):
    try:
        resp = httpx.post(f"{RUSH_BACKEND_URL}/log-ai-usage", json=request, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to log AI usage: {e}")
