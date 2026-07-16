"""
Доменные модели, описывающие данные, которые мы получаем от TikTok API:
трек (музыка) и видео, в котором этот трек звучит.

Эти классы ничего не знают ни про Telegram, ни про конкретный API —
их задача только хранить уже разобранные данные.
"""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VideoSource:
    """Одно видео TikTok, в котором звучит конкретный трек."""

    video_id: str
    author_username: str
    author_nickname: str
    cover_url: str
    play_count: int = 0
    digg_count: int = 0        # лайки
    comment_count: int = 0
    share_count: int = 0
    create_time: int = 0

    @property
    def url(self) -> str:
        handle = self.author_username or "tiktok"
        return f"https://www.tiktok.com/@{handle}/video/{self.video_id}"


@dataclass
class Track:
    """Уникальный трек, найденный в одном или нескольких видео TikTok."""

    music_id: str
    title: str
    author: str
    play_url: str
    cover_url: str = ""
    duration: int = 0
    videos: list[VideoSource] = field(default_factory=list)

    # Заполняется сервисом скачивания после загрузки аудио на диск.
    local_audio_path: Path | None = None

    def add_video(self, video: VideoSource) -> None:
        self.videos.append(video)
