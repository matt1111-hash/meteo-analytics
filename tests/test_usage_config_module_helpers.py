"""Comprehensive tests for src/config/usage_config.py."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


class TestModuleHelpers:
    """Test cases for module helper functions."""

    def test_resolve_config_attr_with_fallback(self) -> None:
        """Should return fallback when attribute not in config module."""
        from src.config.usage_config import _resolve_config_attr

        result = _resolve_config_attr("nonexistent_attr", "fallback_value")
        assert result == "fallback_value"

    def test_get_usage_tracking_file_returns_path(self) -> None:
        """Should return a Path object."""
        from src.config.usage_config import _get_usage_tracking_file

        result = _get_usage_tracking_file()
        assert isinstance(result, Path)

    def test_get_datetime_cls_returns_datetime_class(self) -> None:
        """Should return datetime class."""
        from src.config.usage_config import _get_datetime_cls

        result = _get_datetime_cls()
        assert result is datetime

    def test_now_returns_datetime(self) -> None:
        """Should return current datetime."""
        from src.config.usage_config import _now

        result = _now()
        assert isinstance(result, datetime)
