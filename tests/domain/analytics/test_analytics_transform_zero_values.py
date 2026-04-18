"""Tests for zero-value handling in AnalyticsTransformService.

Validates that legitimate zero values (0mm precipitation, 0 km/h wind, 0C temperature)
are preserved and not replaced by fallback values.
"""

from __future__ import annotations

import pytest
from src.data.enums import AnalyticsMetric
from src.data.models import CityWeatherResult
from src.domain.analytics.models import CityWeatherData
from src.domain.analytics.services.analytics_transform_service import (
    AnalyticsTransformService,
)

QUERY_TYPES = {
    "wettest_today": {
        "name": "Legcsapatosabb ma",
        "metric": "precipitation_sum",
        "unit": "mm",
        "sort_desc": True,
        "question_template": "Hol esett ma a legtöbb csapadek?",
        "metric_enum": AnalyticsMetric.PRECIPITATION_SUM,
    },
    "windiest_today": {
        "name": "Legszelesebb ma",
        "metric": "windspeed_10m_max",
        "unit": "km/h",
        "sort_desc": True,
        "question_template": "Hol fujt ma a legerosebb szel?",
        "metric_enum": AnalyticsMetric.WINDSPEED_10M_MAX,
    },
    "hottest_today": {
        "name": "Legmelegebb ma",
        "metric": "temperature_2m_max",
        "unit": "C",
        "sort_desc": True,
        "question_template": "Hol volt ma a legmelegebb?",
        "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MAX,
    },
}


def _service() -> AnalyticsTransformService:
    return AnalyticsTransformService(QUERY_TYPES)


def _city(
    precipitation: float | None = 1.0,
    windspeed: float | None = 10.0,
    temp_max: float | None = 20.0,
    temp_min: float | None = 10.0,
) -> CityWeatherData:
    return CityWeatherData(
        city="ZeroCity",
        country="X",
        country_code="XX",
        lat=0.0,
        lon=0.0,
        population=1,
        date="2024-01-01",
        temperature_2m_max=temp_max,
        temperature_2m_min=temp_min,
        precipitation_sum=precipitation,
        windspeed_10m_max=windspeed,
        windgusts_10m_max=windspeed,
        fetch_success=True,
    )


def test_zero_precipitation_preserved() -> None:
    """0mm precipitation is a legitimate value (dry day) — must not trigger fallback."""
    service = _service()
    city = _city(precipitation=0.0, temp_max=15.0, temp_min=5.0)

    result = service.transform_to_city_weather_result(city, "wettest_today")

    assert isinstance(result, CityWeatherResult)
    assert result.value == pytest.approx(0.0)


def test_zero_windspeed_preserved() -> None:
    """0 km/h wind is a legitimate value (calm) — must not trigger fallback."""
    service = _service()
    city = _city(windspeed=0.0, temp_max=15.0, temp_min=5.0)

    result = service.transform_to_city_weather_result(city, "windiest_today")

    assert isinstance(result, CityWeatherResult)
    assert result.value == pytest.approx(0.0)


def test_zero_temperature_preserved() -> None:
    """0C temperature is a legitimate value (freezing point) — must not trigger fallback."""
    service = _service()
    city = _city(temp_max=0.0, temp_min=-5.0)

    result = service.transform_to_city_weather_result(city, "hottest_today")

    assert isinstance(result, CityWeatherResult)
    assert result.value == pytest.approx(0.0)


def test_none_still_triggers_fallback() -> None:
    """None value must still trigger fallback — regression guard."""
    service = _service()
    city = _city(windspeed=None, temp_max=20.0, temp_min=10.0)

    result = service.transform_to_city_weather_result(city, "windiest_today")

    assert isinstance(result, CityWeatherResult)
    assert result.value != 0.0  # fallback value, not the zero we'd get from broken logic


def test_process_weather_results_empty_on_all_invalid() -> None:
    """When all records are invalid (fetch_success=False), return empty list."""
    service = _service()
    invalid = _city(windspeed=5.0)
    invalid.fetch_success = False

    processed = service.process_weather_results([invalid], "windiest_today")

    assert processed == []
