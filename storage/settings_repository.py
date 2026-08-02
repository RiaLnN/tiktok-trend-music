"""Storage of user settings.

A simple JSON file + asynchronous lock is more than enough
for a personal/small bot. The interface (get/save) is intentionally narrow,
so that, if necessary, you can painlessly replace the implementation
on SQLite/Redis/Postgres without touching the rest of the bot code."""
import asyncio
import json
import logging
from pathlib import Path

from models.settings import UserSettings

logger = logging.getLogger(__name__)


class SettingsRepository:
    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._lock = asyncio.Lock()
        self._cache: dict[str, UserSettings] | None = None

    async def get(self, user_id: int) -> UserSettings:
        async with self._lock:
            data = self._ensure_loaded()
            key = str(user_id)
            if key not in data:
                data[key] = UserSettings()
                self._flush(data)
            return data[key]

    async def save(self, user_id: int, user_settings: UserSettings) -> None:
        async with self._lock:
            data = self._ensure_loaded()
            data[str(user_id)] = user_settings
            self._flush(data)

    # --- Internal ---------------------------------------------------------

    def _ensure_loaded(self) -> dict[str, UserSettings]:
        if self._cache is not None:
            return self._cache

        if not self._file_path.exists():
            self._cache = {}
            return self._cache

        try:
            raw = json.loads(self._file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read %s: %s. I start with an empty storage.", self._file_path, exc)
            raw = {}

        self._cache = {user_id: UserSettings.from_dict(payload) for user_id, payload in raw.items()}
        return self._cache

    def _flush(self, data: dict[str, UserSettings]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        serializable = {user_id: s.to_dict() for user_id, s in data.items()}
        self._file_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")
