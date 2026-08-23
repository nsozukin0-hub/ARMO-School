from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards import (
    get_main_keyboard,
    get_back_keyboard,
    get_schools_selection_keyboard,
    get_news_keyboard
)
from bot.models.database import SessionLocal
from bot.services.user_service import UserService
from bot.services.school_service import SchoolService
from bot.services.post_service import PostService


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    db = SessionLocal()
    try:
        user_service = UserService(db)
        
        # Создаем или обновляем пользователя
        user = user_service.create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        
        await message.answer(
            f"👋 Привет, {message.from_user.first_name or 'пользователь'}!\n\n"
            "Я бот МАКС для школ района.\n\n"
            "Выберите интересующий вас раздел:",
            reply_markup=get_main_keyboard()
        )
    finally:
        db.close()


@router.message(F.text == "🏫 Мои школы")
async def my_schools(message: Message):
    """Показ списка школ для выбора"""
    db = SessionLocal()
    try:
        user_service = UserService(db)
        school_service = SchoolService(db)
        
        # Получаем пользователя
        user = user_service.get_user_by_telegram_id(message.from_user.id)
        if not user:
            user = user_service.create_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
        
        # Получаем все школы и текущие подписки
        schools = school_service.get_all_schools()
        subscribed_ids = user_service.get_subscribed_school_ids(user.id)
        
        if not schools:
            await message.answer(
                "📭 На данный момент нет доступных школ.\n"
                "Попробуйте позже.",
                reply_markup=get_back_keyboard()
            )
            return
        
        keyboard = get_schools_selection_keyboard(schools, subscribed_ids)
        
        await message.answer(
            "🏫 **Выберите школы**\n\n"
            "Нажмите на школу, чтобы изменить статус подписки.\n"
            "Когда закончите, нажмите «💾 Сохранить».",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    finally:
        db.close()


@router.message(F.text == "📰 Последние новости")
async def latest_news(message: Message):
    """Показ последних новостей от выбранных школ"""
    db = SessionLocal()
    try:
        user_service = UserService(db)
        post_service = PostService(db)
        
        # Получаем пользователя
        user = user_service.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer(
                "⚠️ Сначала нажмите /start для регистрации",
                reply_markup=get_main_keyboard()
            )
            return
        
        # Получаем подписки
        subscribed_school_ids = user_service.get_subscribed_school_ids(user.id)
        
        if not subscribed_school_ids:
            await message.answer(
                "📭 У вас нет подписок на школы.\n\n"
                "Перейдите в раздел «🏫 Мои школы», чтобы выбрать школы.",
                reply_markup=get_back_keyboard()
            )
            return
        
        # Получаем посты из всех выбранных школ
        all_posts = []
        for school_id in subscribed_school_ids:
            posts = post_service.get_posts_by_school(school_id, limit=10)
            for post in posts:
                all_posts.append({
                    'id': post.id,
                    'school_id': post.school_id,
                    'text': post.text,
                    'created_at': post.created_at.strftime('%d.%m.%Y %H:%M'),
                    'media': post.media
                })
        
        # Сортируем по дате (новые сверху)
        all_posts.sort(key=lambda x: x['created_at'], reverse=True)
        
        if not all_posts:
            await message.answer(
                "📭 Новостей пока нет.\n\n"
                "Подпишитесь на школы, чтобы получать уведомления.",
                reply_markup=get_back_keyboard()
            )
            return
        
        # Показываем последние 10 новостей
        for post_data in all_posts[:10]:
            text = f"📰 **Новость от {post_data['created_at']}**\n\n"
            if post_data['text']:
                text += post_data['text']
            else:
                text += "_Без текста_"
            
            # TODO: Отправка с медиа (если есть)
            await message.answer(text, parse_mode="Markdown")
        
    finally:
        db.close()


@router.callback_query(F.data.startswith("toggle_school_"))
async def toggle_school_subscription(callback: CallbackQuery):
    """Переключение подписки на школу"""
    db = SessionLocal()
    try:
        user_service = UserService(db)
        school_service = SchoolService(db)
        
        school_id = int(callback.data.split("_")[-1])
        user = user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Ошибка: пользователь не найден", show_alert=True)
            return
        
        if not school_service.school_exists(school_id):
            await callback.answer("❌ Ошибка: школа не найдена", show_alert=True)
            return
        
        # Переключаем подписку
        if user_service.is_subscribed(user.id, school_id):
            user_service.unsubscribe(user.id, school_id)
            await callback.answer("Отписано от школы", show_alert=False)
        else:
            user_service.subscribe(user.id, school_id)
            await callback.answer("Подписано на школу", show_alert=False)
        
        # Обновляем клавиатуру
        schools = school_service.get_all_schools()
        subscribed_ids = user_service.get_subscribed_school_ids(user.id)
        keyboard = get_schools_selection_keyboard(schools, subscribed_ids)
        
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        
    finally:
        db.close()


@router.callback_query(F.data == "save_subscriptions")
async def save_subscriptions(callback: CallbackQuery):
    """Сохранение выбранных подписок"""
    db = SessionLocal()
    try:
        user_service = UserService(db)
        school_service = SchoolService(db)
        
        user = user_service.get_user_by_telegram_id(callback.from_user.id)
        schools = school_service.get_all_schools()
        subscribed_ids = user_service.get_subscribed_school_ids(user.id)
        
        await callback.answer("✅ Подписки сохранены!", show_alert=True)
        
        # Возвращаем главное меню
        await callback.message.edit_text(
            f"✅ Ваши подписки сохранены!\n\n"
            f"Вы подписаны на {len(subscribed_ids)} школ(ы).\n\n"
            "Теперь вы будете получать новости и уведомления от выбранных школ.",
            reply_markup=get_main_keyboard()
        )
        
    finally:
        db.close()
