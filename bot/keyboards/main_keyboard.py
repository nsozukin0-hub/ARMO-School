from typing import List, Dict, Any


def get_main_keyboard() -> Dict[str, Any]:
    """Главное меню пользователя"""
    return {
        "inline_keyboard": [
            [{"text": "🏫 Мои школы", "callback_data": "menu_my_schools"}],
            [{"text": "📰 Последние новости", "callback_data": "menu_latest_news"}],
            [{"text": "🔐 Админ-панель", "callback_data": "menu_admin"}]
        ]
    }


def get_back_keyboard() -> Dict[str, Any]:
    """Клавиатура с кнопкой Назад"""
    return {
        "inline_keyboard": [
            [{"text": "⬅️ Назад", "callback_data": "menu_back"}]
        ]
    }


def get_schools_selection_keyboard(schools: List[dict], subscribed_ids: List[int]) -> Dict[str, Any]:
    """Клавиатура выбора школ"""
    buttons = []
    
    for school in schools:
        is_subscribed = school['id'] in subscribed_ids
        status = "☑️" if is_subscribed else "⬜"
        button_text = f"{status} {school['name']}"
        buttons.append([
            {"text": button_text, "callback_data": f"toggle_school_{school['id']}"}
        ])
    
    buttons.append([{"text": "💾 Сохранить", "callback_data": "save_subscriptions"}])
    buttons.append([{"text": "⬅️ Назад", "callback_data": "menu_back"}])
    
    return {"inline_keyboard": buttons}


def get_admin_keyboard() -> Dict[str, Any]:
    """Административное меню"""
    return {
        "inline_keyboard": [
            [{"text": "📝 Создать пост", "callback_data": "admin_create_post"}],
            [{"text": "📋 Все посты", "callback_data": "admin_all_posts"}],
            [{"text": "🏫 Управление школами", "callback_data": "admin_manage_schools"}],
            [{"text": "🔔 Уведомления", "callback_data": "admin_notifications"}],
            [{"text": "📊 Статистика", "callback_data": "admin_stats"}],
            [{"text": "⬅️ Назад", "callback_data": "menu_back"}]
        ]
    }


def get_schools_list_keyboard(schools: List[dict], action_prefix: str) -> Dict[str, Any]:
    """Клавиатура со списком школ для выбора"""
    buttons = []
    
    for school in schools:
        buttons.append([
            {"text": school['name'], "callback_data": f"{action_prefix}_{school['id']}"}
        ])
    
    buttons.append([{"text": "⬅️ Назад", "callback_data": "menu_back"}])
    
    return {"inline_keyboard": buttons}


def get_post_actions_keyboard(post_id: int) -> Dict[str, Any]:
    """Клавиатура действий с постом"""
    return {
        "inline_keyboard": [
            [{"text": "✏️ Редактировать", "callback_data": f"edit_post_{post_id}"}],
            [{"text": "🗑 Удалить", "callback_data": f"delete_post_{post_id}"}],
            [{"text": "⬅️ Назад", "callback_data": "admin_all_posts"}]
        ]
    }


def get_manage_schools_keyboard() -> Dict[str, Any]:
    """Клавиатура управления школами"""
    return {
        "inline_keyboard": [
            [{"text": "➕ Добавить школу", "callback_data": "add_school"}],
            [{"text": "🗑 Удалить школу", "callback_data": "delete_school"}],
            [{"text": "⬅️ Назад", "callback_data": "menu_back"}]
        ]
    }
