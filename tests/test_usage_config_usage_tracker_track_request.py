"""Comprehensive tests for UsageTracker instance — track_request()."""

from __future__ import annotations

from datetime import datetime

from src.config.usage_config import UsageTracker


class TestUsageTrackerTrackRequest:
    """Test cases for UsageTracker.track_request() method."""

    def test_track_request_meteostat(self, usage_tracker: UsageTracker) -> None:
        """Tracking Meteostat request should update counters and cost."""
        result = usage_tracker.track_request("meteostat", 5)

        assert result["meteostat"]["requests_this_month"] == 5
        assert result["meteostat"]["estimated_cost_usd"] > 0
        assert result["total_requests"] == 5
        assert "last_request" in result["meteostat"]

    def test_track_request_open_meteo(self, usage_tracker: UsageTracker) -> None:
        """Tracking Open-Meteo request should update counters."""
        result = usage_tracker.track_request("open-meteo", 3)

        assert result["open-meteo"]["requests_this_month"] == 3
        assert result["total_requests"] == 3
        assert "last_request" in result["open-meteo"]

    def test_track_request_accumulates(self, usage_tracker: UsageTracker) -> None:
        """Multiple track_request calls should accumulate."""
        usage_tracker.track_request("meteostat", 5)
        usage_tracker.track_request("meteostat", 3)

        usage = usage_tracker.load_usage_data()
        assert usage["meteostat"]["requests_this_month"] == 8

    def test_track_request_updates_daily_breakdown(self, usage_tracker: UsageTracker) -> None:
        """Tracking should update daily breakdown."""
        usage_tracker.track_request("meteostat", 5)

        usage = usage_tracker.load_usage_data()
        today = datetime.now().strftime("%Y-%m-%d")

        assert today in usage["meteostat"]["daily_breakdown"]
        assert usage["meteostat"]["daily_breakdown"][today] == 5

    def test_track_request_unknown_provider(self, usage_tracker: UsageTracker) -> None:
        """Unknown provider should log warning but not crash."""
        result = usage_tracker.track_request("unknown_provider", 5)

        assert result["total_requests"] == 5
