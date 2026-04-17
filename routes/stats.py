from fastapi import APIRouter
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stats/overview")
def get_stats_overview():
    # TODO: Replace with real DB queries or service calls
    return {
        "totalPlayers": 1245,
        "websiteVisitors": 8921,
        "aiUsage": 312
    }

@router.get("/stats/engagement")
def get_stats_engagement():
    # Dummy time-series data for chart (replace with real analytics)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    data = []
    for i, day in enumerate(days):
        data.append({
            "name": day,
            "players": 200 + i * 50,
            "visitors": 1200 + i * 100,
            "ai": 40 + i * 10
        })
    return data
