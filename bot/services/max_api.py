import aiohttp
import asyncio
from typing import Optional, List, Dict, Any
from bot.config import BOT_TOKEN, MAX_API_URL


class MAXAPIClient:
    """Клиент для работы с MAX API"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://platform-api2.max.ru"
        self.session: Optional[aiohttp.ClientSession] = None
        self._semaphore = asyncio.Semaphore(2)  # Лимит 2 сообщения в секунду
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Закрытие сессии"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def send_message(
        self,
        user_id: str,
        text: str,
        attachments: Optional[List[Dict]] = None,
        notify: bool = False
    ) -> Optional[str]:
        """
        Отправка сообщения пользователю
        
        Args:
            user_id: ID пользователя в MAX
            text: Текст сообщения (до 4000 символов)
            attachments: Список вложений
            notify: Флаг уведомления
            
        Returns:
            ID сообщения или None при ошибке
        """
        async with self._semaphore:
            try:
                session = await self._get_session()
                headers = {
                    "Authorization": self.token,
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "text": text,
                    "notify": notify
                }
                
                if attachments:
                    payload["attachments"] = attachments
                
                url = f"{self.base_url}/messages?user_id={user_id}"
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("message_id")
                    else:
                        error_text = await response.text()
                        print(f"Ошибка отправки сообщения: {response.status} - {error_text}")
                        return None
                        
            except Exception as e:
                print(f"Исключение при отправке сообщения: {e}")
                return None
    
    async def upload_media(self, file_path: str, media_type: str = "image") -> Optional[str]:
        """
        Загрузка медиафайла
        
        Args:
            file_path: Путь к файлу
            media_type: Тип медиа (image, video, audio, file)
            
        Returns:
            Token для использования в attachments или None
        """
        try:
            session = await self._get_session()
            headers = {
                "Authorization": self.token
            }
            
            url = f"{self.base_url}/uploads"
            
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=file_path.split('/')[-1])
                
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("token")
                    else:
                        error_text = await response.text()
                        print(f"Ошибка загрузки медиа: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            print(f"Исключение при загрузке медиа: {e}")
            return None
    
    async def edit_message(
        self,
        message_id: str,
        text: Optional[str] = None,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """Редактирование сообщения"""
        async with self._semaphore:
            try:
                session = await self._get_session()
                headers = {
                    "Authorization": self.token,
                    "Content-Type": "application/json"
                }
                
                payload = {}
                if text:
                    payload["text"] = text
                if attachments:
                    payload["attachments"] = attachments
                
                url = f"{self.base_url}/messages"
                
                async with session.put(url, json=payload, headers=headers) as response:
                    return response.status == 200
                    
            except Exception as e:
                print(f"Исключение при редактировании сообщения: {e}")
                return False
    
    async def delete_message(self, message_id: str) -> bool:
        """Удаление сообщения"""
        try:
            session = await self._get_session()
            headers = {
                "Authorization": self.token
            }
            
            url = f"{self.base_url}/messages?message_id={message_id}"
            
            async with session.delete(url, headers=headers) as response:
                return response.status == 200
                
        except Exception as e:
            print(f"Исключение при удалении сообщения: {e}")
            return False
    
    async def send_answer(self, callback_id: str, text: str) -> bool:
        """Ответ на callback после нажатия кнопки"""
        try:
            session = await self._get_session()
            headers = {
                "Authorization": self.token,
                "Content-Type": "application/json"
            }
            
            payload = {
                "callback_id": callback_id,
                "text": text
            }
            
            url = f"{self.base_url}/answers"
            
            async with session.post(url, json=payload, headers=headers) as response:
                return response.status == 200
                
        except Exception as e:
            print(f"Исключение при отправке ответа: {e}")
            return False
