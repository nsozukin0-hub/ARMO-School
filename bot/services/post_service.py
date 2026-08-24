import aiosqlite
import json
from typing import Optional, List
from datetime import datetime
from bot.database import get_db


class PostService:
    """Сервис для работы с постами"""
    
    async def create_post(
        self,
        school_id: int,
        text: str,
        media: Optional[str] = None,
        max_message_id: Optional[str] = None
    ) -> Optional[dict]:
        """Создание нового поста"""
        db = await get_db()
        try:
            cursor = await db.execute(
                """
                INSERT INTO posts (school_id, text, media, max_message_id)
                VALUES (?, ?, ?, ?)
                RETURNING *
                """,
                (school_id, text, media, max_message_id)
            )
            post = await cursor.fetchone()
            
            # Обновляем статистику
            if post:
                await db.execute(
                    """
                    UPDATE statistics
                    SET post_count = post_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE school_id = ?
                    """,
                    (school_id,)
                )
                await db.commit()
            
            return dict(post) if post else None
        finally:
            await db.close()
    
    async def get_post_by_id(self, post_id: int) -> Optional[dict]:
        """Получение поста по ID"""
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT * FROM posts WHERE id = ?",
                (post_id,)
            )
            post = await cursor.fetchone()
            return dict(post) if post else None
        finally:
            await db.close()
    
    async def get_posts_by_school(
        self,
        school_id: int,
        limit: int = 10
    ) -> List[dict]:
        """Получение постов для школы"""
        db = await get_db()
        try:
            cursor = await db.execute(
                """
                SELECT * FROM posts
                WHERE school_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (school_id, limit)
            )
            posts = await cursor.fetchall()
            return [dict(p) for p in posts]
        finally:
            await db.close()
    
    async def get_all_posts(self, limit: int = 50) -> List[dict]:
        """Получение всех постов"""
        db = await get_db()
        try:
            cursor = await db.execute(
                """
                SELECT p.*, s.name as school_name
                FROM posts p
                JOIN schools s ON p.school_id = s.id
                ORDER BY p.created_at DESC
                LIMIT ?
                """,
                (limit,)
            )
            posts = await cursor.fetchall()
            return [dict(p) for p in posts]
        finally:
            await db.close()
    
    async def update_post(
        self,
        post_id: int,
        text: Optional[str] = None,
        media: Optional[str] = None
    ) -> bool:
        """Обновление поста"""
        db = await get_db()
        try:
            updates = []
            params = []
            
            if text is not None:
                updates.append("text = ?")
                params.append(text)
            if media is not None:
                updates.append("media = ?")
                params.append(media)
            
            if not updates:
                return False
            
            params.append(post_id)
            query = f"UPDATE posts SET {', '.join(updates)} WHERE id = ?"
            
            await db.execute(query, params)
            await db.commit()
            return True
        finally:
            await db.close()
    
    async def delete_post(self, post_id: int) -> bool:
        """Удаление поста"""
        db = await get_db()
        try:
            # Получаем school_id для обновления статистики
            cursor = await db.execute(
                "SELECT school_id FROM posts WHERE id = ?",
                (post_id,)
            )
            post = await cursor.fetchone()
            
            if not post:
                return False
            
            school_id = post['school_id']
            
            await db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            
            # Обновляем статистику
            await db.execute(
                """
                UPDATE statistics
                SET post_count = post_count - 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE school_id = ?
                """,
                (school_id,)
            )
            await db.commit()
            return True
        finally:
            await db.close()
    
    async def update_max_message_id(self, post_id: int, max_message_id: str) -> bool:
        """Обновление ID сообщения в MAX"""
        db = await get_db()
        try:
            await db.execute(
                "UPDATE posts SET max_message_id = ? WHERE id = ?",
                (max_message_id, post_id)
            )
            await db.commit()
            return True
        finally:
            await db.close()
