"""Domain models that describe the data we receive from the TikTok API:
track (music) and video in which this track is heard.

These classes know nothing about Telegram or the specific API -
their task is only to store already parsed data."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VideoSource:
    """One TikTok video that plays a specific track."""

    video_id: str
    author_username: str
    author_nickname: str
    cover_url: str
    play_count: int = 0
    digg_count: int = 0        # cursing
    comment_count: int = 0
    share_count: int = 0
    create_time: int = 0

    @property
    def url(self) -> str:
        handle = self.author_username or "tiktok"
        return f"https://www.tiktok.com/@{handle}/video/{self.video_id}"


@dataclass
class Track:
    """A unique track found in one or more TikTok videos."""

    music_id: str
    title: str
    author: str
    play_url: str
    cover_url: str = ""
    duration: int = 0
    videos: list[VideoSource] = field(default_factory=list)

    # Filled in by the download service after the audio is loaded onto disk.
    local_audio_path: Path | None = None

    def add_video(self, video: VideoSource) -> None:
        self.videos.append(video)
