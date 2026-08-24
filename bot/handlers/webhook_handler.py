"""
Обработчик вебхуков от MAX API

Этот модуль обрабатывает входящие события от платформы МАКС:
- Новые сообщения от пользователей
- Нажатия кнопок (callbacks)
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


async def process_webhook_event(event: Dict[str, Any], max_client) -> Optional[Dict[str, Any]]:
    """
    Обработка входящего события от MAX API
    
    Args:
        event: Данные события от MAX
        max_client: Клиент MAX API для отправки ответов
        
    Returns:
        Ответ для отправки обратно в MAX (если нужен)
    """
    try:
        # Определяем тип события
        if 'message' in event:
            return await handle_message(event['message'], max_client)
        elif 'callback' in event:
            return await handle_callback(event['callback'], max_client)
        else:
            logger.warning(f"Неизвестный тип события: {event.keys()}")
            return None
            
    except Exception as e:
        logger.error(f"Ошибка обработки события: {e}", exc_info=True)
        return None


async def handle_message(message: Dict[str, Any], max_client) -> Optional[Dict[str, Any]]:
    """
    Обработка нового сообщения от пользователя
    
    Поддерживаемые команды:
    - /start - главное меню
    - Текст кнопки: "🏫 Мои школы", "📰 Последние новости", "🔐 Админ-панель"
    """
    from bot.database import SessionLocal
    from bot.services.user_service import UserService
    from bot.services.school_service import SchoolService
    from bot.services.post_service import PostService
    from bot.keyboards.main_keyboard import get_main_keyboard
    from bot.keyboards.user_keyboard import get_schools_selection_keyboard, get_back_keyboard
    from bot.keyboards.admin_keyboard import get_admin_keyboard, get_auth_keyboard
    
    db = SessionLocal()
    try:
        user_id = message.get('user_id')
        text = message.get('text', '').strip()
        
        logger.info(f"Сообщение от пользователя {user_id}: {text}")
        
        # Получаем или создаем пользователя
        user_service = UserService(db)
        user = user_service.get_user_by_max_id(user_id)
        if not user:
            user = user_service.create_user(
                max_id=user_id,
                username=message.get('username', ''),
                first_name=message.get('first_name', '')
            )
            logger.info(f"Создан новый пользователь: {user_id}")
        
        # Обработка команд
        if text == '/start' or text == 'Главное меню':
            await max_client.send_message(
                user_id=user_id,
                text=f"👋 Привет, {user.first_name or 'пользователь'}!\n\n"
                     "Я бот МАКС для школ района.\n\n"
                     "Выберите интересующий вас раздел:",
                reply_markup=get_main_keyboard()
            )
            return None
            
        elif text == '🏫 Мои школы':
            school_service = SchoolService(db)
            schools = school_service.get_all_schools()
            
            # Получаем подписки пользователя
            user_subscriptions = user_service.get_user_subscriptions(user.id)
            subscribed_ids = {sub.school_id for sub in user_subscriptions}
            
            keyboard = get_schools_selection_keyboard(schools, subscribed_ids)
            
            await max_client.send_message(
                user_id=user_id,
                text="🏫 <b>Мои школы</b>\n\n"
                     "Отметьте школы, новости которых вы хотите получать:\n\n"
                     "Нажмите на школу, чтобы выбрать/снять выбор.\n"
                     "Когда закончите, нажмите «💾 Сохранить».",
                reply_markup=keyboard
            )
            return None
            
        elif text == '📰 Последние новости':
            # Получаем новости от выбранных школ
            user_subscriptions = user_service.get_user_subscriptions(user.id)
            
            if not user_subscriptions:
                await max_client.send_message(
                    user_id=user_id,
                    text="📰 <b>Последние новости</b>\n\n"
                         "Вы ещё не подписаны ни на одну школу.\n\n"
                         "Перейдите в раздел «🏫 Мои школы», чтобы выбрать школы.",
                    reply_markup=get_back_keyboard("🏫 Мои школы")
                )
                return None
            
            post_service = PostService(db)
            posts = post_service.get_posts_for_subscriptions(
                [sub.school_id for sub in user_subscriptions],
                limit=10
            )
            
            if not posts:
                await max_client.send_message(
                    user_id=user_id,
                    text="📰 <b>Последние новости</b>\n\n"
                         "Новостей пока нет.\n\n"
                         "Администраторы выбранных школ ещё не опубликовали материалы.",
                    reply_markup=get_back_keyboard("🏫 Мои школы")
                )
                return None
            
            # Показываем последнюю новость
            latest_post = posts[0]
            school = latest_post.school
            
            message_text = f"📰 <b>{latest_post.title}</b>\n\n"
            message_text += f"🏫 <i>{school.name}</i>\n"
            message_text += f"📅 {latest_post.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            message_text += latest_post.content
            
            # TODO: Добавить обработку медиа
            await max_client.send_message(
                user_id=user_id,
                text=message_text,
                reply_markup=get_back_keyboard("📰 Последние новости")
            )
            return None
            
        elif text == '🔐 Админ-панель':
            # Запрашиваем авторизацию
            await max_client.send_message(
                user_id=user_id,
                text="🔐 <b>Админ-панель</b>\n\n"
                     "Введите логин для авторизации:",
                reply_markup=get_auth_keyboard()
            )
            return None
            
        elif text == '💾 Сохранить':
            await max_client.send_message(
                user_id=user_id,
                text="✅ Ваши предпочтения сохранены!\n\n"
                     "Теперь вы будете получать новости от выбранных школ.\n\n"
                     "Вернитесь в главное меню для продолжения.",
                reply_markup=get_main_keyboard()
            )
            return None
            
        elif text == '⬅️ Назад':
            await max_client.send_message(
                user_id=user_id,
                text="Выберите раздел:",
                reply_markup=get_main_keyboard()
            )
            return None
            
        else:
            # Неизвестная команда - показываем главное меню
            await max_client.send_message(
                user_id=user_id,
                text=f"❓ Неизвестная команда: {text}\n\n"
                     "Используйте кнопки меню для навигации.",
                reply_markup=get_main_keyboard()
            )
            return None
            
    finally:
        db.close()


async def handle_callback(callback: Dict[str, Any], max_client) -> Optional[Dict[str, Any]]:
    """
    Обработка нажатия на кнопку (callback)
    
    Поддерживаемые callback:
    - school_select_{id} - выбор/снятие школы
    - admin_auth - начало авторизации
    - edit_post_{id} - редактирование поста
    - delete_post_{id} - удаление поста
    """
    from bot.database import SessionLocal
    from bot.services.user_service import UserService
    from bot.services.school_service import SchoolService
    from bot.services.post_service import PostService
    from bot.keyboards.user_keyboard import get_schools_selection_keyboard
    from bot.keyboards.admin_keyboard import get_admin_keyboard
    
    db = SessionLocal()
    try:
        user_id = callback.get('user_id')
        callback_data = callback.get('data', '')
        
        logger.info(f"Callback от пользователя {user_id}: {callback_data}")
        
        # Отправляем ответ на callback (обязательно по API MAX)
        await max_client.send_answer(callback_id=callback.get('id'))
        
        user_service = UserService(db)
        user = user_service.get_user_by_max_id(user_id)
        
        if not user:
            logger.warning(f"Пользователь {user_id} не найден")
            return None
        
        # Обработка выбора школы
        if callback_data.startswith('school_select_'):
            school_id = int(callback_data.replace('school_select_', ''))
            
            # Переключаем подписку
            is_subscribed = user_service.toggle_subscription(user.id, school_id)
            
            # Обновляем клавиатуру
            school_service = SchoolService(db)
            schools = school_service.get_all_schools()
            user_subscriptions = user_service.get_user_subscriptions(user.id)
            subscribed_ids = {sub.school_id for sub in user_subscriptions}
            
            keyboard = get_schools_selection_keyboard(schools, subscribed_ids)
            
            status = "✅ подписана" if is_subscribed else "⬜ отписана"
            await max_client.send_message(
                user_id=user_id,
                text=f"Школа {school_id} {status}\n\n"
                     "Продолжайте выбор или нажмите «💾 Сохранить»",
                reply_markup=keyboard
            )
            return None
            
        elif callback_data == 'admin_auth':
            # Начало авторизации
            await max_client.send_message(
                user_id=user_id,
                text="🔐 <b>Авторизация администратора</b>\n\n"
                     "Введите логин:",
                reply_markup=None  # Ждём ввод текста
            )
            return None
            
        elif callback_data.startswith('edit_post_'):
            # Редактирование поста (только для админов)
            post_id = int(callback_data.replace('edit_post_', ''))
            await max_client.send_message(
                user_id=user_id,
                text=f"✏️ Редактирование поста #{post_id}\n\n"
                     "Введите новый текст поста:",
                reply_markup=None
            )
            return None
            
        elif callback_data.startswith('delete_post_'):
            # Удаление поста (только для админов)
            post_id = int(callback_data.replace('delete_post_', ''))
            
            post_service = PostService(db)
            post = post_service.get_post(post_id)
            
            if post:
                post_service.delete_post(post_id)
                await max_client.send_message(
                    user_id=user_id,
                    text=f"🗑 Пост #{post_id} удален",
                    reply_markup=get_admin_keyboard()
                )
            else:
                await max_client.send_message(
                    user_id=user_id,
                    text=f"❌ Пост #{post_id} не найден",
                    reply_markup=get_admin_keyboard()
                )
            return None
            
        else:
            logger.warning(f"Неизвестный callback: {callback_data}")
            return None
            
    finally:
        db.close()
