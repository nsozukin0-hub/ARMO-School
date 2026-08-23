from sqlalchemy.orm import Session
from typing import Dict, Any, List

from bot.models.statistics import Statistics
from bot.models.subscription import Subscription
from bot.models.post import Post
from bot.models.user import User


class StatisticsService:
    """Сервис для сбора и предоставления статистики"""

    def __init__(self, db: Session):
        self.db = db

    def get_school_stats(self, school_id: int) -> Dict[str, Any]:
        """Получить статистику по школе"""
        stats = self.db.query(Statistics).filter(Statistics.school_id == school_id).first()
        
        if not stats:
            return {
                'school_id': school_id,
                'subscribers_count': 0,
                'posts_count': 0,
                'notifications_sent': 0,
                'total_views': 0
            }
        
        # Актуализируем количество подписчиков
        subscribers_count = self.db.query(Subscription).filter(
            Subscription.school_id == school_id
        ).count()
        stats.subscribers_count = subscribers_count
        
        # Актуализируем количество постов
        posts_count = self.db.query(Post).filter(Post.school_id == school_id).count()
        stats.posts_count = posts_count
        
        self.db.commit()
        
        return {
            'school_id': school_id,
            'subscribers_count': stats.subscribers_count,
            'posts_count': stats.posts_count,
            'notifications_sent': stats.notifications_sent or 0,
            'total_views': stats.total_views or 0
        }

    def get_overall_stats(self) -> Dict[str, Any]:
        """Получить общую статистику по всем школам"""
        all_stats = self.db.query(Statistics).all()
        
        total_subscribers = sum(s.subscribers_count for s in all_stats)
        total_posts = sum(s.posts_count for s in all_stats)
        total_notifications = sum(s.notifications_sent or 0 for s in all_stats)
        total_views = sum(s.total_views or 0 for s in all_stats)
        
        schools_count = len(all_stats)
        users_count = self.db.query(User).count()
        
        return {
            'schools_count': schools_count,
            'users_count': users_count,
            'total_subscribers': total_subscribers,
            'total_posts': total_posts,
            'total_notifications': total_notifications,
            'total_views': total_views
        }

    def increment_notifications_sent(self, school_id: int, count: int = 1) -> None:
        """Увеличить счетчик отправленных уведомлений"""
        stats = self.db.query(Statistics).filter(Statistics.school_id == school_id).first()
        if stats:
            stats.notifications_sent = (stats.notifications_sent or 0) + count
            self.db.commit()
