import aiosqlite
from typing import Optional, List
from bot.database import get_db


class SchoolService:
    """Сервис для работы со школами"""
    
    async def create_school(self, name: str) -> Optional[dict]:
        """Создание новой школы"""
        db = await get_db()
        try:
            cursor = await db.execute(
                "INSERT INTO schools (name) VALUES (?) RETURNING *",
                (name,)
            )
            school = await cursor.fetchone()
            await db.commit()
            
            # Создаем запись статистики для школы
            if school:
                await db.execute(
                    "INSERT INTO statistics (school_id) VALUES (?)",
                    (school['id'],)
                )
                await db.commit()
            
            return dict(school) if school else None
        except aiosqlite.IntegrityError:
            return None  # Школа с таким именем уже существует
        finally:
            await db.close()
    
    async def delete_school(self, school_id: int) -> bool:
        """Удаление школы"""
        db = await get_db()
        try:
            await db.execute("DELETE FROM schools WHERE id = ?", (school_id,))
            await db.commit()
            return True
        finally:
            await db.close()
    
    async def get_all_schools(self) -> List[dict]:
        """Получение всех школ"""
        db = await get_db()
        try:
            cursor = await db.execute("SELECT * FROM schools ORDER BY name")
            schools = await cursor.fetchall()
            return [dict(s) for s in schools]
        finally:
            await db.close()
    
    async def get_school_by_id(self, school_id: int) -> Optional[dict]:
        """Получение школы по ID"""
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT * FROM schools WHERE id = ?",
                (school_id,)
            )
            school = await cursor.fetchone()
            return dict(school) if school else None
        finally:
            await db.close()
    
    async def school_exists(self, school_id: int) -> bool:
        """Проверка существования школы"""
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT 1 FROM schools WHERE id = ?",
                (school_id,)
            )
            row = await cursor.fetchone()
            return row is not None
        finally:
            await db.close()
