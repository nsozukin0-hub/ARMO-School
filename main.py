import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from bot.database import init_db
from bot.handlers.webhook_handler import router as webhook_router
from bot.services.max_api import MAXAPIClient
from bot.config import BOT_TOKEN, MAX_API_URL

# Настройка логирования для Vercel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Глобальный клиент MAX API
max_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global max_client
    
    # Инициализация при запуске
    logger.info("=" * 50)
    logger.info("Инициализация базы данных...")
    await init_db()
    
    logger.info("Инициализация MAX API клиента...")
    max_client = MAXAPIClient(BOT_TOKEN)
    
    logger.info(f"Бот МАКС запущен! Токен: {BOT_TOKEN[:10]}...")
    logger.info(f"MAX API URL: {MAX_API_URL}")
    logger.info("=" * 50)
    
    yield
    
    # Очистка при остановке
    if max_client:
        await max_client.close()
    logger.info("Бот остановлен")

# Создание приложения FastAPI
app = FastAPI(
    title="МАКС Бот для школ",
    description="Бот для информирования о новостях и событиях школ района",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение роутера вебхука
app.include_router(webhook_router)

@app.get("/")
async def root():
    """Проверка работоспособности"""
    logger.info("Health check запрос на /")
    return {
        "status": "ok",
        "message": "МАКС Бот для школ работает",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья для мониторинга"""
    logger.info("Health check запрос на /health")
    return {"status": "healthy"}

if __name__ == "__main__":
    # Запуск сервера
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
