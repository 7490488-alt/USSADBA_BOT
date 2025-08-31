# main.py
import sys
import os
import asyncio
import logging
from typing import Optional

# Добавляем корневую папку в начало sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем правильный event loop для Windows
if sys.platform == 'win32':
    try:
        from asyncio import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
        print("✅ Установлен WindowsSelectorEventLoopPolicy")
    except Exception as e:
        print(f"⚠️ Не удалось установить event loop policy: {e}")

# Сначала — настройка логирования
from utils.logger import setup_logger
logger = setup_logger()
logger.info("🔧 Логирование инициализировано")

# Подключаем nest_asyncio
try:
    import nest_asyncio
    nest_asyncio.apply()
    logger.info("✅ nest_asyncio применён — поддержка вложенных event loop")
except ImportError as e:
    logger.error("❌ nest_asyncio не установлен. Установите: pip install nest_asyncio")
    raise e

# Импортируем модули с обработкой ошибок
try:
    from bot.application import create_application
    logger.info("✅ Модуль application импортирован")
except Exception as e:
    logger.error(f"❌ Ошибка при импорте application: {e}", exc_info=True)
    raise e

try:
    from services.llm import YandexLLM
    logger.info("✅ Модуль llm импортирован")
except Exception as e:
    logger.error(f"❌ Ошибка при импорте llm: {e}", exc_info=True)
    raise e

try:
    from config import settings
    logger.info("✅ Настройки загружены")
except Exception as e:
    logger.error(f"❌ Ошибка при загрузке settings: {e}", exc_info=True)
    raise e


async def main():
    """Основная асинхронная функция запуска бота"""
    try:
        logger.info("🔧 Инициализация LLM...")
        llm_service = YandexLLM()
        logger.info("✅ LLM инициализирован")

        logger.info("🔧 Создание приложения...")
        application = create_application(settings.bot_token)
        logger.info("✅ Приложение создано")

        logger.info("🔧 Передача сервиса в bot_data...")
        application.bot_data["llm_service"] = llm_service
        logger.info("✅ Сервис передан")

        logger.info("🚀 Бот запущен. Ожидание сообщений...")
        await application.run_polling(
            close_loop=False
        )

    except Exception as e:
        logger.error(f"🔴 Ошибка при запуске: {e}", exc_info=True)


def run():
    """Запуск бота с правильным управлением event loop"""
    logger.info("🔄 Запуск функции run()...")
    
    loop: Optional[asyncio.AbstractEventLoop] = None
    try:
        loop = asyncio.get_running_loop()
        logger.warning("⚠️ Событийный цикл уже запущен. Используем существующий.")
    except RuntimeError as e:
        logger.debug(f"🔁 asyncio.get_running_loop() не запущен: {e}")
    except Exception as e:
        logger.error(f"🔴 Ошибка при проверке loop: {e}")
        return

    try:
        if loop and loop.is_running():
            task = loop.create_task(main())
            return task
        else:
            if loop is None:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"🔴 Ошибка при запуске loop: {e}", exc_info=True)


# 🔥 Самый первый лог — если его нет, значит ошибка до этого
logger.info("🏁 Начало запуска бота...")
if __name__ == "__main__":
    run()