from aiogram import Router

from handlers.admin import router as admin_router
from handlers.settings import router as settings_router
from handlers.start import router as start_router
from handlers.subscription import router as subscription_router
from handlers.trends import router as trends_router


def get_routers() -> list[Router]:
    return [admin_router, start_router, subscription_router, settings_router, trends_router]