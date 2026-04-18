"""Tests for AnalyzeMultiCityUseCase."""

from __future__ import annotations

from typing import Any

import pytest
from src.application.use_cases.analyze_multi_city import AnalyzeMultiCityUseCase
from src.data.enums import AnalyticsMetric
from src.domain.analytics.models import CityWeatherData, MultiCityQuery
from src.domain.analytics.repositories import CityRepositoryProtocol
from src.domain.analytics.services.analytics_transform_service import (
    AnalyticsTransformService,
)
from src.domain.analytics.services.region_resolver import RegionResolverService

QUERY_TYPES = {
    "windiest_today": {
        "name": "Legszelesebb ma",
        "metric": "windspeed_10m_max",
        "unit": "km/h",
        "sort_desc": True,
        "question_template": "Hol fújt ma a legerősebb szél {region}ban?",
        "metric_enum": AnalyticsMetric.WINDSPEED_10M_MAX,
    }
}

REGIONS = {
    "Hungary": {
        "name": "Magyarország",
        "country_codes": ["HU"],
        "max_cities": 5,
        "batch_size": 2,
        "rate_limit_delay": 0.0,
    }
}

HUNGARIAN_MAPPING = {"Budapest": ["Budapest"]}


class FakeCityRepository(CityRepositoryProtocol):
    """In-memory city repository for tests."""

    def __init__(self, cities: list[dict[str, Any]]) -> None:
        self.cities = cities
        self.last_limit: int | None = None

    def validate_paths(self) -> None:
        return None

    def get_cities_for_region(
        self,
        mapped_region: str,
        original_region: str,
        country_codes: list[str],
        limit: int,
        hungarian_mapping: dict[str, list[str]],
    ) -> list[dict[str, object]]:
        self.last_limit = limit
        return self.cities


class FakeWeatherFetchService:
    """Returns pre-seeded weather data."""

    def __init__(self, weather_data: list[CityWeatherData]) -> None:
        self.weather_data = weather_data

    def fetch_weather_data_dual_api_batch(
        self,
        cities: list[dict[str, Any]],
        date: str,
        region_config: dict[str, Any],
        **kwargs: Any,
    ) -> list[CityWeatherData]:
        return self.weather_data


def _city(name: str, windspeed: float) -> CityWeatherData:
    return CityWeatherData(
        city=name,
        country="X",
        country_code="XX",
        lat=0.0,
        lon=0.0,
        population=1,
        date="2024-01-01",
        windspeed_10m_max=windspeed,
        fetch_success=True,
    )


def _use_case(
    repo: FakeCityRepository | None = None,
    weather_data: list[CityWeatherData] | None = None,
) -> AnalyzeMultiCityUseCase:
    resolver = RegionResolverService()
    transform_service = AnalyticsTransformService(QUERY_TYPES)
    city_repo = repo or FakeCityRepository(
        [
            {"city": "A", "country": "X", "country_code": "XX", "lat": 0.0, "lon": 0.0},
            {"city": "B", "country": "X", "country_code": "XX", "lat": 1.0, "lon": 1.0},
        ]
    )
    weather_service = FakeWeatherFetchService(
        weather_data
        or [
            _city("A", 20.0),
            _city("B", 30.0),
        ]
    )

    return AnalyzeMultiCityUseCase(
        region_resolver=resolver,
        city_repository=city_repo,
        weather_fetch_service=weather_service,
        analytics_transform_service=transform_service,
        query_types=QUERY_TYPES,
        regions=REGIONS,
        hungarian_mapping=HUNGARIAN_MAPPING,
    )


def test_execute_returns_ranked_and_limited_results() -> None:
    use_case = _use_case()
    query = MultiCityQuery(
        query_type="windiest_today",
        region="Hungary",
        date="2024-01-01",
        limit=1,
        max_cities=None,
    )

    result = use_case.execute(query)

    assert result.is_success
    assert len(result.data.city_results) == 1
    assert result.data.city_results[0].city_name == "B"
    assert result.data.city_results[0].rank == 1
    assert result.data.total_cities_found == 2
    assert result.data.statistics["max"] == pytest.approx(30.0)


def test_execute_uses_region_default_city_limit_when_missing() -> None:
    repo = FakeCityRepository(
        [{"city": "Only", "country": "X", "country_code": "XX", "lat": 0.0, "lon": 0.0}]
    )
    use_case = _use_case(repo=repo, weather_data=[_city("Only", 12.0)])
    query = MultiCityQuery(
        query_type="windiest_today",
        region="Hungary",
        date="2024-01-01",
        limit=None,
        max_cities=None,
    )

    result = use_case.execute(query)

    assert repo.last_limit == 5  # region default
    assert result.is_success
    assert len(result.data.city_results) == 1


def test_execute_returns_empty_result_on_invalid_region() -> None:
    use_case = _use_case()
    query = MultiCityQuery(
        query_type="windiest_today",
        region="Atlantis",
        date="2024-01-01",
        limit=None,
        max_cities=None,
    )

    result = use_case.execute(query)

    assert result.status.value == "error"
    assert result.data is None
