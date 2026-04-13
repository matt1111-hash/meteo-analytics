"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations

from pathlib import Path


class TestModuleHelpers:
    """Test cases for module helper functions."""

    def test_resolve_config_attr_with_fallback(self) -> None:
        """Should return fallback when attribute not in config module."""
        from src.config.provider_config import _resolve_config_attr  # noqa: PLC0415

        result = _resolve_config_attr("nonexistent_attr", "fallback_value")
        assert result == "fallback_value"

    def test_get_provider_prefs_file_returns_path(self) -> None:
        """Should return a Path object."""
        from src.config.provider_config import _get_provider_prefs_file  # noqa: PLC0415

        result = _get_provider_prefs_file()
        assert isinstance(result, Path)

    def test_freeze_value_preserves_data(self) -> None:
        """Freezing should preserve the original data structure."""
        from src.config.provider_config import _freeze_value  # noqa: PLC0415

        original = {
            "string": "value",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }

        frozen = _freeze_value(original)

        assert frozen["string"] == "value"
        assert frozen["number"] == 42
        assert frozen["list"] == (1, 2, 3)
        assert frozen["nested"]["key"] == "value"
