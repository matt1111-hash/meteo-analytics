"""Comprehensive tests for UsageTracker instance — reset_usage_data()."""

from __future__ import annotations

import json

from src.config.usage_config import UsageTracker


class TestUsageTrackerReset:
    """Test cases for UsageTracker.reset_usage_data() method."""

    def test_reset_usage_data_removes_file(
        self, config_fs: dict[str, str], usage_tracker: UsageTracker
    ) -> None:
        """Reset should remove usage file."""
        config_fs["usage"] = json.dumps({"total_requests": 100})

        result = usage_tracker.reset_usage_data()

        assert result is True
        assert "usage" not in config_fs

    def test_reset_usage_data_when_no_file(
        self, config_fs: dict[str, str], usage_tracker: UsageTracker
    ) -> None:
        """Reset should succeed even when no file exists."""
        config_fs.pop("usage", None)

        result = usage_tracker.reset_usage_data()

        assert result is True
