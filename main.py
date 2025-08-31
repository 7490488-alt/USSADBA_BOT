import sys
import os
import asyncio
import logging
import signal

# Добавляем корневую папку в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования
from utils.logger import setup_logger
logger = setup_logger()
logger.info("🔧 Логирование инициализировано")

# Импортируем модули
from bot.application import create_application
from services.llm import YandexLLM
from services.cache import cache
from config import settings

# Глобальная переменная для хранения приложения
application = None

async def main():
    global application
    
    try:
        if not settings.is_valid():
            logger.error("❌ Неверная конфигурация. Проверьте настройки.")
            return

        # Инициализируем кэш
        await cache.initialize()
        logger.info("✅ Кэш инициализирован")
        
        # Создаем сервис LLM
        llm_service = YandexLLM()
        logger.info("✅ LLM сервис инициализирован")
        
        # Создаем приложение и передаем сервис LLM
        application = create_application(settings.bot_token)
        application.bot_data["llm_service"] = llm_service
        
        logger.info("🤖 Бот запущен. Ожидание сообщений...")
        
        # Запускаем бота с обработкой сигналов
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Бесконечный цикл ожидания
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"🔴 Фатальная ошибка: {e}", exc_info=True)
    finally:
        # Корректное завершение работы
        if application:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
        
        if 'llm_service' in locals():
            await llm_service.close()
            logger.info("✅ Ресурсы освобождены")

def handle_signal(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    logger.info(f"Получен сигнал {signum}, завершаем работу...")
    if application:
        # Создаем задачу для остановки приложения
        asyncio.create_task(application.stop())
    sys.exit(0)

if __name__ == "__main__":
    # Устанавливаем правильный event loop для Windows
    if sys.platform == 'win32':
        try:
            from asyncio import WindowsSelectorEventLoopPolicy
            asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
        except Exception as e:
            print(f"⚠️ Не удалось установить event loop policy: {e}")
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Запускаем приложение
    asyncio.run(main())