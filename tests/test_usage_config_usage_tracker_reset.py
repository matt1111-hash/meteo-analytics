"""Comprehensive tests for src/config/usage_config.py."""

from __future__ import annotations

import json


class TestUsageTrackerReset:
    """Test cases for UsageTracker.reset_usage_data() method."""

    def test_reset_usage_data_removes_file(self, config_fs: dict[str, str]) -> None:
        """Reset should remove usage file."""
        from src.config.usage_config import UsageTracker

        config_fs["usage"] = json.dumps({"total_requests": 100})

        result = UsageTracker.reset_usage_data()

        assert result is True
        assert "usage" not in config_fs

    def test_reset_usage_data_when_no_file(self, config_fs: dict[str, str]) -> None:
        """Reset should succeed even when no file exists."""
        from src.config.usage_config import UsageTracker

        config_fs.pop("usage", None)

        result = UsageTracker.reset_usage_data()

        assert result is True
