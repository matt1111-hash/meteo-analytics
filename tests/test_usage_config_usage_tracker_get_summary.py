"""Comprehensive tests for UsageTracker instance — get_usage_summary()."""

from __future__ import annotations

from src.config.usage_config import UsageTracker


class TestUsageTrackerGetSummary:
    """Test cases for UsageTracker.get_usage_summary() method."""

    def test_get_usage_summary_returns_all_fields(self, usage_tracker: UsageTracker) -> None:
        """Should return all summary fields."""
        summary = usage_tracker.get_usage_summary()

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

    def test_get_usage_summary_with_tracked_requests(self, usage_tracker: UsageTracker) -> None:
        """Summary should reflect tracked requests."""
        usage_tracker.track_request("meteostat", 100)
        usage_tracker.track_request("open-meteo", 50)

        summary = usage_tracker.get_usage_summary()

        assert summary["meteostat_requests"] == 100
        assert summary["openmeteo_requests"] == 50
        assert summary["total_requests"] == 150
