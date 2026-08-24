import asyncpg
from typing import Optional, List
from bot.database import get_db


class UserService:
    """Сервис для работы с пользователями"""
    
    async def create_or_update_user(
        self,
        max_id: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None
    ) -> dict:
        """Создание или обновление пользователя"""
        db = await get_db()
        try:
            user = await db.fetchrow(
                """
                INSERT INTO users (max_id, username, first_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (max_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name
                RETURNING *
                """,
                max_id, username, first_name
            )
            return dict(user) if user else None
        finally:
            await db.close()
    
    async def get_user_by_max_id(self, max_id: str) -> Optional[dict]:
        """Получение пользователя по MAX ID"""
        db = await get_db()
        try:
            user = await db.fetchrow(
                "SELECT * FROM users WHERE max_id = $1",
                max_id
            )
            return dict(user) if user else None
        finally:
            await db.close()
    
    async def get_all_users(self) -> List[dict]:
        """Получение всех пользователей"""
        db = await get_db()
        try:
            users = await db.fetch("SELECT * FROM users")
            return [dict(u) for u in users]
        finally:
            await db.close()
    
    async def subscribe_user_to_school(self, user_id: int, school_id: int) -> bool:
        """Подписка пользователя на школу"""
        db = await get_db()
        try:
            await db.execute(
                """
                INSERT INTO subscriptions (user_id, school_id)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
                """,
                user_id, school_id
            )
            return True
        finally:
            await db.close()
    
    async def unsubscribe_user_from_school(self, user_id: int, school_id: int) -> bool:
        """Отписка пользователя от школы"""
        db = await get_db()
        try:
            await db.execute(
                "DELETE FROM subscriptions WHERE user_id = $1 AND school_id = $2",
                user_id, school_id
            )
            return True
        finally:
            await db.close()
    
    async def get_subscribed_school_ids(self, user_id: int) -> List[int]:
        """Получение ID школ, на которые подписан пользователь"""
        db = await get_db()
        try:
            rows = await db.fetch(
                "SELECT school_id FROM subscriptions WHERE user_id = $1",
                user_id
            )
            return [row['school_id'] for row in rows]
        finally:
            await db.close()
    
    async def is_subscribed(self, user_id: int, school_id: int) -> bool:
        """Проверка подписки пользователя на школу"""
        db = await get_db()
        try:
            row = await db.fetchrow(
                "SELECT 1 FROM subscriptions WHERE user_id = $1 AND school_id = $2",
                user_id, school_id
            )
            return row is not None
        finally:
            await db.close()
    
    async def get_subscribers_for_school(self, school_id: int) -> List[dict]:
        """Получение всех подписчиков школы"""
        db = await get_db()
        try:
            users = await db.fetch(
                """
                SELECT u.* FROM users u
                JOIN subscriptions s ON u.max_id = s.user_id
                WHERE s.school_id = $1
                """,
                school_id
            )
            return [dict(u) for u in users]
        finally:
            await db.close()