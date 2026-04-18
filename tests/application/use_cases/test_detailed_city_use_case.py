"""Tests for DetailedCityUseCase — single-fetch multi-metric extraction."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest
from src.application.use_cases.detailed_city_use_case import DetailedCityUseCase
from src.domain.analytics.models import CityWeatherData
from src.domain.entities.weather import CityWeatherResult
from src.domain.value_objects.enums import AnalyticsMetric


def _city_weather_data(**overrides) -> CityWeatherData:
    defaults = {
        "city": "Budapest",
        "country": "Hungary",
        "country_code": "HU",
        "lat": 47.5,
        "lon": 19.04,
        "date": "2024-01-01",
        "temperature_2m_mean": 5.0,
        "windspeed_10m_max": 25.0,
        "windgusts_10m_max": 45.0,
        "precipitation_sum": 3.0,
        "fetch_success": True,
    }
    defaults.update(overrides)
    return CityWeatherData(**defaults)


def _city_result(value: float, metric: AnalyticsMetric) -> CityWeatherResult:
    return CityWeatherResult(
        city_name="Budapest",
        country="Hungary",
        country_code="HU",
        latitude=47.5,
        longitude=19.04,
        value=value,
        metric=metric,
        date=date(2024, 1, 1),
        rank=1,
    )


def _make_use_case(
    city_repo: MagicMock | None = None,
    fetch_svc: MagicMock | None = None,
    transform_svc: MagicMock | None = None,
) -> DetailedCityUseCase:
    return DetailedCityUseCase(
        city_repository=city_repo or MagicMock(),
        weather_fetch_service=fetch_svc or MagicMock(),
        analytics_transform_service=transform_svc or MagicMock(),
        query_types={"temperature_mean": {"metric": "temperature_2m_mean"}},
        regions={"Global": {"batch_size": 5, "max_cities": 20}},
    )


def test_execute_raises_value_error_when_city_not_found() -> None:
    """Should raise ValueError if city_repository returns empty list."""
    repo = MagicMock()
    repo.get_cities_by_names.return_value = []
    uc = _make_use_case(city_repo=repo)

    with pytest.raises(ValueError, match="City not found: Atlantis"):
        uc.execute(city="Atlantis", start="2024-01-01", end="2024-01-03")


def test_execute_calls_fetch_once_and_transform_four_times() -> None:
    """Single fetch, four metric extractions."""
    repo = MagicMock()
    repo.get_cities_by_names.return_value = [{"city": "Budapest"}]

    fetch_svc = MagicMock()
    raw_data = [_city_weather_data()]
    fetch_svc.fetch_weather_data_dual_api_batch.return_value = raw_data

    transform_svc = MagicMock()
    transform_svc.process_weather_results.return_value = raw_data
    transform_svc.transform_to_city_weather_result.side_effect = [
        _city_result(5.0, AnalyticsMetric.TEMPERATURE_2M_MEAN),
        _city_result(25.0, AnalyticsMetric.WINDSPEED_10M_MAX),
        _city_result(45.0, AnalyticsMetric.WINDGUSTS_10M_MAX),
        _city_result(3.0, AnalyticsMetric.PRECIPITATION_SUM),
    ]

    uc = _make_use_case(city_repo=repo, fetch_svc=fetch_svc, transform_svc=transform_svc)
    result = uc.execute(city="Budapest", start="2024-01-01", end="2024-01-03")

    fetch_svc.fetch_weather_data_dual_api_batch.assert_called_once()
    assert transform_svc.process_weather_results.call_count == 4
    assert result.city == "Budapest"
    assert len(result.temperature_data) == 1
    assert len(result.wind_data) == 1
    assert len(result.wind_gusts_data) == 1
    assert len(result.precipitation_data) == 1


def test_execute_skips_failed_fetches() -> None:
    """CityWeatherData with fetch_success=False should be skipped."""
    repo = MagicMock()
    repo.get_cities_by_names.return_value = [{"city": "Budapest"}]

    failed_data = _city_weather_data(fetch_success=False)
    fetch_svc = MagicMock()
    fetch_svc.fetch_weather_data_dual_api_batch.return_value = [failed_data]

    transform_svc = MagicMock()
    transform_svc.process_weather_results.return_value = [failed_data]

    uc = _make_use_case(city_repo=repo, fetch_svc=fetch_svc, transform_svc=transform_svc)
    result = uc.execute(city="Budapest", start="2024-01-01", end="2024-01-03")

    assert result.temperature_data == []
    assert result.wind_data == []


def test_execute_handles_transform_error_gracefully() -> None:
    """Transform errors should be logged but not crash the use case."""
    repo = MagicMock()
    repo.get_cities_by_names.return_value = [{"city": "Budapest"}]

    good_data = _city_weather_data()
    fetch_svc = MagicMock()
    fetch_svc.fetch_weather_data_dual_api_batch.return_value = [good_data]

    transform_svc = MagicMock()
    transform_svc.process_weather_results.return_value = [good_data]
    transform_svc.transform_to_city_weather_result.side_effect = RuntimeError("transform boom")

    uc = _make_use_case(city_repo=repo, fetch_svc=fetch_svc, transform_svc=transform_svc)
    result = uc.execute(city="Budapest", start="2024-01-01", end="2024-01-03")

    assert result.temperature_data == []
