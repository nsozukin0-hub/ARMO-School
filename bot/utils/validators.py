def validate_school_name(name: str) -> bool:
    """Валидация названия школы"""
    if not name or len(name.strip()) == 0:
        return False
    if len(name) > 255:
        return False
    return True


def validate_post_text(text: str) -> bool:
    """Валидация текста поста"""
    if text is None:
        return True  # Текст может быть пустым (только медиа)
    if len(text) > 4096:  # Ограничение Telegram
        return False
    return True


def validate_notification_message(message: str) -> bool:
    """Валидация сообщения уведомления"""
    if not message or len(message.strip()) == 0:
        return False
    if len(message) > 4096:
        return False
    return True
