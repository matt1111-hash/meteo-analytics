"""Comprehensive tests for src/config/usage_config.py."""

from __future__ import annotations


class TestUsageTrackerDaysRemaining:
    """Test cases for UsageTracker._get_days_remaining_in_month() method."""

    def test_days_remaining_positive(self) -> None:
        """Should return positive number of days."""
        from src.config.usage_config import UsageTracker  # noqa: PLC0415

        result = UsageTracker._get_days_remaining_in_month()

        assert result > 0
        assert result <= 31
