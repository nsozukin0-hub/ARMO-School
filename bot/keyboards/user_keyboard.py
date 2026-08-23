from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from bot.models.school import School


def get_schools_selection_keyboard(schools: List[School], user_subscriptions: List[int]) -> InlineKeyboardMarkup:
    """Клавиатура для выбора школ с чекбоксами"""
    keyboard = []
    
    for school in schools:
        is_subscribed = school.id in user_subscriptions
        checkbox = "☑️" if is_subscribed else "⬜"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{checkbox} {school.name}",
                callback_data=f"toggle_school_{school.id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="💾 Сохранить", callback_data="save_subscriptions")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_news_keyboard(posts: List[dict]) -> InlineKeyboardMarkup:
    """Клавиатура для навигации по новостям"""
    keyboard = []
    
    # Кнопки для просмотра постов
    for i, post in enumerate(posts[:10]):  # Показываем до 10 последних
        keyboard.append([
            InlineKeyboardButton(
                text=f"📰 Пост #{post['id']} ({post['date']})",
                callback_data=f"view_post_{post['id']}"
            )
        ])
    
    if len(posts) > 10:
        keyboard.append([
            InlineKeyboardButton(text="➡️ Следующие", callback_data="news_next_page")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_post_actions_keyboard(post_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с постом (для админа)"""
    keyboard = [
        [
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_post_{post_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_post_{post_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_all_posts")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_schools_keyboard(schools: List[School]) -> InlineKeyboardMarkup:
    """Клавиатура управления школами для админа"""
    keyboard = []
    
    for school in schools:
        keyboard.append([
            InlineKeyboardButton(text=f"🏫 {school.name}", callback_data=f"admin_school_{school.id}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="➕ Добавить школу", callback_data="admin_add_school"),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_school_action_keyboard(school_id: int, school_name: str) -> InlineKeyboardMarkup:
    """Клавиатура действий со школой"""
    keyboard = [
        [
            InlineKeyboardButton(text="📝 Создать пост", callback_data=f"admin_create_post_{school_id}"),
        ],
        [
            InlineKeyboardButton(text="🔔 Отправить уведомление", callback_data=f"admin_notify_{school_id}"),
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить школу", callback_data=f"admin_delete_school_{school_id}"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin_manage_schools"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_stats_keyboard(schools: List[School]) -> InlineKeyboardMarkup:
    """Клавиатура для просмотра статистики"""
    keyboard = []
    
    keyboard.append([
        InlineKeyboardButton(text="📊 Общая статистика", callback_data="stats_overall")
    ])
    
    for school in schools:
        keyboard.append([
            InlineKeyboardButton(text=f"🏫 {school.name}", callback_data=f"stats_school_{school.id}")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
