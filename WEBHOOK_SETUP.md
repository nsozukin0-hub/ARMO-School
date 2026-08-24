# Инструкция по настройке вебхука для MAX API Platform

## 📋 Предварительные требования

1. Установленный Python 3.8+
2. Установленные зависимости: `pip install -r requirements.txt`
3. Настроенный файл `.env` с токеном бота
4. Публичный URL для вебхука (сервер или ngrok для разработки)

## 🔧 Вариант 1: Локальная разработка с ngrok

### Шаг 1: Установите ngrok
```bash
# macOS
brew install ngrok

# Linux
snap install ngrok

# Или скачайте с https://ngrok.com/download
```

### Шаг 2: Запустите бота локально
```bash
python main.py
```

### Шаг 3: Запустите ngrok в другом терминале
```bash
ngrok http 8000
```

Вы получите URL вида: `https://abc123.ngrok.io`

### Шаг 4: Зарегистрируйте вебхук
```bash
python set_webhook.py set https://abc123.ngrok.io/webhook
```

## 🚀 Вариант 2: Продакшен на сервере

### Шаг 1: Разверните приложение на сервере
```bash
# Пример с Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Шаг 2: Настройте反向 прокси (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /webhook {
        proxy_pass http://127.0.0.1:8000/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Шаг 3: Зарегистрируйте вебхук
```bash
python set_webhook.py set https://your-domain.com/webhook
```

## 🧪 Проверка работы

### Получить информацию о вебхуке
```bash
python set_webhook.py info
```

### Удалить вебхук
```bash
python set_webhook.py delete
```

### Протестировать соединение
```bash
python set_webhook.py test
```

## ⚙️ Альтернативная настройка через панель MAX

Если скрипт не работает, настройте вебхук вручную:

1. Войдите в личный кабинет MAX API Platform
2. Перейдите в раздел "Боты" → Ваш бот
3. Нажмите "Настроить вебхук"
4. Укажите URL: `https://your-domain.com/webhook`
5. Сохраните настройки

## 📝 Endpoint'ы API

Скрипт пробует следующие endpoint'ы автоматически:

- `/api/v1/webhooks/register`
- `/api/v1/webhooks/set`
- `/api/webhooks/register`
- `/api/v1/bot/webhook/set`

## 🐛 Решение проблем

### Ошибка SSL
Скрипт уже настроен на игнорирование SSL ошибок для dev среды.

### Ошибка 404
Проверьте:
- Действителен ли токен бота в `.env`
- Правильность URL вебхука (должен заканчиваться на `/webhook`)
- Доступность вашего сервера из интернета

### Вебхук не получает события
1. Проверьте логи бота: `tail -f logs.txt`
2. Убедитесь, что порт 8000 открыт
3. Проверьте firewall настройки

## 📞 Поддержка

Документация MAX API: https://dev.max.ru/docs
