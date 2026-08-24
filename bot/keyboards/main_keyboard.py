from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню пользователя"""
    buttons = [
        [InlineKeyboardButton(text="🏫 Мои школы", callback_data="menu_my_schools")],
        [InlineKeyboardButton(text="📰 Последние новости", callback_data="menu_latest_news")],
        [InlineKeyboardButton(text="🔐 Админ-панель", callback_data="menu_admin")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой Назад"""
    buttons = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_schools_selection_keyboard(schools: List[dict], subscribed_ids: List[int]) -> InlineKeyboardMarkup:
    """Клавиатура выбора школ"""
    buttons = []
    
    for school in schools:
        is_subscribed = school['id'] in subscribed_ids
        status = "☑️" if is_subscribed else "⬜"
        button_text = f"{status} {school['name']}"
        buttons.append([
            InlineKeyboardButton(text=button_text, callback_data=f"toggle_school_{school['id']}")
        ])
    
    buttons.append([InlineKeyboardButton(text="💾 Сохранить", callback_data="save_subscriptions")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Административное меню"""
    buttons = [
        [InlineKeyboardButton(text="📝 Создать пост", callback_data="admin_create_post")],
        [InlineKeyboardButton(text="📋 Все посты", callback_data="admin_all_posts")],
        [InlineKeyboardButton(text="🏫 Управление школами", callback_data="admin_manage_schools")],
        [InlineKeyboardButton(text="🔔 Уведомления", callback_data="admin_notifications")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_schools_list_keyboard(schools: List[dict], action_prefix: str) -> InlineKeyboardMarkup:
    """Клавиатура со списком школ для выбора"""
    buttons = []
    
    for school in schools:
        buttons.append([
            InlineKeyboardButton(text=school['name'], callback_data=f"{action_prefix}_{school['id']}")
        ])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_post_actions_keyboard(post_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с постом"""
    buttons = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_post_{post_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_post_{post_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_all_posts")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_manage_schools_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления школами"""
    buttons = [
        [InlineKeyboardButton(text="➕ Добавить школу", callback_data="add_school")],
        [InlineKeyboardButton(text="🗑 Удалить школу", callback_data="delete_school")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
