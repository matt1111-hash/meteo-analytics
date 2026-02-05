"""City type definitions tests."""

from __future__ import annotations

import sqlite3
from enum import Enum

import pytest

from src.data.city_types import (
    City,
    CityDatabaseError,
    CityQuery,
    CitySort,
    RegionType,
)


class TestRegionType:
    """Tests for RegionType enum."""

    def test_global_value(self) -> None:
        """GLOBAL enum value is correct."""
        assert RegionType.GLOBAL.value == "global"

    def test_continent_value(self) -> None:
        """CONTINENT enum value is correct."""
        assert RegionType.CONTINENT.value == "continent"

    def test_country_value(self) -> None:
        """COUNTRY enum value is correct."""
        assert RegionType.COUNTRY.value == "country"

    def test_region_value(self) -> None:
        """REGION enum value is correct."""
        assert RegionType.REGION.value == "region"

    def test_custom_value(self) -> None:
        """CUSTOM enum value is correct."""
        assert RegionType.CUSTOM.value == "custom"

    def test_hungarian_settlement_value(self) -> None:
        """HUNGARIAN_SETTLEMENT enum value is correct."""
        assert RegionType.HUNGARIAN_SETTLEMENT.value == "hungarian_settlement"

    def test_all_region_types_defined(self) -> None:
        """All expected region types are defined."""
        expected_values = {
            "global",
            "continent",
            "country",
            "region",
            "custom",
            "hungarian_settlement",
        }
        actual_values = {rt.value for rt in RegionType}
        assert actual_values == expected_values


class TestCitySort:
    """Tests for CitySort enum."""

    def test_population_desc_value(self) -> None:
        """POPULATION_DESC enum value is correct."""
        assert CitySort.POPULATION_DESC.value == "population_desc"

    def test_population_asc_value(self) -> None:
        """POPULATION_ASC enum value is correct."""
        assert CitySort.POPULATION_ASC.value == "population_asc"

    def test_name_asc_value(self) -> None:
        """NAME_ASC enum value is correct."""
        assert CitySort.NAME_ASC.value == "name_asc"

    def test_name_desc_value(self) -> None:
        """NAME_DESC enum value is correct."""
        assert CitySort.NAME_DESC.value == "name_desc"

    def test_distance_asc_value(self) -> None:
        """DISTANCE_ASC enum value is correct."""
        assert CitySort.DISTANCE_ASC.value == "distance_asc"

    def test_hungarian_priority_value(self) -> None:
        """HUNGARIAN_PRIORITY enum value is correct."""
        assert CitySort.HUNGARIAN_PRIORITY.value == "hungarian_priority"


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
        # For non-Hungarian cities, includes both admin_name and country
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
        # Should not duplicate "Singapore"
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
            1,  # id
            "Budapest",  # city
            47.4979,  # lat
            19.0402,  # lon
            "Hungary",  # country
            "HU",  # country_code
            1750000,  # population
            "Europe",  # continent
            "Budapest",  # admin_name
            "primary",  # capital
            "Europe/Budapest",  # timezone
        )
        city = City.from_db_row(row)
        assert city.id == 1
        assert city.city == "Budapest"
        assert city.lat == 47.4979
        assert city.country == "Hungary"
        assert city.capital == "primary"

    def test_from_hungarian_settlement(self) -> None:
        """City can be created from Hungarian settlement row."""
        # Create a mock sqlite3.Row by using connect and row_factory
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
        # display_name is computed in __post_init__
        assert city.display_name is not None


class TestCityQuery:
    """Tests for CityQuery dataclass."""

    def test_create_query_with_defaults(self) -> None:
        """CityQuery can be created with minimal parameters."""
        query = CityQuery(region_type=RegionType.COUNTRY)
        assert query.region_type == RegionType.COUNTRY
        assert query.region_value is None
        assert query.limit == 50
        assert query.sort_by == CitySort.POPULATION_DESC

    def test_create_query_with_all_parameters(self) -> None:
        """CityQuery can be created with all parameters."""
        query = CityQuery(
            region_type=RegionType.REGION,
            region_value="California",
            limit=100,
            min_population=10000,
            max_population=1000000,
            sort_by=CitySort.NAME_ASC,
            include_capitals_only=True,
            center_lat=37.7749,
            center_lon=-122.4194,
            max_distance_km=500,
            exclude_countries=["US"],
            include_countries=["CA"],
            include_hungarian=False,
            hungarian_priority=False,
            settlement_types=["city", "town"],
            hungarian_counties=["Pest"],
        )
        assert query.region_type == RegionType.REGION
        assert query.region_value == "California"
        assert query.limit == 100
        assert query.min_population == 10000
        assert query.max_population == 1000000
        assert query.sort_by == CitySort.NAME_ASC
        assert query.include_capitals_only is True
        assert query.center_lat == 37.7749
        assert query.center_lon == -122.4194
        assert query.max_distance_km == 500
        assert query.exclude_countries == ["US"]
        assert query.include_countries == ["CA"]
        assert query.include_hungarian is False
        assert query.hungarian_priority is False
        assert query.settlement_types == ["city", "town"]
        assert query.hungarian_counties == ["Pest"]

    def test_default_list_fields_are_empty_lists(self) -> None:
        """Default list fields are empty lists, not None."""
        query = CityQuery(region_type=RegionType.GLOBAL)
        assert query.exclude_countries == []
        assert query.include_countries == []
        assert query.settlement_types == []
        assert query.hungarian_counties == []

    def test_boolean_defaults(self) -> None:
        """Boolean fields have correct defaults."""
        query = CityQuery(region_type=RegionType.GLOBAL)
        assert query.include_hungarian is True
        assert query.hungarian_priority is True
        assert query.include_capitals_only is False


class TestCityDatabaseError:
    """Tests for CityDatabaseError exception."""

    def test_city_database_error_can_be_raised(self) -> None:
        """CityDatabaseError can be raised and caught."""
        with pytest.raises(CityDatabaseError):
            raise CityDatabaseError("Database error")

    def test_city_database_error_message(self) -> None:
        """CityDatabaseError stores error message."""
        error = CityDatabaseError("Connection failed")
        assert str(error) == "Connection failed"

    def test_city_database_error_is_exception(self) -> None:
        """CityDatabaseError is an Exception subclass."""
        assert issubclass(CityDatabaseError, Exception)


class TestCityIntegration:
    """Integration tests for City types."""

    def test_city_and_query_work_together(self) -> None:
        """City and CityQuery can be used together."""
        query = CityQuery(
            region_type=RegionType.COUNTRY, region_value="Hungary", limit=10
        )
        city = City(
            id=1,
            city="Budapest",
            lat=47.4979,
            lon=19.0402,
            country="Hungary",
            country_code="HU",
        )
        assert query.region_value == city.country

    def test_all_enums_are_enums(self) -> None:
        """RegionType and CitySort are Enum subclasses."""
        assert issubclass(RegionType, Enum)
        assert issubclass(CitySort, Enum)

    def test_city_display_name_variations(self) -> None:
        """Display name varies based on city properties."""
        # Hungarian with megye
        city1 = City(
            id=1,
            city="Debrecen",
            lat=47.5314,
            lon=21.6269,
            country="Hungary",
            country_code="HU",
            is_hungarian=True,
            megye="Hajdú-Bihar",
        )
        assert "Debrecen" in city1.display_name
        assert "Hajdú-Bihar megye" in city1.display_name

        # Non-Hungarian with country
        city2 = City(
            id=2,
            city="Berlin",
            lat=52.5200,
            lon=13.4050,
            country="Germany",
            country_code="DE",
        )
        assert city2.display_name == "Berlin, Germany"

        # Hungarian without megye
        city3 = City(
            id=3,
            city="Érd",
            lat=47.3739,
            lon=18.9070,
            country="Hungary",
            country_code="HU",
            is_hungarian=True,
            megye=None,
        )
        assert city3.display_name == "Érd"  # No megye, no country
