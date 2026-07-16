"""Точка входа: собирает бота из конфига, сервисов и роутеров."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from handlers import get_routers
from services.tiktok_api import TikTokScraperClient
from services.trends_service import TrendsService
from storage.settings_repository import SettingsRepository
from storage.subscription_repository import SubscriptionRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    for router in get_routers():
        dp.include_router(router)

    repo = SettingsRepository(settings.SETTINGS_FILE)
    subscription_repo = SubscriptionRepository(settings.SUBSCRIPTIONS_FILE)
    api_client = TikTokScraperClient(api_key=settings.RAPIDAPI_KEY)
    trends_service = TrendsService(api_client)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Бот запущен")
        await dp.start_polling(
            bot,
            repo=repo,
            subscription_repo=subscription_repo,
            trends_service=trends_service,
        )
    finally:
        await trends_service.close()
        await api_client.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")