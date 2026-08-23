from bot.keyboards.main_keyboard import get_main_keyboard, get_back_keyboard
from bot.keyboards.user_keyboard import (
    get_schools_selection_keyboard,
    get_news_keyboard,
    get_post_actions_keyboard,
    get_admin_schools_keyboard,
    get_admin_school_action_keyboard,
    get_stats_keyboard
)
from bot.keyboards.admin_keyboard import (
    get_admin_menu_keyboard,
    get_admin_post_schools_keyboard,
    get_cancel_keyboard
)

__all__ = [
    'get_main_keyboard',
    'get_back_keyboard',
    'get_schools_selection_keyboard',
    'get_news_keyboard',
    'get_post_actions_keyboard',
    'get_admin_schools_keyboard',
    'get_admin_school_action_keyboard',
    'get_stats_keyboard',
    'get_admin_menu_keyboard',
    'get_admin_post_schools_keyboard',
    'get_cancel_keyboard'
]
