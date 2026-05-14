#!/usr/bin/env python3

"""API usage tracking and monitoring for provider selector."""

from __future__ import annotations

import json
import logging
import threading
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .api_config import APIConfig
from .atomic_io import atomic_write_json
from .provider_config import ProviderConfig

LOGGER = logging.getLogger(__name__)


def _default_now() -> datetime:
    """Default clock — returns current local datetime."""
    return datetime.now()


class UsageTracker:
    """API usage tracking for Provider Selector — instance-based."""

    def __init__(  # noqa: D107
        self,
        storage_path: Path,
        clock: Callable[[], datetime] | None = None,
        ensure_dirs: Callable[[], None] | None = None,
    ) -> None:
        self._storage_path = storage_path
        self._clock = clock or _default_now
        self._ensure_dirs = ensure_dirs
        self._lock = threading.Lock()

    # --- persistence ---

    def load_usage_data(self) -> dict[str, Any]:
        """Load API usage tracking data from JSON file."""
        current_month = self._clock().strftime("%Y-%m")

        default_usage: dict[str, Any] = {
            "current_month": current_month,
            "meteostat": {
                "requests_this_month": 0,
                "estimated_cost_usd": 0.0,
                "last_request": None,
                "daily_breakdown": {},
            },
            "open-meteo": {
                "requests_this_month": 0,
                "last_request": None,
                "daily_breakdown": {},
            },
            "total_requests": 0,
            "month_start_date": f"{current_month}-01",
            "last_updated": self._clock().isoformat(),
        }

        try:
            if self._storage_path.exists():
                with open(self._storage_path, encoding="utf-8") as fh:  # noqa: PTH123
                    usage = json.load(fh)

                    if "open_meteo" in usage and "open-meteo" not in usage:
                        usage["open-meteo"] = usage.pop("open_meteo")

                    if usage.get("current_month") != current_month:
                        usage = self._reset_monthly_usage(usage, current_month)

                    return {**default_usage, **usage}
            return default_usage
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("Usage adatok betöltése sikertelen", exc_info=exc)
            return default_usage

    def save_usage_data(self, usage_data: dict[str, Any]) -> bool:
        """Save usage tracking data atomically."""
        try:
            if self._ensure_dirs:
                self._ensure_dirs()
            usage_data["last_updated"] = self._clock().isoformat()
            atomic_write_json(self._storage_path, usage_data)
            self._storage_path.chmod(0o600)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("Usage adatok mentése sikertelen", exc_info=exc)
            return False

    # --- core operations ---

    def track_request(self, provider: str, request_count: int = 1) -> dict[str, Any]:
        """Track API request usage for *provider*."""
        with self._lock:
            usage = self.load_usage_data()
            today = self._clock().strftime("%Y-%m-%d")
            now = self._clock().isoformat()

            if provider in usage:
                usage[provider]["requests_this_month"] += request_count
                usage[provider]["last_request"] = now

                if "daily_breakdown" not in usage[provider]:
                    usage[provider]["daily_breakdown"] = {}
                if today not in usage[provider]["daily_breakdown"]:
                    usage[provider]["daily_breakdown"][today] = 0
                usage[provider]["daily_breakdown"][today] += request_count

                if provider == "meteostat":
                    cost = ProviderConfig.METEOSTAT_COST_PER_REQUEST
                    usage[provider]["estimated_cost_usd"] = (
                        usage[provider]["requests_this_month"] * cost
                    )
            else:
                tracked: dict[str, int] = {
                    key: usage.get(key, {}).get("requests_this_month", 0)
                    for key in ("meteostat", "open-meteo")
                    if isinstance(usage.get(key), dict)
                }
                LOGGER.warning(
                    "UsageTracker track_request - ismeretlen provider '%s'; számlálók: %s",
                    provider,
                    tracked,
                )

            usage["total_requests"] += request_count
            self.save_usage_data(usage)
            return usage

    def get_usage_summary(self) -> dict[str, Any]:
        """Get usage summary for display."""
        usage = self.load_usage_data()

        meteostat_reqs = usage.get("meteostat", {}).get("requests_this_month", 0)
        meteostat_limit = APIConfig.METEOSTAT_MONTHLY_LIMIT_RATE
        pct = (meteostat_reqs / meteostat_limit) * 100

        return {
            "meteostat_requests": meteostat_reqs,
            "meteostat_limit": meteostat_limit,
            "meteostat_percentage": pct,
            "meteostat_cost": usage.get("meteostat", {}).get("estimated_cost_usd", 0.0),
            "openmeteo_requests": usage.get("open-meteo", {}).get("requests_this_month", 0),
            "total_requests": usage.get("total_requests", 0),
            "warning_level": self._get_warning_level(pct),
            "days_remaining": self._get_days_remaining_in_month(),
        }

    def get_daily_breakdown(self, provider: str, days: int = 7) -> dict[str, int]:
        """Get daily usage breakdown for *provider*."""
        usage = self.load_usage_data()
        breakdown = usage.get(provider, {}).get("daily_breakdown", {})
        result: dict[str, int] = {}
        current = self._clock()
        for i in range(days):
            date = (current - timedelta(days=i)).strftime("%Y-%m-%d")
            result[date] = breakdown.get(date, 0)
        return dict(reversed(result.items()))

    def reset_usage_data(self) -> bool:
        """Delete usage tracking file."""
        try:
            if self._storage_path.exists():
                self._storage_path.unlink()
            return True
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("Usage adatok resetelése sikertelen", exc_info=exc)
            return False

    def save(self) -> None:
        """Persist current state (convenience for ProviderRouting.save_preferences)."""
        usage = self.load_usage_data()
        self.save_usage_data(usage)

    # --- private helpers ---

    def _reset_monthly_usage(self, old: dict[str, Any], new_month: str) -> dict[str, Any]:
        old["current_month"] = new_month
        old["month_start_date"] = f"{new_month}-01"
        for prov in ("meteostat", "open-meteo"):
            if prov in old:
                old[prov]["requests_this_month"] = 0
                old[prov]["daily_breakdown"] = {}
                if prov == "meteostat":
                    old[prov]["estimated_cost_usd"] = 0.0
        old["total_requests"] = 0
        return old

    def _get_warning_level(self, percentage: float) -> str:
        if percentage >= ProviderConfig.CRITICAL_THRESHOLD * 100:
            return "critical"
        if percentage >= ProviderConfig.WARNING_THRESHOLD * 100:
            return "warning"
        return "normal"

    def _get_days_remaining_in_month(self) -> int:
        now = self._clock()
        if now.month == 12:  # noqa: PLR2004
            nxt = now.replace(year=now.year + 1, month=1, day=1)
        else:
            nxt = now.replace(month=now.month + 1, day=1)
        return (nxt - now).days


# --- module-level helpers for backward compat / test fixtures ---


def _resolve_ensure_dirs() -> Callable[[], None] | None:
    """Return ensure_directories from config module if monkeypatched in tests."""
    import sys  # noqa: PLC0415

    from .paths_config import ensure_directories  # noqa: PLC0415

    mod = sys.modules.get("src.config")
    if mod and hasattr(mod, "ensure_directories"):
        fn = mod.ensure_directories
        if callable(fn):
            return fn  # type: ignore[return-value]
    return ensure_directories


def build_usage_tracker(
    storage_path: Path | None = None,
    clock: Callable[[], datetime] | None = None,
) -> UsageTracker:
    """Factory: build a fully configured UsageTracker instance."""
    from .paths_config import USAGE_TRACKING_FILE  # noqa: PLC0415

    return UsageTracker(
        storage_path=storage_path or USAGE_TRACKING_FILE,
        clock=clock,
        ensure_dirs=_resolve_ensure_dirs(),
    )
