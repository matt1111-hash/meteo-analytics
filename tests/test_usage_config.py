"""Comprehensive tests for src/config/usage_config.py."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest


class TestModuleHelpers:
    """Test cases for module helper functions."""

    def test_resolve_config_attr_with_fallback(self) -> None:
        """Should return fallback when attribute not in config module."""
        from src.config.usage_config import _resolve_config_attr

        result = _resolve_config_attr("nonexistent_attr", "fallback_value")
        assert result == "fallback_value"

    def test_get_usage_tracking_file_returns_path(self) -> None:
        """Should return a Path object."""
        from src.config.usage_config import _get_usage_tracking_file

        result = _get_usage_tracking_file()
        assert isinstance(result, Path)

    def test_get_datetime_cls_returns_datetime_class(self) -> None:
        """Should return datetime class."""
        from src.config.usage_config import _get_datetime_cls

        result = _get_datetime_cls()
        assert result is datetime

    def test_now_returns_datetime(self) -> None:
        """Should return current datetime."""
        from src.config.usage_config import _now

        result = _now()
        assert isinstance(result, datetime)


class TestUsageTrackerLoad:
    """Test cases for UsageTracker.load_usage_data() method."""

    def test_load_usage_returns_default_when_file_missing(
        self, config_fs: dict[str, str]
    ) -> None:
        """Missing usage file should return default usage data."""
        from src.config.usage_config import UsageTracker

        # Remove usage file if it exists
        config_fs.pop("usage", None)

        usage = UsageTracker.load_usage_data()

        assert "current_month" in usage
        assert "meteostat" in usage
        assert "open_meteo" in usage
        assert usage["meteostat"]["requests_this_month"] == 0
        assert usage["open_meteo"]["requests_this_month"] == 0
        assert usage["total_requests"] == 0

    def test_load_usage_returns_saved_data(self, config_fs: dict[str, str]) -> None:
        """Should return saved usage data."""
        from src.config.usage_config import UsageTracker

        # First save some data
        UsageTracker.track_request("meteostat", 100)
        UsageTracker.track_request("open_meteo", 50)

        # Then load it
        usage = UsageTracker.load_usage_data()

        assert usage["meteostat"]["requests_this_month"] == 100
        assert usage["open_meteo"]["requests_this_month"] == 50
        assert usage["total_requests"] == 150

    def test_load_usage_resets_on_new_month(
        self, config_fs: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should reset usage data when month changes."""
        from src import config
        from src.config.usage_config import UsageTracker

        # Create usage data from previous month by manually setting it
        UsageTracker.track_request("meteostat", 100)

        # Manually set to previous month
        usage = UsageTracker.load_usage_data()
        usage["current_month"] = "2024-01"
        UsageTracker.save_usage_data(usage)

        # Mock datetime to return February 2024
        fixed_now = datetime(2024, 2, 15, 12, 0, 0)

        class FakeDatetime:
            @classmethod
            def now(cls):
                return fixed_now

        # Patch datetime in the config module so _get_datetime_cls returns our fake
        monkeypatch.setattr(config, "datetime", FakeDatetime)

        # Force reload of usage data
        usage = UsageTracker.load_usage_data()

        # Counters should be reset
        assert usage["current_month"] == "2024-02"
        assert usage["meteostat"]["requests_this_month"] == 0
        assert usage["total_requests"] == 0

    def test_load_usage_handles_corrupted_json(self, config_fs: dict[str, str]) -> None:
        """Corrupted JSON should return default usage data."""
        from src.config.usage_config import UsageTracker

        config_fs["usage"] = "{ not valid json"

        usage = UsageTracker.load_usage_data()

        assert usage["total_requests"] == 0
        assert usage["meteostat"]["requests_this_month"] == 0


class TestUsageTrackerSave:
    """Test cases for UsageTracker.save_usage_data() method."""

    def test_save_usage_writes_to_file(self, config_fs: dict[str, str]) -> None:
        """Saving usage data should write to file."""
        from src.config.usage_config import UsageTracker

        usage_data = {
            "current_month": "2024-01",
            "meteostat": {"requests_this_month": 10},
            "open_meteo": {"requests_this_month": 5},
            "total_requests": 15,
        }

        result = UsageTracker.save_usage_data(usage_data)

        assert result is True
        assert "usage" in config_fs

        saved = json.loads(config_fs["usage"])
        assert saved["total_requests"] == 15

    def test_save_usage_adds_timestamp(self, config_fs: dict[str, str]) -> None:
        """Saving should add last_updated timestamp."""
        from src.config.usage_config import UsageTracker

        usage_data = {"total_requests": 5}

        UsageTracker.save_usage_data(usage_data)

        saved = json.loads(config_fs["usage"])
        assert "last_updated" in saved


class TestUsageTrackerTrackRequest:
    """Test cases for UsageTracker.track_request() method."""

    def test_track_request_meteostat(self, config_fs: dict[str, str]) -> None:
        """Tracking Meteostat request should update counters and cost."""
        from src.config.usage_config import UsageTracker

        result = UsageTracker.track_request("meteostat", 5)

        assert result["meteostat"]["requests_this_month"] == 5
        assert result["meteostat"]["estimated_cost_usd"] > 0
        assert result["total_requests"] == 5
        assert "last_request" in result["meteostat"]

    def test_track_request_open_meteo(self, config_fs: dict[str, str]) -> None:
        """Tracking Open-Meteo request should update counters."""
        from src.config.usage_config import UsageTracker

        result = UsageTracker.track_request("open_meteo", 3)

        assert result["open_meteo"]["requests_this_month"] == 3
        assert result["total_requests"] == 3
        assert "last_request" in result["open_meteo"]

    def test_track_request_accumulates(self, config_fs: dict[str, str]) -> None:
        """Multiple track_request calls should accumulate."""
        from src.config.usage_config import UsageTracker

        UsageTracker.track_request("meteostat", 5)
        UsageTracker.track_request("meteostat", 3)

        usage = UsageTracker.load_usage_data()
        assert usage["meteostat"]["requests_this_month"] == 8

    def test_track_request_updates_daily_breakdown(
        self, config_fs: dict[str, str]
    ) -> None:
        """Tracking should update daily breakdown."""
        from src.config.usage_config import UsageTracker

        UsageTracker.track_request("meteostat", 5)

        usage = UsageTracker.load_usage_data()
        today = datetime.now().strftime("%Y-%m-%d")

        assert today in usage["meteostat"]["daily_breakdown"]
        assert usage["meteostat"]["daily_breakdown"][today] == 5

    def test_track_request_unknown_provider(self, config_fs: dict[str, str]) -> None:
        """Unknown provider should log warning but not crash."""
        from src.config.usage_config import UsageTracker

        # Should not raise exception
        result = UsageTracker.track_request("unknown_provider", 5)

        # Total should still be updated
        assert result["total_requests"] == 5


class TestUsageTrackerGetSummary:
    """Test cases for UsageTracker.get_usage_summary() method."""

    def test_get_usage_summary_returns_all_fields(
        self, config_fs: dict[str, str]
    ) -> None:
        """Should return all summary fields."""
        from src.config.usage_config import UsageTracker

        summary = UsageTracker.get_usage_summary()

        expected_keys = {
            "meteostat_requests",
            "meteostat_limit",
            "meteostat_percentage",
            "meteostat_cost",
            "openmeteo_requests",
            "total_requests",
            "warning_level",
            "days_remaining",
        }

        assert set(summary.keys()) == expected_keys

    def test_get_usage_summary_with_tracked_requests(
        self, config_fs: dict[str, str]
    ) -> None:
        """Summary should reflect tracked requests."""
        from src.config.usage_config import UsageTracker

        UsageTracker.track_request("meteostat", 100)
        UsageTracker.track_request("open_meteo", 50)

        summary = UsageTracker.get_usage_summary()

        assert summary["meteostat_requests"] == 100
        assert summary["openmeteo_requests"] == 50
        assert summary["total_requests"] == 150


class TestUsageTrackerWarningLevel:
    """Test cases for UsageTracker._get_warning_level() method."""

    def test_warning_level_normal(self) -> None:
        """Low percentage should return 'normal'."""
        from src.config.usage_config import UsageTracker

        result = UsageTracker._get_warning_level(50.0)
        assert result == "normal"

    def test_warning_level_warning(self) -> None:
        """Percentage at warning threshold should return 'warning'."""
        from src.config.usage_config import ProviderConfig, UsageTracker

        warning_threshold = ProviderConfig.WARNING_THRESHOLD * 100  # 80
        result = UsageTracker._get_warning_level(warning_threshold)
        assert result == "warning"

    def test_warning_level_critical(self) -> None:
        """Percentage at critical threshold should return 'critical'."""
        from src.config.usage_config import ProviderConfig, UsageTracker

        critical_threshold = ProviderConfig.CRITICAL_THRESHOLD * 100  # 95
        result = UsageTracker._get_warning_level(critical_threshold)
        assert result == "critical"


class TestUsageTrackerDaysRemaining:
    """Test cases for UsageTracker._get_days_remaining_in_month() method."""

    def test_days_remaining_positive(self) -> None:
        """Should return positive number of days."""
        from src.config.usage_config import UsageTracker

        result = UsageTracker._get_days_remaining_in_month()

        assert result > 0
        assert result <= 31


class TestUsageTrackerResetMonthly:
    """Test cases for UsageTracker._reset_monthly_usage() method."""

    def test_reset_monthly_usage_clears_counters(self) -> None:
        """Reset should clear monthly counters."""
        from src.config.usage_config import UsageTracker

        old_usage = {
            "current_month": "2024-01",
            "meteostat": {
                "requests_this_month": 100,
                "estimated_cost_usd": 0.1,
                "daily_breakdown": {"2024-01-15": 50},
            },
            "open_meteo": {
                "requests_this_month": 50,
                "daily_breakdown": {"2024-01-15": 25},
            },
            "total_requests": 150,
        }

        result = UsageTracker._reset_monthly_usage(old_usage, "2024-02")

        assert result["current_month"] == "2024-02"
        assert result["meteostat"]["requests_this_month"] == 0
        assert result["open_meteo"]["requests_this_month"] == 0
        assert result["total_requests"] == 0
        assert result["meteostat"]["daily_breakdown"] == {}
        assert result["meteostat"]["estimated_cost_usd"] == 0.0


class TestUsageTrackerDailyBreakdown:
    """Test cases for UsageTracker.get_daily_breakdown() method."""

    def test_get_daily_breakdown_returns_dict(self) -> None:
        """Should return dictionary with daily breakdown."""
        from src.config.usage_config import UsageTracker

        result = UsageTracker.get_daily_breakdown("meteostat")

        assert isinstance(result, dict)

    def test_get_daily_breakdown_with_tracked_requests(
        self, config_fs: dict[str, str]
    ) -> None:
        """Should return tracked daily breakdown."""
        from src.config.usage_config import UsageTracker

        UsageTracker.track_request("meteostat", 10)

        result = UsageTracker.get_daily_breakdown("meteostat", days=1)

        # Should have today's data
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in result
        assert result[today] == 10

    def test_get_daily_breakdown_multiple_days(self, config_fs: dict[str, str]) -> None:
        """Should return breakdown for multiple days."""
        from src.config.usage_config import UsageTracker

        result = UsageTracker.get_daily_breakdown("meteostat", days=7)

        assert len(result) == 7

    def test_get_daily_breakdown_chronological_order(
        self, config_fs: dict[str, str]
    ) -> None:
        """Should return data in chronological order."""
        from src.config.usage_config import UsageTracker

        result = UsageTracker.get_daily_breakdown("meteostat", days=3)

        dates = list(result.keys())
        # First date should be oldest
        assert dates == sorted(dates)


class TestUsageTrackerReset:
    """Test cases for UsageTracker.reset_usage_data() method."""

    def test_reset_usage_data_removes_file(self, config_fs: dict[str, str]) -> None:
        """Reset should remove usage file."""
        from src.config.usage_config import UsageTracker

        # Create usage file
        config_fs["usage"] = json.dumps({"total_requests": 100})

        result = UsageTracker.reset_usage_data()

        assert result is True
        assert "usage" not in config_fs

    def test_reset_usage_data_when_no_file(self, config_fs: dict[str, str]) -> None:
        """Reset should succeed even when no file exists."""
        from src.config.usage_config import UsageTracker

        config_fs.pop("usage", None)

        result = UsageTracker.reset_usage_data()

        assert result is True


class TestIntegration:
    """Integration tests for usage_config module."""

    def test_track_and_get_summary_roundtrip(self, config_fs: dict[str, str]) -> None:
        """Tracking and getting summary should work correctly."""
        from src.config.usage_config import UsageTracker

        # Track some requests
        UsageTracker.track_request("meteostat", 100)
        UsageTracker.track_request("open_meteo", 50)

        # Get summary
        summary = UsageTracker.get_usage_summary()

        assert summary["meteostat_requests"] == 100
        assert summary["openmeteo_requests"] == 50
        assert summary["total_requests"] == 150

    def test_daily_breakdown_persists_across_loads(
        self, config_fs: dict[str, str]
    ) -> None:
        """Daily breakdown should persist across loads."""
        from src.config.usage_config import UsageTracker

        # Track requests
        UsageTracker.track_request("meteostat", 10)

        # Reload
        UsageTracker.load_usage_data()

        # Get breakdown
        breakdown = UsageTracker.get_daily_breakdown("meteostat", days=1)

        # Should have the tracked data
        today = datetime.now().strftime("%Y-%m-%d")
        assert breakdown.get(today, 0) == 10

    def test_warning_level_updates_with_usage(self, config_fs: dict[str, str]) -> None:
        """Warning level should update as usage increases."""
        from src.config.usage_config import APIConfig, UsageTracker

        # Track few requests - should be normal
        UsageTracker.track_request("meteostat", 100)
        summary = UsageTracker.get_usage_summary()
        assert summary["warning_level"] == "normal"

        # Track many requests - should reach warning
        UsageTracker.track_request(
            "meteostat",
            int(APIConfig.METEOSTAT_MONTHLY_LIMIT_RATE * 0.85) - 100,
        )
        summary = UsageTracker.get_usage_summary()
        assert summary["warning_level"] == "warning"

    def test_cost_estimation_accurate(self, config_fs: dict[str, str]) -> None:
        """Cost estimation should be accurate."""
        from src.config.usage_config import ProviderConfig, UsageTracker

        requests = 500
        UsageTracker.track_request("meteostat", requests)

        usage = UsageTracker.load_usage_data()
        expected_cost = requests * ProviderConfig.METEOSTAT_COST_PER_REQUEST

        assert usage["meteostat"]["estimated_cost_usd"] == expected_cost

    def test_multiple_providers_tracked_separately(
        self, config_fs: dict[str, str]
    ) -> None:
        """Multiple providers should be tracked separately."""
        from src.config.usage_config import UsageTracker

        UsageTracker.track_request("meteostat", 100)
        UsageTracker.track_request("open_meteo", 200)

        usage = UsageTracker.load_usage_data()

        assert usage["meteostat"]["requests_this_month"] == 100
        assert usage["open_meteo"]["requests_this_month"] == 200

    def test_reset_clears_all_data(self, config_fs: dict[str, str]) -> None:
        """Reset should clear all tracked data."""
        from src.config.usage_config import UsageTracker

        # Track some data
        UsageTracker.track_request("meteostat", 100)

        # Reset
        UsageTracker.reset_usage_data()

        # Load should return defaults
        usage = UsageTracker.load_usage_data()
        assert usage["total_requests"] == 0
        assert usage["meteostat"]["requests_this_month"] == 0
