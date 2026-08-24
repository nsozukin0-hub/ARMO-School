import aiohttp
import asyncio
import logging
from typing import Optional, List, Dict, Any
from bot.config import BOT_TOKEN, MAX_API_URL

logger = logging.getLogger(__name__)


class MAXAPIClient:
    """Клиент для работы с MAX API"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = MAX_API_URL.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self._semaphore = asyncio.Semaphore(2)  # Лимит 2 запроса в секунду
    
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
        keyboard: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict]] = None,
        notify: bool = False
    ) -> Optional[str]:
        """
        Отправка сообщения пользователю через MAX API
        
        Args:
            user_id: ID пользователя в MAX
            text: Текст сообщения (до 4000 символов)
            keyboard: Inline клавиатура
            attachments: Список вложений
            notify: Флаг уведомления
            
        Returns:
            ID сообщения или None при ошибке
        """
        async with self._semaphore:
            try:
                session = await self._get_session()
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "user_id": user_id,
                    "text": text,
                    "notify": notify
                }
                
                if keyboard:
                    payload["inline_keyboard"] = keyboard
                
                if attachments:
                    payload["attachments"] = attachments
                
                url = f"{self.base_url}/api/v1/messages/send"
                
                logger.info(f"Отправка сообщения пользователю {user_id}: {text[:50]}...")
                async with session.post(url, json=payload, headers=headers) as response:
                    response_data = await response.json()
                    logger.info(f"Ответ MAX API: {response.status} - {response_data}")
                    
                    if response.status in (200, 201):
                        return response_data.get("message_id") or response_data.get("id")
                    else:
                        logger.error(f"Ошибка отправки сообщения: {response.status} - {response_data}")
                        return None
                        
            except Exception as e:
                logger.error(f"Исключение при отправке сообщения: {e}", exc_info=True)
                return None
    
    async def upload_media(self, file_path: str, media_type: str = "image") -> Optional[str]:
        """
        Загрузка медиафайла в MAX
        
        Args:
            file_path: Путь к файлу
            media_type: Тип медиа (image, video, audio, file)
            
        Returns:
            Token для использования в attachments или None
        """
        try:
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            url = f"{self.base_url}/api/v1/uploads"
            
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=file_path.split('/')[-1])
                data.add_field('type', media_type)
                
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("token")
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка загрузки медиа: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Исключение при загрузке медиа: {e}", exc_info=True)
            return None
    
    async def edit_message(
        self,
        message_id: str,
        text: Optional[str] = None,
        keyboard: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """Редактирование сообщения в MAX"""
        async with self._semaphore:
            try:
                session = await self._get_session()
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                
                payload = {}
                if text:
                    payload["text"] = text
                if keyboard:
                    payload["inline_keyboard"] = keyboard
                if attachments:
                    payload["attachments"] = attachments
                
                url = f"{self.base_url}/api/v1/messages/{message_id}/edit"
                
                async with session.put(url, json=payload, headers=headers) as response:
                    return response.status in (200, 201)
                    
            except Exception as e:
                logger.error(f"Исключение при редактировании сообщения: {e}", exc_info=True)
                return False
    
    async def delete_message(self, message_id: str) -> bool:
        """Удаление сообщения из MAX"""
        try:
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            url = f"{self.base_url}/api/v1/messages/{message_id}"
            
            async with session.delete(url, headers=headers) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Исключение при удалении сообщения: {e}", exc_info=True)
            return False
    
    async def send_answer(self, callback_id: str, text: str) -> bool:
        """Ответ на callback после нажатия кнопки в MAX"""
        try:
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "callback_id": callback_id,
                "text": text
            }
            
            url = f"{self.base_url}/api/v1/callbacks/answer"
            
            async with session.post(url, json=payload, headers=headers) as response:
                return response.status in (200, 201)
                
        except Exception as e:
            logger.error(f"Исключение при отправке ответа на callback: {e}", exc_info=True)
            return False
    
    async def edit_message_keyboard(
        self,
        message_id: str,
        keyboard: Dict[str, Any]
    ) -> bool:
        """Редактирование клавиатуры сообщения"""
        return await self.edit_message(message_id=message_id, keyboard=keyboard)
