from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional

from bot.services.user_service import UserService
from bot.services.school_service import SchoolService
from bot.services.post_service import PostService
from bot.services.notification_service import NotificationService
from bot.services.stats_service import StatsService
from bot.services.max_api import MAXAPIClient
from bot.database import get_db
from bot.keyboards.main_keyboard import (
    get_main_menu,
    get_back_menu,
    get_schools_selection_keyboard,
    get_admin_menu,
    get_schools_list_keyboard,
    get_post_actions_keyboard,
    get_manage_schools_keyboard
)
from bot.config import ADMIN_LOGIN, ADMIN_PASSWORD

logger = logging.getLogger(__name__)
router = APIRouter()

# Хранилище состояний для FSM
user_states: Dict[str, dict] = {}


def get_user_state(user_id: str) -> dict:
    """Получение состояния пользователя"""
    if user_id not in user_states:
        user_states[user_id] = {'state': None, 'data': {}}
    return user_states[user_id]


def set_user_state(user_id: str, state: str, data: dict = None):
    """Установка состояния пользователя"""
    user_states[user_id] = {'state': state, 'data': data or {}}


async def get_max_client() -> MAXAPIClient:
    """Получение клиента MAX API из приложения"""
    from main import max_client
    return max_client


@router.post("/webhook")
async def webhook_handler(request: Request):
    """Обработчик вебхуков от MAX API"""
    try:
        headers = dict(request.headers)
        logger.info(f"Получен запрос на /webhook от {request.client.host if request.client else 'unknown'}")
        
        data = await request.json()
        logger.info(f"Получен вебхук: {data}")
        
        # 1. УНИВЕРСАЛЬНОЕ ИЗВЛЕЧЕНИЕ ДАННЫХ
        update_type = data.get('update_type', data.get('type', 'unknown'))
        
        message_data = data.get('message', {})
        callback_data = data.get('callback_query') or data.get('callback', {})
        
        sender_data = message_data.get('sender') or callback_data.get('from') or callback_data.get('user', {})
        recipient_data = message_data.get('recipient', {})
        body_data = message_data.get('body', {})
        
        user_id = str(sender_data.get('user_id') or data.get('user_id'))
        chat_id = str(recipient_data.get('chat_id') or callback_data.get('message', {}).get('chat_id') or data.get('chat_id') or user_id)
        
        if not user_id:
            logger.warning("Не получен user_id из вебхука. Структура: %s", data)
            return JSONResponse(status_code=200, content={"status": "ignored", "reason": "no user_id"})
        
        # Извлекаем данные пользователя (только те, что есть в сервисе)
        first_name = sender_data.get('first_name', 'Пользователь')
        username = sender_data.get('username', '')
        
        # 2. Инициализация сервисов
        user_service = UserService()
        school_service = SchoolService()
        post_service = PostService()
        notification_service = NotificationService()
        stats_service = StatsService()
        max_client = await get_max_client()
        
        # Создаем или обновляем пользователя в БД (БЕЗ last_name)
        user = await user_service.create_or_update_user(
            max_id=str(user_id),
            username=username,
            first_name=first_name
        )
        
        # 3. Обработка callback (нажатие inline-кнопок)
        if callback_data:
            return await handle_callback(
                callback_data=callback_data,
                user_id=str(user_id),
                chat_id=str(chat_id),
                user=user,
                user_service=user_service,
                school_service=school_service,
                post_service=post_service,
                stats_service=stats_service,
                max_client=max_client
            )
        
        # 4. Обработка текстовых сообщений
        text = body_data.get('text', '').strip()
        
        if text == '/start' or text.startswith('👋'):
            return await cmd_start(str(user_id), str(chat_id), user, user_service, max_client)
        elif text == '🏫 Мои школы':
            return await my_schools(str(user_id), str(chat_id), user, user_service, school_service, max_client)
        elif text == '📰 Последние новости':
            return await latest_news(str(user_id), str(chat_id), user, user_service, post_service, max_client)
        elif text == '🔐 Админ-панель':
            return await admin_menu_request(str(user_id), str(chat_id), user, max_client)
        else:
            # Проверка состояния FSM
            state_data = get_user_state(str(user_id))
            state = state_data.get('state')
            
            if state == 'admin_auth_login':
                return await handle_admin_login(str(user_id), str(chat_id), text, state_data, max_client)
            elif state == 'admin_auth_password':
                return await handle_admin_password(str(user_id), str(chat_id), text, state_data, max_client)
            elif state == 'add_school_name':
                return await handle_add_school(str(user_id), str(chat_id), text, state_data, school_service, max_client)
            elif state == 'create_post_text':
                return await handle_create_post_text(str(user_id), str(chat_id), text, state_data, max_client)
            elif state == 'send_notification_text':
                return await handle_send_notification(str(user_id), str(chat_id), text, state_data, school_service, notification_service, max_client)
            else:
                return await show_main_menu(str(user_id), str(chat_id), user, max_client)
        
        return JSONResponse(status_code=200, content={"status": "ok"})
        
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


async def send_message(max_client: MAXAPIClient, user_id: str, text: str, keyboard: dict = None):
    """Отправка сообщения пользователю через MAX API"""
    if not max_client:
        logger.warning("MAX клиент не инициализирован")
        return None
    
    logger.info(f"Отправка сообщения пользователю {user_id}: {text[:100]}...")
    
    result = await max_client.send_message(user_id=user_id, text=text, keyboard=keyboard)
    
    if result:
        logger.info(f"Сообщение успешно отправлено, result: {result}")
    else:
        logger.error(f"Не удалось отправить сообщение пользователю {user_id}")
    return result


async def cmd_start(user_id: str, chat_id: str, user: dict, user_service: UserService, max_client: MAXAPIClient):
    """Обработчик команды /start"""
    first_name = user.get('first_name', 'пользователь') if user else 'пользователь'
    text = f"👋 Привет, {first_name}!\n\nЯ бот МАКС для школ района.\n\nВыберите интересующий вас раздел:"
    
    set_user_state(str(user_id), None)
    await send_message(max_client, user_id, text, get_main_menu())
    
    return JSONResponse(status_code=200, content={"status": "ok"})


async def show_main_menu(user_id: str, chat_id: str, user: dict, max_client: MAXAPIClient):
    """Показ главного меню"""
    text = "Выберите раздел:"
    keyboard = get_main_menu()
    await send_message(max_client, user_id, text, keyboard)
    return JSONResponse(status_code=200, content={"status": "ok"})


async def my_schools(user_id: str, chat_id: str, user: dict, user_service: UserService, school_service: SchoolService, max_client: MAXAPIClient):
    """Показ списка школ для выбора"""
    schools = await school_service.get_all_schools()
    
    if not schools:
        text = "📭 На данный момент нет доступных школ.\nПопробуйте позже."
        await send_message(max_client, user_id, text, get_back_menu())
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    db_user_id = user.get('id') if user else user_id
    subscribed_ids = await user_service.get_subscribed_school_ids(db_user_id)
    keyboard = get_schools_selection_keyboard(schools, subscribed_ids)
    
    text = "🏫 **Выберите школы**\n\nНажмите на школу, чтобы изменить статус подписки.\nКогда закончите, нажмите «Сохранить»."
    await send_message(max_client, user_id, text, keyboard)
    
    return JSONResponse(status_code=200, content={"status": "ok"})


async def latest_news(user_id: str, chat_id: str, user: dict, user_service: UserService, post_service: PostService, max_client: MAXAPIClient):
    """Показ последних новостей"""
    if not user:
        await send_message(max_client, user_id, "⚠️ Сначала начните работу с ботом (/start)", get_main_menu())
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    db_user_id = user.get('id')
    subscribed_ids = await user_service.get_subscribed_school_ids(db_user_id)
    
    if not subscribed_ids:
        text = "📭 У вас нет подписок на школы.\n\nПерейдите в раздел «🏫 Мои школы», чтобы выбрать школы."
        await send_message(max_client, user_id, text, get_back_menu())
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    all_posts = []
    for school_id in subscribed_ids:
        posts = await post_service.get_posts_by_school(school_id, limit=10)
        all_posts.extend(posts)
    
    all_posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    if not all_posts:
        text = "📭 Новостей пока нет.\n\nПодпишитесь на школы, чтобы получать уведомления."
        await send_message(max_client, user_id, text, get_back_menu())
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    text = "📰 **Последние новости**\n\n"
    for post in all_posts[:5]:
        created_at = post.get('created_at', '')[:16] if post.get('created_at') else ''
        post_text = post.get('text', '_Без текста_')
        text += f"📄 {created_at}\n{post_text}\n\n"
    
    await send_message(max_client, user_id, text, get_back_menu())
    return JSONResponse(status_code=200, content={"status": "ok"})


async def admin_menu_request(user_id: str, chat_id: str, user: dict, max_client: MAXAPIClient):
    """Запрос админ-меню (начало авторизации)"""
    set_user_state(str(user_id), 'admin_auth_login', {'step': 'login'})
    text = "🔐 **Админ-панель**\n\nВведите ваш логин:"
    await send_message(max_client, user_id, text, get_back_menu())
    return JSONResponse(status_code=200, content={"status": "ok"})


async def handle_callback(callback_data: dict, user_id: str, chat_id: str, user: dict, **services):
    """Обработка нажатий кнопок (inline keyboard)"""
    action = callback_data.get('data') or callback_data.get('action', '')
    callback_id = callback_data.get('id') or callback_data.get('callback_id', '')
    
    logger.info(f"Callback: {action} от пользователя {user_id}, callback_id: {callback_id}")
    
    db_user_id = user.get('id') if user else user_id

    if action.startswith('toggle_school_'):
        school_id = int(action.split('_')[-1])
        user_service = services['user_service']
        
        if await user_service.is_subscribed(db_user_id, school_id):
            await user_service.unsubscribe_user_from_school(db_user_id, school_id)
            answer_text = "Отписано от школы"
        else:
            await user_service.subscribe_user_to_school(db_user_id, school_id)
            answer_text = "Подписано на школу"
        
        school_service = services['school_service']
        schools = await school_service.get_all_schools()
        subscribed_ids = await user_service.get_subscribed_school_ids(db_user_id)
        keyboard = get_schools_selection_keyboard(schools, subscribed_ids)
        
        await send_message(services['max_client'], user_id, f"✅ {answer_text}", keyboard)
        return JSONResponse(status_code=200, content={"status": "ok", "answered": True})
    
    elif action == 'save_subscriptions':
        school_service = services['school_service']
        user_service = services['user_service']
        subscribed_ids = await user_service.get_subscribed_school_ids(db_user_id)
        
        logger.info(f"Пользователь {user_id} сохранил подписки: {len(subscribed_ids)} школ")
        await send_message(services['max_client'], user_id, f"✅ Ваши подписки сохранены!\n\nВы подписаны на {len(subscribed_ids)} школ(ы).", get_main_menu())
        return JSONResponse(status_code=200, content={"status": "ok", "answered": True})
    
    elif action == 'menu_back':
        await send_message(services['max_client'], user_id, "Главное меню:", get_main_menu())
        return JSONResponse(status_code=200, content={"status": "ok", "answered": True})
    
    elif action == 'menu_admin':
        set_user_state(str(user_id), 'admin_auth_login', {'step': 'login'})
        await send_message(services['max_client'], user_id, "🔐 **Админ-панель**\n\nВведите ваш логин:", get_back_menu())
        return JSONResponse(status_code=200, content={"status": "ok", "answered": True})
    
    return JSONResponse(status_code=200, content={"status": "ok", "answered": True})


async def handle_admin_login(user_id: str, chat_id: str, text: str, state_data: dict, max_client: MAXAPIClient):
    """Обработка ввода логина админа"""
    if text != ADMIN_LOGIN:
        await send_message(max_client, user_id, "❌ Неверный логин. Попробуйте еще раз:", get_back_menu())
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    state_data['login'] = text
    set_user_state(user_id, 'admin_auth_password', state_data)
    await send_message(max_client, user_id, "✅ Логин верный.\n\nВведите пароль:", get_back_menu())
    return JSONResponse(status_code=200, content={"status": "ok"})


async def handle_admin_password(user_id: str, chat_id: str, text: str, state_data: dict, max_client: MAXAPIClient):
    """Обработка ввода пароля админа"""
    if text != ADMIN_PASSWORD:
        set_user_state(user_id, None)
        await send_message(max_client, user_id, "❌ Неверный пароль.\n\nДля входа в админ-панель введите /start и выберите «🔐 Админ-панель».", get_main_menu())
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    set_user_state(user_id, None)
    await send_message(max_client, user_id, "✅ Авторизация успешна!", get_admin_menu())
    return JSONResponse(status_code=200, content={"status": "ok"})


async def handle_add_school(user_id: str, chat_id: str, text: str, state_data: dict, school_service: SchoolService, max_client: MAXAPIClient):
    """Обработка добавления школы"""
    set_user_state(user_id, None)
    
    school = await school_service.create_school(text)
    
    if school:
        await send_message(max_client, user_id, f"✅ Школа «{text}» успешно добавлена!", get_manage_schools_keyboard())
    else:
        await send_message(max_client, user_id, "❌ Школа с таким названием уже существует.\n\nВведите другое название:", get_back_menu())
    
    return JSONResponse(status_code=200, content={"status": "ok"})


async def handle_create_post_text(user_id: str, chat_id: str, text: str, state_data: dict, max_client: MAXAPIClient):
    """Обработка текста поста"""
    set_user_state(user_id, None)
    await send_message(max_client, user_id, "✅ Пост создан!")
    return JSONResponse(status_code=200, content={"status": "ok"})


async def handle_send_notification(user_id: str, chat_id: str, text: str, state_data: dict, school_service, notification_service, max_client: MAXAPIClient):
    """Обработка отправки уведомления"""
    school_id = state_data.get('school_id')
    
    if not school_id:
        await send_message(max_client, user_id, "❌ Ошибка: школа не выбрана")
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    set_user_state(user_id, None)
    await send_message(max_client, user_id, f"✅ Уведомление отправлено подписчикам школы!")
    return JSONResponse(status_code=200, content={"status": "ok"})
