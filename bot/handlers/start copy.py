# bot/handlers/start.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
    if update.message is None:
        return

    keyboard = [
        ["📄 Презентация", "📝 Бизнес-план"],
        ["💬 Задать вопрос"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Я — ваш помощник из «Усадьба».\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )