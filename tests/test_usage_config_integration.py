"""Integration tests for UsageTracker instance."""

from __future__ import annotations

from datetime import datetime

from src.config.api_config import APIConfig
from src.config.provider_config import ProviderConfig
from src.config.usage_config import UsageTracker


class TestIntegration:
    """Integration tests for usage_config module."""

    def test_track_and_get_summary_roundtrip(self, usage_tracker: UsageTracker) -> None:
        """Tracking and getting summary should work correctly."""
        usage_tracker.track_request("meteostat", 100)
        usage_tracker.track_request("open-meteo", 50)

        summary = usage_tracker.get_usage_summary()

        assert summary["meteostat_requests"] == 100
        assert summary["openmeteo_requests"] == 50
        assert summary["total_requests"] == 150

    def test_daily_breakdown_persists_across_loads(self, usage_tracker: UsageTracker) -> None:
        """Daily breakdown should persist across loads."""
        usage_tracker.track_request("meteostat", 10)
        usage_tracker.load_usage_data()

        breakdown = usage_tracker.get_daily_breakdown("meteostat", days=1)

        today = datetime.now().strftime("%Y-%m-%d")
        assert breakdown.get(today, 0) == 10

    def test_warning_level_updates_with_usage(self, usage_tracker: UsageTracker) -> None:
        """Warning level should update as usage increases."""
        usage_tracker.track_request("meteostat", 100)
        summary = usage_tracker.get_usage_summary()
        assert summary["warning_level"] == "normal"

        usage_tracker.track_request(
            "meteostat",
            int(APIConfig.METEOSTAT_MONTHLY_LIMIT_RATE * 0.85) - 100,
        )
        summary = usage_tracker.get_usage_summary()
        assert summary["warning_level"] == "warning"

    def test_cost_estimation_accurate(self, usage_tracker: UsageTracker) -> None:
        """Cost estimation should be accurate."""
        requests = 500
        usage_tracker.track_request("meteostat", requests)

        usage = usage_tracker.load_usage_data()
        expected_cost = requests * ProviderConfig.METEOSTAT_COST_PER_REQUEST

        assert usage["meteostat"]["estimated_cost_usd"] == expected_cost

    def test_multiple_providers_tracked_separately(self, usage_tracker: UsageTracker) -> None:
        """Multiple providers should be tracked separately."""
        usage_tracker.track_request("meteostat", 100)
        usage_tracker.track_request("open-meteo", 200)

        usage = usage_tracker.load_usage_data()

        assert usage["meteostat"]["requests_this_month"] == 100
        assert usage["open-meteo"]["requests_this_month"] == 200

    def test_reset_clears_all_data(self, usage_tracker: UsageTracker) -> None:
        """Reset should clear all tracked data."""
        usage_tracker.track_request("meteostat", 100)
        usage_tracker.reset_usage_data()

        usage = usage_tracker.load_usage_data()
        assert usage["total_requests"] == 0
        assert usage["meteostat"]["requests_this_month"] == 0
