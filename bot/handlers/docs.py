from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from config import settings
import os
import logging

logger = logging.getLogger(__name__)

def get_available_documents():
    if not os.path.exists(settings.documents_dir):
        logger.warning(f"Папка документов не существует: {settings.documents_dir}")
        return []
    
    documents = []
    for f in os.listdir(settings.documents_dir):
        file_path = os.path.join(settings.documents_dir, f)
        # Проверяем, что файл не пустой и с разрешенным расширением
        if (f.lower().endswith(tuple(settings.allowed_document_types)) and 
            os.path.isfile(file_path) and os.path.getsize(file_path) > 0):
            # Нормализуем имя файла (убираем расширение)
            name_without_ext = os.path.splitext(f)[0]
            documents.append((f, name_without_ext))
    
    # Убираем дубликаты по имени (без расширения)
    unique_documents = []
    seen_names = set()
    
    for file_path, name in documents:
        if name not in seen_names:
            seen_names.add(name)
            unique_documents.append(file_path)
    
    logger.info(f"Найдено документов: {unique_documents}")
    return unique_documents

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
        
        # Проверяем, что файл не пустой
        if os.path.getsize(file_path) == 0:
            logger.error(f"Файл бизнес-плана пустой: {file_path}")
            await update.message.reply_text(
                "❌ Бизнес-план временно недоступен (файл пустой).",
                reply_markup=create_docs_keyboard()
            )
            return
            
        try:
            with open(file_path, 'rb') as f:
                await update.message.reply_document(
                    f, 
                    caption="📘 Бизнес-план проекта",
                    reply_markup=create_docs_keyboard()
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке бизнес-плана: {e}")
            await update.message.reply_text(
                "❌ Ошибка при отправке бизнес-плана.",
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
        
        # Проверяем, что файл не пустой
        if os.path.getsize(file_path) == 0:
            logger.error(f"Файл финансовой модели пустой: {file_path}")
            await update.message.reply_text(
                "❌ Финансовая модель временно недоступна (файл пустой).",
                reply_markup=create_docs_keyboard()
            )
            return
            
        try:
            with open(file_path, 'rb') as f:
                await update.message.reply_document(
                    f, 
                    caption="📊 Финансовая модель",
                    reply_markup=create_docs_keyboard()
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке финансовой модели: {e}")
            await update.message.reply_text(
                "❌ Ошибка при отправке финансовой модели.",
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
    
    logger.info(f"Поиск документа: '{doc_name}'")
    logger.info(f"Доступные документы: {docs}")
    
    # Ищем документ по имени (без учета регистра и расширения)
    for f in docs:
        filename_without_ext = os.path.splitext(f)[0]
        logger.info(f"Проверка файла: '{f}' -> '{filename_without_ext}'")
        
        if doc_name.lower() == filename_without_ext.lower():
            found = f
            logger.info(f"Найден точный match: {found}")
            break
        elif doc_name.lower() in filename_without_ext.lower():
            found = f
            logger.info(f"Найден частичный match: {found}")
            break
    
    if found:
        file_path = os.path.join(settings.documents_dir, found)
        logger.info(f"Попытка отправить файл: {file_path}")
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            logger.error(f"Файл не существует: {file_path}")
            await update.message.reply_text(
                "❌ Файл не найден на сервере.",
                reply_markup=create_docs_keyboard()
            )
            return
            
        # Проверяем доступность файла для чтения
        if not os.access(file_path, os.R_OK):
            logger.error(f"Нет доступа к файлу: {file_path}")
            await update.message.reply_text(
                "❌ Нет доступа к файлу.",
                reply_markup=create_docs_keyboard()
            )
            return
            
        # Проверяем, что файл не пустой
        if os.path.getsize(file_path) == 0:
            logger.error(f"Файл пустой: {file_path}")
            await update.message.reply_text(
                "❌ Файл пустой и не может быть отправлен.",
                reply_markup=create_docs_keyboard()
            )
            return
            
        try:
            with open(file_path, 'rb') as f:
                await update.message.reply_document(
                    f, 
                    caption=f"📎 {os.path.splitext(found)[0]}",
                    reply_markup=create_docs_keyboard()
                )
            logger.info(f"Файл успешно отправлен: {found}")
        except Exception as e:
            logger.error(f"Ошибка при отправке документа {found}: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Ошибка при отправке документа.",
                reply_markup=create_docs_keyboard()
            )
    else:
        logger.warning(f"Документ не найден: '{doc_name}'")
        # Предлагаем альтернативы
        alt_docs = []
        for f in docs:
            if doc_name.lower() in os.path.splitext(f)[0].lower():
                alt_docs.append(os.path.splitext(f)[0])
        
        if alt_docs:
            msg = f"❌ Документ '{doc_name}' не найден.\n\nВозможно вы имели в виду:\n" + "\n".join([f"• {d}" for d in alt_docs])
        else:
            msg = f"❌ Документ '{doc_name}' не найден."
            
        await update.message.reply_text(
            msg,
            reply_markup=create_docs_keyboard()
        )