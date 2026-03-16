"""City type definitions tests."""

from __future__ import annotations

from enum import Enum

import pytest

from src.data.city_types import City, CityDatabaseError, CityQuery, CitySort, RegionType


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

        city2 = City(
            id=2,
            city="Berlin",
            lat=52.5200,
            lon=13.4050,
            country="Germany",
            country_code="DE",
        )
        assert city2.display_name == "Berlin, Germany"

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
        assert city3.display_name == "Érd"
