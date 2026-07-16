"""
Хранилище пользовательских настроек.

Простой JSON-файл + асинхронный lock — этого более чем достаточно
для личного/небольшого бота. Интерфейс (get/save) намеренно узкий,
чтобы при необходимости можно было безболезненно заменить реализацию
на SQLite/Redis/Postgres, не трогая остальной код бота.
"""
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

    # --- Внутреннее ---------------------------------------------------------

    def _ensure_loaded(self) -> dict[str, UserSettings]:
        if self._cache is not None:
            return self._cache

        if not self._file_path.exists():
            self._cache = {}
            return self._cache

        try:
            raw = json.loads(self._file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Не удалось прочитать %s: %s. Начинаю с пустого хранилища.", self._file_path, exc)
            raw = {}

        self._cache = {user_id: UserSettings.from_dict(payload) for user_id, payload in raw.items()}
        return self._cache

    def _flush(self, data: dict[str, UserSettings]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        serializable = {user_id: s.to_dict() for user_id, s in data.items()}
        self._file_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")
