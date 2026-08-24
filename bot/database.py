import asyncpg
import os
import asyncio
from typing import Optional

# Получаем URL из переменных окружения Vercel
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Переменная окружения DATABASE_URL не найдена! Проверьте настройки Vercel.")

# Глобальный пул соединений для переиспользования в Vercel
_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """Инициализация и получение пула соединений"""
    global _pool
    if _pool is None:
        # min_size=1, max_size=5 оптимально для Vercel, чтобы не перегружать Supabase
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def get_db() -> asyncpg.Connection:
    """Получение соединения из пула (аналог вашего старого get_db)"""
    pool = await get_pool()
    return await pool.acquire()


async def release_db(conn: asyncpg.Connection):
    """Освобождение соединения обратно в пул после использования"""
    pool = await get_pool()
    if conn:
        await pool.release(conn)


async def init_db():
    """Инициализация базы данных и создание таблиц (синтаксис PostgreSQL)"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Таблица пользователей
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                max_id TEXT UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица школ
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schools (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица подписок
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                school_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                UNIQUE(user_id, school_id)
            )
        """)
        
        # Таблица постов
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                school_id INTEGER NOT NULL,
                text TEXT,
                media TEXT,
                max_message_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
            )
        """)
        
        # Таблица статистики
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id SERIAL PRIMARY KEY,
                school_id INTEGER NOT NULL,
                subscriber_count INTEGER DEFAULT 0,
                post_count INTEGER DEFAULT 0,
                notification_count INTEGER DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
            )
        """)
        
    print("✅ База данных инициализирована (PostgreSQL / Supabase)")
