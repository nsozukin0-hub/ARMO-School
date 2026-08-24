import aiosqlite
from typing import Optional, List
from bot.database import get_db


class NotificationService:
    """Сервис для работы с уведомлениями"""
    
    async def send_notification_to_school_subscribers(
        self,
        school_id: int,
        text: str,
        max_client
    ) -> int:
        """
        Отправка уведомления всем подписчикам школы
        
        Args:
            school_id: ID школы
            text: Текст уведомления
            max_client: Клиент MAX API
            
        Returns:
            Количество отправленных уведомлений
        """
        db = await get_db()
        try:
            # Получаем всех подписчиков школы
            cursor = await db.execute(
                """
                SELECT u.max_id FROM users u
                JOIN subscriptions s ON u.id = s.user_id
                WHERE s.school_id = ?
                """,
                (school_id,)
            )
            subscribers = await cursor.fetchall()
            
            sent_count = 0
            for subscriber in subscribers:
                max_id = subscriber['max_id']
                if max_id:
                    message_id = await max_client.send_message(
                        user_id=max_id,
                        text=text,
                        notify=True
                    )
                    if message_id:
                        sent_count += 1
            
            # Обновляем статистику
            await db.execute(
                """
                UPDATE statistics
                SET notification_count = notification_count + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE school_id = ?
                """,
                (sent_count, school_id)
            )
            await db.commit()
            
            return sent_count
        finally:
            await db.close()
