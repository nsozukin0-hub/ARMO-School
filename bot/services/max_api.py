import aiohttp
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from bot.config import BOT_TOKEN


class MAXAPIClient:
    """Клиент для работы с API МАКС (platform-api2.max.ru)"""
    
    BASE_URL = "https://platform-api2.max.ru"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Получить или создать HTTP сессию"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Закрыть HTTP сессию"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Получить заголовки для запросов"""
        return {
            "Authorization": self.access_token,
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self,
        user_id: Optional[int] = None,
        chat_id: Optional[int] = None,
        text: str = "",
        attachments: Optional[List[Dict[str, Any]]] = None,
        notify: bool = True,
        format_type: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Отправить сообщение пользователю или в чат
        
        Args:
            user_id: ID пользователя MAX
            chat_id: ID чата MAX
            text: Текст сообщения (до 4000 символов)
            attachments: Список медиа-вложений
            notify: Флаг уведомления
            format_type: Формат текста (markdown/html)
        
        Returns:
            Ответ от API
        """
        if not user_id and not chat_id:
            raise ValueError("Необходимо указать user_id или chat_id")
        
        session = await self.get_session()
        url = f"{self.BASE_URL}/messages"
        
        # Формируем query параметры
        params = {}
        if user_id:
            params["user_id"] = user_id
        elif chat_id:
            params["chat_id"] = chat_id
        
        # Формируем тело запроса
        payload = {
            "text": text,
            "notify": notify,
            "format": format_type
        }
        
        if attachments:
            payload["attachments"] = attachments
        
        headers = self._get_headers()
        
        async with session.post(url, params=params, json=payload, headers=headers) as response:
            result = await response.json()
            
            if response.status != 200:
                raise Exception(f"Ошибка API МАКС: {response.status} - {result}")
            
            return result
    
    async def upload_media(
        self,
        file_path: str,
        media_type: str = "image"
    ) -> Dict[str, Any]:
        """
        Загрузить медиафайл для последующей отправки
        
        Args:
            file_path: Путь к файлу
            media_type: Тип медиа (image, video, audio, file)
        
        Returns:
            Токен загруженного файла
        """
        session = await self.get_session()
        url = f"{self.BASE_URL}/uploads"
        
        headers = {"Authorization": self.access_token}
        
        # Определяем тип контента
        content_type_map = {
            "image": "image/jpeg",
            "photo": "image/jpeg",
            "video": "video/mp4",
            "audio": "audio/mpeg",
            "file": "application/octet-stream",
            "document": "application/octet-stream"
        }
        
        content_type = content_type_map.get(media_type.lower(), "application/octet-stream")
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        data = aiohttp.FormData()
        data.add_field(
            'file',
            file_data,
            filename=file_path.split('/')[-1],
            content_type=content_type
        )
        
        async with session.post(url, data=data, headers=headers) as response:
            result = await response.json()
            
            if response.status != 200:
                raise Exception(f"Ошибка загрузки медиа: {response.status} - {result}")
            
            return result
    
    async def get_messages(
        self,
        user_id: Optional[int] = None,
        chat_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Получить сообщения
        
        Args:
            user_id: ID пользователя
            chat_id: ID чата
            limit: Количество сообщений
            offset: Смещение
        
        Returns:
            Список сообщений
        """
        session = await self.get_session()
        url = f"{self.BASE_URL}/messages"
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if user_id:
            params["user_id"] = user_id
        elif chat_id:
            params["chat_id"] = chat_id
        
        headers = self._get_headers()
        
        async with session.get(url, params=params, headers=headers) as response:
            result = await response.json()
            
            if response.status != 200:
                raise Exception(f"Ошибка получения сообщений: {response.status} - {result}")
            
            return result.get('items', [])
    
    async def edit_message(
        self,
        message_id: int,
        text: str = "",
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Редактировать сообщение
        
        Args:
            message_id: ID сообщения
            text: Новый текст
            attachments: Новые вложения
        
        Returns:
            Обновленное сообщение
        """
        session = await self.get_session()
        url = f"{self.BASE_URL}/messages"
        
        payload = {
            "message_id": message_id,
            "text": text
        }
        
        if attachments:
            payload["attachments"] = attachments
        
        headers = self._get_headers()
        
        async with session.put(url, json=payload, headers=headers) as response:
            result = await response.json()
            
            if response.status != 200:
                raise Exception(f"Ошибка редактирования: {response.status} - {result}")
            
            return result
    
    async def delete_message(self, message_id: int) -> bool:
        """
        Удалить сообщение
        
        Args:
            message_id: ID сообщения
        
        Returns:
            True если успешно
        """
        session = await self.get_session()
        url = f"{self.BASE_URL}/messages"
        
        payload = {"message_id": message_id}
        headers = self._get_headers()
        
        async with session.delete(url, json=payload, headers=headers) as response:
            if response.status != 200:
                result = await response.json()
                raise Exception(f"Ошибка удаления: {response.status} - {result}")
            
            return True
    
    async def send_answer(
        self,
        callback_query_id: str,
        text: str = ""
    ) -> Dict[str, Any]:
        """
        Ответ на callback запрос (нажатие кнопки)
        
        Args:
            callback_query_id: ID callback запроса
            text: Текст ответа
        
        Returns:
            Ответ от API
        """
        session = await self.get_session()
        url = f"{self.BASE_URL}/answers"
        
        payload = {
            "callback_query_id": callback_query_id,
            "text": text
        }
        
        headers = self._get_headers()
        
        async with session.post(url, json=payload, headers=headers) as response:
            result = await response.json()
            
            if response.status != 200:
                raise Exception(f"Ошибка ответа на callback: {response.status} - {result}")
            
            return result


# Глобальный экземпляр клиента
max_client = MAXAPIClient(BOT_TOKEN)
