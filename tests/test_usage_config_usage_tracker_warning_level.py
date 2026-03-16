"""Comprehensive tests for src/config/usage_config.py."""

from __future__ import annotations


class TestUsageTrackerWarningLevel:
    """Test cases for UsageTracker._get_warning_level() method."""

    def test_warning_level_normal(self) -> None:
        """Low percentage should return 'normal'."""
        from src.config.usage_config import UsageTracker

        result = UsageTracker._get_warning_level(50.0)
        assert result == "normal"

    def test_warning_level_warning(self) -> None:
        """Percentage at warning threshold should return 'warning'."""
        from src.config.usage_config import ProviderConfig, UsageTracker

        warning_threshold = ProviderConfig.WARNING_THRESHOLD * 100
        result = UsageTracker._get_warning_level(warning_threshold)
        assert result == "warning"

    def test_warning_level_critical(self) -> None:
        """Percentage at critical threshold should return 'critical'."""
        from src.config.usage_config import ProviderConfig, UsageTracker

        critical_threshold = ProviderConfig.CRITICAL_THRESHOLD * 100
        result = UsageTracker._get_warning_level(critical_threshold)
        assert result == "critical"
