"""Tests for domain analytics models."""

from __future__ import annotations

from src.domain.analytics.models import CityWeatherData, MultiCityQuery
from src.domain.value_objects.enums import RegionScope


def test_multi_city_query_uses_defaults_when_optional_fields_omitted() -> None:
    """MultiCityQuery sets sensible defaults for optional fields."""
    query = MultiCityQuery(query_type="trend", region="Europe", date="2024-01-01")
    assert query.max_cities == 50
    assert query.limit is None
    assert query.question is None
    assert query.region_scope is None


def test_multi_city_query_accepts_custom_limit_and_scope() -> None:
    """MultiCityQuery stores provided limit and region scope."""
    query = MultiCityQuery(
        query_type="top-cities",
        region="Asia",
        date="2024-06-01",
        limit=10,
        region_scope=RegionScope.CONTINENT,
    )
    assert query.limit == 10
    assert query.region_scope == RegionScope.CONTINENT


def test_city_weather_data_to_dict_includes_all_fields() -> None:
    """CityWeatherData.to_dict exports all attributes."""
    weather = CityWeatherData(
        city="Budapest",
        country="Hungary",
        country_code="HU",
        lat=47.4979,
        lon=19.0402,
        population=1750000,
        temperature_2m_max=30.5,
        data_source="open-meteo",
        fetch_success=False,
        error_message="timeout",
        retry_count=1,
        temperature_range=12.5,
    )
    data = weather.to_dict()
    assert data["city"] == "Budapest"
    assert data["data_source"] == "open-meteo"
    assert data["fetch_success"] is False
    assert data["temperature_range"] == 12.5
    assert data["population"] == 1750000


def test_city_weather_data_to_dict_returns_copy() -> None:
    """CityWeatherData.to_dict returns a copy that does not mutate the model."""
    weather = CityWeatherData(
        city="Vienna",
        country="Austria",
        country_code="AT",
        lat=48.2082,
        lon=16.3738,
    )
    exported: dict[str, object] = weather.to_dict()
    exported["city"] = "Graz"
    assert weather.city == "Vienna"


def test_city_weather_data_defaults_apply_when_not_provided() -> None:
    """CityWeatherData applies default values for status-related fields."""
    weather = CityWeatherData(
        city="Prague",
        country="Czechia",
        country_code="CZ",
        lat=50.0755,
        lon=14.4378,
    )
    assert weather.data_source == "dual-api"
    assert weather.fetch_success is True
    assert weather.retry_count == 0
    assert weather.error_message is None
