"""Keyboard for selecting a subscription tariff."""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.callback_data import SubscriptionCB
from models.subscription import SUBSCRIPTION_PLANS


def plans_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for plan in SUBSCRIPTION_PLANS:
        builder.button(
            text=f"{plan.title} — {plan.stars_price} ⭐",
            callback_data=SubscriptionCB(plan_id=plan.plan_id),
        )
    builder.adjust(1)
    return builder.as_markup()