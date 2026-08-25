import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота MAX (без префикса Bearer)
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Webhook secret для проверки запросов от MAX
MAX_WEBHOOK_SECRET = os.getenv('MAX_WEBHOOK_SECRET', '')

# Админские учетные данные
ADMIN_LOGIN = os.getenv('ADMIN_LOGIN', 'Admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'armobotschool2026!')

# MAX API URL
MAX_API_URL = os.getenv('MAX_API_URL', 'https://platform-api2.max.ru')

# Логирование
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
