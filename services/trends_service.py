"""Business logic for searching for trends.

TrendsService integrates TikTokScraperClient (raw API requests)
and audio_downloader (downloading files), and is also responsible for:
  - bypassing several user keywords;
  - pagination within one keyword until we type
    the required number of unique tracks;
  - deduplication of tracks by music_id and collection of multiple video sources
    to the track;
  - parallel downloading of audio for all found tracks."""
import asyncio
import logging
from pathlib import Path

import httpx

from config import settings as app_settings
from models.settings import UserSettings
from models.tiktok import Track, VideoSource
from services.audio_downloader import download_file
from services.tiktok_api import TikTokAPIError, TikTokScraperClient
from utils.constants import DEFAULT_KEYWORD, MAX_PAGES_PER_KEYWORD, SEARCH_PAGE_SIZE
from utils.formatting import safe_filename

logger = logging.getLogger(__name__)


class TrendsCollectionError(Exception):
    """Not a single request to the TikTok API completed successfully (all keywords failed)."""


class TrendsService:
    def __init__(self, api_client: TikTokScraperClient, audio_dir: Path = app_settings.AUDIO_DIR) -> None:
        self._api = api_client
        self._audio_dir = audio_dir
        self._download_client = httpx.AsyncClient(timeout=app_settings.HTTP_TIMEOUT)

    async def close(self) -> None:
        await self._download_client.aclose()

    # --- Search for tracks -------------------------------------------------------

    async def collect_trending_tracks(self, user_settings: UserSettings) -> list[Track]:
        """Returns up to user_settings.tracks_count of unique tracks by user settings."""
        keywords = user_settings.keywords or [DEFAULT_KEYWORD]
        tracks: dict[str, Track] = {}
        successful_requests = 0

        for keyword in keywords:
            if await self._collect_for_keyword(keyword, user_settings, tracks):
                successful_requests += 1

        if successful_requests == 0:
            raise TrendsCollectionError("All requests to TikTok API failed")

        return list(tracks.values())[: user_settings.tracks_count]

    async def _collect_for_keyword(
        self, keyword: str, user_settings: UserSettings, tracks: dict[str, Track]
    ) -> bool:
        """Queries the API for one keyword (with pagination). Returns the success of the request."""
        cursor = 0
        got_successful_response = False

        for _ in range(MAX_PAGES_PER_KEYWORD):
            try:
                payload = await self._api.search_feed(
                    keywords=keyword,
                    count=SEARCH_PAGE_SIZE,
                    cursor=cursor,
                    region=user_settings.region,
                    publish_time=user_settings.publish_time.value,
                    sort_type=user_settings.sort_type.value,
                )
            except (httpx.HTTPError, TikTokAPIError) as exc:
                logger.warning("TikTok API request error for word %r: %s", keyword, exc)
                break

            got_successful_response = True
            data = payload.get("data", {})

            for video in data.get("videos", []):
                self._register_video(video, tracks, user_settings.tracks_count, user_settings.videos_per_track)

            if len(tracks) >= user_settings.tracks_count or not data.get("hasMore"):
                break

            cursor = data.get("cursor", cursor + SEARCH_PAGE_SIZE)

        return got_successful_response

    @staticmethod
    def _register_video(
        video: dict, tracks: dict[str, Track], tracks_limit: int, videos_per_track: int
    ) -> None:
        music = video.get("music_info") or {}
        music_id = music.get("id")
        play_url = music.get("play")

        if not music_id or not play_url:
            return  # the video does not have a track with a working link - skip it

        track = tracks.get(music_id)
        if track is None:
            if len(tracks) >= tracks_limit:
                return  # the new track will not fit into the limit - but the old ones can still be supplemented
            track = Track(
                music_id=music_id,
                title=music.get("title") or "Неизвестный трек",
                author=music.get("author") or "Неизвестен",
                play_url=play_url,
                cover_url=music.get("cover", ""),
                duration=music.get("duration", 0),
            )
            tracks[music_id] = track

        if len(track.videos) >= videos_per_track:
            return  # We have already collected enough video sources for this track

        author_info = video.get("author") or {}
        track.add_video(
            VideoSource(
                video_id=str(video.get("video_id", "")),
                author_username=author_info.get("unique_id", ""),
                author_nickname=author_info.get("nickname", ""),
                cover_url=video.get("cover", ""),
                play_count=video.get("play_count", 0),
                digg_count=video.get("digg_count", 0),
                comment_count=video.get("comment_count", 0),
                share_count=video.get("share_count", 0),
                create_time=video.get("create_time", 0),
            )
        )

    # ---Download audio ------------------------------------------------------------------

    async def download_tracks_audio(self, tracks: list[Track]) -> None:
        """Simultaneously downloads audio for all tracks and sets track.local_audio_path."""
        await asyncio.gather(*(self._download_one(track) for track in tracks))

    async def _download_one(self, track: Track) -> None:
        filename = safe_filename(f"{track.author} - {track.title}") + ".mp3"
        # music_id at the beginning of the file name protects against collisions with the same names.
        destination = self._audio_dir / f"{track.music_id}_{filename}"

        try:
            await download_file(self._download_client, track.play_url, destination)
        except httpx.HTTPError as exc:
            logger.warning("Failed to download track %r: %s", track.title, exc)
            return

        track.local_audio_path = destination
