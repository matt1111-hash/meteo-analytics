"""geo_utils re-export modul tesztjei."""

from __future__ import annotations

from src.data import geo_utils
from src.infrastructure.geo import (
    distance_calculator,
    geo_utils_analytics,
    geo_utils_core,
    geo_utils_region,
)


class TestGeoUtilsReexports:
    """Teszteli, hogy a geo_utils.py modul helyesen re-exportálja az összes komponenst."""

    def test_reexports_types(self) -> None:
        """A geo_types modul összes típusa elérhető."""
        assert hasattr(geo_utils, "GeoPoint")
        assert hasattr(geo_utils, "BoundingBox")
        assert hasattr(geo_utils, "DistanceUnit")
        assert hasattr(geo_utils, "CoordinateSystem")
        assert hasattr(geo_utils, "GeographicRegion")

    def test_reexports_calculator(self) -> None:
        """A DistanceCalculator elérhető."""
        assert hasattr(geo_utils, "DistanceCalculator")
        assert geo_utils.DistanceCalculator is distance_calculator.DistanceCalculator

    def test_reexports_geoutils_classes(self) -> None:
        """A GeoUtils osztályok elérhetőek."""
        assert hasattr(geo_utils, "GeoUtils")
        assert hasattr(geo_utils, "GeoUtilsRegion")
        assert hasattr(geo_utils, "GeoUtilsAnalytics")

        assert geo_utils.GeoUtils is geo_utils_core.GeoUtils
        assert geo_utils.GeoUtilsRegion is geo_utils_region.GeoUtilsRegion
        assert geo_utils.GeoUtilsAnalytics is geo_utils_analytics.GeoUtilsAnalytics

    def test_reexports_demo_function(self) -> None:
        """Demo functions removed — module should not expose demo_geo_utils."""
        assert not hasattr(geo_utils, "demo_geo_utils")

    def test_all_exports_defined(self) -> None:
        """A __all__ lista tartalmazza az összes exportot."""
        expected_all = {
            "DistanceUnit",
            "CoordinateSystem",
            "GeoPoint",
            "BoundingBox",
            "GeographicRegion",
            "DistanceCalculator",
            "GeoUtils",
            "GeoUtilsRegion",
            "GeoUtilsAnalytics",
        }
        actual_all = set(geo_utils.__all__)
        assert actual_all == expected_all

    def test_all_exports_actually_exist(self) -> None:
        """A __all__-ban felsorolt exportok tényleg léteznek."""
        for name in geo_utils.__all__:
            assert hasattr(geo_utils, name), f"Missing export: {name}"

    def test_types_are_correct_classes(self) -> None:
        """A típusok megfelelő osztályok."""
        assert isinstance(geo_utils.GeoPoint, type)
        assert isinstance(geo_utils.BoundingBox, type)
        assert isinstance(geo_utils.DistanceUnit, type)
        assert isinstance(geo_utils.CoordinateSystem, type)
        assert isinstance(geo_utils.GeographicRegion, type)

    def test_geoutils_is_instantiable(self) -> None:
        """A GeoUtils példányosítható."""
        utils = geo_utils.GeoUtils()
        assert utils is not None

    def test_geoutilsregion_is_instantiable(self) -> None:
        """A GeoUtilsRegion példányosítható."""
        utils = geo_utils.GeoUtilsRegion()
        assert utils is not None

    def test_geoutilsanalytics_is_instantiable(self) -> None:
        """A GeoUtilsAnalytics példányosítható."""
        utils = geo_utils.GeoUtilsAnalytics()
        assert utils is not None

    def test_distance_calculator_is_instantiable(self) -> None:
        """A DistanceCalculator példányosítható."""
        calc = geo_utils.DistanceCalculator()
        assert calc is not None

    def test_geopoint_is_dataclass(self) -> None:
        """A GeoPoint dataclass rendelkezik a szükséges mezőkkel."""
        assert hasattr(geo_utils.GeoPoint, "__dataclass_fields__")

        fields = geo_utils.GeoPoint.__dataclass_fields__
        expected_fields = {"latitude", "longitude", "name"}
        assert expected_fields.issubset(set(fields.keys()))

    def test_boundingbox_is_dataclass(self) -> None:
        """A BoundingBox dataclass rendelkezik a szükséges mezőkkel."""
        assert hasattr(geo_utils.BoundingBox, "__dataclass_fields__")

        fields = geo_utils.BoundingBox.__dataclass_fields__
        expected_fields = {
            "min_latitude",
            "max_latitude",
            "min_longitude",
            "max_longitude",
        }
        assert expected_fields.issubset(set(fields.keys()))

    def test_module_docstring_exists(self) -> None:
        """A modul rendelkezik dokumentációval."""
        assert geo_utils.__doc__ is not None
        assert len(geo_utils.__doc__) > 0

    def test_module_structure_matches_documentation(self) -> None:
        """A modul dokumentációja alapján ellenőrizzük a struktúrát."""
        doc = geo_utils.__doc__
        assert "geo_types.py" in doc
        assert "distance_calculator.py" in doc
        assert "geo_utils_core.py" in doc
        assert "geo_utils_region.py" in doc
        assert "geo_utils_analytics.py" in doc


class TestBackwardCompatibility:
    """Teszteli a visszafelé kompatibilitást."""

    def test_legacy_import_pattern_works(self) -> None:
        """A dokumentációban leírt legacy import működik."""
        from src.data.geo_utils import (  # noqa: PLC0415
            DistanceCalculator,
            GeoPoint,
            GeoUtils,
        )

        assert GeoUtils is not None
        assert DistanceCalculator is not None
        assert GeoPoint is not None

    def test_recommended_import_pattern_works(self) -> None:
        """A dokumentációban javasolt új import minta működik."""
        from src.infrastructure.geo.distance_calculator import DistanceCalculator  # noqa: PLC0415
        from src.infrastructure.geo.geo_types import GeoPoint  # noqa: PLC0415
        from src.infrastructure.geo.geo_utils_core import GeoUtils  # noqa: PLC0415

        assert GeoUtils is not None
        assert DistanceCalculator is not None
        assert GeoPoint is not None

    def test_both_imports_reference_same_class(self) -> None:
        """A GeoUtils mindkét import módszerrel ugyanazt az osztályt adja."""
        from src.data.geo_utils import GeoUtils as LegacyGeoUtils  # noqa: PLC0415
        from src.infrastructure.geo.geo_utils_core import GeoUtils as CoreGeoUtils  # noqa: PLC0415

        assert LegacyGeoUtils is CoreGeoUtils


class TestClassHierarchy:
    """Osztály hierarchia tesztek."""

    def test_geoutilsregion_inherits_from_geoutils(self) -> None:
        """A GeoUtilsRegion a GeoUtils-ból származik."""
        assert issubclass(geo_utils.GeoUtilsRegion, geo_utils.GeoUtils)

    def test_geoutilsanalytics_inherits_from_geoutilsregion(self) -> None:
        """A GeoUtilsAnalytics a GeoUtilsRegion-ból származik."""
        assert issubclass(geo_utils.GeoUtilsAnalytics, geo_utils.GeoUtilsRegion)

    def test_geoutilsanalytics_inherits_from_geoutils(self) -> None:
        """A GeoUtilsAnalytics közvetve a GeoUtils-ból is származik."""
        assert issubclass(geo_utils.GeoUtilsAnalytics, geo_utils.GeoUtils)
