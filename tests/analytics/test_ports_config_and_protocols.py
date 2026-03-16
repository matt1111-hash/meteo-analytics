#!/usr/bin/env python3
"""
Tests for src/analytics/ports/__init__.py
Analytics Layer Ports (Abstractions)
"""

from dataclasses import fields
from typing import Protocol

from src.analytics.ports import (
    AnalyticsQueryPort,
    AnomalyDetectionPort,
    MultiCityEngineConfig,
    MultiCityEnginePort,
    QueryTypeConfigPort,
    WindAnalysisPort,
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
        from dataclasses import is_dataclass

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


class TestWindAnalysisPort:
    """Test WindAnalysisPort protocol."""

    def test_is_protocol(self) -> None:
        """Should be a Protocol."""
        assert issubclass(WindAnalysisPort, Protocol)

    def test_has_required_methods(self) -> None:
        """Should define required methods."""
        required_methods = [
            "analyze_wind_data",
            "detect_windy_days",
            "calculate_wind_statistics",
        ]
        for method in required_methods:
            assert hasattr(WindAnalysisPort, method)

    def test_has_threshold_constant(self) -> None:
        """Should define WINDY_DAY_THRESHOLD_KMH."""
        assert hasattr(WindAnalysisPort, "WINDY_DAY_THRESHOLD_KMH")
        assert WindAnalysisPort.WINDY_DAY_THRESHOLD_KMH == 50.0


class TestAnomalyDetectionPort:
    """Test AnomalyDetectionPort protocol."""

    def test_is_protocol(self) -> None:
        """Should be a Protocol."""
        assert issubclass(AnomalyDetectionPort, Protocol)

    def test_has_required_methods(self) -> None:
        """Should define required methods."""
        required_methods = [
            "detect_anomalies",
            "classify_severity",
            "calculate_z_score",
        ]
        for method in required_methods:
            assert hasattr(AnomalyDetectionPort, method)


class TestAnalyticsQueryPort:
    """Test AnalyticsQueryPort protocol."""

    def test_is_protocol(self) -> None:
        """Should be a Protocol."""
        assert issubclass(AnalyticsQueryPort, Protocol)

    def test_has_required_methods(self) -> None:
        """Should define required methods."""
        required_methods = ["create_query", "validate_query"]
        for method in required_methods:
            assert hasattr(AnalyticsQueryPort, method)


class TestQueryTypeConfigPort:
    """Test QueryTypeConfigPort protocol."""

    def test_is_protocol(self) -> None:
        """Should be a Protocol."""
        assert issubclass(QueryTypeConfigPort, Protocol)

    def test_has_required_methods(self) -> None:
        """Should define required methods."""
        required_methods = [
            "get_query_types",
            "get_query_type",
            "get_metric_for_query_type",
            "get_unit_for_query_type",
        ]
        for method in required_methods:
            assert hasattr(QueryTypeConfigPort, method)
