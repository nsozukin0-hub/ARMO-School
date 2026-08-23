from bot.config import ADMIN_LOGIN, ADMIN_PASSWORD


def verify_admin_credentials(login: str, password: str) -> bool:
    """Проверка учетных данных администратора"""
    return login == ADMIN_LOGIN and password == ADMIN_PASSWORD
