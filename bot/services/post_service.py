from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from sqlalchemy import func

from bot.models.post import Post
from bot.utils.validators import validate_post_text


class PostService:
    """Сервис для работы с постами"""

    def __init__(self, db: Session):
        self.db = db

    def create_post(
        self,
        school_id: int,
        text: str = None,
        media: List[Dict[str, Any]] = None
    ) -> Optional[Post]:
        """Создать пост"""
        if text and not validate_post_text(text):
            return None
        
        # Ограничиваем количество медиа до 9
        if media and len(media) > 9:
            media = media[:9]
        
        post = Post(
            school_id=school_id,
            text=text,
            media=json.dumps(media) if media else None
        )
        
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        
        # Обновляем статистику школы
        self._update_school_posts_count(school_id)
        
        return post

    def update_post(
        self,
        post_id: int,
        text: str = None,
        media: List[Dict[str, Any]] = None
    ) -> Optional[Post]:
        """Обновить пост"""
        post = self.get_post(post_id)
        if not post:
            return None
        
        if text is not None:
            if not validate_post_text(text):
                return None
            post.text = text
        
        if media is not None:
            # Ограничиваем количество медиа до 9
            if len(media) > 9:
                media = media[:9]
            post.media = json.dumps(media) if media else None
        
        post.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(post)
        
        return post

    def delete_post(self, post_id: int) -> bool:
        """Удалить пост"""
        post = self.get_post(post_id)
        if not post:
            return False
        
        school_id = post.school_id
        self.db.delete(post)
        self.db.commit()
        
        # Обновляем статистику школы
        self._update_school_posts_count(school_id)
        
        return True

    def get_post(self, post_id: int) -> Optional[Post]:
        """Получить пост по ID"""
        return self.db.query(Post).filter(Post.id == post_id).first()

    def get_posts_by_school(self, school_id: int, limit: int = 20, offset: int = 0) -> List[Post]:
        """Получить посты школы"""
        return self.db.query(Post).filter(
            Post.school_id == school_id
        ).order_by(Post.created_at.desc()).limit(limit).offset(offset).all()

    def get_all_posts(self, limit: int = 50) -> List[Post]:
        """Получить все посты"""
        return self.db.query(Post).order_by(Post.created_at.desc()).limit(limit).all()

    def increment_views(self, post_id: int) -> None:
        """Увеличить счетчик просмотров"""
        post = self.get_post(post_id)
        if post:
            post.views = (post.views or 0) + 1
            self.db.commit()
            
            # Обновляем общую статистику просмотров школы
            self._update_school_total_views(post.school_id)

    def _update_school_posts_count(self, school_id: int) -> None:
        """Обновить количество постов в статистике школы"""
        from bot.models.statistics import Statistics
        
        stats = self.db.query(Statistics).filter(Statistics.school_id == school_id).first()
        if stats:
            posts_count = self.db.query(Post).filter(Post.school_id == school_id).count()
            stats.posts_count = posts_count
            self.db.commit()

    def _update_school_total_views(self, school_id: int) -> None:
        """Обновить общее количество просмотров в статистике школы"""
        from bot.models.statistics import Statistics
        
        stats = self.db.query(Statistics).filter(Statistics.school_id == school_id).first()
        if stats:
            total_views = self.db.query(Post).filter(
                Post.school_id == school_id
            ).with_entities(func.sum(Post.views)).scalar() or 0
            stats.total_views = total_views
            self.db.commit()
