"""Tests for public-API input-size limits (P2 finding #1 / CWE-400).

These guard against a single request triggering unbounded external API fan-out
(one city + one huge date range used to be able to generate thousands of
provider calls).
"""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from src.api.adapters.weather_adapter import to_multi_city_query
from src.api.dto.weather_request import (
    WeatherAnalysisRequest,
    validate_date_span,
    validate_iso_date,
)
from src.api.routes.anomalies import AnomalyDetectionRequest
from src.api.routes.detailed_city import DetailedCityRequest
from src.api.routes.single_city import SingleCityRequest
from src.api.routes.wind_rose_part1 import WindRoseRequest
from src.config.config_settings import RequestLimits

MAX_CITIES = RequestLimits.MAX_CITIES_PER_REQUEST
MAX_DAYS = RequestLimits.MAX_DATE_RANGE_DAYS


# --- helper validators -------------------------------------------------------


def test_validate_iso_date_accepts_iso() -> None:
    """A well-formed YYYY-MM-DD date passes through unchanged."""
    assert validate_iso_date("2026-03-15") == "2026-03-15"


@pytest.mark.parametrize("bad", ["", "2026/03/15", "not-a-date", "2026-13-40", "2026-03"])
def test_validate_iso_date_rejects_malformed(bad: str) -> None:
    """Malformed dates are rejected at the API boundary."""
    with pytest.raises(ValueError):
        validate_iso_date(bad)


def test_validate_date_span_rejects_inverted_range() -> None:
    """An end date before the start date is rejected."""
    with pytest.raises(ValueError):
        validate_date_span("2026-03-20", "2026-03-15")


def test_validate_date_span_rejects_oversized_range() -> None:
    """A span exceeding the limit is rejected (resource-exhaustion guard)."""
    start = datetime(2020, 1, 1)
    end = start.replace(year=start.year + 20)  # ~20 years >> MAX_DAYS
    with pytest.raises(ValueError):
        validate_date_span(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))


def test_validate_date_span_accepts_bounded_range() -> None:
    """A span within the limit is accepted."""
    validate_date_span("2026-01-01", "2026-03-31")  # ~90 days, well within limit


# --- WeatherAnalysisRequest --------------------------------------------------


def _valid_request(**overrides: object) -> WeatherAnalysisRequest:
    base: dict[str, object] = {
        "cities": ["Budapest"],
        "date_range": {"start": "2026-03-01", "end": "2026-03-15"},
        "metric": "temperature_2m_max",
    }
    base.update(overrides)
    return WeatherAnalysisRequest(**base)  # type: ignore[arg-type]


def test_weather_request_accepts_valid_payload() -> None:
    """A minimal valid payload parses without error."""
    req = _valid_request()
    assert req.cities == ["Budapest"]


def test_weather_request_rejects_too_many_cities() -> None:
    """A city list exceeding the cap is rejected."""
    too_many = [f"City{i}" for i in range(MAX_CITIES + 1)]
    with pytest.raises(ValidationError):
        _valid_request(cities=too_many)


def test_weather_request_accepts_cities_at_cap() -> None:
    """Exactly the cap number of cities is accepted (boundary)."""
    at_cap = [f"City{i}" for i in range(MAX_CITIES)]
    req = _valid_request(cities=at_cap)
    assert len(req.cities) == MAX_CITIES


def test_weather_request_rejects_oversized_date_span() -> None:
    """A date_range span larger than the limit is rejected."""
    start = datetime(2020, 1, 1)
    end = start.replace(year=start.year + 10)  # ~10 years
    with pytest.raises(ValidationError):
        _valid_request(
            date_range={
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d"),
            }
        )


def test_weather_request_rejects_malformed_date() -> None:
    """A malformed date in date_range is rejected."""
    with pytest.raises(ValidationError):
        _valid_request(date_range={"start": "2026-03-01", "end": "not-a-date"})


# --- adapter cap -------------------------------------------------------------


def test_adapter_caps_max_cities_at_limit() -> None:
    """Defense-in-depth: even bypassing DTO validation, the adapter caps max_cities.

    The DTO's ``max_length`` is the authoritative gate at the API boundary; this
    confirms the adapter itself never forwards an oversized list.
    """
    fake_request = SimpleNamespace(
        cities=[f"City{i}" for i in range(MAX_CITIES + 5)],
        date_range={"start": "2026-03-01", "end": "2026-03-15"},
        metric="temperature_2m_max",
    )
    query = to_multi_city_query(fake_request)  # type: ignore[arg-type]
    assert query.max_cities == MAX_CITIES
    assert query.limit == MAX_CITIES


def test_adapter_forwards_valid_city_count() -> None:
    """A valid (≤ cap) request forwards its actual city count unchanged."""
    request = WeatherAnalysisRequest(
        cities=["Budapest", "Debrecen"],
        date_range={"start": "2026-03-01", "end": "2026-03-15"},
    )
    query = to_multi_city_query(request)
    assert query.max_cities == 2
    assert query.limit == 2


# --- route-level inline DTOs -------------------------------------------------


@pytest.mark.parametrize(
    "dto",
    [SingleCityRequest, DetailedCityRequest, AnomalyDetectionRequest, WindRoseRequest],
)
def test_route_dtos_reject_malformed_date(dto: type) -> None:
    """Every route DTO rejects a malformed date at the API boundary."""
    kwargs = {"city": "Budapest", "start": "not-a-date", "end": "2026-03-15"}
    if dto is WindRoseRequest:
        # WindRoseRequest has no extra required fields
        pass
    with pytest.raises(ValidationError):
        dto(**kwargs)


@pytest.mark.parametrize(
    "dto",
    [SingleCityRequest, DetailedCityRequest, AnomalyDetectionRequest, WindRoseRequest],
)
def test_route_dtos_reject_inverted_range(dto: type) -> None:
    """Every route DTO rejects an inverted date range."""
    kwargs = {"city": "Budapest", "start": "2026-03-20", "end": "2026-03-15"}
    with pytest.raises(ValidationError):
        dto(**kwargs)


@pytest.mark.parametrize(
    "dto",
    [SingleCityRequest, DetailedCityRequest, AnomalyDetectionRequest, WindRoseRequest],
)
def test_route_dtos_reject_oversized_span(dto: type) -> None:
    """Every route DTO rejects a span larger than the limit."""
    start = datetime(2020, 1, 1)
    end = start.replace(year=start.year + 10)  # ~10 years
    kwargs = {
        "city": "Budapest",
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
    }
    with pytest.raises(ValidationError):
        dto(**kwargs)
