# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""API usage tracking and monitoring for provider selector."""

from __future__ import annotations

import json
import logging
import threading
from datetime import timedelta
from pathlib import Path
from typing import Any

from .api_config import APIConfig
from .atomic_io import atomic_write_json
from .paths_config import (
    USAGE_TRACKING_FILE as DEFAULT_USAGE_TRACKING_FILE,
)
from .paths_config import (
    ensure_directories as default_ensure_directories,
)
from .provider_config import ProviderConfig
from .usage_config_helpers import (
    _ensure_directories,
    _get_usage_tracking_file,
    _now,
)

LOGGER = logging.getLogger(__name__)


def _get_usage_tracking_file_resolved() -> Path:
    return _get_usage_tracking_file(DEFAULT_USAGE_TRACKING_FILE)


def _ensure_dirs_resolved() -> None:
    _ensure_directories(default_ensure_directories)


class UsageTracker:
    """API usage tracking for Provider Selector."""

    _lock: threading.Lock = threading.Lock()

    @staticmethod
    def load_usage_data() -> dict[str, Any]:
        """
        Load API usage tracking data.

        Returns:
            Dictionary with usage statistics
        """
        current_month = _now().strftime("%Y-%m")

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
            "last_updated": _now().isoformat(),
        }

        usage_file = _get_usage_tracking_file_resolved()

        try:
            if usage_file.exists():
                with open(usage_file, encoding="utf-8") as file_obj:  # noqa: PTH123
                    usage = json.load(file_obj)

                    # Normalize legacy provider key
                    if "open_meteo" in usage and "open-meteo" not in usage:
                        usage["open-meteo"] = usage.pop("open_meteo")

                    # Reset if new month
                    if usage.get("current_month") != current_month:
                        usage = UsageTracker._reset_monthly_usage(usage, current_month)

                    return {**default_usage, **usage}
            else:
                return default_usage
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("Usage adatok betöltése sikertelen", exc_info=exc)
            return default_usage

    @staticmethod
    def save_usage_data(usage_data: dict[str, Any]) -> bool:
        """
        Save usage tracking data.

        Args:
            usage_data: Usage statistics dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        usage_file = _get_usage_tracking_file_resolved()

        try:
            _ensure_dirs_resolved()
            usage_data["last_updated"] = _now().isoformat()

            atomic_write_json(usage_file, usage_data)
            usage_file.chmod(0o600)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("Usage adatok mentése sikertelen", exc_info=exc)
            return False

    @staticmethod
    def track_request(provider: str, request_count: int = 1) -> dict[str, Any]:
        """
        Track API request usage.

        Args:
            provider: Provider name ("open-meteo" or "meteostat")
            request_count: Number of requests to track

        Returns:
            Updated usage statistics
        """
        with UsageTracker._lock:
            usage = UsageTracker.load_usage_data()
            today = _now().strftime("%Y-%m-%d")
            now = _now().isoformat()

            if provider in usage:
                # Update provider-specific stats
                usage[provider]["requests_this_month"] += request_count
                usage[provider]["last_request"] = now

                # Update daily breakdown
                if "daily_breakdown" not in usage[provider]:
                    usage[provider]["daily_breakdown"] = {}

                if today not in usage[provider]["daily_breakdown"]:
                    usage[provider]["daily_breakdown"][today] = 0
                usage[provider]["daily_breakdown"][today] += request_count

                # Update Meteostat cost estimation
                if provider == "meteostat":
                    cost_per_request = ProviderConfig.METEOSTAT_COST_PER_REQUEST
                    usage[provider]["estimated_cost_usd"] = (
                        usage[provider]["requests_this_month"] * cost_per_request
                    )
            else:
                tracked_state: dict[str, int] = {
                    key: usage.get(key, {}).get("requests_this_month", 0)
                    for key in ("meteostat", "open-meteo")
                    if isinstance(usage.get(key), dict)
                }
                LOGGER.warning(
                    "UsageTracker track_request - ismeretlen provider '%s'; számlálók: %s",
                    provider,
                    tracked_state,
                )

            # Update total
            usage["total_requests"] += request_count

            # Save and return
            UsageTracker.save_usage_data(usage)
            return usage

    @staticmethod
    def get_usage_summary() -> dict[str, Any]:
        """
        Get usage summary for display.

        Returns:
            Dictionary with usage summary
        """
        usage = UsageTracker.load_usage_data()

        meteostat_requests = usage.get("meteostat", {}).get("requests_this_month", 0)
        meteostat_limit = APIConfig.METEOSTAT_MONTHLY_LIMIT_RATE
        meteostat_percentage = (meteostat_requests / meteostat_limit) * 100

        return {
            "meteostat_requests": meteostat_requests,
            "meteostat_limit": meteostat_limit,
            "meteostat_percentage": meteostat_percentage,
            "meteostat_cost": usage.get("meteostat", {}).get("estimated_cost_usd", 0.0),
            "openmeteo_requests": usage.get("open-meteo", {}).get("requests_this_month", 0),
            "total_requests": usage.get("total_requests", 0),
            "warning_level": UsageTracker._get_warning_level(meteostat_percentage),
            "days_remaining": UsageTracker._get_days_remaining_in_month(),
        }

    @staticmethod
    def _reset_monthly_usage(old_usage: dict[str, Any], new_month: str) -> dict[str, Any]:
        """Reset usage data for new month."""
        old_usage["current_month"] = new_month
        old_usage["month_start_date"] = f"{new_month}-01"

        # Reset monthly counters but keep historical data
        for provider in ["meteostat", "open-meteo"]:
            if provider in old_usage:
                old_usage[provider]["requests_this_month"] = 0
                old_usage[provider]["daily_breakdown"] = {}
                if provider == "meteostat":
                    old_usage[provider]["estimated_cost_usd"] = 0.0

        old_usage["total_requests"] = 0
        return old_usage

    @staticmethod
    def _get_warning_level(percentage: float) -> str:
        """Get warning level based on usage percentage."""
        if percentage >= ProviderConfig.CRITICAL_THRESHOLD * 100:
            return "critical"
        elif percentage >= ProviderConfig.WARNING_THRESHOLD * 100:
            return "warning"
        else:
            return "normal"

    @staticmethod
    def _get_days_remaining_in_month() -> int:
        """Get number of days remaining in current month."""
        now = _now()
        if now.month == 12:  # noqa: PLR2004
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)

        return (next_month - now).days

    @staticmethod
    def get_daily_breakdown(provider: str, days: int = 7) -> dict[str, int]:
        """
        Get daily usage breakdown for a provider.

        Args:
            provider: Provider name
            days: Number of days to include

        Returns:
            Dictionary with daily usage counts
        """
        usage = UsageTracker.load_usage_data()
        daily_breakdown = usage.get(provider, {}).get("daily_breakdown", {})

        # Get last N days
        result = {}
        current = _now()
        for i in range(days):
            date = (current - timedelta(days=i)).strftime("%Y-%m-%d")
            result[date] = daily_breakdown.get(date, 0)

        return dict(reversed(result.items()))  # Chronological order

    @staticmethod
    def reset_usage_data() -> bool:
        """
        Reset all usage tracking data.

        Returns:
            True if reset successfully, False otherwise
        """
        usage_file = _get_usage_tracking_file_resolved()
        try:
            if usage_file.exists():
                usage_file.unlink()
            return True
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("Usage adatok resetelése sikertelen", exc_info=exc)
            return False
