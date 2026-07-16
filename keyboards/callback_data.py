from aiogram.filters.callback_data import CallbackData


class SettingsCB(CallbackData, prefix="stg"):
    """Полезная нагрузка callback-кнопок меню /settings.

    action — что делает кнопка ("menu", "region", "set_region", ...)
    value  — дополнительное значение (код региона, ключевое слово и т.д.)
    """

    action: str
    value: str = ""


class SubscriptionCB(CallbackData, prefix="sub"):
    """Полезная нагрузка кнопок выбора тарифа подписки в /subscribe."""

    plan_id: str