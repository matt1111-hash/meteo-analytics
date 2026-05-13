"""City type definitions tests."""

from __future__ import annotations

import sqlite3

from src.infrastructure.city_manager.city_types import City


class TestCity:
    """Tests for City dataclass."""

    def test_create_city_with_required_fields(self) -> None:
        """City can be created with required fields."""
        city = City(
            id=1,
            city="Budapest",
            lat=47.4979,
            lon=19.0402,
            country="Hungary",
            country_code="HU",
        )
        assert city.id == 1
        assert city.city == "Budapest"
        assert city.lat == 47.4979
        assert city.lon == 19.0402
        assert city.country == "Hungary"
        assert city.country_code == "HU"

    def test_create_city_with_optional_fields(self) -> None:
        """City can be created with all optional fields."""
        city = City(
            id=1,
            city="Budapest",
            lat=47.4979,
            lon=19.0402,
            country="Hungary",
            country_code="HU",
            population=1750000,
            continent="Europe",
            admin_name="Budapest",
            capital="primary",
            timezone="Europe/Budapest",
        )
        assert city.population == 1750000
        assert city.continent == "Europe"
        assert city.admin_name == "Budapest"
        assert city.capital == "primary"
        assert city.timezone == "Europe/Budapest"

    def test_create_city_with_hungarian_fields(self) -> None:
        """City can be created with Hungarian-specific fields."""
        city = City(
            id=1,
            city="Budapest",
            lat=47.4979,
            lon=19.0402,
            country="Hungary",
            country_code="HU",
            settlement_type="város",
            megye="Budapest",
            jaras=None,
            climate_zone="continental",
            region_priority=1,
            is_hungarian=True,
            terulet_hektar=52500,
            lakasok_szama=800000,
        )
        assert city.settlement_type == "város"
        assert city.megye == "Budapest"
        assert city.climate_zone == "continental"
        assert city.region_priority == 1
        assert city.is_hungarian is True
        assert city.terulet_hektar == 52500
        assert city.lakasok_szama == 800000

    def test_post_init_generates_display_name_hungarian(self) -> None:
        """Display name is generated for Hungarian city."""
        city = City(
            id=1,
            city="Budapest",
            lat=47.4979,
            lon=19.0402,
            country="Hungary",
            country_code="HU",
            is_hungarian=True,
            megye="Budapest",
        )
        assert city.display_name == "Budapest, Budapest megye"

    def test_post_init_generates_display_name_non_hungarian(self) -> None:
        """Display name is generated for non-Hungarian city."""
        city = City(
            id=1,
            city="Paris",
            lat=48.8566,
            lon=2.3522,
            country="France",
            country_code="FR",
            is_hungarian=False,
        )
        assert city.display_name == "Paris, France"

    def test_post_init_generates_display_name_with_admin(self) -> None:
        """Display name includes admin_name for non-Hungarian cities."""
        city = City(
            id=1,
            city="London",
            lat=51.5074,
            lon=-0.1278,
            country="United Kingdom",
            country_code="GB",
            admin_name="England",
            is_hungarian=False,
        )
        assert "London" in city.display_name
        assert "England" in city.display_name

    def test_post_init_admin_name_same_as_city(self) -> None:
        """Display name doesn't duplicate when admin_name equals city."""
        city = City(
            id=1,
            city="Singapore",
            lat=1.3521,
            lon=103.8198,
            country="Singapore",
            country_code="SG",
            admin_name="Singapore",
            is_hungarian=False,
        )
        assert "Singapore" in city.display_name

    def test_to_dict(self) -> None:
        """to_dict converts City to dictionary."""
        city = City(
            id=1,
            city="Budapest",
            lat=47.4979,
            lon=19.0402,
            country="Hungary",
            country_code="HU",
            population=1750000,
        )
        result = city.to_dict()
        assert result["id"] == 1
        assert result["city"] == "Budapest"
        assert result["lat"] == 47.4979
        assert result["lon"] == 19.0402
        assert result["country"] == "Hungary"
        assert result["country_code"] == "HU"
        assert result["population"] == 1750000

    def test_to_dict_includes_hungarian_fields(self) -> None:
        """to_dict includes Hungarian-specific fields."""
        city = City(
            id=1,
            city="Budapest",
            lat=47.4979,
            lon=19.0402,
            country="Hungary",
            country_code="HU",
            is_hungarian=True,
            megye="Budapest",
        )
        result = city.to_dict()
        assert result["is_hungarian"] is True
        assert result["megye"] == "Budapest"

    def test_from_db_row(self) -> None:
        """City can be created from database row tuple."""
        row = (
            1,
            "Budapest",
            47.4979,
            19.0402,
            "Hungary",
            "HU",
            1750000,
            "Europe",
            "Budapest",
            "primary",
            "Europe/Budapest",
        )
        city = City.from_db_row(row)
        assert city.id == 1
        assert city.city == "Budapest"
        assert city.lat == 47.4979
        assert city.country == "Hungary"
        assert city.capital == "primary"

    def test_from_hungarian_settlement(self) -> None:
        """City can be created from Hungarian settlement row."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 as id, 'Budapest' as name, 47.4979 as latitude, "
            "19.0402 as longitude, 1750000 as population, 'Budapest' as megye, "
            "'város' as settlement_type, NULL as jaras, 'continental' as climate_zone, "
            "1 as region_priority, 52500 as terulet_hektar, 800000 as lakasok_szama"
        )
        row = cursor.fetchone()

        city = City.from_hungarian_settlement(row)
        assert city.id == 1
        assert city.city == "Budapest"
        assert city.lat == 47.4979
        assert city.lon == 19.0402
        assert city.country == "Magyarország"
        assert city.country_code == "HU"
        assert city.population == 1750000
        assert city.is_hungarian is True
        assert city.megye == "Budapest"
        assert city.settlement_type == "város"
        assert city.jaras is None
        assert city.climate_zone == "continental"
        assert city.region_priority == 1
        assert city.terulet_hektar == 52500
        assert city.lakasok_szama == 800000

    def test_distance_and_display_name_not_in_init(self) -> None:
        """distance_km and display_name are not in init parameters."""
        city = City(
            id=1,
            city="Budapest",
            lat=47.4979,
            lon=19.0402,
            country="Hungary",
            country_code="HU",
        )
        assert city.distance_km is None
        assert city.display_name is not None
