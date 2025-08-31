from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для неподдерживаемых типов сообщений"""
    if update.message:
        await update.message.reply_text(
            "Извините, я пока могу обрабатывать только текстовые сообщения. "
            "Попробуйте отправить текстовый запрос или воспользуйтесь кнопками меню."
        )
    logger.warning(f"Получен неподдерживаемый тип сообщения: {update}")