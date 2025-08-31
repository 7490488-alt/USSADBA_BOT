import os
import json
import aiofiles
import asyncio
from typing import Optional
from config import settings
from utils.logger import setup_logger

logger = setup_logger()

class FileCache:
    def __init__(self):
        self.filename = settings.cache_file
        self.lock = asyncio.Lock()
        self.max_size = 1000
        self._cache = {}
        self._loaded = False
        self._memory_cache = {}  # Быстрый in-memory кэш

    async def initialize(self):
        """Инициализировать кэш (должен быть вызван после запуска event loop)"""
        await self._load_cache()
        self._loaded = True

    async def _load_cache(self):
        async with self.lock:
            if not os.path.exists(self.filename):
                self._cache = {}
                return
                
            try:
                async with aiofiles.open(self.filename, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if not content.strip():
                        self._cache = {}
                    else:
                        self._cache = json.loads(content)
                        # Загружаем в memory cache
                        self._memory_cache = self._cache.copy()
            except Exception as e:
                logger.error(f"❌ Ошибка при загрузке кэша: {e}")
                self._cache = {}

    async def _save_cache(self):
        async with self.lock:
            try:
                os.makedirs(os.path.dirname(self.filename), exist_ok=True)
                async with aiofiles.open(self.filename, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(self._cache, ensure_ascii=False, indent=2))
            except Exception as e:
                logger.error(f"❌ Ошибка при сохранении кэша: {e}")

    async def get(self, key: str) -> Optional[str]:
        if not self._loaded:
            await self.initialize()
        
        # Сначала проверяем in-memory кэш
        if key in self._memory_cache:
            return self._memory_cache[key]
            
        return self._cache.get(key)

    async def set(self, key: str, value: str):
        if not self._loaded:
            await self.initialize()
            
        self._cache[key] = value
        self._memory_cache[key] = value  # Сохраняем в memory cache
        
        if len(self._cache) > self.max_size:
            # Удаляем самые старые ключи
            keys_to_remove = list(self._cache.keys())[:100]
            for k in keys_to_remove:
                del self._cache[k]
                if k in self._memory_cache:
                    del self._memory_cache[k]
                    
        # Сохраняем асинхронно без блокировки
        asyncio.create_task(self._save_cache())

    async def clear(self):
        if not self._loaded:
            await self.initialize()
            
        self._cache.clear()
        self._memory_cache.clear()
        await self._save_cache()

# Глобальный экземпляр кэша
cache = FileCache()