from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
import os

class Settings(BaseSettings):
    bot_token: str = Field(..., description="Токен Telegram-бота")
    ya_api_key: str = Field(..., description="API-ключ Yandex Cloud")
    ya_folder_id: str = Field(..., description="ID облака в Yandex Cloud")

    documents_dir: str = "data/documents"
    history_dir: str = "data/history"
    logs_dir: str = "data/logs"
    cache_file: str = "data/cache.json"
    prompts_dir: str = "prompts"

    rate_limit_sec: int = 2
    max_history_pairs: int = 10  # Уменьшено для производительности
    max_cache_size: int = 1000

    llm_temperature: float = 0.3
    llm_max_tokens: int = 1000  # Увеличено для более полных ответов

    debug: bool = False
    use_cache: bool = True

    allowed_document_types: List[str] = ['.pdf', '.txt', '.docx', '.xlsx', '.pptx', '.jpg', '.png']

    admin_chat_id: Optional[int] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @validator('documents_dir', 'history_dir', 'logs_dir', 'prompts_dir', pre=True)
    def ensure_directories_exist(cls, v):
        """Создает директории при их инициализации"""
        os.makedirs(v, exist_ok=True)
        return v

    def ensure_directories(self):
        """Убедиться, что все директории существуют"""
        for path in [self.documents_dir, self.history_dir, self.logs_dir, self.prompts_dir]:
            os.makedirs(path, exist_ok=True)
            print(f"✅ Убедились, что существует: {path}")

    def get_log_file_path(self) -> str:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.logs_dir, f"bot_{date_str}.log")

    def is_valid(self) -> bool:
        try:
            self.ensure_directories()
            if not self.bot_token or len(self.bot_token) < 10:
                return False
            if not self.ya_api_key or len(self.ya_api_key) < 10:
                return False
            if not self.ya_folder_id or len(self.ya_folder_id) < 5:
                return False
            return True
        except Exception:
            return False

settings = Settings()
settings.ensure_directories()