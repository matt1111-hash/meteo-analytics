"""Comprehensive tests for UsageTracker instance — _get_warning_level()."""

from __future__ import annotations

from src.config.provider_config import ProviderConfig
from src.config.usage_config import UsageTracker


class TestUsageTrackerWarningLevel:
    """Test cases for UsageTracker._get_warning_level() method."""

    def test_warning_level_normal(self, usage_tracker: UsageTracker) -> None:
        """Low percentage should return 'normal'."""
        result = usage_tracker._get_warning_level(50.0)
        assert result == "normal"

    def test_warning_level_warning(self, usage_tracker: UsageTracker) -> None:
        """Percentage at warning threshold should return 'warning'."""
        warning_threshold = ProviderConfig.WARNING_THRESHOLD * 100
        result = usage_tracker._get_warning_level(warning_threshold)
        assert result == "warning"

    def test_warning_level_critical(self, usage_tracker: UsageTracker) -> None:
        """Percentage at critical threshold should return 'critical'."""
        critical_threshold = ProviderConfig.CRITICAL_THRESHOLD * 100
        result = usage_tracker._get_warning_level(critical_threshold)
        assert result == "critical"
