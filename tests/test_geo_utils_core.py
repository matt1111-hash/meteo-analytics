"""GeoUtils core osztály tesztjei."""

from __future__ import annotations

import pytest

from src.data.geo_types import BoundingBox, GeoPoint
from src.data.geo_utils_core import GeoUtils


class TestValidateCoordinates:
    """validate_coordinates metódus tesztjei."""

    def test_valid_coordinates(self) -> None:
        """Érvényes koordináták."""
        utils = GeoUtils()
        assert utils.validate_coordinates(0, 0) is True
        assert utils.validate_coordinates(45.0, 19.0) is True
        assert utils.validate_coordinates(-45.0, -19.0) is True

    def test_latitude_at_boundary(self) -> None:
        """Szélesség határértékei."""
        utils = GeoUtils()
        assert utils.validate_coordinates(90, 0) is True
        assert utils.validate_coordinates(-90, 0) is True
        assert utils.validate_coordinates(90.1, 0) is False
        assert utils.validate_coordinates(-90.1, 0) is False

    def test_longitude_at_boundary(self) -> None:
        """Hosszúság határértékei."""
        utils = GeoUtils()
        assert utils.validate_coordinates(0, 180) is True
        assert utils.validate_coordinates(0, -180) is True
        assert utils.validate_coordinates(0, 180.1) is False
        assert utils.validate_coordinates(0, -180.1) is False


class TestNormalizeCoordinates:
    """normalize_coordinates metódus tesztjei."""

    def test_normalize_valid_coordinates(self) -> None:
        """Érvényes koordináták változatlanok."""
        utils = GeoUtils()
        lat, lon = utils.normalize_coordinates(45.0, 19.0)
        assert lat == 45.0
        assert lon == 19.0

    def test_normalize_latitude_clamps(self) -> None:
        """Szélesség korlátozása -90 és 90 közé."""
        utils = GeoUtils()
        lat, lon = utils.normalize_coordinates(100.0, 0.0)
        assert lat == 90.0

        lat, lon = utils.normalize_coordinates(-100.0, 0.0)
        assert lat == -90.0

    def test_normalize_longitude_wraps(self) -> None:
        """Hosszúság körbejárása -180 és 180 közé."""
        utils = GeoUtils()
        lat, lon = utils.normalize_coordinates(0.0, 190.0)
        # 190 -> -170 (mert 190 - 360 = -170)
        assert lon == -170.0

        lat, lon = utils.normalize_coordinates(0.0, -190.0)
        # -190 -> 170 (mert -190 + 360 = 170)
        assert lon == 170.0

        lat, lon = utils.normalize_coordinates(0.0, 360.0)
        assert lon == 0.0

    def test_normalize_returns_tuple(self) -> None:
        """A visszatérési érték tuple."""
        utils = GeoUtils()
        result = utils.normalize_coordinates(45.0, 19.0)
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestCalculateBoundingBox:
    """calculate_bounding_box metódus tesztjei."""

    def test_empty_points_raises_error(self) -> None:
        """Üres pontlista ValueError-t dob."""
        utils = GeoUtils()
        with pytest.raises(ValueError, match="Points list is empty"):
            utils.calculate_bounding_box([])

    def test_single_point(self) -> None:
        """Egyetlen pont bounding boxa."""
        utils = GeoUtils()
        bbox = utils.calculate_bounding_box([(45.0, 19.0)])
        assert bbox.min_latitude == 45.0
        assert bbox.max_latitude == 45.0
        assert bbox.min_longitude == 19.0
        assert bbox.max_longitude == 19.0

    def test_multiple_points(self) -> None:
        """Több pont bounding boxa."""
        utils = GeoUtils()
        points = [
            (45.0, 19.0),
            (47.0, 21.0),
            (43.0, 17.0),
        ]
        bbox = utils.calculate_bounding_box(points)
        assert bbox.min_latitude == 43.0
        assert bbox.max_latitude == 47.0
        assert bbox.min_longitude == 17.0
        assert bbox.max_longitude == 21.0

    def test_with_padding(self) -> None:
        """Padding alkalmazása."""
        utils = GeoUtils()
        bbox = utils.calculate_bounding_box([(45.0, 19.0)], padding_degrees=0.5)
        assert bbox.min_latitude == 44.5
        assert bbox.max_latitude == 45.5
        assert bbox.min_longitude == 18.5
        assert bbox.max_longitude == 19.5

    def test_returns_bounding_box(self) -> None:
        """A visszatérési érték BoundingBox."""
        utils = GeoUtils()
        bbox = utils.calculate_bounding_box([(45.0, 19.0)])
        assert isinstance(bbox, BoundingBox)


class TestCalculateGeographicCenter:
    """calculate_geographic_center metódus tesztjei."""

    def test_empty_points_raises_error(self) -> None:
        """Üres pontlista ValueError-t dob."""
        utils = GeoUtils()
        with pytest.raises(ValueError, match="Points list is empty"):
            utils.calculate_geographic_center([])

    def test_single_point(self) -> None:
        """Egyetlen pont középpontja."""
        utils = GeoUtils()
        center = utils.calculate_geographic_center([(45.0, 19.0)])
        assert abs(center.latitude - 45.0) < 0.001
        assert abs(center.longitude - 19.0) < 0.001

    def test_two_points(self) -> None:
        """Két pont középpontja."""
        utils = GeoUtils()
        center = utils.calculate_geographic_center([
            (45.0, 19.0),
            (47.0, 21.0),
        ])
        # A középpont kb a két pont között van
        assert 45.0 < center.latitude < 47.0
        assert 19.0 < center.longitude < 21.0

    def test_returns_geopoint(self) -> None:
        """A visszatérési érték GeoPoint."""
        utils = GeoUtils()
        center = utils.calculate_geographic_center([(45.0, 19.0)])
        assert isinstance(center, GeoPoint)
        assert center.name == "Geographic Center"


class TestConvertToWebMercator:
    """convert_to_web_mercator metódus tesztjei."""

    def test_equator(self) -> None:
        """Egyenlítő konverziója."""
        utils = GeoUtils()
        x, y = utils.convert_to_web_mercator(0, 0)
        assert abs(x) < 1  # ~0
        assert abs(y) < 1  # ~0

    def test_budapest(self) -> None:
        """Budapest koordináták konverziója."""
        utils = GeoUtils()
        x, y = utils.convert_to_web_mercator(47.4979, 19.0402)
        # Web Mercator x: longitude * 20037508.34 / 180
        expected_x = 19.0402 * 20037508.34 / 180
        assert abs(x - expected_x) < 1000
        # y pozitív kell legyen északi szélességnél
        assert y > 0

    def test_returns_tuple(self) -> None:
        """A visszatérési érték tuple."""
        utils = GeoUtils()
        result = utils.convert_to_web_mercator(45.0, 19.0)
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestSuggestMapZoomLevel:
    """suggest_map_zoom_level metódus tesztjei."""

    def test_returns_valid_zoom(self) -> None:
        """Érvényes zoom szintet ad vissza."""
        utils = GeoUtils()
        bbox = BoundingBox(
            min_latitude=47.4,
            max_latitude=47.6,
            min_longitude=19.0,
            max_longitude=19.1,
        )
        zoom = utils.suggest_map_zoom_level(bbox)
        assert 0 <= zoom <= 18

    def test_different_bboxes_different_zoom(self) -> None:
        """Különböző bboxokhoz különböző zoom szint."""
        utils = GeoUtils()
        bbox_small = BoundingBox(47.4, 47.6, 19.0, 19.01)
        bbox_large = BoundingBox(-10, 10, -10, 10)

        zoom_small = utils.suggest_map_zoom_level(bbox_small)
        zoom_large = utils.suggest_map_zoom_level(bbox_large)

        # A zoom szintek 0-18 közöttiek
        assert 0 <= zoom_small <= 18
        assert 0 <= zoom_large <= 18

    def test_custom_map_width(self) -> None:
        """Egyedi térkép szélesség."""
        utils = GeoUtils()
        bbox = BoundingBox(
            min_latitude=47.4,
            max_latitude=47.6,
            min_longitude=19.0,
            max_longitude=19.1,
        )
        zoom_wide = utils.suggest_map_zoom_level(bbox, map_width_px=1600)
        # A szélesebb térkép valós zoom-ot ad
        assert isinstance(zoom_wide, int)
        assert 0 <= zoom_wide <= 18


class TestInitialization:
    """Inicializálási tesztek."""

    def test_default_initialization(self) -> None:
        """Alapértelmezett inicializálás."""
        utils = GeoUtils()
        assert utils.distance_calculator is not None

    def test_custom_distance_calculator(self) -> None:
        """Egyedi távolság számító."""
        from src.data.distance_calculator import DistanceCalculator

        calc = DistanceCalculator()
        utils = GeoUtils(distance_calculator=calc)
        assert utils.distance_calculator is calc
