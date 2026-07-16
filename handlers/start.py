from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! 👋\n\n"
        "Я нахожу трендовые треки из TikTok и присылаю их сюда в виде аудио, "
        "вместе с видео, в которых они звучат.\n\n"
        "📌 <b>Команды</b>\n"
        "/trends — найти треки по текущим настройкам (нужна подписка)\n"
        "/settings — ключевые слова, страна, период, сортировка\n"
        "/subscribe — оформить подписку за Telegram Stars ⭐\n"
        "/mysub — статус моей подписки\n"
        "/help — как это работает",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "ℹ️ <b>Как устроен поиск трендов:</b>\n\n"
        "1️⃣ <b>Настройка фильтров</b>\n"
        "Через команду /settings выберите страну, период публикации, ключевые слова, "
        "лимиты на количество треков и видео, а также сортировку (по лайкам или релевантности).\n\n"
        "2️⃣ <b>Активация доступа</b>\n"
        "Функция поиска доступна подписчикам. Оформить подписку можно в меню /subscribe "
        "за Telegram Stars ⭐.\n\n"
        "3️⃣ <b>Получение результатов</b>\n"
        "После отправки /trends бот пришлет подборку: аудиофайлы (сразу загруженные в Telegram) "
        "и превью оригинальных роликов, чтобы вы могли оценить контекст тренда.\n\n"
        "🔄 <i>Все настройки сохраняются автоматически — вам не нужно вводить их заново при каждом поиске.</i>",
        parse_mode="HTML"
    )