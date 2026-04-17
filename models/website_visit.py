from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.db.database import Base

class WebsiteVisit(Base):
    __tablename__ = "website_visits"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(64), nullable=True)
    user_agent = Column(String, nullable=True)
    visited_at = Column(DateTime, default=datetime.utcnow, nullable=False)
