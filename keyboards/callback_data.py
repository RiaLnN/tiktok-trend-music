from aiogram.filters.callback_data import CallbackData


class SettingsCB(CallbackData, prefix="stg"):
    """Payload of the /settings menu callback buttons.

    action - what the button does ("menu", "region", "set_region", ...)
    value - additional value (region code, keyword, etc.)"""

    action: str
    value: str = ""


class SubscriptionCB(CallbackData, prefix="sub"):
    """Payload of subscription tariff selection buttons in /subscribe."""

    plan_id: str