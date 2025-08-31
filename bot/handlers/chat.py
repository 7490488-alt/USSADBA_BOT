from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from services.llm import YandexLLM
from services.history import load_history, save_history
from services.cache import cache
from utils.helpers import get_cache_key
from config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from services.llm import YandexLLM
from services.history import load_history, save_history
from services.cache import cache
from utils.helpers import get_cache_key
from config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        logger.warning("Пустое сообщение или отсутствует текст")
        return

    user_message = update.message.text.strip()
    if not user_message:
        logger.warning("Пустое сообщение после очистки")
        return

    logger.info(f"Получено сообщение: {user_message}")

    # ... остальной код без изменений ...
    # Проверяем, не является ли сообщение командой смены контекста
    if user_message.lower() in ["сменить контекст", "другой вопрос", "новый вопрос"]:
        if "history" in context.chat_data:
            del context.chat_data["history"]
        if "selected_prompt" in context.user_data:
            del context.user_data["selected_prompt"]
        if "prompt_confirmed" in context.user_data:
            del context.user_data["prompt_confirmed"]
        
        keyboard = [["📄 Документы", "💬 Задать вопрос"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Контекст сброшен. Выберите действие:",
            reply_markup=reply_markup
        )
        return

    # Определяем интент
    if "llm_service" not in context.application.bot_data:
        logger.error("❌ llm_service не инициализирован")
        await update.message.reply_text("Извините, сервис ИИ недоступен.")
        return

    llm_service = context.application.bot_data["llm_service"]
    prompt_type = llm_service.determine_intent(user_message)
    
    # Сохраняем выбранный промпт в user_data для последующего использования
    context.user_data["selected_prompt"] = prompt_type

    # Показываем пользователю определенный контекст (только при первом сообщении)
    if "prompt_confirmed" not in context.user_data:
        prompt_names = {
            "buyer": "🏡 Участок для жизни",
            "investor": "💼 Инвестиции", 
            "partner": "🤝 Партнёрство",
            "general": "ℹ️ О проекте"
        }
        
        await update.message.reply_text(
            f"Я понял, что вас интересует: *{prompt_names[prompt_type]}*.\n"
            "Задавайте ваш вопрос! Если хотите сменить тему, напишите 'Сменить контекст'.",
            parse_mode="Markdown"
        )
        context.user_data["prompt_confirmed"] = True

    # Работа с историей
    chat_id = update.effective_chat.id
    if "history" not in context.chat_data:
        loaded_history = await load_history(chat_id)
        sys_prompt = llm_service.select_prompt(prompt_type)
        # Добавляем системный промпт только если его еще нет в истории
        if not any(msg.get("role") == "system" for msg in loaded_history):
            loaded_history.insert(0, {"role": "system", "content": sys_prompt})
        context.chat_data["history"] = loaded_history

    history = context.chat_data["history"]
    
    # Обновляем системный промпт если он изменился
    current_sys_prompt = llm_service.select_prompt(prompt_type)
    if history and history[0].get("role") == "system":
        history[0]["content"] = current_sys_prompt
    else:
        history.insert(0, {"role": "system", "content": current_sys_prompt})

    # Проверяем кэш
    cache_key = get_cache_key(user_message, history)
    if cache_key and (cached := await cache.get(cache_key)):
        response = cached
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": response})
        
        # Сохраняем историю асинхронно без блокировки
        asyncio.create_task(save_history(chat_id, history))
        
        await update.message.reply_text(response)
        return

    # Делаем запрос к LLM
    try:
        response = await llm_service.chat(user_message, history, prompt_type)
    except Exception as e:
        logger.error(f"Ошибка при запросе к LLM: {e}", exc_info=True)
        await update.message.reply_text("Извините, произошла ошибка при генерации ответа.")
        return

    # Обновляем историю
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": response})

    # Ограничиваем размер истории
    max_len = settings.max_history_pairs * 2 + 1  # +1 для системного промпта
    if len(history) > max_len:
        # Сохраняем системный промпт и последние сообщения
        system_prompt = history[0]
        recent = [msg for msg in history if msg["role"] in ("user", "assistant")][-max_len+1:]
        context.chat_data["history"] = [system_prompt] + recent

    # Асинхронно сохраняем историю и кэш
    asyncio.create_task(save_history(chat_id, context.chat_data["history"]))
    if cache_key:
        asyncio.create_task(cache.set(cache_key, response))

    await update.message.reply_text(response)