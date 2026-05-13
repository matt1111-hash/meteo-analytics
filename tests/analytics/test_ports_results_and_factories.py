#!/usr/bin/env python3
"""
Tests for src/analytics/ports/__init__.py
Analytics Layer Ports (Abstractions)
"""

from unittest.mock import MagicMock, patch

from src.analytics.ports import (
    MultiCityEngineConfig,
    WindAnalysisResult,
    get_multi_city_engine_port,
)


class TestWindAnalysisResult:
    """Test WindAnalysisResult dataclass."""

    def test_requires_data_parameter(self) -> None:
        """data field is required."""
        result = WindAnalysisResult(
            windy_days_count=5,
            total_days=30,
            windy_percentage=16.67,
            max_wind_speed=80.5,
            max_wind_date="2026-02-10",
            avg_wind_speed=25.3,
            data=[],
            threshold=50.0,
        )
        assert result.data == []

    def test_custom_data_list(self) -> None:
        """Should accept custom data list."""
        custom_data = [{"date": "2026-02-10", "speed": 80.5}]
        result = WindAnalysisResult(
            windy_days_count=1,
            total_days=30,
            windy_percentage=3.33,
            max_wind_speed=80.5,
            max_wind_date="2026-02-10",
            avg_wind_speed=25.3,
            data=custom_data,
            threshold=50.0,
        )
        assert result.data == custom_data

    def test_field_types(self) -> None:
        """Should have correct field types."""
        result = WindAnalysisResult(
            windy_days_count=5,
            total_days=30,
            windy_percentage=16.67,
            max_wind_speed=80.5,
            max_wind_date="2026-02-10",
            avg_wind_speed=25.3,
            data=[],
            threshold=50.0,
        )
        assert isinstance(result.windy_days_count, int)
        assert isinstance(result.total_days, int)
        assert isinstance(result.windy_percentage, float)
        assert isinstance(result.max_wind_speed, float)
        assert isinstance(result.max_wind_date, str)
        assert isinstance(result.avg_wind_speed, float)
        assert isinstance(result.data, list)
        assert isinstance(result.threshold, float)


class TestGetMultiCityEnginePort:
    """Test get_multi_city_engine_port factory function."""

    def test_returns_multi_city_engine_port(self) -> None:
        """Should return MultiCityEnginePort implementation."""
        with (
            patch("src.analytics.multi_city_engine_core.MultiCityEngine") as mock_engine_class,
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
        ):
            mock_instance = MagicMock()
            mock_engine_class.return_value = mock_instance

            result = get_multi_city_engine_port()

            mock_engine_class.assert_called_once()
            assert result == mock_instance

    def test_accepts_optional_city_repository(self) -> None:
        """Should accept optional city_repository parameter."""
        mock_repo = MagicMock()

        with (
            patch("src.analytics.multi_city_engine_core.MultiCityEngine") as mock_engine_class,
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
        ):
            mock_instance = MagicMock()
            mock_engine_class.return_value = mock_instance

            get_multi_city_engine_port(city_repository=mock_repo)

            call_kwargs = mock_engine_class.call_args[1]
            assert call_kwargs["city_repository"] == mock_repo

    def test_accepts_optional_weather_client(self) -> None:
        """Should accept optional weather_client parameter."""
        mock_client = MagicMock()

        with (
            patch("src.analytics.multi_city_engine_core.MultiCityEngine") as mock_engine_class,
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
        ):
            mock_instance = MagicMock()
            mock_engine_class.return_value = mock_instance

            get_multi_city_engine_port(weather_client=mock_client)

            call_kwargs = mock_engine_class.call_args[1]
            assert call_kwargs["city_repository"] is None

    def test_accepts_optional_config(self) -> None:
        """Should accept optional config parameter (but doesn't pass it)."""
        config = MultiCityEngineConfig(max_workers=16)

        with (
            patch("src.analytics.multi_city_engine_core.MultiCityEngine") as mock_engine_class,
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
        ):
            mock_instance = MagicMock()
            mock_engine_class.return_value = mock_instance

            get_multi_city_engine_port(config=config)

            mock_engine_class.assert_called_once()
