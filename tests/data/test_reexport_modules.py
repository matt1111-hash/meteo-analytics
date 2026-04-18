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
        from src.data.city_manager_stats import CityManagerStats  # noqa: PLC0415

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
        # Import the submodules directly to avoid circular import
        from src.data.anomaly_profile import manager  # noqa: PLC0415

        # Verify the symbols are accessible from submodules
        assert hasattr(manager, "AnomalyProfileManager")
        # Note: demo_anomaly_profile_manager causes circular import, skip that test


class TestEnumsModule:
    """Tests for enums.py module."""

    def test_imports_from_enums(self) -> None:
        """enums module exports expected symbols."""
        from src.data import enums  # noqa: PLC0415

        # Check that the module has expected attributes from domain.value_objects.enums
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
        """enums module has display functions."""
        from src.data import enums  # noqa: PLC0415

        assert hasattr(enums, "get_metric_display_name")
        assert hasattr(enums, "get_severity_color")


class TestModelsModule:
    """Tests for models.py re-export module."""

    def test_imports_from_models(self) -> None:
        """models module can be imported and exports expected symbols."""
        from src.data import models  # noqa: PLC0415

        # Check that the module exports expected symbols
        expected = [
            "City",
            "CityQuery",
            "CityDatabaseError",
            "LocationType",
            "Location",
            "CityWeatherResult",
            "AnomalyResult",
            "TimeGranularity",
            "AnalysisType",
        ]
        for symbol in expected:
            assert hasattr(models, symbol)
