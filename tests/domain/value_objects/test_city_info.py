#!/usr/bin/env python3
"""Tests for domain CityInfo value object."""

import pytest
from src.domain.value_objects.city_info import CityInfo


class TestCityInfo:
    """Tests for CityInfo value object."""

    def test_city_info_creation(self):
        """Test basic CityInfo creation."""
        city = CityInfo(
            id=1,
            city="Budapest",
            lat=47.4979,
            lon=19.0402,
            country_code="HU",
            country="Magyarország",
        )

        assert city.id == 1
        assert city.city == "Budapest"
        assert city.lat == 47.4979
        assert city.lon == 19.0402
        assert city.country_code == "HU"
        assert city.country == "Magyarország"

    def test_city_info_frozen(self):
        """Test that CityInfo is immutable (frozen)."""
        city = CityInfo(
            id=1,
            city="Budapest",
            lat=47.4979,
            lon=19.0402,
            country_code="HU",
        )

        with pytest.raises(AttributeError):
            city.city = "Debrecen"

    def test_city_info_display_name_auto_generation(self):
        """Test automatic display_name generation."""
        city = CityInfo(
            id=1,
            city="Debrecen",
            lat=47.5316,
            lon=21.6273,
            country_code="HU",
            admin_name="Hajdú-Bihar",
        )

        # Should auto-generate display_name
        assert city.display_name is not None
        assert "Debrecen" in city.display_name

    def test_city_info_to_dict(self):
        """Test CityInfo to_dict method."""
        city = CityInfo(
            id=1,
            city="Budapest",
            lat=47.4979,
            lon=19.0402,
            country_code="HU",
            country="Magyarország",
            population=1752286,
        )

        result = city.to_dict()

        assert result["id"] == 1
        assert result["city"] == "Budapest"
        assert result["lat"] == 47.4979
        assert result["lon"] == 19.0402
        assert result["country_code"] == "HU"
        assert result["country"] == "Magyarország"
        assert result["population"] == 1752286

    def test_city_info_from_dict(self):
        """Test CityInfo from_dict class method."""
        data = {
            "id": 2,
            "city": "Szeged",
            "lat": 46.2530,
            "lon": 20.1414,
            "country_code": "HU",
            "country": "Magyarország",
            "population": 161137,
            "admin_name": "Csongrád-Csanád",
        }

        city = CityInfo.from_dict(data)

        assert city.id == 2
        assert city.city == "Szeged"
        assert city.lat == 46.2530
        assert city.lon == 20.1414
        assert city.country_code == "HU"
        assert city.population == 161137
        assert city.admin_name == "Csongrád-Csanád"

    def test_city_info_hungarian_flag(self):
        """Test Hungarian settlement flag."""
        city = CityInfo(
            id=1,
            city="Pécs",
            lat=46.0727,
            lon=18.2323,
            country_code="HU",
            is_hungarian=True,
        )

        assert city.is_hungarian is True

    def test_city_info_optional_fields(self):
        """Test that optional fields have correct defaults."""
        city = CityInfo(
            id=1,
            city="Test City",
            lat=0.0,
            lon=0.0,
            country_code="XX",
        )

        assert city.country == ""
        assert city.population is None
        assert city.timezone is None
        assert city.admin_name is None
        assert city.is_hungarian is False

    def test_city_info_importable_from_domain_value_objects(self):
        """Test that CityInfo is importable from domain.value_objects."""
        from src.domain.value_objects import CityInfo as ImportedCityInfo

        assert ImportedCityInfo is CityInfo
