"""Tests for module helper functions in usage_config_helpers."""

from __future__ import annotations

from datetime import datetime

from src.config.usage_config import UsageTracker, build_usage_tracker
from src.config.usage_config_helpers import _get_datetime_cls, _now, _resolve_config_attr


class TestModuleHelpers:
    """Test cases for module helper functions."""

    def test_resolve_config_attr_with_fallback(self) -> None:
        """Should return fallback when attribute not in config module."""
        result = _resolve_config_attr("nonexistent_attr", "fallback_value")
        assert result == "fallback_value"

    def test_build_usage_tracker_returns_instance(self) -> None:
        """build_usage_tracker should return a UsageTracker instance."""
        tracker = build_usage_tracker()
        assert isinstance(tracker, UsageTracker)

    def test_get_datetime_cls_returns_datetime_class(self) -> None:
        """Should return datetime class."""
        result = _get_datetime_cls()
        assert result is datetime

    def test_now_returns_datetime(self) -> None:
        """Should return current datetime."""
        result = _now()
        assert isinstance(result, datetime)
