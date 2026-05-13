"""Tests for re-export modules to improve overall coverage."""

from __future__ import annotations


class TestCityManagerReExport:
    """Tests for city_manager.py re-export module."""

    def test_imports_from_city_manager(self) -> None:
        """city_manager module exports expected symbols."""
        from src.data import city_manager  # noqa: PLC0415

        expected = {
            "CityManager",
            "City",
            "CityDatabaseError",
            "CityManagerDB",
            "CityManagerHungarian",
            "CityManagerSearch",
            "CityManagerStats",
            "demo_dual_database_city_manager",
        }
        for symbol in expected:
            assert hasattr(city_manager, symbol)

    def test_city_manager_is_city_manager_stats(self) -> None:
        """CityManager is aliased to CityManagerStats."""
        from src.data.city_manager import CityManager  # noqa: PLC0415
        from src.infrastructure.city_manager.city_manager_stats import (  # noqa: PLC0415
            CityManagerStats,
        )

        # They should be the same class
        assert CityManager is CityManagerStats


class TestGeoUtilsReExport:
    """Tests for geo_utils.py re-export module."""

    def test_imports_from_geo_utils(self) -> None:
        """geo_utils module exports expected symbols."""
        from src.data import geo_utils  # noqa: PLC0415

        expected = {
            "DistanceUnit",
            "GeoPoint",
            "BoundingBox",
            "GeographicRegion",
            "DistanceCalculator",
            "GeoUtils",
            "GeoUtilsRegion",
            "GeoUtilsAnalytics",
        }
        for symbol in expected:
            assert hasattr(geo_utils, symbol)


class TestAnomalyProfileManagerReExport:
    """Tests for anomaly_profile_manager.py re-export module."""

    def test_imports_from_anomaly_profile_manager(self) -> None:
        """anomaly_profile_manager module can be imported."""
        from src.infrastructure.anomaly_profile import manager  # noqa: PLC0415

        # Verify the symbols are accessible from submodules
        assert hasattr(manager, "AnomalyProfileManager")


class TestEnumsModule:
    """Tests for domain enums (previously in src.data.enums)."""

    def test_imports_from_domain_enums(self) -> None:
        """Domain enums module exports expected symbols."""
        from src.domain.value_objects import enums  # noqa: PLC0415

        expected = {
            "AnalysisType",
            "AnalyticsMetric",
            "RegionType",
            "DataProvider",
            "AnomalyType",
            "AnomalySeverity",
        }
        for symbol in expected:
            assert hasattr(enums, symbol)

    def test_enums_has_display_functions(self) -> None:
        """Domain enums module has display functions."""
        from src.domain.value_objects import enums  # noqa: PLC0415

        assert hasattr(enums, "get_metric_display_name")
        assert hasattr(enums, "get_severity_color")


class TestModelsModule:
    """Tests for domain models (previously in src.data.models)."""

    def test_imports_from_domain(self) -> None:
        """Domain entities can be imported and export expected symbols."""
        from src.domain.entities.analytics_models import AnalyticsResult  # noqa: PLC0415
        from src.domain.entities.location import Location  # noqa: PLC0415
        from src.domain.entities.location_types import LocationType  # noqa: PLC0415
        from src.domain.entities.weather import AnomalyResult, CityWeatherResult  # noqa: PLC0415

        # Verify symbols exist
        assert AnalyticsResult is not None
        assert Location is not None
        assert LocationType is not None
        assert CityWeatherResult is not None
        assert AnomalyResult is not None
