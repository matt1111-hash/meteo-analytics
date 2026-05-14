"""Comprehensive tests for UsageTracker instance — get_daily_breakdown()."""

from __future__ import annotations

from datetime import datetime

from src.config.usage_config import UsageTracker


class TestUsageTrackerDailyBreakdown:
    """Test cases for UsageTracker.get_daily_breakdown() method."""

    def test_get_daily_breakdown_returns_dict(self, usage_tracker: UsageTracker) -> None:
        """Should return dictionary with daily breakdown."""
        result = usage_tracker.get_daily_breakdown("meteostat")

        assert isinstance(result, dict)

    def test_get_daily_breakdown_with_tracked_requests(self, usage_tracker: UsageTracker) -> None:
        """Should return tracked daily breakdown."""
        usage_tracker.track_request("meteostat", 10)

        result = usage_tracker.get_daily_breakdown("meteostat", days=1)

        today = datetime.now().strftime("%Y-%m-%d")
        assert today in result
        assert result[today] == 10

    def test_get_daily_breakdown_multiple_days(self, usage_tracker: UsageTracker) -> None:
        """Should return breakdown for multiple days."""
        result = usage_tracker.get_daily_breakdown("meteostat", days=7)

        assert len(result) == 7

    def test_get_daily_breakdown_chronological_order(self, usage_tracker: UsageTracker) -> None:
        """Should return data in chronological order."""
        result = usage_tracker.get_daily_breakdown("meteostat", days=3)

        dates = list(result.keys())
        assert dates == sorted(dates)
