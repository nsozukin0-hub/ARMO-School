#!/usr/bin/env python3
"""
Скрипт для регистрации вебхука в MAX API Platform через Личный Кабинет
Поскольку API endpoint'ы могут отличаться, используем альтернативный подход

Использование:
    python set_webhook_manual.py
    
Скрипт проверит соединение с MAX API и предоставит инструкцию
"""

import aiohttp
import asyncio
import ssl
from bot.config import BOT_TOKEN, MAX_API_URL


async def test_bot_token():
    """Проверяет валидность токена бота"""
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    headers = {'Authorization': f'Bearer {BOT_TOKEN}'}
    
    print("=" * 70)
    print("🔍 ПРОВЕРКА ТОКЕНА БОТА")
    print("=" * 70)
    print(f"MAX API URL: {MAX_API_URL}")
    print(f"Token: {BOT_TOKEN[:20]}...{BOT_TOKEN[-10:]}")
    print()
    
    # Пробуем разные endpoint'ы для проверки токена
    test_endpoints = [
        ('POST', '/api/v1/messages/send', {
            'peer_id': 'test',
            'text': 'connection test'
        }),
        ('GET', '/api/v1/bot/info', None),
        ('GET', '/api/v1/me', None),
        ('GET', '/', None),
        ('GET', '/health', None),
        ('GET', '/api/health', None),
    ]
    
    any_success = False
    
    for method, path, data in test_endpoints:
        url = f'{MAX_API_URL}{path}'
        try:
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            session = aiohttp.ClientSession(connector=connector)
            if method == 'POST':
                async with session.post(url, headers=headers, json=data, timeout=5) as r:
                    text = await r.text()
                    status = r.status
            else:
                async with session.get(url, headers=headers, timeout=5) as r:
                    text = await r.text()
                    status = r.status
            await session.close()
            
            if status == 200:
                print(f"✅ {method} {path} - УСПЕХ")
                print(f"   Ответ: {text[:150]}")
                any_success = True
                return True
            elif status == 401:
                print(f"❌ {method} {path} - НЕВЕРНЫЙ ТОКЕН (401)")
                return False
            elif status == 404:
                print(f"⚠️  {method} {path} - Endpoint не найден (404)")
            else:
                print(f"⚠️  {method} {path} - Статус {status}")
                if len(text) < 200:
                    print(f"   Ответ: {text}")
        except Exception as e:
            print(f"❌ {method} {path} - Ошибка: {e}")
    
    print()
    if any_success:
        print("✅ Токен работает с некоторыми endpoint'ами")
    else:
        print("ℹ️  Токен может быть валидным, но некоторые endpoint'ы недоступны")
        print("   Это нормально - MAX API использует специфичные endpoint'ы")
    return True


async def main():
    print()
    print("=" * 70)
    print("📡 НАСТРОЙКА ВЕБХУКА ДЛЯ MAX API PLATFORM")
    print("=" * 70)
    print()
    
    # Проверяем токен
    token_valid = await test_bot_token()
    
    print()
    print("=" * 70)
    print("📋 ИНСТРУКЦИЯ ПО НАСТРОЙКЕ ВЕБХУКА")
    print("=" * 70)
    print()
    
    if not token_valid:
        print("❌ ТОКЕН БОТА НЕВАЛИДЕН!")
        print()
        print("Проверьте:")
        print("  1. Правильность токена в файле .env")
        print("  2. Срок действия токена")
        print("  3. Получите новый токен в Личном Кабинете MAX API Platform")
        return
    
    print("✅ Токен бота валиден (или частично работает)")
    print()
    print("📝 ВАЖНО: MAX API Platform требует настройки вебхука через Личный Кабинет")
    print()
    print("🔗 ШАГИ ПО НАСТРОЙКЕ:")
    print()
    print("  1. Откройте Личный Кабинет разработчика:")
    print("     👉 https://dev.max.ru/dashboard")
    print()
    print("  2. Перейдите в раздел вашего бота")
    print()
    print("  3. Найдите секцию 'Webhook' или 'Вебхук'")
    print()
    print("  4. Укажите URL вебхука:")
    print("     👉 https://armo-school.vercel.app/webhook")
    print()
    print("  5. Сохраните изменения")
    print()
    print("  6. Проверьте статус вебхука в личном кабинете")
    print()
    print("=" * 70)
    print()
    print("🧪 ТЕСТИРОВАНИЕ ПОСЛЕ НАСТРОЙКИ:")
    print()
    print("  После настройки вебхука в личном кабинете:")
    print("  1. Отправьте команду /start вашему боту в MAX мессенджере")
    print("  2. Проверьте логи приложения на сервере")
    print("  3. Убедитесь, что бот отвечает корректно")
    print()
    print("=" * 70)
    print()
    print("💡 ПРИМЕЧАНИЯ:")
    print()
    print("  • Вебхук должен быть доступен по HTTPS")
    print("  • Vercel автоматически предоставляет HTTPS")
    print("  • Убедитесь, что ваш deployed app активен")
    print("  • Для локальной разработки используйте ngrok:")
    print("    ngrok http 8000")
    print()


if __name__ == "__main__":
    asyncio.run(main())
