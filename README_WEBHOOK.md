# 🎣 Настройка вебхука для School Bot

## ✅ Созданные файлы

1. **`set_webhook.py`** - Скрипт для управления вебхуком
2. **`WEBHOOK_SETUP.md`** - Полная инструкция по настройке

## 🚀 Быстрый старт

### Для локальной разработки:

```bash
# 1. Запустите бота
python main.py

# 2. В другом терминале запустите ngrok
ngrok http 8000

# 3. Скопируйте URL из ngrok (например, https://abc123.ngrok.io)
# 4. Зарегистрируйте вебхук
python set_webhook.py set https://abc123.ngrok.io/webhook
```

### Для продакшена:

```bash
# Замените your-domain.com на ваш домен
python set_webhook.py set https://your-domain.com/webhook
```

## 📋 Команды скрипта

| Команда | Описание |
|---------|----------|
| `python set_webhook.py set <URL>` | Зарегистрировать вебхук |
| `python set_webhook.py info` | Получить информацию о вебхуке |
| `python set_webhook.py delete` | Удалить вебхук |
| `python set_webhook.py test` | Протестировать соединение с MAX API |

## 🔍 Как это работает

Скрипт автоматически пробует несколько endpoint'ов MAX API:

1. `/api/v1/webhooks/register`
2. `/api/v1/webhooks/set`
3. `/api/webhooks/register`
4. `/api/v1/bot/webhook/set`

Это обеспечивает совместимость с разными версиями MAX API Platform.

## ⚠️ Важно

- Вебхук должен быть доступен из интернета (не localhost!)
- URL должен заканчиваться на `/webhook`
- SSL сертификат должен быть действительным (или используйте ngrok)

## 📖 Полная документация

См. файл `WEBHOOK_SETUP.md` для подробной инструкции.
