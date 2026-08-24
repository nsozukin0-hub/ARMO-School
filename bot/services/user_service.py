import aiosqlite
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
            cursor = await db.execute(
                """
                INSERT INTO users (max_id, username, first_name)
                VALUES (?, ?, ?)
                ON CONFLICT(max_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name
                RETURNING *
                """,
                (max_id, username, first_name)
            )
            user = await cursor.fetchone()
            await db.commit()
            return dict(user) if user else None
        finally:
            await db.close()
    
    async def get_user_by_max_id(self, max_id: str) -> Optional[dict]:
        """Получение пользователя по MAX ID"""
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT * FROM users WHERE max_id = ?",
                (max_id,)
            )
            user = await cursor.fetchone()
            return dict(user) if user else None
        finally:
            await db.close()
    
    async def get_all_users(self) -> List[dict]:
        """Получение всех пользователей"""
        db = await get_db()
        try:
            cursor = await db.execute("SELECT * FROM users")
            users = await cursor.fetchall()
            return [dict(u) for u in users]
        finally:
            await db.close()
    
    async def subscribe_user_to_school(self, user_id: int, school_id: int) -> bool:
        """Подписка пользователя на школу"""
        db = await get_db()
        try:
            await db.execute(
                """
                INSERT OR IGNORE INTO subscriptions (user_id, school_id)
                VALUES (?, ?)
                """,
                (user_id, school_id)
            )
            await db.commit()
            return True
        finally:
            await db.close()
    
    async def unsubscribe_user_from_school(self, user_id: int, school_id: int) -> bool:
        """Отписка пользователя от школы"""
        db = await get_db()
        try:
            await db.execute(
                "DELETE FROM subscriptions WHERE user_id = ? AND school_id = ?",
                (user_id, school_id)
            )
            await db.commit()
            return True
        finally:
            await db.close()
    
    async def get_subscribed_school_ids(self, user_id: int) -> List[int]:
        """Получение ID школ, на которые подписан пользователь"""
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT school_id FROM subscriptions WHERE user_id = ?",
                (user_id,)
            )
            rows = await cursor.fetchall()
            return [row['school_id'] for row in rows]
        finally:
            await db.close()
    
    async def is_subscribed(self, user_id: int, school_id: int) -> bool:
        """Проверка подписки пользователя на школу"""
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT 1 FROM subscriptions WHERE user_id = ? AND school_id = ?",
                (user_id, school_id)
            )
            row = await cursor.fetchone()
            return row is not None
        finally:
            await db.close()
    
    async def get_subscribers_for_school(self, school_id: int) -> List[dict]:
        """Получение всех подписчиков школы"""
        db = await get_db()
        try:
            cursor = await db.execute(
                """
                SELECT u.* FROM users u
                JOIN subscriptions s ON u.id = s.user_id
                WHERE s.school_id = ?
                """,
                (school_id,)
            )
            users = await cursor.fetchall()
            return [dict(u) for u in users]
        finally:
            await db.close()
