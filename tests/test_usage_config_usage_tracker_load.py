"""Comprehensive tests for UsageTracker instance — load_usage_data()."""

from __future__ import annotations

from datetime import datetime

from src.config.usage_config import UsageTracker


class TestUsageTrackerLoad:
    """Test cases for UsageTracker.load_usage_data() method."""

    def test_load_usage_returns_default_when_file_missing(
        self, config_fs: dict[str, str], usage_tracker: UsageTracker
    ) -> None:
        """Missing usage file should return default usage data."""
        config_fs.pop("usage", None)

        usage = usage_tracker.load_usage_data()

        assert "current_month" in usage
        assert "meteostat" in usage
        assert "open-meteo" in usage
        assert usage["meteostat"]["requests_this_month"] == 0
        assert usage["open-meteo"]["requests_this_month"] == 0
        assert usage["total_requests"] == 0

    def test_load_usage_returns_saved_data(self, usage_tracker: UsageTracker) -> None:
        """Should return saved usage data."""
        usage_tracker.track_request("meteostat", 100)
        usage_tracker.track_request("open-meteo", 50)

        usage = usage_tracker.load_usage_data()

        assert usage["meteostat"]["requests_this_month"] == 100
        assert usage["open-meteo"]["requests_this_month"] == 50
        assert usage["total_requests"] == 150

    def test_load_usage_resets_on_new_month(
        self,
        config_fs: dict[str, str],
    ) -> None:
        """Should reset usage data when month changes."""
        fixed_now = datetime(2024, 2, 15, 12, 0, 0)
        tracker = UsageTracker(
            storage_path=_FakePath("usage", config_fs),
            clock=lambda: fixed_now,
            ensure_dirs=lambda: None,
        )

        # Seed with old-month data
        old_data = {
            "current_month": "2024-01",
            "meteostat": {
                "requests_this_month": 100,
                "daily_breakdown": {},
                "estimated_cost_usd": 0.0,
            },
            "open-meteo": {"requests_this_month": 0, "daily_breakdown": {}},
            "total_requests": 100,
            "month_start_date": "2024-01-01",
            "last_updated": "2024-01-15T12:00:00",
        }
        config_fs["usage"] = __import__("json").dumps(old_data)

        usage = tracker.load_usage_data()

        assert usage["current_month"] == "2024-02"
        assert usage["meteostat"]["requests_this_month"] == 0
        assert usage["total_requests"] == 0

    def test_load_usage_handles_corrupted_json(
        self, config_fs: dict[str, str], usage_tracker: UsageTracker
    ) -> None:
        """Corrupted JSON should return default usage data."""
        config_fs["usage"] = "{ not valid json"

        usage = usage_tracker.load_usage_data()

        assert usage["total_requests"] == 0
        assert usage["meteostat"]["requests_this_month"] == 0


# Re-export _FakePath from conftest for inline construction
from tests.conftest import _FakePath  # noqa: E402
