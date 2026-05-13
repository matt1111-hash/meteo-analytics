#!/usr/bin/env python3
"""
Tests for src/analytics/ports/__init__.py
Analytics Layer Ports (Abstractions)
"""

from dataclasses import fields
from typing import Protocol

from src.analytics.ports import (
    MultiCityEngineConfig,
    MultiCityEnginePort,
)


class TestMultiCityEngineConfig:
    """Test MultiCityEngineConfig dataclass."""

    def test_default_values(self) -> None:
        """Should have correct default values."""
        config = MultiCityEngineConfig()
        assert config.max_workers == 8
        assert config.request_timeout == 90
        assert config.max_retries == 2
        assert config.retry_delay == 3.0

    def test_custom_values(self) -> None:
        """Should accept custom values."""
        config = MultiCityEngineConfig(
            max_workers=16,
            request_timeout=120,
            max_retries=5,
            retry_delay=5.0,
        )
        assert config.max_workers == 16
        assert config.request_timeout == 120
        assert config.max_retries == 5
        assert config.retry_delay == 5.0

    def test_is_dataclass(self) -> None:
        """Should be a dataclass."""
        from dataclasses import is_dataclass  # noqa: PLC0415

        assert is_dataclass(MultiCityEngineConfig)

    def test_field_count(self) -> None:
        """Should have exactly 4 fields."""
        field_list = list(fields(MultiCityEngineConfig))
        assert len(field_list) == 4


class TestMultiCityEnginePort:
    """Test MultiCityEnginePort protocol."""

    def test_is_protocol(self) -> None:
        """Should be a Protocol."""
        assert issubclass(MultiCityEnginePort, Protocol)

    def test_has_required_methods(self) -> None:
        """Should define required methods."""
        required_methods = [
            "analyze_multi_city",
            "execute_analytics_query",
            "get_cities_for_region",
            "resolve_region_name",
        ]
        for method in required_methods:
            assert hasattr(MultiCityEnginePort, method)
