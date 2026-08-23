from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from bot.models.database import Base


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    text = Column(Text, nullable=True)
    media = Column(JSON, nullable=True)  # Список медиа: [{"type": "photo", "file_id": "..."}, ...]
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views = Column(Integer, default=0)

    school = relationship('School', back_populates='posts')

    def __repr__(self):
        return f"<Post(id={self.id}, school_id={self.school_id}, created_at='{self.created_at}')>"
