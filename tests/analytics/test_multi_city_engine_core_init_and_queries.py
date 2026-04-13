#!/usr/bin/env python3
"""
Tests for src/analytics/multi_city_engine_core.py
Main MultiCityEngine class for multi-city weather analytics
"""

from unittest.mock import MagicMock, patch

from tests.analytics.multi_city_engine_core_support import (
    AnalyticsMetric,
    MultiCityEngine,
)

pytest_plugins = ("tests.analytics.multi_city_engine_core_support",)


class TestMultiCityEngineInit:
    """Test MultiCityEngine initialization."""

    def test_initializes_with_default_paths(self, mock_city_repository: MagicMock) -> None:
        """Should initialize with default database paths."""
        with (
            patch(
                "src.analytics.multi_city_engine_core.get_city_repository_port",
                return_value=mock_city_repository,
            ),
            patch(
                "src.analytics.multi_city_engine_core.get_weather_client_port",
                return_value=MagicMock(),
            ),
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
            patch("src.analytics.multi_city_engine_core.WeatherFetchService"),
            patch("src.analytics.multi_city_engine_core.AnalyticsTransformService"),
            patch("src.analytics.multi_city_engine_core.AnalyzeMultiCityUseCase"),
        ):
            engine = MultiCityEngine(city_repository=mock_city_repository)

            assert engine.db_path.name == "cities.db"
            assert engine.hungarian_db_path.name == "hungarian_settlements.db"

    def test_initializes_with_custom_paths(self, mock_city_repository: MagicMock) -> None:
        """Should accept custom database paths."""
        with (
            patch(
                "src.analytics.multi_city_engine_core.get_city_repository_port",
                return_value=mock_city_repository,
            ),
            patch(
                "src.analytics.multi_city_engine_core.get_weather_client_port",
                return_value=MagicMock(),
            ),
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
            patch("src.analytics.multi_city_engine_core.WeatherFetchService"),
            patch("src.analytics.multi_city_engine_core.AnalyticsTransformService"),
            patch("src.analytics.multi_city_engine_core.AnalyzeMultiCityUseCase"),
        ):
            engine = MultiCityEngine(
                db_path="/custom/cities.db",
                hungarian_db_path="/custom/hungarian.db",
                city_repository=mock_city_repository,
            )

            assert str(engine.db_path) == "/custom/cities.db"
            assert str(engine.hungarian_db_path) == "/custom/hungarian.db"

    def test_initializes_default_configuration(self, mock_city_repository: MagicMock) -> None:
        """Should have default configuration values."""
        with (
            patch(
                "src.analytics.multi_city_engine_core.get_city_repository_port",
                return_value=mock_city_repository,
            ),
            patch(
                "src.analytics.multi_city_engine_core.get_weather_client_port",
                return_value=MagicMock(),
            ),
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
            patch("src.analytics.multi_city_engine_core.WeatherFetchService"),
            patch("src.analytics.multi_city_engine_core.AnalyticsTransformService"),
            patch("src.analytics.multi_city_engine_core.AnalyzeMultiCityUseCase"),
        ):
            engine = MultiCityEngine(city_repository=mock_city_repository)

            assert engine.max_workers == 8
            assert engine.request_timeout == 90
            assert engine.max_retries == 2
            assert engine.retry_delay == 3.0

    def test_handles_weather_client_import_error(self, mock_city_repository: MagicMock) -> None:
        """Should handle ImportError when weather client is not available."""
        with (
            patch(
                "src.analytics.multi_city_engine_core.get_city_repository_port",
                return_value=mock_city_repository,
            ),
            patch(
                "src.analytics.multi_city_engine_core.get_weather_client_port",
                side_effect=ImportError("No module"),
            ),
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
            patch("src.analytics.multi_city_engine_core.WeatherFetchService"),
            patch("src.analytics.multi_city_engine_core.AnalyticsTransformService"),
            patch("src.analytics.multi_city_engine_core.AnalyzeMultiCityUseCase"),
        ):
            engine = MultiCityEngine(city_repository=mock_city_repository)

            assert engine.weather_client is None


class TestMultiCityEngineQueryTypes:
    """Test QUERY_TYPES configuration."""

    def test_query_types_exist(self) -> None:
        """QUERY_TYPES should be defined."""
        assert hasattr(MultiCityEngine, "QUERY_TYPES")
        assert isinstance(MultiCityEngine.QUERY_TYPES, dict)

    def test_query_types_has_required_entries(self) -> None:
        """QUERY_TYPES should have all required query types."""
        required_types = [
            "hottest_today",
            "coldest_today",
            "temperature_mean",
            "wettest_today",
            "windiest_today",
            "wind_gusts",
            "temperature_range",
        ]
        for qt in required_types:
            assert qt in MultiCityEngine.QUERY_TYPES, f"Missing query type: {qt}"

    def test_query_types_have_required_fields(self) -> None:
        """Each query type should have required fields."""
        required_fields = [
            "name",
            "metric",
            "unit",
            "sort_desc",
            "question_template",
            "metric_enum",
        ]
        for qt_name, qt_config in MultiCityEngine.QUERY_TYPES.items():
            for field in required_fields:
                assert field in qt_config, f"Missing field {field} in {qt_name}"

    def test_hottest_today_config(self) -> None:
        """hottest_today should have correct configuration."""
        config = MultiCityEngine.QUERY_TYPES["hottest_today"]
        assert config["name"] == "Legmelegebb ma"
        assert config["metric"] == "temperature_2m_max"
        assert config["unit"] == "°C"
        assert config["sort_desc"] is True
        assert config["metric_enum"] == AnalyticsMetric.TEMPERATURE_2M_MAX

    def test_coldest_today_config(self) -> None:
        """coldest_today should have correct configuration."""
        config = MultiCityEngine.QUERY_TYPES["coldest_today"]
        assert config["name"] == "Leghidegebb ma"
        assert config["metric"] == "temperature_2m_min"
        assert config["sort_desc"] is False

    def test_wettest_today_config(self) -> None:
        """wettest_today should have correct configuration."""
        config = MultiCityEngine.QUERY_TYPES["wettest_today"]
        assert config["name"] == "Legcsapadékosabb ma"
        assert config["metric"] == "precipitation_sum"
        assert config["unit"] == "mm"

    def test_windiest_today_config(self) -> None:
        """windiest_today should have correct configuration."""
        config = MultiCityEngine.QUERY_TYPES["windiest_today"]
        assert config["name"] == "Legszelesebb ma"
        assert config["metric"] == "windspeed_10m_max"
        assert config["unit"] == "km/h"
