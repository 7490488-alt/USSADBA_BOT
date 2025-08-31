import os
import json
import aiofiles
from config import settings
from utils.logger import setup_logger

logger = setup_logger()

async def load_history(chat_id: int) -> list:
    path = os.path.join(settings.history_dir, f"chat_{chat_id}.json")
    if os.path.exists(path):
        try:
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                content = await f.read()
                return json.loads(content) if content.strip() else []
        except Exception as e:
            logger.error(f"Ошибка при загрузке истории: {e}")
    return []

async def save_history(chat_id: int, history: list):
    path = os.path.join(settings.history_dir, f"chat_{chat_id}.json")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(history, ensure_ascii=False, indent=2))
    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении истории: {e}")