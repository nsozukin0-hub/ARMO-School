#!/usr/bin/env python3
"""
Скрипт для регистрации вебхука в MAX API Platform
Запускается один раз после деплоя бота на сервер

Использование:
    python set_webhook.py set <webhook_url>  - Зарегистрировать вебхук
    python set_webhook.py info               - Получить информацию о вебхуке  
    python set_webhook.py delete             - Удалить вебхук

Примеры:
    python set_webhook.py set https://your-domain.com/webhook
    python set_webhook.py set https://abc123.ngrok.io/webhook
"""

import asyncio
import aiohttp
import ssl
from bot.config import BOT_TOKEN, MAX_API_URL


# Создаем SSL контекст без проверки сертификатов (для dev среды)
# В продакшене используйте ssl.create_default_context()
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


async def get_bot_info():
    """Получает информацию о боте"""
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print(f"🔍 Получаем информацию о боте...")
        
        # Пробуем разные варианты endpoint'ов
        endpoints = [
            f'{MAX_API_URL}/api/v1/bot/info',
            f'{MAX_API_URL}/api/v1/bot/me',
            f'{MAX_API_URL}/api/bot/info',
        ]
        
        for endpoint in endpoints:
            try:
                async with session.get(
                    endpoint,
                    headers={'Authorization': f'Bearer {BOT_TOKEN}'}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        username = data.get('username', data.get('name', 'unknown'))
                        bot_id = data.get('id', 'unknown')
                        print(f"✅ Бот найден: @{username} (ID: {bot_id})")
                        return data
                    elif resp.status != 404:
                        text = await resp.text()
                        print(f"⚠️  Статус {resp.status}: {text}")
            except Exception as e:
                print(f"⚠️  Ошибка {endpoint}: {e}")
        
        # Если все endpoint'ы не сработали, пробуем просто отправить тестовое сообщение
        print("ℹ️  Не удалось получить информацию о боте через API")
        print("   Продолжаем с известным токеном...")
        return None


async def set_webhook(webhook_url: str):
    """Регистрирует вебхук в MAX API Platform"""
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Получаем информацию о боте (не критично если не получится)
        await get_bot_info()
        
        print(f"\n📡 Регистрируем вебхук: {webhook_url}")
        
        # Пробуем разные варианты endpoint'ов для регистрации вебхука
        endpoints = [
            f'{MAX_API_URL}/api/v1/webhooks/register',
            f'{MAX_API_URL}/api/v1/webhooks/set',
            f'{MAX_API_URL}/api/webhooks/register',
            f'{MAX_API_URL}/api/v1/bot/webhook/set',
        ]
        
        for endpoint in endpoints:
            try:
                async with session.post(
                    endpoint,
                    headers={
                        'Authorization': f'Bearer {BOT_TOKEN}',
                        'Content-Type': 'application/json'
                    },
                    json={'url': webhook_url}
                ) as resp:
                    result = await resp.json()
                    
                    if resp.status in (200, 201, 204):
                        print(f"✅ Вебхук успешно зарегистрирован!")
                        print(f"📋 Ответ API: {result}")
                        return True
                    else:
                        print(f"⚠️  Статус {resp.status}: {result}")
            except Exception as e:
                print(f"⚠️  Ошибка {endpoint}: {e}")
        
        print("\n❌ Не удалось зарегистрировать вебхук через стандартные endpoint'ы")
        print("\n💡 Возможные решения:")
        print("   1. Проверьте документацию MAX API: https://dev.max.ru/docs")
        print("   2. Убедитесь, что токен бота действителен")
        print("   3. Попробуйте зарегистрировать вебхук через панель управления MAX")
        print("\n📝 Альтернативный вариант:")
        print("   Настройте вебхук вручную в личном кабинете MAX API Platform")
        print(f"   URL вебхука: {webhook_url}")
        return False


async def get_webhook_info():
    """Получает информацию о текущем вебхуке"""
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print(f"📡 Получаем информацию о вебхуке...")
        
        endpoints = [
            f'{MAX_API_URL}/api/v1/webhooks/info',
            f'{MAX_API_URL}/api/v1/webhooks/get',
            f'{MAX_API_URL}/api/v1/bot/webhook/info',
        ]
        
        for endpoint in endpoints:
            try:
                async with session.get(
                    endpoint,
                    headers={'Authorization': f'Bearer {BOT_TOKEN}'}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"✅ Информация о вебхуке:")
                        print(f"📋 {data}")
                        return data
                    elif resp.status != 404:
                        text = await resp.text()
                        print(f"⚠️  Статус {resp.status}: {text}")
            except Exception as e:
                print(f"⚠️  Ошибка {endpoint}: {e}")
        
        print("❌ Не удалось получить информацию о вебхуке")
        return None


async def delete_webhook():
    """Удаляет текущий вебхук"""
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print(f"🗑️  Удаляем вебхук...")
        
        endpoints = [
            f'{MAX_API_URL}/api/v1/webhooks/unregister',
            f'{MAX_API_URL}/api/v1/webhooks/delete',
            f'{MAX_API_URL}/api/v1/bot/webhook/delete',
        ]
        
        for endpoint in endpoints:
            try:
                async with session.delete(
                    endpoint,
                    headers={'Authorization': f'Bearer {BOT_TOKEN}'}
                ) as resp:
                    if resp.status in (200, 201, 204):
                        data = await resp.json() if resp.status != 204 else {}
                        print(f"✅ Вебхук удален!")
                        print(f"📋 {data}")
                        return True
                    elif resp.status != 404:
                        text = await resp.text()
                        print(f"⚠️  Статус {resp.status}: {text}")
            except Exception as e:
                print(f"⚠️  Ошибка {endpoint}: {e}")
        
        print("❌ Не удалось удалить вебхук")
        return False


async def test_connection():
    """Тестирует соединение с MAX API"""
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print(f"🧪 Тестируем соединение с MAX API...")
        print(f"   URL: {MAX_API_URL}")
        print(f"   Token: {BOT_TOKEN[:20]}...")
        
        try:
            async with session.get(
                f'{MAX_API_URL}/health',
                headers={'Authorization': f'Bearer {BOT_TOKEN}'}
            ) as resp:
                print(f"✅ Health check: {resp.status}")
        except Exception as e:
            print(f"⚠️  Health check failed: {e}")
        
        # Пробуем просто сделать запрос к корню API
        try:
            async with session.get(
                MAX_API_URL,
                headers={'Authorization': f'Bearer {BOT_TOKEN}'}
            ) as resp:
                print(f"✅ Root endpoint: {resp.status}")
        except Exception as e:
            print(f"⚠️  Root endpoint failed: {e}")


async def main():
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "set" and len(sys.argv) > 2:
            webhook_url = sys.argv[2]
            await set_webhook(webhook_url)
        elif command == "info":
            await get_webhook_info()
        elif command == "delete":
            await delete_webhook()
        elif command == "test":
            await test_connection()
        else:
            print(__doc__)
    else:
        # Показать справку
        print(__doc__)
        print("\n" + "="*60)
        await test_connection()


if __name__ == "__main__":
    asyncio.run(main())
