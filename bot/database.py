import aiosqlite
import asyncio
from typing import Optional

DB_PATH = "school_bot.db"


async def get_db() -> aiosqlite.Connection:
    """Получение соединения с базой данных"""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Инициализация базы данных и создание таблиц"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                max_id TEXT UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица школ
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица подписок
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                school_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                UNIQUE(user_id, school_id)
            )
        """)
        
        # Таблица постов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER NOT NULL,
                text TEXT,
                media TEXT,
                max_message_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
            )
        """)
        
        # Таблица статистики
        await db.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER NOT NULL,
                subscriber_count INTEGER DEFAULT 0,
                post_count INTEGER DEFAULT 0,
                notification_count INTEGER DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
            )
        """)
        
        await db.commit()
    
    print("База данных инициализирована")
