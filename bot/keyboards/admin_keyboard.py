from typing import List, Dict, Any


def get_admin_menu_keyboard() -> Dict[str, Any]:
    """Административное меню для MAX API"""
    return {
        "inline_keyboard": [
            [{"text": "📝 Создать пост", "callback_data": "admin_create_post"}],
            [{"text": "📋 Все посты", "callback_data": "admin_all_posts"}],
            [{"text": "🏫 Управление школами", "callback_data": "admin_manage_schools"}],
            [{"text": "🔔 Уведомления", "callback_data": "admin_notifications"}],
            [{"text": "📊 Статистика", "callback_data": "admin_stats"}],
        ]
    }


def get_admin_post_schools_keyboard(schools: List[Dict]) -> Dict[str, Any]:
    """Выбор школы для создания поста"""
    inline_keyboard = []
    for school in schools:
        inline_keyboard.append([
            {"text": f"🏫 {school['name']}", "callback_data": f"admin_post_school_{school['id']}"}
        ])
    return {"inline_keyboard": inline_keyboard}


def get_cancel_keyboard() -> Dict[str, Any]:
    """Клавиатура отмены"""
    return {
        "inline_keyboard": [
            [{"text": "❌ Отмена", "callback_data": "admin_cancel"}]
        ]
    }
