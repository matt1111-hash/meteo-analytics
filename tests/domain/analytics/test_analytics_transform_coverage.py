"""Tests for AnalyticsTransformService — additional coverage for missing branches."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest
from src.data.enums import AnalyticsMetric
from src.data.models import CityWeatherResult
from src.domain.analytics.models import CityWeatherData
from src.domain.analytics.services.analytics_transform_service import (
    AnalyticsTransformService,
)
from src.domain.value_objects.enums import AnalyticsMetric as DomainMetric

QUERY_TYPES = {
    "windiest_today": {
        "name": "Legszelesebb ma",
        "metric": "windspeed_10m_max",
        "unit": "km/h",
        "sort_desc": True,
        "question_template": "Hol fújt ma a legerősebb szél?",
        "metric_enum": AnalyticsMetric.WINDSPEED_10M_MAX,
    },
    "temperature_range": {
        "name": "Legnagyobb hőingás",
        "metric": "temperature_range",
        "unit": "°C",
        "sort_desc": True,
        "question_template": "Hol volt a legnagyobb hőingás?",
        "metric_enum": AnalyticsMetric.TEMPERATURE_RANGE,
    },
    "precipitation": {
        "name": "Csapadék",
        "metric": "precipitation_sum",
        "unit": "mm",
        "sort_desc": True,
        "question_template": "Hol esett a legtöbb csapadék?",
        "metric_enum": AnalyticsMetric.PRECIPITATION_SUM,
    },
    "temp_max_asc": {
        "name": "Leghidegebb",
        "metric": "temperature_2m_max",
        "unit": "°C",
        "sort_desc": False,
        "question_template": "Hol volt a leghidegebb?",
        "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MAX,
    },
}


def _service() -> AnalyticsTransformService:
    return AnalyticsTransformService(QUERY_TYPES)


def _city(
    name: str = "Test",
    windspeed: float | None = 10.0,
    temp_max: float | None = 20.0,
    temp_min: float | None = 10.0,
    precip: float | None = 1.0,
    success: bool = True,
    date_str: str = "2024-01-01",
) -> CityWeatherData:
    return CityWeatherData(
        city=name,
        country="X",
        country_code="XX",
        lat=0.0,
        lon=0.0,
        population=1,
        date=date_str,
        temperature_2m_max=temp_max,
        temperature_2m_min=temp_min,
        precipitation_sum=precip,
        windspeed_10m_max=windspeed,
        windgusts_10m_max=windspeed,
        fetch_success=success,
    )


class TestConstructorValidation:
    """Cover line 31: empty query_types raises ValueError."""

    def test_empty_query_types_raises(self) -> None:
        with pytest.raises(ValueError, match="query_types"):
            AnalyticsTransformService({})


class TestUnknownQueryType:
    """Cover line 41: unknown query_type raises ValueError."""

    def test_unknown_query_type_raises(self) -> None:
        service = _service()
        with pytest.raises(ValueError, match="Ismeretlen query_type"):
            service.transform_to_city_weather_result(_city(), "nonexistent_query_type")

    def test_unknown_query_type_in_process(self) -> None:
        service = _service()
        with pytest.raises(ValueError, match="Ismeretlen query_type"):
            service.process_weather_results([_city()], "nonexistent_query_type")


class TestTemperatureRangeMetric:
    """Cover lines 82, 145-155: temperature_range extraction and computation."""

    def test_temperature_range_computed_via_process(self) -> None:
        service = _service()
        city = _city(temp_max=25.0, temp_min=5.0)

        processed = service.process_weather_results([city], "temperature_range", aggregate=True)
        assert len(processed) == 1
        assert processed[0].temperature_range == pytest.approx(20.0)

    def test_temperature_range_skips_failed_fetch(self) -> None:
        service = _service()
        city = _city(temp_max=25.0, temp_min=5.0, success=False)
        processed = service.process_weather_results([city], "temperature_range", aggregate=True)
        assert len(processed) == 0

    def test_temperature_range_skips_none_temp(self) -> None:
        service = _service()
        city = _city(temp_max=None, temp_min=5.0)
        processed = service.process_weather_results([city], "temperature_range", aggregate=True)
        assert len(processed) == 0


class TestPrecipitationFallback:
    """Cover line 109: precipitation fallback is 0.0."""

    def test_precipitation_fallback_is_zero(self) -> None:
        service = _service()
        city = _city(precip=None, windspeed=None, temp_max=None, temp_min=None)

        result = service.transform_to_city_weather_result(city, "precipitation")
        assert result.value == pytest.approx(0.0)


class TestCityAggregation:
    """Cover lines 171-175: aggregation keeps highest value."""

    def test_aggregation_keeps_max_value_per_city(self) -> None:
        service = _service()
        a = _city(name="CityA", windspeed=10.0, date_str="2024-01-01")
        b = _city(name="CityA", windspeed=25.0, date_str="2024-01-02")
        c = _city(name="CityB", windspeed=15.0, date_str="2024-01-01")

        processed = service.process_weather_results([a, b, c], "windiest_today", aggregate=True)
        cities = {p.city: p.windspeed_10m_max for p in processed}
        assert cities["CityA"] == 25.0
        assert cities["CityB"] == 15.0


class TestSortingEdgeCases:
    """Cover lines 215, 218-219, 223-225: sort with None values and errors."""

    def test_sort_desc_with_mixed_values(self) -> None:
        service = _service()
        a = _city(name="A", windspeed=10.0)
        _unused_b = _city(name="B", windspeed=None, success=False)
        c = _city(name="C", windspeed=5.0)

        processed = service.process_weather_results([a, c], "windiest_today", aggregate=False)
        assert len(processed) == 2
        assert processed[0].windspeed_10m_max >= processed[1].windspeed_10m_max

    def test_sort_error_handling_returns_unsorted(self) -> None:
        service = _service()
        a = _city(windspeed=10.0)
        b = _city(windspeed=20.0)

        with patch(
            "src.domain.analytics.services.analytics_transform_service.sorted",
            side_effect=Exception("sort error"),
        ):
            processed = service.process_weather_results([a, b], "windiest_today", aggregate=False)
            assert len(processed) == 2


class TestStatisticsEdgeCases:
    """Cover lines 280-281, 289-302: statistics with empty/None values."""

    def test_statistics_empty_results(self) -> None:
        service = _service()
        stats = service.calculate_statistics_for_results_none_safe([])
        assert stats == {}

    def test_statistics_range_calculated(self) -> None:
        service = _service()
        results = [
            CityWeatherResult(
                city_name="A",
                country="X",
                country_code="XX",
                latitude=0.0,
                longitude=0.0,
                value=5.0,
                metric=DomainMetric.TEMPERATURE_2M_MAX,
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
                value=15.0,
                metric=DomainMetric.TEMPERATURE_2M_MAX,
                date=date(2024, 1, 1),
                population=None,
                quality_score=0.0,
            ),
        ]
        stats = service.calculate_statistics_for_results_none_safe(results)
        assert stats["range"] == pytest.approx(10.0)
        assert stats["min"] == pytest.approx(5.0)
        assert stats["max"] == pytest.approx(15.0)
        assert stats["mean"] == pytest.approx(10.0)


class TestCreateEmptyResultEdgeCase:
    """Cover lines 335-337: exception in create_empty_analytics_result."""

    def test_raises_when_question_creation_fails(self) -> None:
        service = _service()
        with (
            patch(
                "src.domain.analytics.services.analytics_transform_service.AnalyticsQuestion",
                side_effect=TypeError("bad question"),
            ),
            pytest.raises(TypeError),
        ):
            service.create_empty_analytics_result(None, "error")


class TestProviderStats:
    """Cover provider_stats method."""

    def test_provider_stats_counts_sources(self) -> None:
        service = _service()
        data = [
            _city(name="A"),
            _city(name="B"),
        ]
        data[0].data_source = "open-meteo"
        data[1].data_source = "open-meteo"

        stats = service.get_provider_stats(data)
        assert stats["open-meteo"] == 2

    def test_provider_stats_unknown_source(self) -> None:
        service = _service()
        data = [_city()]
        data[0].data_source = None

        stats = service.get_provider_stats(data)
        assert stats["unknown"] == 1


class TestNonAggregateMode:
    """Cover non-aggregate process_weather_results path."""

    def test_non_aggregate_returns_all_records(self) -> None:
        service = _service()
        records = [
            _city(name="A", windspeed=10.0, date_str="2024-01-01"),
            _city(name="A", windspeed=20.0, date_str="2024-01-02"),
        ]
        processed = service.process_weather_results(records, "windiest_today", aggregate=False)
        assert len(processed) == 2
