#!/usr/bin/env python3
"""Tests for city_adapter — dict/City to CityInfo conversion."""

from __future__ import annotations

from unittest.mock import MagicMock

from src.domain.value_objects.city_info import CityInfo
from src.infrastructure.adapters.city_adapter import (
    city_dict_to_city_info,
    city_to_city_info,
)


class TestCityDictToCityInfo:
    """Tests for city_dict_to_city_info."""

    def test_full_dict_returns_city_info(self) -> None:
        data: dict = {
            "id": 1,
            "city": "Budapest",
            "lat": 47.4979,
            "lon": 19.0402,
            "country_code": "HU",
            "country": "Hungary",
            "display_name": "Budapest, Hungary",
            "population": 1750000,
            "timezone": "Europe/Budapest",
            "admin_name": "Budapest",
            "is_hungarian": True,
        }
        result = city_dict_to_city_info(data)

        assert isinstance(result, CityInfo)
        assert result.id == 1
        assert result.city == "Budapest"
        assert result.lat == 47.4979
        assert result.lon == 19.0402
        assert result.country_code == "HU"
        assert result.country == "Hungary"
        assert result.display_name == "Budapest, Hungary"
        assert result.population == 1750000
        assert result.timezone == "Europe/Budapest"
        assert result.admin_name == "Budapest"
        assert result.is_hungarian is True

    def test_empty_dict_uses_defaults(self) -> None:
        result = city_dict_to_city_info({})

        assert result.id == 0
        assert result.city == ""
        assert result.lat == 0.0
        assert result.lon == 0.0
        assert result.country_code == ""
        assert result.country == ""
        assert result.population is None
        assert result.timezone is None
        assert result.admin_name is None
        assert result.is_hungarian is False

    def test_partial_dict_preserves_given_values(self) -> None:
        data: dict = {
            "id": 42,
            "city": "Berlin",
            "lat": 52.52,
            "lon": 13.405,
        }
        result = city_dict_to_city_info(data)

        assert result.id == 42
        assert result.city == "Berlin"
        assert result.lat == 52.52
        assert result.lon == 13.405
        assert result.country_code == ""
        assert result.country == ""
        assert result.is_hungarian is False

    def test_missing_optional_fields_get_defaults(self) -> None:
        data: dict = {"id": 5, "city": "Debrecen", "lat": 47.53, "lon": 21.63}
        result = city_dict_to_city_info(data)

        assert result.population is None
        assert result.timezone is None
        assert result.admin_name is None


class TestCityToCityInfo:
    """Tests for city_to_city_info."""

    def test_converts_city_mock_to_city_info(self) -> None:
        city = MagicMock()
        city.id = 10
        city.city = "Szeged"
        city.lat = 46.25
        city.lon = 20.15
        city.country_code = "HU"
        city.country = "Hungary"
        city.display_name = "Szeged, Csongrád-Csanád"
        city.population = 160000
        city.timezone = "Europe/Budapest"
        city.admin_name = "Csongrád-Csanád"
        city.is_hungarian = True

        result = city_to_city_info(city)

        assert isinstance(result, CityInfo)
        assert result.id == 10
        assert result.city == "Szeged"
        assert result.lat == 46.25
        assert result.lon == 20.15
        assert result.country_code == "HU"
        assert result.country == "Hungary"
        assert result.display_name == "Szeged, Csongrád-Csanád"
        assert result.population == 160000
        assert result.timezone == "Europe/Budapest"
        assert result.admin_name == "Csongrád-Csanád"
        assert result.is_hungarian is True

    def test_converts_non_hungarian_city(self) -> None:
        city = MagicMock()
        city.id = 99
        city.city = "Vienna"
        city.lat = 48.21
        city.lon = 16.37
        city.country_code = "AT"
        city.country = "Austria"
        city.display_name = "Vienna, Austria"
        city.population = 1900000
        city.timezone = "Europe/Vienna"
        city.admin_name = "Wien"
        city.is_hungarian = False

        result = city_to_city_info(city)

        assert result.country_code == "AT"
        assert result.is_hungarian is False
        assert result.city == "Vienna"
