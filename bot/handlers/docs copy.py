from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.ext import CallbackQueryHandler
from config import settings
import os
import logging

logger = logging.getLogger(__name__)

def get_available_documents():
    if not os.path.exists(settings.documents_dir):
        return []
    return [
        f for f in os.listdir(settings.documents_dir)
        if f.lower().endswith(tuple(settings.allowed_document_types))
    ]

def create_keyboard():
    docs = get_available_documents()
    buttons = []
    
    # Добавляем кнопки для каждого документа
    for f in docs[:8]:
        doc_name = os.path.splitext(f)[0]
        buttons.append([f"📎 {doc_name}"])
    
    # Добавляем служебные кнопки
    buttons.append(["📄 Документы", "💬 Задать вопрос"])
    buttons.append(["📝 Бизнес-план", "📊 Финансовая модель"])
    
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

async def send_presentation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 Скачать презентацию", callback_data="download_presentation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Да, у меня есть презентация проекта. Нажмите кнопку ниже, чтобы получить её:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download_presentation":
        file_path = os.path.join(settings.documents_dir, "Презентация.pdf")
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                await query.message.reply_document(f, caption="📘 Презентация проекта")
        else:
            await query.message.reply_text("❌ Презентация временно недоступна.")

async def docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    logger.info(f"Обработка команды docs: {text}")

    # Обрабатываем оба варианта - с эмодзи и без
    if text in ["Документы", "📄 Документы"]:
        await list_documents(update, context)
        return

    if text in ["Бизнес-план", "📝 Бизнес-план"]:
        await send_business_plan(update, context)
        return

    if text in ["Финансовая модель", "📊 Финансовая модель"]:
        await send_financial_model(update, context)
        return

    if text in ["Задать вопрос", "💬 Задать вопрос"]:
        await update.message.reply_text("💬 Задайте любой вопрос о проекте!")
        return

    # Обработка кнопок с документами
    if text.startswith("📎 "):
        doc_name = text[2:]
        await send_document_by_name(update, context, doc_name)
        return
    
    # В функции docs() в docs.py
    if text == "📎 Презентация":
        await send_document_by_name(update, context, "Презентация")

        await list_documents(update, context)

async def list_documents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    docs = get_available_documents()
    if not docs:
        await update.message.reply_text("📂 Нет доступных документов.")
        return
    
    # Отправляем сообщение с клавиатурой
    msg = "📂 Доступные документы:\n" + "\n".join([f"• {os.path.splitext(f)[0]}" for f in docs])
    await update.message.reply_text(msg, reply_markup=create_keyboard())

async def send_business_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ищем файл бизнес-плана (с различными расширениями)
    docs = get_available_documents()
    business_plan = None
    
    for doc in docs:
        name = os.path.splitext(doc)[0].lower()
        if any(keyword in name for keyword in ["бизнес", "business", "план", "plan"]):
            business_plan = doc
            break
    
    if business_plan:
        file_path = os.path.join(settings.documents_dir, business_plan)
        with open(file_path, 'rb') as f:
            await update.message.reply_document(f, caption="📘 Бизнес-план проекта")
    else:
        await update.message.reply_text("❌ Бизнес-план временно недоступен.")

async def send_financial_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ищем файл финансовой модели (с различными расширениями)
    docs = get_available_documents()
    financial_model = None
    
    for doc in docs:
        name = os.path.splitext(doc)[0].lower()
        if any(keyword in name for keyword in ["финанс", "financial", "модель", "model"]):
            financial_model = doc
            break
    
    if financial_model:
        file_path = os.path.join(settings.documents_dir, financial_model)
        with open(file_path, 'rb') as f:
            await update.message.reply_document(f, caption="📊 Финансовая модель")
    else:
        await update.message.reply_text("❌ Финансовая модель временно недоступна.")

async def send_document_by_name(update: Update, context: ContextTypes.DEFAULT_TYPE, doc_name: str):
    docs = get_available_documents()
    found = None
    
    # Ищем документ по имени (без учета регистра и расширения)
    for f in docs:
        if doc_name.lower() in os.path.splitext(f)[0].lower():
            found = f
            break
    
    if found:
        file_path = os.path.join(settings.documents_dir, found)
        try:
            with open(file_path, 'rb') as f:
                await update.message.reply_document(f, caption=f"📎 {os.path.splitext(found)[0]}")
        except Exception as e:
            logger.error(f"Ошибка при отправке документа: {e}")
            await update.message.reply_text("❌ Ошибка при отправке документа.")
    else:
        await update.message.reply_text("❌ Документ не найден.", reply_markup=create_keyboard())