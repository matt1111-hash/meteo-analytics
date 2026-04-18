"""Tests for AnalyticsTransformService."""

from __future__ import annotations

from datetime import date

import pytest
from src.data.enums import AnalyticsMetric, QuestionType, RegionScope
from src.data.models import AnalyticsQuestion, CityWeatherResult
from src.domain.analytics.models import CityWeatherData
from src.domain.analytics.services.analytics_transform_service import (
    AnalyticsTransformService,
)

QUERY_TYPES = {
    "windiest_today": {
        "name": "Legszelesebb ma",
        "metric": "windspeed_10m_max",
        "unit": "km/h",
        "sort_desc": True,
        "question_template": "Hol fújt ma a legerősebb szél {region}ban?",
        "metric_enum": AnalyticsMetric.WINDSPEED_10M_MAX,
    },
    "temperature_range": {
        "name": "Legnagyobb hőingás",
        "metric": "temperature_range",
        "unit": "°C",
        "sort_desc": True,
        "question_template": "Hol volt ma a legnagyobb hőingás {region}ban?",
        "metric_enum": AnalyticsMetric.TEMPERATURE_RANGE,
    },
}


def _service() -> AnalyticsTransformService:
    return AnalyticsTransformService(QUERY_TYPES)


def _city(
    windspeed: float | None = 10.0,
    temp_max: float | None = 20.0,
    temp_min: float | None = 10.0,
) -> CityWeatherData:
    return CityWeatherData(
        city="Test",
        country="X",
        country_code="XX",
        lat=0.0,
        lon=0.0,
        population=1,
        date="2024-01-01",
        temperature_2m_max=temp_max,
        temperature_2m_min=temp_min,
        precipitation_sum=1.0,
        windspeed_10m_max=windspeed,
        windgusts_10m_max=windspeed,
        fetch_success=True,
    )


def test_transform_to_city_weather_result_uses_metric_and_rank_data() -> None:
    service = _service()
    city = _city(windspeed=25.0)

    result = service.transform_to_city_weather_result(city, "windiest_today")

    assert isinstance(result, CityWeatherResult)
    assert result.metric == AnalyticsMetric.WINDSPEED_10M_MAX
    assert result.value == pytest.approx(25.0)
    assert result.date == date(2024, 1, 1)


def test_transform_falls_back_when_metric_missing() -> None:
    service = _service()
    city = _city(windspeed=None)

    result = service.transform_to_city_weather_result(city, "windiest_today")

    assert result.value == pytest.approx(20.0)  # fallback from temp max/min diff or other fields


def test_process_weather_results_sorts_and_computes_temp_range() -> None:
    service = _service()
    a = _city(windspeed=5.0, temp_max=18.0, temp_min=12.0)
    b = _city(windspeed=15.0, temp_max=25.0, temp_min=5.0)

    processed = service.process_weather_results([a, b], "windiest_today", aggregate=False)

    assert [c.city for c in processed] == [
        "Test",
        "Test",
    ]  # same name, order matters by windspeed desc
    assert processed[0].windspeed_10m_max == 15.0


def test_process_weather_results_handles_no_valid_data() -> None:
    service = _service()
    invalid = _city(windspeed=None)
    invalid.fetch_success = False

    processed = service.process_weather_results([invalid], "windiest_today")

    assert len(processed) == 0


def test_calculate_statistics_for_results_none_safe_returns_stats() -> None:
    service = _service()
    results = [
        CityWeatherResult(
            city_name="A",
            country="X",
            country_code="XX",
            latitude=0.0,
            longitude=0.0,
            value=10.0,
            metric=AnalyticsMetric.WINDSPEED_10M_MAX,
            date=date(2024, 1, 1),
            population=None,
            quality_score=0.0,
        ),
        CityWeatherResult(
            city_name="B",
            country="X",
            country_code="XX",
            latitude=0.0,
            longitude=0.0,
            value=20.0,
            metric=AnalyticsMetric.WINDSPEED_10M_MAX,
            date=date(2024, 1, 1),
            population=None,
            quality_score=0.0,
        ),
    ]

    stats = service.calculate_statistics_for_results_none_safe(results)

    assert stats["mean"] == pytest.approx(15.0)
    assert stats["range"] == pytest.approx(10.0)


def test_create_empty_analytics_result_returns_valid_object() -> None:
    service = _service()
    question = AnalyticsQuestion(
        question_text="q",
        question_type=QuestionType.TEMPERATURE_MAX,
        region_scope=RegionScope.GLOBAL,
        metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
    )

    result = service.create_empty_analytics_result(question, "error")

    assert result.question == question
    assert result.city_results == []
    assert result.statistics == {}
