from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Административное меню"""
    keyboard = [
        [InlineKeyboardButton(text="📝 Создать пост", callback_data="admin_create_post")],
        [InlineKeyboardButton(text="📋 Все посты", callback_data="admin_all_posts")],
        [InlineKeyboardButton(text="🏫 Управление школами", callback_data="admin_manage_schools")],
        [InlineKeyboardButton(text="🔔 Уведомления", callback_data="admin_notifications")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_post_schools_keyboard(schools: list) -> InlineKeyboardMarkup:
    """Выбор школы для создания поста"""
    keyboard = []
    for school in schools:
        keyboard.append([
            InlineKeyboardButton(text=f"🏫 {school.name}", callback_data=f"admin_post_school_{school.id}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура отмены"""
    keyboard = [
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
