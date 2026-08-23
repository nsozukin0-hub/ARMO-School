from sqlalchemy.orm import Session
from typing import List, Optional

from bot.models.user import User
from bot.models.subscription import Subscription


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, telegram_id: int, username: str = None, first_name: str = None) -> User:
        """Создать или обновить пользователя"""
        user = self.get_user_by_telegram_id(telegram_id)
        
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            # Обновляем данные пользователя
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            self.db.commit()
        
        return user

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()

    def subscribe(self, user_id: int, school_id: int) -> bool:
        """Подписать пользователя на школу"""
        # Проверяем существующую подписку
        existing = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.school_id == school_id
        ).first()
        
        if existing:
            return False  # Уже подписан
        
        subscription = Subscription(user_id=user_id, school_id=school_id)
        self.db.add(subscription)
        self.db.commit()
        return True

    def unsubscribe(self, user_id: int, school_id: int) -> bool:
        """Отписать пользователя от школы"""
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.school_id == school_id
        ).first()
        
        if not subscription:
            return False
        
        self.db.delete(subscription)
        self.db.commit()
        return True

    def get_subscriptions(self, user_id: int) -> List[Subscription]:
        """Получить все подписки пользователя"""
        return self.db.query(Subscription).filter(Subscription.user_id == user_id).all()

    def get_subscribed_school_ids(self, user_id: int) -> List[int]:
        """Получить IDs школ, на которые подписан пользователь"""
        subscriptions = self.get_subscriptions(user_id)
        return [sub.school_id for sub in subscriptions]

    def is_subscribed(self, user_id: int, school_id: int) -> bool:
        """Проверить, подписан ли пользователь на школу"""
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.school_id == school_id
        ).first()
        return subscription is not None

    def get_all_users(self) -> List[User]:
        """Получить всех пользователей"""
        return self.db.query(User).all()

    def get_subscribers_for_school(self, school_id: int) -> List[User]:
        """Получить всех пользователей, подписанных на школу"""
        subscriptions = self.db.query(Subscription).filter(
            Subscription.school_id == school_id
        ).all()
        
        user_ids = [sub.user_id for sub in subscriptions]
        return self.db.query(User).filter(User.id.in_(user_ids)).all()
