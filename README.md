# 🤖 МАКС - Бот для школ района

Многофункциональный Telegram-бот для информирования пользователей о новостях и событиях школ района с развитой админ-панелью.

## 📋 Основной функционал

### Для пользователей
- 🏫 **Мои школы** — подписка на интересующие школы
- 📰 **Последние новости** — просмотр новостей в хронологическом порядке
- 🔔 **Уведомления** — получение важной информации от выбранных школ

### Для администраторов
- 📝 **Создать пост** — публикация новостей с текстом, фото, видео, документами
- 📋 **Все посты** — управление (редактирование, удаление) опубликованными постами
- 🏫 **Управление школами** — добавление/удаление школ
- 🔔 **Уведомления** — отправка адресных сообщений подписчикам
- 📊 **Статистика** — просмотр статистики по школам

## 🚀 Технический стек

- **Язык:** Python 3.9+
- **Фреймворк:** aiogram 3.x (Telegram Bot API)
- **База данных:** SQLite (разработка) / PostgreSQL (production)
- **ORM:** SQLAlchemy
- **Дополнительно:** python-dotenv, Pillow, requests

## 📁 Структура проекта

```
ARMO-School/
├── bot/
│   ├── __init__.py
│   ├── main.py                 # Точка входа приложения
│   ├── config.py               # Конфигурация
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── user_handlers.py    # Обработчики команд пользователя
│   │   ├── admin_handlers.py   # Обработчики админ-панели
│   │   └── callbacks.py        # Обработчики callback-кнопок
│   ├── services/
│   │   ├── __init__.py
│   │   ├── school_service.py   # Логика работы со школами
│   │   ├── post_service.py     # Логика работы с постами
│   │   ├── user_service.py     # Логика работы с пользователями
│   │   ├── stats_service.py    # Сбор статистики
│   │   └── notification_service.py  # Отправка уведомлений
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # Инициализация БД
│   │   ├── school.py           # Модель School
│   │   ├── user.py             # Модель User
│   │   ├── post.py             # Модель Post
│   │   ├── subscription.py     # Модель Subscription
│   │   └── statistics.py       # Модель Statistics
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── main_keyboard.py    # Главное меню
│   │   ├── user_keyboard.py    # Клавиатуры пользователя
│   │   └── admin_keyboard.py   # Клавиатуры администратора
│   ├── states/
│   │   ├── __init__.py
│   │   └── fsm_states.py       # FSM состояния для диалогов
│   └── utils/
│       ├── __init__.py
│       ├── auth.py             # Проверка доступа администратора
│       └── validators.py       # Валидация данных
├── database/
│   └── migrations/             # Миграции БД (если используется Alembic)
├── tests/
│   ├── __init__.py
│   ├── test_services.py
│   └── test_handlers.py
├── .env.example                # Пример переменных окружения
├── requirements.txt            # Зависимости проекта
├── docker-compose.yml          # Docker конфигурация
├── Dockerfile                  # Контейнеризация
└── setup.py                    # Setup для установки пакета
```

## 🔧 Установка и запуск

### 1. Предварительные требования
- Python 3.9+
- pip
- Git

### 2. Клонирование репозитория
```bash
git clone https://github.com/nsozukin0-hub/ARMO-School.git
cd ARMO-School
```

### 3. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 4. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 5. Конфигурация
Создайте файл `.env`:
```bash
cp .env.example .env
```

Отредактируйте `.env` и добавьте:
```
# Telegram Bot
BOT_TOKEN=your_bot_token_here

# Admin credentials
ADMIN_LOGIN=Admin
ADMIN_PASSWORD=armobotschool2026!

# Database
DATABASE_URL=sqlite:///school_bot.db
# Для PostgreSQL: postgresql://user:password@localhost/school_bot

# Logging
LOG_LEVEL=INFO
```

### 6. Инициализация базы данных
```bash
python -c "from bot.models.database import init_db; init_db()"
```

### 7. Запуск бота
```bash
python -m bot.main
```

## 🐳 Запуск в Docker

```bash
docker-compose up -d
```

## 📚 API и методы

### Основные сервисы

**SchoolService**
- `add_school(name)` — добавить школу
- `delete_school(school_id)` — удалить школу
- `get_all_schools()` — получить все школы
- `get_school(school_id)` — получить школу по ID

**UserService**
- `create_user(user_id, username)` — создать пользователя
- `subscribe(user_id, school_id)` — подписать на школу
- `unsubscribe(user_id, school_id)` — отписать от школы
- `get_subscriptions(user_id)` — получить подписки пользователя

**PostService**
- `create_post(school_id, text, media)` — создать пост
- `update_post(post_id, text, media)` — обновить пост
- `delete_post(post_id)` — удалить пост
- `get_posts(school_id, limit)` — получить посты школы

**NotificationService**
- `send_notification(school_id, message)` — отправить уведомление всем подписчикам

**StatisticsService**
- `get_school_stats(school_id)` — получить статистику школы
- `get_overall_stats()` — получить общую статистику

## 🔐 Безопасность

- Авторизация администратора через логин/пароль
- Защита от несанкционированного доступа к админ-панели
- Хеширование паролей (при необходимости)
- Валидация всех вводимых данных

## 📝 Лицензия

MIT License

## 👥 Поддержка

Для вопросов и предложений создавайте Issues в репозитории.

---

**Версия:** 1.0.0  
**Статус:** В разработке 🚀
