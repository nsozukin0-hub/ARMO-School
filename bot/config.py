import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_LOGIN = os.getenv('ADMIN_LOGIN', 'Admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'armobotschool2026!')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///school_bot.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MAX_API_URL = os.getenv('MAX_API_URL', 'https://platform-api2.max.ru')
