import hashlib
import json
from typing import List, Dict

def get_cache_key(user_message: str, history: List[Dict]) -> str:
    """
    Генерирует ключ кэша на основе пользовательского сообщения и истории.
    Учитывает только последние несколько сообщений для эффективности.
    """
    if not user_message:
        return None
    
    # Ограничиваем историю для ключа кэша (последние 3 пары вопрос-ответ + системный промпт)
    max_history_for_cache = 3 * 2 + 1  # 3 пары + системный промпт
    
    if len(history) > max_history_for_cache:
        relevant_history = history[:1] + history[-max_history_for_cache+1:]
    else:
        relevant_history = history
    
    # Создаем словарь для хэширования
    data_to_hash = {
        "user_message": user_message,
        "history": relevant_history
    }
    
    # Преобразуем в JSON и хэшируем
    json_str = json.dumps(data_to_hash, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(json_str.encode('utf-8')).hexdigest()

def format_file_size(size_bytes: int) -> str:
    """Форматирует размер файла в читаемом виде"""
    if size_bytes == 0:
        return "0B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    import math
    digit_group = int(math.floor(math.log(size_bytes, 1024)))
    return f"{size_bytes / (1024 ** digit_group):.2f} {units[digit_group]}"