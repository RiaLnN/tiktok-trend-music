"""Subscription and payment via Telegram Stars.

Payment flow:
  /subscribe -> rate button -> send_invoice (currency="XTR")
  -> pre_checkout_query (must confirm within 10 seconds)
  -> successful_payment (renew subscription in SubscriptionRepository)

No additional payment provider settings in BotFather for Stars
no need - provider_token is always an empty string for them."""
import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

from keyboards.callback_data import SubscriptionCB
from keyboards.subscription_kb import plans_kb
from models.subscription import find_plan
from storage.subscription_repository import SubscriptionRepository
from utils.formatting import format_subscription_status

logger = logging.getLogger(__name__)
router = Router(name="subscription")

# invoice_payload is limited to 1-128 bytes and is not shown to the user -
# We put in it only the tariff id with a small prefix for the readability of the logs.
_PAYLOAD_PREFIX = "sub_"


async def ensure_active_subscription(message: Message, subscription_repo: SubscriptionRepository) -> bool:
    """Checking access for paid teams (see handlers/trends.py).

    Returns True if execution of the handler can continue. If subscriptions
    no - it explains to the user what to do and returns False."""
    if not message.from_user: return False
    if await subscription_repo.is_active(message.from_user.id):
        return True

    await message.answer("🔒 Поиск трендов доступен по подписке.\nОформить: /subscribe")
    return False


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message, subscription_repo: SubscriptionRepository) -> None:
    if not message.from_user: return
    sub = await subscription_repo.get(message.from_user.id)
    await message.answer(
        f"{format_subscription_status(sub)}\n\n"
        "Выберите тариф — оплата происходит внутри Telegram через Stars ⭐:",
        reply_markup=plans_kb(),
    )


@router.message(Command("mysub"))
async def cmd_mysub(message: Message, subscription_repo: SubscriptionRepository) -> None:
    if not message.from_user: return
    sub = await subscription_repo.get(message.from_user.id)
    await message.answer(format_subscription_status(sub))


@router.message(Command("paysupport"))
async def cmd_paysupport(message: Message) -> None:
    # Telegram requires bots that accept payment for digital goods
    # and services, supported by the /paysupport team.
    await message.answer(
        "По вопросам оплаты Stars пишите в поддержку.\n"
        "Вернуть последний платёж самостоятельно можно командой /refund."
    )


@router.message(Command("refund"))
async def cmd_refund(message: Message, bot: Bot, subscription_repo: SubscriptionRepository) -> None:
    if not message.from_user: return
    
    sub = await subscription_repo.get(message.from_user.id)
    if not sub.last_charge_id:
        await message.answer("Не нахожу платежей Stars, которые можно вернуть через бота.")
        return

    await bot.refund_star_payment(
        user_id=message.from_user.id,
        telegram_payment_charge_id=sub.last_charge_id,
    )
    await subscription_repo.revoke(message.from_user.id)
    await message.answer("💫 Платёж возвращён, подписка отменена.")


@router.callback_query(SubscriptionCB.filter())
async def cb_buy_plan(callback: CallbackQuery, callback_data: SubscriptionCB, bot: Bot) -> None:
    plan = find_plan(callback_data.plan_id)
    if plan is None:
        await callback.answer("Такого тарифа больше нет, обновите список: /subscribe", show_alert=True)
        return

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=plan.title,
        description=plan.description,
        payload=f"{_PAYLOAD_PREFIX}{plan.plan_id}",
        currency="XTR",
        prices=[LabeledPrice(label=plan.title, amount=plan.stars_price)],
        provider_token="",  # for Telegram Stars the provider token must be empty
    )
    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery) -> None:
    plan_id = pre_checkout_query.invoice_payload.removeprefix(_PAYLOAD_PREFIX)
    if find_plan(plan_id) is None:
        await pre_checkout_query.answer(ok=False, error_message="Такого тарифа больше нет.")
        return
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, subscription_repo: SubscriptionRepository) -> None:
    payment = message.successful_payment
    if not payment: return
    plan = find_plan(payment.invoice_payload.removeprefix(_PAYLOAD_PREFIX))

    if plan is None:
        logger.error("Successful payment with unrecognized payload: %r", payment.invoice_payload)
        await message.answer("Оплата прошла, но тариф не распознан. Напишите /paysupport.")
        return

    if not message.from_user: return
    
    sub = await subscription_repo.extend(
        message.from_user.id,
        plan.days,
        source="stars",
        charge_id=payment.telegram_payment_charge_id,
    )
    await message.answer(
        f"✅ Спасибо! Оплата {plan.stars_price} ⭐ прошла успешно.\n"
        f"{format_subscription_status(sub)}\n\nМожно пользоваться /trends."
    )