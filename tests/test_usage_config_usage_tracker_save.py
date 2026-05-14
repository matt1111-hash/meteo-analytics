"""Comprehensive tests for UsageTracker instance — save_usage_data()."""

from __future__ import annotations

import json

from src.config.usage_config import UsageTracker


class TestUsageTrackerSave:
    """Test cases for UsageTracker.save_usage_data() method."""

    def test_save_usage_writes_to_file(
        self, config_fs: dict[str, str], usage_tracker: UsageTracker
    ) -> None:
        """Saving usage data should write to file."""
        usage_data = {
            "current_month": "2024-01",
            "meteostat": {"requests_this_month": 10},
            "open-meteo": {"requests_this_month": 5},
            "total_requests": 15,
        }

        result = usage_tracker.save_usage_data(usage_data)

        assert result is True
        assert "usage" in config_fs

        saved = json.loads(config_fs["usage"])
        assert saved["total_requests"] == 15

    def test_save_usage_adds_timestamp(
        self, config_fs: dict[str, str], usage_tracker: UsageTracker
    ) -> None:
        """Saving should add last_updated timestamp."""
        usage_data = {"total_requests": 5}

        usage_tracker.save_usage_data(usage_data)

        saved = json.loads(config_fs["usage"])
        assert "last_updated" in saved
