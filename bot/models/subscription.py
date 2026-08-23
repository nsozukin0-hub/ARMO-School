from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from bot.models.database import Base


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='subscriptions')
    school = relationship('School', back_populates='subscriptions')

    __table_args__ = (
        UniqueConstraint('user_id', 'school_id', name='unique_user_school'),
    )

    def __repr__(self):
        return f"<Subscription(user_id={self.user_id}, school_id={self.school_id})>"
