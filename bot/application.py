from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.handlers.start import start
from bot.handlers.docs import docs
from bot.handlers.chat import chat
from bot.handlers.other import handle_other
from utils.logger import setup_logger

logger = setup_logger()

def create_application(token: str):
    # Создаем приложение
    application = Application.builder().token(token).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("docs", docs))

    # Обработчик для кнопок меню
    application.add_handler(
        MessageHandler(
            filters.TEXT & (
                filters.Regex(r"^(📄 Документы|📝 Бизнес-план|📊 Финансовая модель|💬 Задать вопрос)$") |
                filters.Regex(r"^(Документы|Бизнес-план|Финансовая модель|Задать вопрос)$")
            ),
            docs
        )
    )

    # Обработчик для кнопок с документами (начинающихся с 📎)
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r"^📎 "),
            docs
        )
    )

    # Обработчик для обычных текстовых сообщений
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    # Обработчик для всех остальных типов сообщений
    application.add_handler(
        MessageHandler(
            filters.ALL,
            handle_other
        )
    )

    # Обработчик ошибок
    application.add_error_handler(
        lambda update, context: logger.error(f"Ошибка: {context.error}", exc_info=True)
    )

    logger.info("✅ Обработчики зарегистрированы")
    return application