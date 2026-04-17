
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.user import User
from app.models.game_session import GameSession
from app.models.website_visit import WebsiteVisit
from app.models.ai_usage import AIUsage

router = APIRouter()

@router.get("/stats/overview")
def get_stats_overview(db: Session = Depends(get_db)):
    total_players = db.query(User).count()
    website_visitors = db.query(WebsiteVisit).count()
    ai_usage = db.query(AIUsage).count()
    return {
        "totalPlayers": total_players,
        "websiteVisitors": website_visitors,
        "aiUsage": ai_usage
    }

@router.get("/stats/engagement")
def get_stats_engagement(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    day_names = [d.strftime("%a") for d in days]
    data = []
    for d, name in zip(days, day_names):
        # Unique players
        players = db.query(GameSession.user_id).filter(
            GameSession.status == "finished",
            GameSession.ended_at >= datetime.combine(d, datetime.min.time()),
            GameSession.ended_at < datetime.combine(d + timedelta(days=1), datetime.min.time())
        ).distinct().count()
        # Unique visitors
        visitors = db.query(WebsiteVisit.ip).filter(
            WebsiteVisit.visited_at >= datetime.combine(d, datetime.min.time()),
            WebsiteVisit.visited_at < datetime.combine(d + timedelta(days=1), datetime.min.time())
        ).distinct().count()
        # AI usage
        ai = db.query(AIUsage).filter(
            AIUsage.timestamp >= datetime.combine(d, datetime.min.time()),
            AIUsage.timestamp < datetime.combine(d + timedelta(days=1), datetime.min.time())
        ).count()
        data.append({
            "name": name,
            "players": players,
            "visitors": visitors,
            "ai": ai
        })
    return data

# Endpoint to log a website visit
@router.post("/log-visit")
def log_website_visit(request: dict, db: Session = Depends(get_db)):
    ip = request.get("ip")
    user_agent = request.get("user_agent")
    visit = WebsiteVisit(ip=ip, user_agent=user_agent)
    db.add(visit)
    db.commit()
    return {"status": "ok"}

# Endpoint to log AI usage
@router.post("/log-ai-usage")
def log_ai_usage(request: dict, db: Session = Depends(get_db)):
    user_id = request.get("user_id")
    action = request.get("action")
    usage = AIUsage(user_id=user_id, action=action)
    db.add(usage)
    db.commit()
    return {"status": "ok"}
