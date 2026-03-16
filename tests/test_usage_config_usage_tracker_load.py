"""Comprehensive tests for src/config/usage_config.py."""

from __future__ import annotations

from datetime import datetime

import pytest


class TestUsageTrackerLoad:
    """Test cases for UsageTracker.load_usage_data() method."""

    def test_load_usage_returns_default_when_file_missing(
        self, config_fs: dict[str, str]
    ) -> None:
        """Missing usage file should return default usage data."""
        from src.config.usage_config import UsageTracker

        config_fs.pop("usage", None)

        usage = UsageTracker.load_usage_data()

        assert "current_month" in usage
        assert "meteostat" in usage
        assert "open_meteo" in usage
        assert usage["meteostat"]["requests_this_month"] == 0
        assert usage["open_meteo"]["requests_this_month"] == 0
        assert usage["total_requests"] == 0

    def test_load_usage_returns_saved_data(self, config_fs: dict[str, str]) -> None:
        """Should return saved usage data."""
        from src.config.usage_config import UsageTracker

        UsageTracker.track_request("meteostat", 100)
        UsageTracker.track_request("open_meteo", 50)

        usage = UsageTracker.load_usage_data()

        assert usage["meteostat"]["requests_this_month"] == 100
        assert usage["open_meteo"]["requests_this_month"] == 50
        assert usage["total_requests"] == 150

    def test_load_usage_resets_on_new_month(
        self, config_fs: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should reset usage data when month changes."""
        from src import config
        from src.config.usage_config import UsageTracker

        UsageTracker.track_request("meteostat", 100)

        usage = UsageTracker.load_usage_data()
        usage["current_month"] = "2024-01"
        UsageTracker.save_usage_data(usage)

        fixed_now = datetime(2024, 2, 15, 12, 0, 0)

        class FakeDatetime:
            @classmethod
            def now(cls):
                return fixed_now

        monkeypatch.setattr(config, "datetime", FakeDatetime)

        usage = UsageTracker.load_usage_data()

        assert usage["current_month"] == "2024-02"
        assert usage["meteostat"]["requests_this_month"] == 0
        assert usage["total_requests"] == 0

    def test_load_usage_handles_corrupted_json(self, config_fs: dict[str, str]) -> None:
        """Corrupted JSON should return default usage data."""
        from src.config.usage_config import UsageTracker

        config_fs["usage"] = "{ not valid json"

        usage = UsageTracker.load_usage_data()

        assert usage["total_requests"] == 0
        assert usage["meteostat"]["requests_this_month"] == 0
