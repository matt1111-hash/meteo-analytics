"""Comprehensive tests for UsageTracker instance — _get_days_remaining_in_month()."""

from __future__ import annotations

from src.config.usage_config import UsageTracker


class TestUsageTrackerDaysRemaining:
    """Test cases for UsageTracker._get_days_remaining_in_month() method."""

    def test_days_remaining_positive(self, usage_tracker: UsageTracker) -> None:
        """Should return positive number of days."""
        result = usage_tracker._get_days_remaining_in_month()

        assert result > 0
        assert result <= 31
