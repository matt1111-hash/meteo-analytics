"""Comprehensive tests for src/config/usage_config.py."""

from __future__ import annotations

from datetime import datetime


class TestIntegration:
    """Integration tests for usage_config module."""

    def test_track_and_get_summary_roundtrip(self, config_fs: dict[str, str]) -> None:
        """Tracking and getting summary should work correctly."""
        from src.config.usage_config import UsageTracker  # noqa: PLC0415

        UsageTracker.track_request("meteostat", 100)
        UsageTracker.track_request("open-meteo", 50)

        summary = UsageTracker.get_usage_summary()

        assert summary["meteostat_requests"] == 100
        assert summary["openmeteo_requests"] == 50
        assert summary["total_requests"] == 150

    def test_daily_breakdown_persists_across_loads(self, config_fs: dict[str, str]) -> None:
        """Daily breakdown should persist across loads."""
        from src.config.usage_config import UsageTracker  # noqa: PLC0415

        UsageTracker.track_request("meteostat", 10)
        UsageTracker.load_usage_data()

        breakdown = UsageTracker.get_daily_breakdown("meteostat", days=1)

        today = datetime.now().strftime("%Y-%m-%d")
        assert breakdown.get(today, 0) == 10

    def test_warning_level_updates_with_usage(self, config_fs: dict[str, str]) -> None:
        """Warning level should update as usage increases."""
        from src.config.usage_config import APIConfig, UsageTracker  # noqa: PLC0415

        UsageTracker.track_request("meteostat", 100)
        summary = UsageTracker.get_usage_summary()
        assert summary["warning_level"] == "normal"

        UsageTracker.track_request(
            "meteostat",
            int(APIConfig.METEOSTAT_MONTHLY_LIMIT_RATE * 0.85) - 100,
        )
        summary = UsageTracker.get_usage_summary()
        assert summary["warning_level"] == "warning"

    def test_cost_estimation_accurate(self, config_fs: dict[str, str]) -> None:
        """Cost estimation should be accurate."""
        from src.config.usage_config import ProviderConfig, UsageTracker  # noqa: PLC0415

        requests = 500
        UsageTracker.track_request("meteostat", requests)

        usage = UsageTracker.load_usage_data()
        expected_cost = requests * ProviderConfig.METEOSTAT_COST_PER_REQUEST

        assert usage["meteostat"]["estimated_cost_usd"] == expected_cost

    def test_multiple_providers_tracked_separately(self, config_fs: dict[str, str]) -> None:
        """Multiple providers should be tracked separately."""
        from src.config.usage_config import UsageTracker  # noqa: PLC0415

        UsageTracker.track_request("meteostat", 100)
        UsageTracker.track_request("open-meteo", 200)

        usage = UsageTracker.load_usage_data()

        assert usage["meteostat"]["requests_this_month"] == 100
        assert usage["open-meteo"]["requests_this_month"] == 200

    def test_reset_clears_all_data(self, config_fs: dict[str, str]) -> None:
        """Reset should clear all tracked data."""
        from src.config.usage_config import UsageTracker  # noqa: PLC0415

        UsageTracker.track_request("meteostat", 100)
        UsageTracker.reset_usage_data()

        usage = UsageTracker.load_usage_data()
        assert usage["total_requests"] == 0
        assert usage["meteostat"]["requests_this_month"] == 0
