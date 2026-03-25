from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, time


class SubscriptionError(ValueError):
    pass


@dataclass(slots=True)
class SubscriptionExtension:
    duration: str
    target_timestamp: int


def parse_prolong_until(value: str) -> datetime:
    normalized = value.strip()
    if not normalized:
        raise SubscriptionError("Поле prolong_until не должно быть пустым.")

    try:
        dt = datetime.strptime(normalized, "%d.%m.%Y")
        dt = datetime.combine(dt.date(), time(23, 59, 59))
    except ValueError as exc:
        raise SubscriptionError("Неверный формат prolong_until. Используй ДД.ММ.ГГГГ.") from exc
    return dt


def format_timestamp(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def calculate_extension(target_dt: datetime, current_expiry_ts: int | None, now_ts: int) -> SubscriptionExtension:
    target_ts = int(target_dt.timestamp())

    if current_expiry_ts is not None and target_ts <= current_expiry_ts:
        raise SubscriptionError(
            f"У клиента уже есть подписка до {format_timestamp(current_expiry_ts)}. "
            "Новая дата должна быть больше текущей."
        )

    if target_ts <= now_ts:
        raise SubscriptionError("Новая дата подписки должна быть в будущем.")

    base_ts = max(now_ts, current_expiry_ts or 0)
    diff_seconds = target_ts - base_ts
    hours = max(1, math.ceil(diff_seconds / 3600))

    if hours % (24 * 7) == 0:
        duration = f"{hours // (24 * 7)}w"
    elif hours % 24 == 0:
        duration = f"{hours // 24}d"
    else:
        duration = f"{hours}h"

    return SubscriptionExtension(duration=duration, target_timestamp=target_ts)
