"""GeoUtils infrastructure module tests."""

from __future__ import annotations

from src.infrastructure.geo import (
    distance_calculator,
    geo_types,
    geo_utils_analytics,
    geo_utils_core,
    geo_utils_region,
)


class TestGeoUtilsClasses:
    """GeoUtils osztalyok tesztjei."""

    def test_geoutils_is_instantiable(self) -> None:
        """A GeoUtils peldanyosithato."""
        utils = geo_utils_core.GeoUtils()
        assert utils is not None

    def test_geoutilsregion_is_instantiable(self) -> None:
        """A GeoUtilsRegion peldanyosithato."""
        utils = geo_utils_region.GeoUtilsRegion()
        assert utils is not None

    def test_geoutilsanalytics_is_instantiable(self) -> None:
        """A GeoUtilsAnalytics peldanyosithato."""
        utils = geo_utils_analytics.GeoUtilsAnalytics()
        assert utils is not None

    def test_distance_calculator_is_instantiable(self) -> None:
        """A DistanceCalculator peldanyosithato."""
        calc = distance_calculator.DistanceCalculator()
        assert calc is not None

    def test_geopoint_is_dataclass(self) -> None:
        """A GeoPoint dataclass rendelkezik a szukseges mezokkel."""
        assert hasattr(geo_types.GeoPoint, "__dataclass_fields__")

        fields = geo_types.GeoPoint.__dataclass_fields__
        expected_fields = {"latitude", "longitude", "name"}
        assert expected_fields.issubset(set(fields.keys()))

    def test_boundingbox_is_dataclass(self) -> None:
        """A BoundingBox dataclass rendelkezik a szukseges mezokkel."""
        assert hasattr(geo_types.BoundingBox, "__dataclass_fields__")

        fields = geo_types.BoundingBox.__dataclass_fields__
        expected_fields = {
            "min_latitude",
            "max_latitude",
            "min_longitude",
            "max_longitude",
        }
        assert expected_fields.issubset(set(fields.keys()))


class TestClassHierarchy:
    """Osztaly hierarchia tesztek."""

    def test_geoutilsregion_inherits_from_geoutils(self) -> None:
        """A GeoUtilsRegion a GeoUtils-bol szarmazik."""
        assert issubclass(geo_utils_region.GeoUtilsRegion, geo_utils_core.GeoUtils)

    def test_geoutilsanalytics_inherits_from_geoutilsregion(self) -> None:
        """A GeoUtilsAnalytics a GeoUtilsRegion-bol szarmazik."""
        assert issubclass(geo_utils_analytics.GeoUtilsAnalytics, geo_utils_region.GeoUtilsRegion)

    def test_geoutilsanalytics_inherits_from_geoutils(self) -> None:
        """A GeoUtilsAnalytics kozvetve a GeoUtils-bol is szarmazik."""
        assert issubclass(geo_utils_analytics.GeoUtilsAnalytics, geo_utils_core.GeoUtils)
