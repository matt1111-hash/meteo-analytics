"""Comprehensive tests for src/config/usage_config.py."""

from __future__ import annotations


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
