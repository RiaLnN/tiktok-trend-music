"""Admin commands: manual issuance/cancellation of subscription by the bot owner.

The entire router is closed by the IsAdmin filter - for all other users these
the commands simply do not exist (the handler does not work and does not respond)."""
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from filters.admin import IsAdmin
from storage.subscription_repository import SubscriptionRepository
from utils.formatting import format_subscription_status

router = Router(name="admin")
router.message.filter(IsAdmin())


@router.message(Command("admin"))
async def cmd_admin_help(message: Message) -> None:
    await message.answer(
        "🛠 <b>Админ-команды</b>\n\n"
        "/grant <code>user_id дней</code> — выдать/продлить подписку вручную\n"
        "/revoke <code>user_id</code> — отменить подписку\n"
        "/subinfo <code>user_id</code> — статус подписки любого пользователя\n\n"
        "Для «навсегда» укажите большое число дней, например 36500 (100 лет)."
    )


@router.message(Command("grant"))
async def cmd_grant(message: Message, command: CommandObject, subscription_repo: SubscriptionRepository) -> None:
    args = (command.args or "").split()
    if len(args) != 2:
        await message.answer("Использование: /grant <user_id> <дней>")
        return

    try:
        user_id, days = int(args[0]), int(args[1])
    except ValueError:
        await message.answer("user_id и количество дней должны быть целыми числами.")
        return

    if days <= 0:
        await message.answer("Количество дней должно быть положительным.")
        return

    sub = await subscription_repo.extend(user_id, days, source="admin")
    await message.answer(f"✅ Пользователю <code>{user_id}</code> выдана подписка.\n{format_subscription_status(sub)}")


@router.message(Command("revoke"))
async def cmd_revoke(message: Message, command: CommandObject, subscription_repo: SubscriptionRepository) -> None:
    args = (command.args or "").split()
    if len(args) != 1:
        await message.answer("Использование: /revoke <user_id>")
        return

    try:
        user_id = int(args[0])
    except ValueError:
        await message.answer("user_id должен быть числом.")
        return

    await subscription_repo.revoke(user_id)
    await message.answer(f"🚫 Подписка пользователя <code>{user_id}</code> отменена.")


@router.message(Command("subinfo"))
async def cmd_subinfo(message: Message, command: CommandObject, subscription_repo: SubscriptionRepository) -> None:
    args = (command.args or "").split()
    if len(args) != 1:
        await message.answer("Использование: /subinfo <user_id>")
        return

    try:
        user_id = int(args[0])
    except ValueError:
        await message.answer("user_id должен быть числом.")
        return

    sub = await subscription_repo.get(user_id)
    await message.answer(f"Пользователь <code>{user_id}</code>:\n{format_subscription_status(sub)}")