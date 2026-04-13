"""Comprehensive tests for src/config/usage_config.py."""

from __future__ import annotations

from datetime import datetime


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

    def test_track_request_updates_daily_breakdown(self, config_fs: dict[str, str]) -> None:
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

        result = UsageTracker.track_request("unknown_provider", 5)

        assert result["total_requests"] == 5
