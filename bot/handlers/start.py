# bot/handlers/start.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📄 Документы", "💬 Задать вопрос"],
        ["📝 Бизнес-план", "📊 Финансовая модель"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🏡 Добро пожаловать в проект *«Усадьба»*!\n\n"
        "Я — ваш цифровой помощник. Могу:\n"
        "• 📎 Прислать презентацию, бизнес-план и другие документы\n"
        "• 💬 Ответить на вопросы о проекте\n"
        "• 📊 Показать финансовую модель\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )