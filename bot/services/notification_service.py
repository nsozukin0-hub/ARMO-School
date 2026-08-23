from sqlalchemy.orm import Session
from typing import List
from aiogram import Bot

from bot.models.user import User
from bot.models.subscription import Subscription
from bot.services.user_service import UserService
from bot.services.stats_service import StatisticsService


class NotificationService:
    """Сервис для отправки уведомлений пользователям"""

    def __init__(self, db: Session, bot: Bot):
        self.db = db
        self.bot = bot
        self.user_service = UserService(db)
        self.stats_service = StatisticsService(db)

    async def send_notification_to_school_subscribers(
        self,
        school_id: int,
        message: str
    ) -> int:
        """Отправить уведомление всем подписчикам школы"""
        subscribers = self.user_service.get_subscribers_for_school(school_id)
        
        sent_count = 0
        failed_count = 0
        
        for subscriber in subscribers:
            try:
                await self.bot.send_message(
                    chat_id=subscriber.telegram_id,
                    text=f"🔔 **Важное уведомление**\n\n{message}",
                    parse_mode="Markdown"
                )
                sent_count += 1
            except Exception as e:
                # Логирование ошибки (можно добавить полноценное логирование)
                print(f"Failed to send notification to user {subscriber.telegram_id}: {e}")
                failed_count += 1
        
        # Обновляем статистику
        self.stats_service.increment_notifications_sent(school_id, sent_count)
        
        return sent_count

    async def send_notification_to_all_users(
        self,
        message: str
    ) -> int:
        """Отправить уведомление всем пользователям"""
        users = self.user_service.get_all_users()
        
        sent_count = 0
        
        for user in users:
            try:
                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=message
                )
                sent_count += 1
            except Exception as e:
                print(f"Failed to send notification to user {user.telegram_id}: {e}")
        
        return sent_count
