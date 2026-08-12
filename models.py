from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from database import Base
import datetime

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)

    category_id = Column(Integer)
    channel_id = Column(Integer, nullable=True)

    title = Column(String(255))
    description = Column(Text)

    source = Column(String(255), nullable=True)

    video_link = Column(String(255), nullable=True)
    video_link_type = Column(String(50), nullable=True)

    images = Column(Text)  # JSON string

    is_public = Column(Boolean, default=False)
    notify = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)