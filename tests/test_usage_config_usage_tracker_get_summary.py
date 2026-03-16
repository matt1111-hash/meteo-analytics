"""Comprehensive tests for src/config/usage_config.py."""

from __future__ import annotations


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
