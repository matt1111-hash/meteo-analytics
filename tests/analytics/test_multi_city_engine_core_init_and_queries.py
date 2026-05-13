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

    def test_init_with_injected_use_case(self) -> None:
        """Should use injected use case and derive attributes from it."""
        mock_use_case = MagicMock()
        mock_repo = MagicMock()
        mock_use_case.city_repository = mock_repo
        mock_use_case.analytics_transform_service = MagicMock()

        with patch(
            "src.analytics.multi_city_engine_core.RegionResolverService",
        ):
            engine = MultiCityEngine(use_case=mock_use_case)

        assert engine.use_case is mock_use_case
        assert engine.city_repository is mock_repo

    def test_init_with_injected_use_case_and_explicit_repo(self) -> None:
        """Should prefer explicit city_repository over use_case's repo."""
        mock_use_case = MagicMock()
        mock_use_case.city_repository = MagicMock()
        explicit_repo = MagicMock()
        mock_use_case.analytics_transform_service = MagicMock()

        with patch(
            "src.analytics.multi_city_engine_core.RegionResolverService",
        ):
            engine = MultiCityEngine(
                use_case=mock_use_case,
                city_repository=explicit_repo,
            )

        assert engine.city_repository is explicit_repo

    def test_init_builds_use_case_when_not_injected(self) -> None:
        """Should call build_analyze_multi_city_use_case when no use_case given."""
        mock_use_case = MagicMock()
        mock_use_case.city_repository = MagicMock()
        mock_use_case.analytics_transform_service = MagicMock()

        with (
            patch(
                "src.analytics.multi_city_engine_core.build_analyze_multi_city_use_case",
                return_value=mock_use_case,
            ) as build_fn,
            patch(
                "src.analytics.multi_city_engine_core.RegionResolverService",
            ),
        ):
            engine = MultiCityEngine()

        build_fn.assert_called_once()
        assert engine.use_case is mock_use_case

    def test_init_creates_region_resolver(self) -> None:
        """Should create RegionResolverService instance."""
        mock_resolver = MagicMock()

        with (
            patch(
                "src.analytics.multi_city_engine_core.build_analyze_multi_city_use_case",
                return_value=MagicMock(
                    city_repository=MagicMock(),
                    analytics_transform_service=MagicMock(),
                ),
            ),
            patch(
                "src.analytics.multi_city_engine_core.RegionResolverService",
                return_value=mock_resolver,
            ),
        ):
            engine = MultiCityEngine()

        assert engine.region_resolver is mock_resolver

    def test_init_exposes_transform_service_from_use_case(self) -> None:
        """Should expose analytics_transform_service from use case."""
        mock_transform = MagicMock()
        mock_use_case = MagicMock()
        mock_use_case.city_repository = MagicMock()
        mock_use_case.analytics_transform_service = mock_transform

        with patch(
            "src.analytics.multi_city_engine_core.RegionResolverService",
        ):
            engine = MultiCityEngine(use_case=mock_use_case)

        assert engine.analytics_transform_service is mock_transform


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
