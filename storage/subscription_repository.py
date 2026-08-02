"""Storage of user subscriptions.

Same approach as SettingsRepository: JSON file + asyncio.Lock.
As the load grows, you can replace it with SQLite/Postgres without touching the caller
code - it only works through get/is_active/extend/revoke."""
import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from models.subscription import Subscription

logger = logging.getLogger(__name__)


class SubscriptionRepository:
    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._lock = asyncio.Lock()
        self._cache: dict[str, Subscription] | None = None

    async def get(self, user_id: int) -> Subscription:
        async with self._lock:
            data = self._ensure_loaded()
            return data.get(str(user_id), Subscription())

    async def is_active(self, user_id: int) -> bool:
        async with self._lock:
            data = self._ensure_loaded()
            return data.get(str(user_id), Subscription()).is_active()

    async def extend(
        self, user_id: int, days: int, source: str, charge_id: str | None = None
    ) -> Subscription:
        """Extends the subscription for `days` days.

        If the current subscription is still active, it counts from its expires_at (extension
        "on top" of the balance), otherwise - from the current moment (new subscription)."""
        async with self._lock:
            data = self._ensure_loaded()
            key = str(user_id)
            current = data.get(key, Subscription())
            now = datetime.now(timezone.utc)
            base = current.expires_at if current.is_active(now) else now

            updated = Subscription(
                expires_at=base + timedelta(days=days), # type: ignore
                source=source,
                last_charge_id=charge_id if charge_id else current.last_charge_id,
            )
            data[key] = updated
            self._flush(data)
            return updated

    async def revoke(self, user_id: int) -> None:
        async with self._lock:
            data = self._ensure_loaded()
            data[str(user_id)] = Subscription()
            self._flush(data)

    # --- Internal ---------------------------------------------------------

    def _ensure_loaded(self) -> dict[str, Subscription]:
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

        self._cache = {user_id: Subscription.from_dict(payload) for user_id, payload in raw.items()}
        return self._cache

    def _flush(self, data: dict[str, Subscription]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        serializable = {user_id: s.to_dict() for user_id, s in data.items()}
        self._file_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")