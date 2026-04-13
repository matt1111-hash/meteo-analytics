"""Tests for API weather adapter helpers."""

from __future__ import annotations

import pytest
from src.api.adapters.weather_adapter import (
    DEFAULT_QUERY_TYPE,
    _extract_date_range,
    _metric_to_query_type,
    to_multi_city_query,
)
from src.api.dto.weather_request import WeatherAnalysisRequest


def test_metric_to_query_type_maps_known_metric() -> None:
    """Known metrics should map to the expected query type."""
    assert _metric_to_query_type("windspeed_10m_max") == "windiest_today"


def test_metric_to_query_type_falls_back_to_default() -> None:
    """Unknown metrics should fall back to the default query type."""
    assert _metric_to_query_type("unknown_metric") == DEFAULT_QUERY_TYPE


def test_extract_date_range_uses_single_date_mode() -> None:
    """Single-date payloads should populate only the primary date."""
    request = WeatherAnalysisRequest(
        cities=["Budapest"],
        date_range={"date": "2026-03-15"},
        metric="temperature_2m_max",
    )

    assert _extract_date_range(request) == {
        "date": "2026-03-15",
        "start_date": None,
        "end_date": None,
    }


def test_extract_date_range_uses_start_end_range() -> None:
    """Date ranges should expose compatible start and end fields."""
    request = WeatherAnalysisRequest(
        cities=["Budapest"],
        date_range={"start": "2026-03-01", "end": "2026-03-03"},
        metric="temperature_2m_max",
    )

    assert _extract_date_range(request) == {
        "date": "2026-03-01",
        "start_date": "2026-03-01",
        "end_date": "2026-03-03",
    }


def test_extract_date_range_falls_back_to_any_available_date() -> None:
    """Partial ranges should still expose a compatible primary date."""
    request = WeatherAnalysisRequest(
        cities=["Budapest"],
        date_range={"end": "2026-03-20"},
        metric="temperature_2m_max",
    )

    assert _extract_date_range(request) == {
        "date": "2026-03-20",
        "start_date": None,
        "end_date": None,
    }


def test_extract_date_range_raises_for_missing_values() -> None:
    """Empty date payloads should raise a value error."""
    request = WeatherAnalysisRequest.model_construct(
        cities=["Budapest"],
        date_range={},
        metric="temperature_2m_max",
    )

    with pytest.raises(ValueError, match="érvényes dátumot"):
        _extract_date_range(request)


def test_to_multi_city_query_uses_metric_and_city_count() -> None:
    """Adapter should build a multi-city query with metric-derived type."""
    request = WeatherAnalysisRequest(
        cities=["Budapest", "Szeged"],
        date_range={"start": "2026-03-01", "end": "2026-03-02"},
        metric="precipitation_sum",
    )

    query = to_multi_city_query(request)

    assert query.query_type == "wettest_today"
    assert query.region == "Global"
    assert query.date == "2026-03-01"
    assert query.start_date == "2026-03-01"
    assert query.end_date == "2026-03-02"
    assert query.limit == 2
    assert query.max_cities == 2
    assert query.cities == ["Budapest", "Szeged"]
