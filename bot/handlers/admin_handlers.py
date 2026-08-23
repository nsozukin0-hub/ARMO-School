from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import (
    get_main_keyboard,
    get_admin_menu_keyboard,
    get_admin_post_schools_keyboard,
    get_cancel_keyboard
)
from bot.states import AdminAuth, CreatePost, AddSchool, SendNotification
from bot.utils.auth import verify_admin_credentials
from bot.models.database import SessionLocal
from bot.services.school_service import SchoolService
from bot.services.user_service import UserService
from bot.services.post_service import PostService
from bot.services.stats_service import StatisticsService
from bot.services.notification_service import NotificationService


router = Router()

# Хранилище данных для создания поста
post_data = {}


@router.message(F.text == "🔐 Админ-панель")
async def admin_panel_button(message: Message, state: FSMContext):
    """Кнопка админ-панели в главном меню"""
    await state.set_state(AdminAuth.waiting_for_login)
    await message.answer(
        "🔐 **Авторизация администратора**\n\n"
        "Введите ваш логин:",
        parse_mode="Markdown"
    )


@router.message(AdminAuth.waiting_for_login)
async def process_admin_login(message: Message, state: FSMContext):
    """Обработка ввода логина"""
    login = message.text.strip()
    
    # Сохраняем логин во временное хранилище
    await state.update_data(login=login)
    await state.set_state(AdminAuth.waiting_for_password)
    
    await message.answer(
        "✅ Логин принят.\n\n"
        "Теперь введите пароль:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AdminAuth.waiting_for_password)
async def process_admin_password(message: Message, state: FSMContext):
    """Обработка ввода пароля"""
    password = message.text.strip()
    
    # Получаем логин из состояния
    data = await state.get_data()
    login = data.get('login', '')
    
    # Проверяем учетные данные
    if verify_admin_credentials(login, password):
        await state.clear()
        await message.answer(
            "✅ **Авторизация успешна!**\n\n"
            "Добро пожаловать в админ-панель.",
            reply_markup=get_admin_menu_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await state.clear()
        await message.answer(
            "❌ **Неверный логин или пароль**\n\n"
            "Попробуйте снова или нажмите /start для возврата в главное меню.",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "admin_create_post")
async def admin_create_post_start(callback: CallbackQuery):
    """Начало создания поста - выбор школы"""
    db = SessionLocal()
    try:
        school_service = SchoolService(db)
        schools = school_service.get_all_schools()
        
        if not schools:
            await callback.answer("❌ Нет доступных школ", show_alert=True)
            return
        
        keyboard = get_admin_post_schools_keyboard(schools)
        
        await callback.message.edit_text(
            "📝 **Создание поста**\n\n"
            "Выберите школу, для которой будет создан пост:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    finally:
        db.close()


@router.callback_query(F.data.startswith("admin_post_school_"))
async def admin_select_school_for_post(callback: CallbackQuery, state: FSMContext):
    """Выбор школы для создания поста"""
    school_id = int(callback.data.split("_")[-1])
    
    await state.update_data(post_school_id=school_id)
    await state.set_state(CreatePost.waiting_for_text)
    
    # Сохраняем школьный ID в глобальное хранилище
    post_data[callback.from_user.id] = {'school_id': school_id}
    
    await callback.message.edit_text(
        "📝 **Создание поста**\n\n"
        "Введите текст поста (или отправьте только медиа):\n\n"
        "Если хотите отправить только медиа, напишите «.» (точка)",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )


@router.message(CreatePost.waiting_for_text)
async def process_post_text(message: Message, state: FSMContext):
    """Обработка текста поста"""
    text = message.text.strip()
    
    if text == ".":
        text = None
    
    await state.update_data(post_text=text)
    await state.set_state(CreatePost.waiting_for_media)
    
    # Сохраняем текст в глобальное хранилище
    user_data = post_data.get(message.from_user.id, {})
    user_data['text'] = text
    post_data[message.from_user.id] = user_data
    
    await message.answer(
        "📎 **Добавление медиа**\n\n"
        "Отправьте фотографии (до 9), видео или документы.\n\n"
        "Если медиа не нужны, напишите «готово» или отправьте любой текст.",
        reply_markup=get_cancel_keyboard()
    )


@router.message(CreatePost.waiting_for_media)
async def process_post_media(message: Message, state: FSMContext):
    """Обработка медиа поста"""
    media_list = []
    
    # Проверяем, есть ли медиа в сообщении
    if message.photo:
        for photo in message.photo[-1:]:  # Берем фото наилучшего качества
            media_list.append({'type': 'photo', 'file_id': photo.file_id})
    elif message.video:
        media_list.append({'type': 'video', 'file_id': message.video.file_id})
    elif message.document:
        media_list.append({'type': 'document', 'file_id': message.document.file_id})
    elif message.text and message.text.strip().lower() == 'готово':
        pass  # Медиа не добавляем
    else:
        # Игнорируем другие сообщения
        return
    
    # Сохраняем медиа
    user_data = post_data.get(message.from_user.id, {})
    existing_media = user_data.get('media', [])
    existing_media.extend(media_list)
    
    # Ограничиваем до 9 элементов
    if len(existing_media) > 9:
        existing_media = existing_media[:9]
    
    user_data['media'] = existing_media
    post_data[message.from_user.id] = user_data
    
    if len(existing_media) < 9:
        await message.answer(
            f"✅ Добавлено медиа: {len(existing_media)}\n\n"
            "Можете отправить ещё или написать «готово» для публикации.",
            reply_markup=get_cancel_keyboard()
        )
    else:
        await message.answer(
            "📎 Достигнут лимит медиа (9 шт.)\n\n"
            "Напишите «готово» для публикации.",
            reply_markup=get_cancel_keyboard()
        )


@router.message(CreatePost.waiting_for_media, F.text, lambda x: x.strip().lower() == 'готово')
async def publish_post(message: Message, state: FSMContext):
    """Публикация поста"""
    db = SessionLocal()
    try:
        user_data = post_data.get(message.from_user.id, {})
        school_id = user_data.get('school_id')
        text = user_data.get('text')
        media = user_data.get('media', [])
        
        if not school_id:
            await message.answer("❌ Ошибка: школа не выбрана")
            await state.clear()
            return
        
        post_service = PostService(db)
        post = post_service.create_post(school_id=school_id, text=text, media=media)
        
        if post:
            await message.answer(
                f"✅ **Пост опубликован!**\n\n"
                f"ID поста: {post.id}\n"
                f"Школа ID: {school_id}",
                reply_markup=get_admin_menu_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await message.answer("❌ Ошибка при создании поста")
        
        # Очищаем состояние
        await state.clear()
        post_data.pop(message.from_user.id, None)
        
    finally:
        db.close()


@router.callback_query(F.data == "admin_cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Отмена текущего действия"""
    await state.clear()
    post_data.pop(callback.from_user.id, None)
    
    await callback.message.edit_text(
        "❌ Действие отменено.\n\n"
        "Выберите раздел админ-панели:",
        reply_markup=get_admin_menu_keyboard()
    )


@router.callback_query(F.data == "admin_all_posts")
async def admin_all_posts(callback: CallbackQuery):
    """Показ всех постов"""
    db = SessionLocal()
    try:
        post_service = PostService(db)
        posts = post_service.get_all_posts(limit=20)
        
        if not posts:
            await callback.answer("📭 Постов пока нет", show_alert=True)
            return
        
        text = "📋 **Все посты**\n\n"
        for post in posts[:10]:
            school_name = post.school.name if post.school else "Unknown"
            date = post.created_at.strftime('%d.%m.%Y %H:%M')
            text += f"📰 #{post.id} | {school_name} | {date}\n"
            if post.text:
                preview = post.text[:50] + "..." if len(post.text) > 50 else post.text
                text += f"   _{preview}_\n"
            text += "\n"
        
        # TODO: Добавить кнопки редактирования/удаления для каждого поста
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown"
        )
    finally:
        db.close()


@router.callback_query(F.data == "admin_manage_schools")
async def admin_manage_schools(callback: CallbackQuery):
    """Управление школами"""
    db = SessionLocal()
    try:
        school_service = SchoolService(db)
        schools = school_service.get_all_schools()
        
        if not schools:
            text = "🏫 **Управление школами**\n\n"
            text += "📭 Школ пока нет.\n\n"
            text += "Нажмите «➕ Добавить школу», чтобы создать первую."
        else:
            text = "🏫 **Управление школами**\n\n"
            text += "Выберите школу для управления:\n\n"
            for school in schools:
                text += f"• {school.name}\n"
        
        # TODO: Добавить inline-клавиатуру со школами
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown"
            # reply_markup=get_admin_schools_keyboard(schools)
        )
    finally:
        db.close()


@router.callback_query(F.data == "admin_notifications")
async def admin_notifications(callback: CallbackQuery, state: FSMContext):
    """Отправка уведомлений"""
    db = SessionLocal()
    try:
        school_service = SchoolService(db)
        schools = school_service.get_all_schools()
        
        if not schools:
            await callback.answer("❌ Нет школ для отправки уведомлений", show_alert=True)
            return
        
        # TODO: Реализовать выбор школы и отправку уведомления
        
        await callback.answer("🔔 Раздел в разработке", show_alert=True)
    finally:
        db.close()


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Показ статистики"""
    db = SessionLocal()
    try:
        stats_service = StatisticsService(db)
        overall_stats = stats_service.get_overall_stats()
        
        text = "📊 **Общая статистика**\n\n"
        text += f"🏫 Школ: {overall_stats['schools_count']}\n"
        text += f"👥 Пользователей: {overall_stats['users_count']}\n"
        text += f"📰 Публикаций: {overall_stats['total_posts']}\n"
        text += f"🔔 Уведомлений: {overall_stats['total_notifications']}\n"
        text += f"👀 Просмотров: {overall_stats['total_views']}\n"
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown"
        )
    finally:
        db.close()
