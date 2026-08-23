from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏫 Мои школы")],
            [KeyboardButton(text="📰 Последние новости")],
            [KeyboardButton(text="🔐 Админ-панель")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой Назад"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True
    )
    return keyboard
