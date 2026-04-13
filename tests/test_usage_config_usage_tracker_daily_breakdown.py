"""Comprehensive tests for src/config/usage_config.py."""

from __future__ import annotations

from datetime import datetime


class TestUsageTrackerDailyBreakdown:
    """Test cases for UsageTracker.get_daily_breakdown() method."""

    def test_get_daily_breakdown_returns_dict(self) -> None:
        """Should return dictionary with daily breakdown."""
        from src.config.usage_config import UsageTracker

        result = UsageTracker.get_daily_breakdown("meteostat")

        assert isinstance(result, dict)

    def test_get_daily_breakdown_with_tracked_requests(self, config_fs: dict[str, str]) -> None:
        """Should return tracked daily breakdown."""
        from src.config.usage_config import UsageTracker

        UsageTracker.track_request("meteostat", 10)

        result = UsageTracker.get_daily_breakdown("meteostat", days=1)

        today = datetime.now().strftime("%Y-%m-%d")
        assert today in result
        assert result[today] == 10

    def test_get_daily_breakdown_multiple_days(self, config_fs: dict[str, str]) -> None:
        """Should return breakdown for multiple days."""
        from src.config.usage_config import UsageTracker

        result = UsageTracker.get_daily_breakdown("meteostat", days=7)

        assert len(result) == 7

    def test_get_daily_breakdown_chronological_order(self, config_fs: dict[str, str]) -> None:
        """Should return data in chronological order."""
        from src.config.usage_config import UsageTracker

        result = UsageTracker.get_daily_breakdown("meteostat", days=3)

        dates = list(result.keys())
        assert dates == sorted(dates)
