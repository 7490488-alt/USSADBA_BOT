import os
import json
from typing import Dict, List
from config import settings
from utils.logger import setup_logger

logger = setup_logger()

class IntentRecognizer:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir
        self.prompt_map = self._load_prompt_map()
        
    def _load_prompt_map(self) -> Dict[str, List[str]]:
        try:
            map_path = os.path.join(self.prompts_dir, "prompt_map.json")
            if os.path.exists(map_path):
                with open(map_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"❌ Не удалось загрузить prompt_map.json: {e}")
        
        # Fallback mapping
        return {
            "buyer": ["купить", "участок", "земля", "дом", "цена", "стоимость", "покупка"],
            "investor": ["инвест", "доход", "прибыль", "рентабельность", "окупаемость", "вложение"],
            "partner": ["партнёр", "сотрудничество", "совместный", "предложение", "коллаборация"],
            "general": ["что", "расскажи", "проект", "информация", "подробнее", "общее"]
        }
    
    def determine_intent(self, user_message: str) -> str:
        user_message = user_message.lower().strip()
        if not user_message:
            return "general"
        
        scores = {}
        for intent_type, keywords in self.prompt_map.items():
            scores[intent_type] = sum(1 for kw in keywords if kw in user_message)
        
        # Если ни один интент не набрал очков, возвращаем general
        if max(scores.values()) == 0:
            return "general"
            
        return max(scores, key=scores.get)