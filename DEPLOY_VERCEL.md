# 🚀 Деплой на Vercel

## Изменения для логирования

### ✅ Выполнено:

1. **Обновлен `main.py`**:
   - Добавлено логирование в stdout/stderr для Vercel
   - Добавлены логи инициализации приложения
   - Добавлены логи health check запросов

2. **Обновлен `bot/handlers/webhook_handler.py`**:
   - Логирование входящих запросов (IP, заголовки)
   - Логирование callback'ов с callback_id
   - Логирование отправки сообщений в MAX API
   - Логирование сохранения подписок

3. **Создан `vercel.json`**:
   - Конфигурация для Python FastAPI
   - Настройка роутинга всех запросов на main.py
   - Версия Python 3.12

## 🔧 Как задеплоить

### Вариант 1: Через Vercel CLI (рекомендуется)

```bash
# 1. Авторизуйтесь в Vercel
vercel login

# 2. Задеплойте проект
vercel --prod
```

### Вариант 2: Через GitHub Integration

1. Залейте изменения в GitHub:
   ```bash
   git push origin your-branch
   ```

2. В личном кабинете Vercel:
   - Import Project → Выберите репозиторий ARMO-School
   - Framework Preset: Python
   - Root Directory: `/`
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: оставить пустым
   - Install Command: `pip install -r requirements.txt`

3. Добавьте переменные окружения в Vercel Dashboard:
   - `BOT_TOKEN` - токен вашего бота
   - `MAX_API_URL` - URL MAX API (https://platform-api2.max.ru)
   - `ADMIN_LOGIN` - логин администратора
   - `ADMIN_PASSWORD` - пароль администратора

## 📊 Просмотр логов

### Через CLI:
```bash
# Логи в реальном времени
vercel logs --follow

# Логи production деплоя
vercel logs --prod --follow
```

### Через веб-интерфейс:
1. Откройте https://vercel.com/dashboard
2. Выберите проект ARMO-School
3. Перейдите во вкладку "Logs"
4. Фильтруйте по уровням: INFO, ERROR, WARNING

## 🧪 Тестирование после деплоя

1. Проверьте health endpoint:
   ```
   https://armo-school.vercel.app/health
   ```

2. Проверьте главный endpoint:
   ```
   https://armo-school.vercel.app/
   ```

3. Настройте webhook в MAX API Platform:
   - URL: `https://armo-school.vercel.app/webhook`
   - Метод: POST

4. Отправьте `/start` боту в MAX мессенджере

5. Проверьте логи на наличие запросов

## ⚠️ Важные замечания

- Vercel не поддерживает постоянные соединения (WebSocket, long polling)
- База данных SQLite будет сбрасываться при каждом деплое
- Для продакшена рекомендуется использовать PostgreSQL
- Максимальное время выполнения функции: 10 секунд (Hobby), 60 секунд (Pro)

## 🔗 Полезные ссылки

- [Vercel Python Runtime](https://vercel.com/docs/runtimes/python)
- [Vercel Logs](https://vercel.com/docs/observability/logs)
- [FastAPI на Vercel](https://vercel.com/templates/python/fastapi-serverless)
