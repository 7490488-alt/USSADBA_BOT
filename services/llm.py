import httpx
import os
import json
from typing import List, Dict
from config import settings
from utils.logger import setup_logger
from services.intent_recognizer import IntentRecognizer  # Добавляем импорт

logger = setup_logger()

class PromptManager:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir
        self.intent_recognizer = IntentRecognizer(prompts_dir)
        self._prompt_cache = {}  # Кэш промптов
        
    def get_prompt(self, intent_type: str) -> str:
        """Получить промпт по типу интента с кэшированием"""
        if intent_type in self._prompt_cache:
            return self._prompt_cache[intent_type]
            
        path = os.path.join(self.prompts_dir, f"{intent_type}.txt")
        try:
            with open(path, "r", encoding="utf-8") as f:
                prompt = f.read().strip()
                self._prompt_cache[intent_type] = prompt
                return prompt
        except FileNotFoundError:
            logger.warning(f"⚠️ Файл промпта не найден: {path}")
            # Fallback на general промпт
            return self.get_prompt("general")
    
    def determine_intent(self, user_message: str) -> str:
        """Определить интент пользовательского сообщения"""
        return self.intent_recognizer.determine_intent(user_message)

class YandexAPIClient:
    def __init__(self):
        self.api_key = settings.ya_api_key
        self.folder_id = settings.ya_folder_id
        self.model_uri = f"gpt://{self.folder_id}/yandexgpt/latest"  # Обновленный URI
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Закрыть HTTP-клиент"""
        await self.client.aclose()
    
    async def make_request(self, messages: List[Dict]) -> str:
        """Выполнить запрос к Yandex API"""
        payload = {
            "modelUri": self.model_uri,
            "completionOptions": {
                "temperature": settings.llm_temperature,
                "maxTokens": settings.llm_max_tokens
            },
            "messages": messages
        }

        try:
            response = await self.client.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["result"]["alternatives"][0]["message"]["text"].strip()
        except httpx.ConnectError:
            logger.error("🔴 Не удалось подключиться к Yandex LLM")
            return "Не удалось подключиться к ИИ. Проверьте интернет."
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 401:
                logger.error("🔴 Ошибка аутентификации: неверный YA_API_KEY")
                return "Ошибка: неверный API-ключ. Проверьте YA_API_KEY."
            elif status == 429:
                logger.error("🔴 Слишком много запросов к LLM")
                return "Слишком много запросов. Попробуйте позже."
            else:
                logger.error(f"🔴 Ошибка API: {e}")
                return "Ошибка при обработке запроса."
        except Exception as e:
            logger.error(f"🔴 Неизвестная ошибка: {e}", exc_info=True)
            return "Извините, произошла ошибка при генерации ответа."

class YandexLLM:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompt_manager = PromptManager(prompts_dir)
        self.api_client = YandexAPIClient()
        logger.info("✅ YandexLLM инициализирован")
    
    async def close(self):
        """Закрыть ресурсы"""
        await self.api_client.close()
    
    def select_prompt(self, prompt_name: str) -> str:
        """Выбрать промпт (совместимость со старым кодом)"""
        return self.prompt_manager.get_prompt(prompt_name)
    
    def determine_intent(self, user_message: str) -> str:
        """Определить интент (совместимость со старым кодом)"""
        return self.prompt_manager.determine_intent(user_message)
    
    async def chat(self, user_message: str, history: List[Dict[str, str]], prompt_type: str = "general") -> str:
        """Основной метод для общения с ИИ"""
        sys_prompt = self.select_prompt(prompt_type)
        messages = [{"role": "system", "text": sys_prompt}]
        
        for msg in history:
            if msg["role"] in ("user", "assistant"):
                messages.append({
                    "role": msg["role"],
                    "text": msg["content"]
                })
        
        messages.append({"role": "user", "text": user_message})
        
        return await self.api_client.make_request(messages)