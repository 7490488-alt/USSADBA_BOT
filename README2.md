Задача: Перейти от одного статического промпта к умной системе сценариев, где бот определяет интерес пользователя (участок, инвестиции, общее описание) и подключает соответствующий промпт. Это не просто улучшение — это переход к сегментированному, целевому диалогу, как в продвинутых sales-ботах.

✅ Почему это круто?
🎯 Персонализация: бот отвечает по-разному в зависимости от цели пользователя
💬 Глубина диалога: можно вести разные сценарии (продажа, инвестиции, аренда)
📈 Конверсия: повышается шанс перевести пользователя в лид
🧠 Гибкость: легко добавлять новые сценарии (например, «аренда», «строительство»)
🚀 Как реализовать: пошаговый план

1. 📁 Создай папку с промптами
prompts/
├── general.txt           # Общее описание проекта
├── buyer.txt             # Покупка участка
├── investor.txt          # Инвестиции
├── partner.txt           # Партнёрство (опционально)
└── prompt_map.json       # Карта: ключевые слова → промпт

2. 📄 Примеры промптов:

prompts/buyer.txt
Ты — эксперт по продаже участков в «Усадьбе». Отвечай о земле, ценах, инфраструктуре, документах.  
Говори о выгоде, тишине, экологии.  
Не упоминай инвестиции, если не спрашивают.  
Максимум — 3 предложения.

prompts/investor.txt
Ты — финансовый консультант проекта «Усадьба». Говори о доходности, сроках окупаемости, рисках, ставках.  
Приводи примеры: "При аренде коттеджей — доход 8–12% годовых".  
Не углубляйся в эмоции, только факты и цифры.

prompts/general.txt
Ты — дружелюбный помощник «Усадьбы». Расскажи о проекте: 50 га, лес, озеро, экология, безопасность.  
Говори просто, с теплотой.  
Если пользователь уточняет — переключайся на buyer/investor.

3. 🔍 Определи интерес по ключевым словам
Создай файл в папке prompts/prompt_map.json:
{
  "buyer": ["участок", "купить", "земля", "дом", "семья", "жить", "дети", "поселиться"],
  "investor": ["инвестировать", "доход", "вложить", "рентабельность", "проект", "прибыль", "ROI", "бизнес"],
  "general": ["что это", "расскажи", "проект", "где", "кто", "как", "что такое"]
}

4. 🧠 Добавь логику выбора промпта в services/llm.py
# services/llm.py
import os
import json
from typing import Dict, List

class YandexLLM:
    def __init__(self):
        self.prompts_dir = "prompts"
        self.prompt_map = self._load_prompt_map()
        self.current_prompt = None
        self.current_prompt_name = None

    def _load_prompt_map(self) -> Dict[str, List[str]]:
        with open(os.path.join(self.prompts_dir, "prompt_map.json"), "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_prompt(self, name: str) -> str:
        path = os.path.join(self.prompts_dir, f"{name}.txt")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return self._load_prompt("general")

    def select_prompt(self, user_message: str) -> str:
        user_message = user_message.lower()
        for prompt_name, keywords in self.prompt_map.items():
            if any(kw in user_message for kw in keywords):
                return self._load_prompt(prompt_name)
        return self._load_prompt("general")  # по умолчанию

5. 🔄 Обнови метод chat — чтобы он выбирал промпт динамически
async def chat(self, user_message: str, history: List[Dict[str, str]]) -> str:
    # Выбираем промпт по сообщению
    sys_prompt = self.select_prompt(user_message)

    messages = [{"role": "system", "text": sys_prompt}]
    for msg in history:
        if msg["role"] in ("user", "assistant"):
            messages.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "text": msg["content"]
            })
    messages.append({"role": "user", "text": user_message})

    # ... остальной код запроса к LLM

6. 💡 Улучшение: запоминай выбор пользователя 
Добавь в context.user_data:
# В chat.py
if "selected_prompt" not in context.user_data:
    # Определяем по первому сообщению
    sys_prompt = llm_service.select_prompt(user_message)
    # Сохраняем тип
    for name in ["buyer", "investor", "general"]:
        if any(kw in user_message.lower() for kw in llm_service.prompt_map[name]):
            context.user_data["selected_prompt"] = name
            break
    else:
        context.user_data["selected_prompt"] = "general"
else:
    # Используем уже выбранный
    sys_prompt = llm_service._load_prompt(context.user_data["selected_prompt"])

7. 🎯 Дополнительно: предложи выбор
После /start бот может спросить:
await update.message.reply_text(
    "Чем я могу помочь?"
    "1. Хочу купить участок 🏡"
    "2. Интересуюсь инвестициями 💼"
    "3. Просто хочу узнать о проекте ℹ️",
    reply_markup=ReplyKeyboardMarkup([
        ["🏡 Участок", "💼 Инвестиции"],
        ["ℹ️ Расскажи о проекте"]
    ], resize_keyboard=True)
)
И сразу установить selected_prompt.

✅ Преимущества такого подхода
Множество промптов
Гибкость и точность ответов
Ключевые слова
Автоматическое определение цели
Запоминание выбора
Непрерывный диалог
Кнопки
Удобный UX
Легко масштабировать
Добавляй новые сценарии: "аренда", "строительство" и т.д.


🛠 Что добавить потом?
📊 Аналитика: сколько пользователей — покупатели vs инвесторы
🔄 Переключение сценария: "А если про инвестиции?"
📄 Генерация документов: "Создай мне коммерческое предложение"
🧩 Интеграция с CRM: отправка контакта менеджеру