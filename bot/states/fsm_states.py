from aiogram.fsm.state import State, StatesGroup


class AdminAuth(StatesGroup):
    """Состояния для авторизации администратора"""
    waiting_for_login = State()
    waiting_for_password = State()


class CreatePost(StatesGroup):
    """Состояния для создания поста"""
    selecting_school = State()
    waiting_for_text = State()
    waiting_for_media = State()
    confirming_publish = State()


class AddSchool(StatesGroup):
    """Состояния для добавления школы"""
    waiting_for_name = State()


class SendNotification(StatesGroup):
    """Состояния для отправки уведомления"""
    selecting_school = State()
    waiting_for_message = State()


class EditPost(StatesGroup):
    """Состояния для редактирования поста"""
    waiting_for_new_text = State()
    waiting_for_new_media = State()
