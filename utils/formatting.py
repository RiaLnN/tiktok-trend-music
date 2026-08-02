"""Formatting aids: file names and message signatures."""
import re
from html import escape

from models.subscription import Subscription
from models.tiktok import Track

_ILLEGAL_FILENAME_CHARS = re.compile(r'[\\/*?:"<>|]')


def safe_filename(name: str, fallback: str = "audio", max_length: int = 100) -> str:
    """Removes characters that are not allowed in file names on most operating systems."""
    cleaned = _ILLEGAL_FILENAME_CHARS.sub("", name).strip()
    cleaned = cleaned or fallback
    return cleaned[:max_length]


def format_count(value: int) -> str:
    """Compact representation of a number: 12345 -> '12.3K', 2_500_000 -> '2.5M'."""
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def format_audio_caption(track: Track) -> str:
    """The signature that comes with the track's audio file."""
    return f"🎵 <b>{escape(track.title)}</b>\n👤 {escape(track.author)}"


def format_video_caption(track: Track) -> str:
    """Signature with a list of video sources of the track (with links and statistics)."""
    lines = [f"🎬 <b>Видео с треком «{escape(track.title)}»</b>"]

    for i, video in enumerate(track.videos, start=1):
        handle = escape(video.author_username or video.author_nickname or "аноним")
        stats = f"👁 {format_count(video.play_count)} · ❤️ {format_count(video.digg_count)}"
        lines.append(f'{i}. <a href="{video.url}">@{handle}</a> — {stats}')

    return "\n".join(lines)


def format_subscription_status(sub: Subscription) -> str:
    """Human-readable subscription status - for /mysub, /subscribe, /subinfo."""
    if sub.is_active():
        return f"✅ Подписка активна до {sub.expires_at:%d.%m.%Y %H:%M} UTC"
    if sub.expires_at is not None:
        return f"❌ Подписка истекла {sub.expires_at:%d.%m.%Y} и сейчас неактивна"
    return "❌ Подписки нет"