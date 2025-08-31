from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
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

def create_docs_keyboard():
    """Создает клавиатуру с доступными документами"""
    docs = get_available_documents()
    buttons = []
    
    # Добавляем кнопки для каждого документа
    for f in docs[:8]:
        doc_name = os.path.splitext(f)[0]
        buttons.append([KeyboardButton(f"📎 {doc_name}")])
    
    # Добавляем основные кнопки меню
    buttons.append([
        KeyboardButton("📄 Документы"),
        KeyboardButton("💬 Задать вопрос")
    ])
    buttons.append([
        KeyboardButton("📝 Бизнес-план"), 
        KeyboardButton("📊 Финансовая модель")
    ])
    
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def create_main_keyboard():
    """Создает основную клавиатуру меню"""
    keyboard = [
        ["📄 Документы", "💬 Задать вопрос"],
        ["📝 Бизнес-план", "📊 Финансовая модель"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

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
        await update.message.reply_text(
            "💬 Задайте любой вопрос о проекте!",
            reply_markup=create_main_keyboard()
        )
        return

    # Обработка кнопок с документами
    if text.startswith("📎 "):
        doc_name = text[2:]
        await send_document_by_name(update, context, doc_name)
        return

    await list_documents(update, context)

async def list_documents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    docs = get_available_documents()
    if not docs:
        await update.message.reply_text(
            "📂 Нет доступных документов.",
            reply_markup=create_main_keyboard()
        )
        return
    
    # Отправляем сообщение с клавиатурой
    msg = "📂 Доступные документы:\n" + "\n".join([f"• {os.path.splitext(f)[0]}" for f in docs])
    await update.message.reply_text(
        msg, 
        reply_markup=create_docs_keyboard()
    )

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
        try:
            with open(file_path, 'rb') as f:
                await update.message.reply_document(
                    f, 
                    caption="📘 Бизнес-план проекта",
                    reply_markup=create_docs_keyboard()
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке документа: {e}")
            await update.message.reply_text(
                "❌ Ошибка при отправке документа.",
                reply_markup=create_docs_keyboard()
            )
    else:
        await update.message.reply_text(
            "❌ Бизнес-план временно недоступен.",
            reply_markup=create_docs_keyboard()
        )

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
        try:
            with open(file_path, 'rb') as f:
                await update.message.reply_document(
                    f, 
                    caption="📊 Финансовая модель",
                    reply_markup=create_docs_keyboard()
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке документа: {e}")
            await update.message.reply_text(
                "❌ Ошибка при отправке документа.",
                reply_markup=create_docs_keyboard()
            )
    else:
        await update.message.reply_text(
            "❌ Финансовая модель временно недоступна.",
            reply_markup=create_docs_keyboard()
        )

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
                await update.message.reply_document(
                    f, 
                    caption=f"📎 {os.path.splitext(found)[0]}",
                    reply_markup=create_docs_keyboard()
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке документа: {e}")
            await update.message.reply_text(
                "❌ Ошибка при отправке документа.",
                reply_markup=create_docs_keyboard()
            )
    else:
        await update.message.reply_text(
            "❌ Документ не найден.",
            reply_markup=create_docs_keyboard()
        )