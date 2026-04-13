"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations

from types import MappingProxyType

import pytest


class TestFreezeValue:
    """Test cases for _freeze_value() function."""

    def test_freeze_value_with_dict(self) -> None:
        """Freezing a dict should return MappingProxyType."""
        from src.config.provider_config import _freeze_value  # noqa: PLC0415

        result = _freeze_value({"key": "value", "nested": {"inner": "data"}})

        assert isinstance(result, MappingProxyType)
        with pytest.raises(TypeError):
            result["new_key"] = "new_value"

    def test_freeze_value_with_list(self) -> None:
        """Freezing a list should return a tuple."""
        from src.config.provider_config import _freeze_value  # noqa: PLC0415

        result = _freeze_value([1, 2, 3, "four"])

        assert isinstance(result, tuple)
        assert result == (1, 2, 3, "four")

    def test_freeze_value_with_nested_structures(self) -> None:
        """Freezing nested structures should recursively freeze all elements."""
        from src.config.provider_config import _freeze_value  # noqa: PLC0415

        result = _freeze_value(
            {
                "dict_value": {"inner": "data"},
                "list_value": [1, 2, {"nested": "dict"}],
                "string": "text",
                "int": 42,
            }
        )

        assert isinstance(result, MappingProxyType)
        assert isinstance(result["list_value"], tuple)
        assert isinstance(result["dict_value"], MappingProxyType)
        assert isinstance(result["list_value"][2], MappingProxyType)

    def test_freeze_value_with_primitives(self) -> None:
        """Freezing primitive values should return them unchanged."""
        from src.config.provider_config import _freeze_value  # noqa: PLC0415

        assert _freeze_value("string") == "string"
        assert _freeze_value(42) == 42
        assert _freeze_value(3.14) == 3.14
        assert _freeze_value(True) is True
        assert _freeze_value(None) is None
