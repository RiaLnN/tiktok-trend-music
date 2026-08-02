"""The /trends command handler is the main bot script."""
import asyncio
import logging

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import FSInputFile, InputMediaPhoto, Message

from models.tiktok import Track
from services.trends_service import TrendsCollectionError, TrendsService
from storage.settings_repository import SettingsRepository
from storage.subscription_repository import SubscriptionRepository
from handlers.subscription import ensure_active_subscription
from utils.formatting import format_audio_caption, format_video_caption

logger = logging.getLogger(__name__)
router = Router(name="trends")

# A short pause between sending tracks, so as not to run into Telegram limits
# by the number of messages in one chat.
DELAY_BETWEEN_TRACKS = 0.5


@router.message(Command("trends", "get_trends"))
async def cmd_trends(
    message: Message,
    repo: SettingsRepository,
    trends_service: TrendsService,
    subscription_repo: SubscriptionRepository,
) -> None:
    if not await ensure_active_subscription(message, subscription_repo):
        return

    if not message.from_user: return
    user_settings = await repo.get(message.from_user.id)

    if not user_settings.keywords:
        await message.answer("Сначала задайте хотя бы одно ключевое слово в /settings 🙂")
        return

    status = await message.answer("🔍 Ищу трендовые треки, это может занять до минуты...")

    try:
        tracks = await trends_service.collect_trending_tracks(user_settings)
    except TrendsCollectionError:
        await status.edit_text(
            "❌ TikTok API сейчас недоступен (проверьте RAPIDAPI_KEY или лимиты запросов). "
            "Попробуйте позже."
        )
        return
    except Exception:
        logger.exception("Unexpected error while retrieving trends")
        await status.edit_text("❌ Произошла непредвиденная ошибка. Попробуйте позже.")
        return

    if not tracks:
        await status.edit_text(
            "Ничего не нашлось по текущим настройкам 😢\n"
            "Попробуйте другие ключевые слова, страну или период в /settings."
        )
        return

    await status.edit_text(f"🎵 Нашёл {len(tracks)} треков. Скачиваю аудио и отправляю...")
    await trends_service.download_tracks_audio(tracks)

    for track in tracks:
        await _send_track(message, track)
        await asyncio.sleep(DELAY_BETWEEN_TRACKS)

    await status.delete()


async def _send_track(message: Message, track: Track) -> None:
    if track.local_audio_path is None or not track.local_audio_path.exists():
        await message.answer(f"⚠️ Не удалось скачать «{track.title}» — {track.author}")
        return

    audio = FSInputFile(track.local_audio_path)
    try:
        await message.answer_audio(
            audio,
            title=track.title,
            performer=track.author,
            caption=format_audio_caption(track),
        )
    finally:
        track.local_audio_path.unlink(missing_ok=True)

    if track.videos:
        await _send_source_videos(message, track)


async def _send_source_videos(message: Message, track: Track) -> None:
    """Sends covers of video sources of the track along with links and statistics."""
    photos = [video for video in track.videos if video.cover_url]
    caption = format_video_caption(track)

    try:
        if not photos:
            await message.answer(caption, disable_web_page_preview=True)
        elif len(photos) == 1:
            await message.answer_photo(photos[0].cover_url, caption=caption)
        else:
            media_group = [
                InputMediaPhoto(media=video.cover_url, caption=caption if i == 0 else None)
                for i, video in enumerate(photos)
            ]
            await message.answer_media_group(media_group) # type: ignore
    except TelegramBadRequest as exc:
        # TikTok sometimes gives broken/expired links to covers - we don’t drop the bot because of this.
        logger.warning("Failed to send video preview for track %r: %s", track.title, exc)
        await message.answer(caption, disable_web_page_preview=True)