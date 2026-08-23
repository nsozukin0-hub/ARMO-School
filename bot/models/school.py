from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from bot.models.database import Base


class School(Base):
    __tablename__ = 'schools'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship('Post', back_populates='school', cascade='all, delete-orphan')
    subscriptions = relationship('Subscription', back_populates='school', cascade='all, delete-orphan')
    statistics = relationship('Statistics', back_populates='school', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<School(id={self.id}, name='{self.name}')>"
