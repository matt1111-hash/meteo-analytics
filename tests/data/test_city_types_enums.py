"""City type definitions tests."""

from __future__ import annotations

from src.infrastructure.city_manager.city_types import CitySort, RegionType


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
