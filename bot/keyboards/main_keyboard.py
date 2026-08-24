from typing import List, Dict, Any


def get_main_keyboard() -> Dict[str, Any]:
    """Главное меню бота для MAX API"""
    return {
        "inline_keyboard": [
            [{"text": "🏫 Мои школы", "callback_data": "my_schools"}],
            [{"text": "📰 Последние новости", "callback_data": "latest_news"}],
            [{"text": "🔐 Админ-панель", "callback_data": "admin_panel"}],
        ]
    }


def get_back_keyboard(return_text: str = "Главное меню") -> Dict[str, Any]:
    """Клавиатура с кнопкой Назад"""
    callback = "main_menu" if return_text == "Главное меню" else return_text
    return {
        "inline_keyboard": [
            [{"text": "⬅️ Назад", "callback_data": callback}],
        ]
    }


def get_auth_keyboard() -> Dict[str, Any]:
    """Клавиатура авторизации"""
    return {
        "inline_keyboard": [
            [{"text": "🔐 Войти", "callback_data": "admin_auth"}],
        ]
    }
