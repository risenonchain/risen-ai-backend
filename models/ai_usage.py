from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.db.database import Base

class AIUsage(Base):
    __tablename__ = "ai_usage"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(128), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
