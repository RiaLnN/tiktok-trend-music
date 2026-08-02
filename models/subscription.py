"""Subscription models: current user status and list of available plans.

The subscription is renewed in two ways, but through the same method
SubscriptionRepository.extend(...):
    - the user pays himself via Telegram Stars (handlers/subscription.py);
    - the bot owner issues a subscription manually (handlers/admin.py)."""
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Subscription:
    """Subscription status of one user."""

    expires_at: datetime | None = None    # None = never subscribed
    source: str = ""                       # "stars" | "admin" - how it was issued last time
    last_charge_id: str | None = None      # id of the last Stars payment (for /refund)

    def is_active(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        now = now or datetime.now(timezone.utc)
        return self.expires_at > now

    def to_dict(self) -> dict:
        return {
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "source": self.source,
            "last_charge_id": self.last_charge_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Subscription":
        raw_expires_at = data.get("expires_at")
        return cls(
            expires_at=datetime.fromisoformat(raw_expires_at) if raw_expires_at else None,
            source=data.get("source", ""),
            last_charge_id=data.get("last_charge_id"),
        )


@dataclass(frozen=True)
class SubscriptionPlan:
    plan_id: str
    days: int
    stars_price: int
    title: str
    description: str


SUBSCRIPTION_PLANS: list[SubscriptionPlan] = [
    SubscriptionPlan(
        plan_id="1m",
        days=30,
        stars_price=149,
        title="Подписка на 1 месяц",
        description="Доступ к поиску трендов TikTok на 30 дней",
    ),
    SubscriptionPlan(
        plan_id="3m",
        days=90,
        stars_price=399,
        title="Подписка на 3 месяца",
        description="Доступ к поиску трендов TikTok на 90 дней",
    ),
    SubscriptionPlan(
        plan_id="12m",
        days=365,
        stars_price=1299,
        title="Подписка на 1 год",
        description="Доступ к поиску трендов TikTok на 365 дней",
    ),
]


def find_plan(plan_id: str) -> SubscriptionPlan | None:
    return next((p for p in SUBSCRIPTION_PLANS if p.plan_id == plan_id), None)