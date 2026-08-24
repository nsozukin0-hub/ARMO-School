import aiosqlite
from typing import Optional, List, Dict
from bot.database import get_db


class StatsService:
    """Сервис для работы со статистикой"""
    
    async def get_school_stats(self, school_id: int) -> Optional[dict]:
        """Получение статистики по школе"""
        db = await get_db()
        try:
            # Получаем основную статистику
            cursor = await db.execute(
                """
                SELECT s.subscriber_count, s.post_count, 
                       s.notification_count, s.view_count,
                       sch.name as school_name
                FROM statistics s
                JOIN schools sch ON s.school_id = sch.id
                WHERE s.school_id = ?
                """,
                (school_id,)
            )
            stats = await cursor.fetchone()
            
            if not stats:
                return None
            
            result = dict(stats)
            
            # Получаем актуальное количество подписчиков
            cursor = await db.execute(
                "SELECT COUNT(*) as count FROM subscriptions WHERE school_id = ?",
                (school_id,)
            )
            sub_count = await cursor.fetchone()
            result['subscriber_count'] = sub_count['count'] if sub_count else 0
            
            # Получаем актуальное количество постов
            cursor = await db.execute(
                "SELECT COUNT(*) as count FROM posts WHERE school_id = ?",
                (school_id,)
            )
            post_count = await cursor.fetchone()
            result['post_count'] = post_count['count'] if post_count else 0
            
            return result
        finally:
            await db.close()
    
    async def get_all_schools_stats(self) -> List[dict]:
        """Получение статистики по всем школам"""
        db = await get_db()
        try:
            cursor = await db.execute(
                """
                SELECT sch.id, sch.name,
                       s.subscriber_count, s.post_count,
                       s.notification_count, s.view_count
                FROM schools sch
                LEFT JOIN statistics s ON sch.id = s.school_id
                ORDER BY sch.name
                """
            )
            schools = await cursor.fetchall()
            
            result = []
            for school in schools:
                stats_dict = dict(school)
                school_id = stats_dict['id']
                
                # Получаем актуальное количество подписчиков
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM subscriptions WHERE school_id = ?",
                    (school_id,)
                )
                sub_count = await cursor.fetchone()
                stats_dict['subscriber_count'] = sub_count['count'] if sub_count else 0
                
                # Получаем актуальное количество постов
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM posts WHERE school_id = ?",
                    (school_id,)
                )
                post_count = await cursor.fetchone()
                stats_dict['post_count'] = post_count['count'] if post_count else 0
                
                result.append(stats_dict)
            
            return result
        finally:
            await db.close()
    
    async def get_total_stats(self) -> Dict[str, int]:
        """Получение общей статистики по всем школам"""
        db = await get_db()
        try:
            # Общее количество пользователей
            cursor = await db.execute("SELECT COUNT(*) as count FROM users")
            total_users = await cursor.fetchone()
            
            # Общее количество школ
            cursor = await db.execute("SELECT COUNT(*) as count FROM schools")
            total_schools = await cursor.fetchone()
            
            # Общее количество постов
            cursor = await db.execute("SELECT COUNT(*) as count FROM posts")
            total_posts = await cursor.fetchone()
            
            # Общее количество подписок
            cursor = await db.execute("SELECT COUNT(*) as count FROM subscriptions")
            total_subscriptions = await cursor.fetchone()
            
            return {
                'total_users': total_users['count'] if total_users else 0,
                'total_schools': total_schools['count'] if total_schools else 0,
                'total_posts': total_posts['count'] if total_posts else 0,
                'total_subscriptions': total_subscriptions['count'] if total_subscriptions else 0
            }
        finally:
            await db.close()
    
    async def increment_view_count(self, school_id: int) -> bool:
        """Увеличение счетчика просмотров"""
        db = await get_db()
        try:
            await db.execute(
                """
                UPDATE statistics
                SET view_count = view_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE school_id = ?
                """,
                (school_id,)
            )
            await db.commit()
            return True
        finally:
            await db.close()
