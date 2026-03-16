#!/usr/bin/env python3
"""
Tests for src/analytics/multi_city_types.py
Type aliases, constants, and configuration mappings
"""

from src.analytics.multi_city_types import (
    HUNGARIAN_REGIONAL_MAPPING,
    REGIONS,
    Number,
    NumberOrNone,
)


class TestTypeAliases:
    """Test type aliases are properly defined."""

    def test_number_union_type_exists(self) -> None:
        """Number should be a union of float and int."""
        # Runtime check - isinstance works with concrete types
        assert isinstance(1, (int, float))
        assert isinstance(1.5, (int, float))
        assert isinstance(-1, (int, float))
        assert isinstance(0.0, (int, float))

    def test_number_or_none_union_type_exists(self) -> None:
        """NumberOrNone should allow None in addition to numbers."""
        valid_values: list[NumberOrNone] = [1, 1.5, -1, 0.0, None]
        assert len(valid_values) == 5

    def test_number_accepts_int_subtypes(self) -> None:
        """Number should accept bool as int subtype."""
        # bool is a subclass of int in Python
        val: Number = True  # type: ignore[assignment]
        assert isinstance(val, int)


class TestHungarianRegionalMapping:
    """Test Hungarian regional mapping constants."""

    def test_mapping_exists_and_not_empty(self) -> None:
        """HUNGARIAN_REGIONAL_MAPPING should exist and have entries."""
        assert isinstance(HUNGARIAN_REGIONAL_MAPPING, dict)
        assert len(HUNGARIAN_REGIONAL_MAPPING) > 0

    def test_seven_statistical_regions_exist(self) -> None:
        """Should contain the 7 official Hungarian statistical regions."""
        official_regions = [
            "Észak-Magyarország",
            "Közép-Magyarország",
            "Észak-Alföld",
            "Dél-Alföld",
            "Dél-Dunántúl",
            "Nyugat-Dunántúl",
            "Közép-Dunántúl",
        ]
        for region in official_regions:
            assert region in HUNGARIAN_REGIONAL_MAPPING, f"Missing region: {region}"

    def test_budapest_maps_to_itself(self) -> None:
        """Budapest should map to a single-element list."""
        assert HUNGARIAN_REGIONAL_MAPPING["Budapest"] == ["Budapest"]

    def test_kozep_magyarország_contains_budapest_and_pest(self) -> None:
        """Közép-Magyarország should contain Budapest and Pest."""
        counties = HUNGARIAN_REGIONAL_MAPPING["Közép-Magyarország"]
        assert "Budapest" in counties
        assert "Pest" in counties
        assert len(counties) == 2

    def test_észak_magyarország_contains_three_counties(self) -> None:
        """Észak-Magyarország should contain 3 counties."""
        counties = HUNGARIAN_REGIONAL_MAPPING["Észak-Magyarország"]
        assert len(counties) == 3
        assert "Borsod-Abaúj-Zemplén" in counties
        assert "Heves" in counties
        assert "Nógrád" in counties

    def test_all_counties_have_individual_entries(self) -> None:
        """Each county should have a self-mapping entry."""
        expected_counties = [
            "Budapest",
            "Pest",
            "Borsod-Abaúj-Zemplén",
            "Heves",
            "Nógrád",
            "Hajdú-Bihar",
            "Jász-Nagykun-Szolnok",
            "Szabolcs-Szatmár-Bereg",
            "Bács-Kiskun",
            "Békés",
            "Csongrád-Csanád",
            "Baranya",
            "Somogy",
            "Tolna",
            "Győr-Moson-Sopron",
            "Vas",
            "Zala",
            "Fejér",
            "Komárom-Esztergom",
            "Veszprém",
        ]
        for county in expected_counties:
            assert county in HUNGARIAN_REGIONAL_MAPPING, f"Missing county: {county}"
            assert HUNGARIAN_REGIONAL_MAPPING[county] == [county]

    def test_all_values_are_lists(self) -> None:
        """All mapping values should be lists."""
        for key, value in HUNGARIAN_REGIONAL_MAPPING.items():
            assert isinstance(value, list), f"Value for {key} is not a list"

    def test_all_list_items_are_strings(self) -> None:
        """All items in mapping lists should be strings."""
        for key, value in HUNGARIAN_REGIONAL_MAPPING.items():
            for item in value:
                assert isinstance(item, str), f"Item {item} in {key} is not a string"


class TestRegions:
    """Test region configuration constants."""

    def test_regions_exists_and_not_empty(self) -> None:
        """REGIONS should exist and have entries."""
        assert isinstance(REGIONS, dict)
        assert len(REGIONS) > 0

    def test_hungary_region_exists(self) -> None:
        """Should contain Hungary configuration."""
        assert "Hungary" in REGIONS
        config = REGIONS["Hungary"]
        assert config["name"] == "Magyarország"
        assert "HU" in config["country_codes"]

    def test_europe_region_exists(self) -> None:
        """Should contain Europe configuration."""
        assert "Europe" in REGIONS
        config = REGIONS["Europe"]
        assert config["name"] == "Európa"
        assert len(config["country_codes"]) > 20  # Many EU countries

    def test_global_region_exists(self) -> None:
        """Should contain Global configuration."""
        assert "Global" in REGIONS
        config = REGIONS["Global"]
        assert config["name"] == "Globális"
        assert config["country_codes"] == []  # No country filter

    def test_all_regions_have_required_fields(self) -> None:
        """Each region should have required configuration fields."""
        required_fields = [
            "name",
            "country_codes",
            "max_cities",
            "batch_size",
            "rate_limit_delay",
        ]
        for region_name, config in REGIONS.items():
            for field in required_fields:
                assert field in config, f"Missing field {field} in {region_name}"

    def test_max_cities_are_positive_integers(self) -> None:
        """max_cities should be positive integers."""
        for region_name, config in REGIONS.items():
            max_cities = config["max_cities"]
            assert isinstance(max_cities, int), (
                f"max_cities in {region_name} is not int"
            )
            assert max_cities > 0, f"max_cities in {region_name} is not positive"

    def test_batch_sizes_are_positive_integers(self) -> None:
        """batch_size should be positive integers."""
        for region_name, config in REGIONS.items():
            batch_size = config["batch_size"]
            assert isinstance(batch_size, int), (
                f"batch_size in {region_name} is not int"
            )
            assert batch_size > 0, f"batch_size in {region_name} is not positive"

    def test_rate_limit_delays_are_positive_numbers(self) -> None:
        """rate_limit_delay should be positive numbers."""
        for region_name, config in REGIONS.items():
            delay = config["rate_limit_delay"]
            assert isinstance(delay, (int, float)), (
                f"rate_limit_delay in {region_name} is not number"
            )
            assert delay > 0, f"rate_limit_delay in {region_name} is not positive"

    def test_europe_contains_hungary(self) -> None:
        """Europe region should include Hungary country code."""
        europe_codes = REGIONS["Europe"]["country_codes"]
        assert "HU" in europe_codes

    def test_europe_contains_major_countries(self) -> None:
        """Europe region should contain major EU countries."""
        europe_codes = REGIONS["Europe"]["country_codes"]
        major_countries = ["DE", "FR", "IT", "ES", "PL"]
        for country in major_countries:
            assert country in europe_codes, f"Missing {country} in Europe"

    def test_hungary_max_cities_matches_expected(self) -> None:
        """Hungary should have expected max_cities count."""
        assert REGIONS["Hungary"]["max_cities"] == 165

    def test_hungary_batch_size_matches_expected(self) -> None:
        """Hungary should have expected batch_size."""
        assert REGIONS["Hungary"]["batch_size"] == 8

    def test_hungary_rate_limit_matches_expected(self) -> None:
        """Hungary should have expected rate_limit_delay."""
        assert REGIONS["Hungary"]["rate_limit_delay"] == 0.2


class TestExports:
    """Test module exports via __all__."""

    def test_all_exports_exist(self) -> None:
        """All items in __all__ should be accessible."""
        from src.analytics import multi_city_types

        expected_exports = [
            "Number",
            "NumberOrNone",
            "HUNGARIAN_REGIONAL_MAPPING",
            "REGIONS",
        ]
        for export in expected_exports:
            assert hasattr(multi_city_types, export), f"Missing export: {export}"
