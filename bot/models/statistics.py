from sqlalchemy import Column, Integer, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime

from bot.models.database import Base


class Statistics(Base):
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    
    # Подсчет подписчиков (можно вычислять, но для производительности храним здесь)
    subscribers_count = Column(Integer, default=0)
    
    # Количество публикаций
    posts_count = Column(Integer, default=0)
    
    # Отправлено уведомлений
    notifications_sent = Column(BigInteger, default=0)
    
    # Просмотров публикаций (суммарно)
    total_views = Column(BigInteger, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    school = relationship('School', back_populates='statistics')

    def __repr__(self):
        return f"<Statistics(school_id={self.school_id}, subscribers={self.subscribers_count})>"
