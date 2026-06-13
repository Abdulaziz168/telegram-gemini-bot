"""
Main entry point for the Telegram bot.
Multimodal Gemini AI + Groq STT bot.
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import Config
from handlers import message_router, voice_router
from database import ChatHistoryDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Actions to perform on bot startup."""
    logger.info("🚀 Bot ishga tushmoqda...")
    
    # Initialize database
    db = ChatHistoryDB()
    logger.info("✅ Ma'lumotlar bazasi tayyor")
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"✅ Bot tayyor: @{bot_info.username}")


async def on_shutdown(bot: Bot):
    """Actions to perform on bot shutdown."""
    logger.info("🛑 Bot to'xtatilmoqda...")
    await bot.session.close()
    logger.info("✅ Bot to'xtatildi")


async def main():
    """Main function to run the bot."""
    try:
        # Validate configuration
        Config.validate()
        logger.info("✅ Konfiguratsiya tekshirildi")
        
    except ValueError as e:
        logger.error(f"❌ Konfiguratsiya xatosi: {e}")
        sys.exit(1)
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=Config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(message_router)
    dp.include_router(voice_router)
    
    # Register startup and shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start polling
    try:
        logger.info("📡 Polling boshlanmoqda...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ Bot ishga tushirishda xatolik: {e}")
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Bot foydalanuvchi tomonidan to'xtatildi")
    except Exception as e:
        logger.error(f"❌ Kutilmagan xatolik: {e}")
        sys.exit(1)
