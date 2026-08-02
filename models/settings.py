"""User Settings and References for TikTok API Options
(tiktok-scraper7 -> GET /feed/search).

The enum values below are what the endpoint actually takes
/feed/search: publish_time and sort_type copy filters that
is in the TikTok search itself (publication period and sorting by
relevance/likes)."""
from dataclasses import dataclass, field
from enum import Enum


class SortType(str, Enum):
    RELEVANCE = "0"
    MOST_LIKED = "1"


class PublishTime(str, Enum):
    ALL_TIME = "0"
    LAST_24_HOURS = "1"
    LAST_WEEK = "7"
    LAST_MONTH = "30"
    LAST_3_MONTHS = "90"
    LAST_6_MONTHS = "180"


SORT_TYPE_LABELS: dict[SortType, str] = {
    SortType.RELEVANCE: "🔎 По релевантности",
    SortType.MOST_LIKED: "🔥 По популярности (лайки)",
}

PUBLISH_TIME_LABELS: dict[PublishTime, str] = {
    PublishTime.ALL_TIME: "За всё время",
    PublishTime.LAST_24_HOURS: "За последние 24 часа",
    PublishTime.LAST_WEEK: "За последнюю неделю",
    PublishTime.LAST_MONTH: "За последний месяц",
    PublishTime.LAST_3_MONTHS: "За последние 3 месяца",
    PublishTime.LAST_6_MONTHS: "За последние 6 месяцев",
}

# "" = no region restrictions (global search).
# You can expand the list with any ISO 3166-1 alpha-2 country codes.
REGIONS: dict[str, str] = {
    "": "🌍 Без ограничений",
    "US": "🇺🇸 США",
    "GB": "🇬🇧 Великобритания",
    "RU": "🇷🇺 Россия",
    "UA": "🇺🇦 Украина",
    "KZ": "🇰🇿 Казахстан",
    "BY": "🇧🇾 Беларусь",
    "DE": "🇩🇪 Германия",
    "FR": "🇫🇷 Франция",
    "BR": "🇧🇷 Бразилия",
    "IN": "🇮🇳 Индия",
    "ID": "🇮🇩 Индонезия",
    "JP": "🇯🇵 Япония",
    "KR": "🇰🇷 Южная Корея",
    "TR": "🇹🇷 Турция",
    "VN": "🇻🇳 Вьетнам",
    "PL": "🇵🇱 Польша",
}


@dataclass
class UserSettings:
    """Personal settings for trend search for one bot user."""

    keywords: list[str] = field(default_factory=lambda: ["trending"])
    region: str = ""                          # "" = global, otherwise country code, e.g. "US"
    publish_time: PublishTime = PublishTime.LAST_WEEK
    sort_type: SortType = SortType.MOST_LIKED
    tracks_count: int = 5                      # how many unique tracks to give away per one /trends
    videos_per_track: int = 3                  # how many original videos to show under the track

    def to_dict(self) -> dict:
        return {
            "keywords": self.keywords,
            "region": self.region,
            "publish_time": self.publish_time.value,
            "sort_type": self.sort_type.value,
            "tracks_count": self.tracks_count,
            "videos_per_track": self.videos_per_track,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserSettings":
        return cls(
            keywords=list(data.get("keywords") or ["trending"]),
            region=data.get("region", ""),
            publish_time=PublishTime(data.get("publish_time", PublishTime.LAST_WEEK.value)),
            sort_type=SortType(data.get("sort_type", SortType.MOST_LIKED.value)),
            tracks_count=int(data.get("tracks_count", 5)),
            videos_per_track=int(data.get("videos_per_track", 3)),
        )
