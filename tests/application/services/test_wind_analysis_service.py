"""Tests for the application-layer wind analysis service."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd

from src.application.services import wind_analysis_service
from src.application.services.wind_analysis_service import (
    WindAnalysisResultDTO,
    WindAnalysisService,
)


def test_result_dto_from_domain_converts_nested_objects() -> None:
    """Domain-like results should be converted into DTO values."""
    result = SimpleNamespace(
        location_name="Budapest",
        threshold_kmh=42.0,
        total_days=3,
        total_windy_days=1,
        overall_windy_percentage=33.3,
        avg_max_wind_speed=25.0,
        max_wind_speed=60.0,
        windiest_month="March",
        calmest_month="April",
        monthly_stats=[
            SimpleNamespace(
                month="March",
                windy_days_count=1,
                total_days=3,
                windy_percentage=33.3,
                avg_max_speed=25.0,
            )
        ],
        windy_days=[
            SimpleNamespace(
                date=pd.Timestamp("2026-03-15"),
                max_wind_speed_kmh=60.0,
                avg_wind_speed_kmh=30.0,
                direction="NW",
                is_windy=True,
            )
        ],
    )

    dto = WindAnalysisResultDTO.from_domain(result)

    assert dto.location_name == "Budapest"
    assert dto.monthly_stats[0].month == "March"
    assert dto.windy_days[0].date == "2026-03-15T00:00:00"
    assert dto.windy_days[0].direction == "NW"


def test_result_dto_from_domain_handles_plain_string_dates() -> None:
    """Date conversion should fall back to string when isoformat is unavailable."""
    result = SimpleNamespace(
        location_name="Budapest",
        threshold_kmh=42.0,
        total_days=1,
        total_windy_days=0,
        overall_windy_percentage=0.0,
        avg_max_wind_speed=10.0,
        max_wind_speed=10.0,
        windiest_month=None,
        calmest_month=None,
        monthly_stats=[],
        windy_days=[
            SimpleNamespace(
                date="2026-03-16",
                max_wind_speed_kmh=10.0,
                avg_wind_speed_kmh=None,
                direction=None,
                is_windy=False,
            )
        ],
    )

    dto = WindAnalysisResultDTO.from_domain(result)

    assert dto.windy_days[0].date == "2026-03-16"


def test_analyze_delegates_to_domain_service_and_wraps_result() -> None:
    """Application service should delegate to the domain service."""
    weather_data = pd.DataFrame({"wind_gusts_max": [10.0]})
    domain_result = SimpleNamespace(
        location_name="Budapest",
        threshold_kmh=43.0,
        total_days=1,
        total_windy_days=0,
        overall_windy_percentage=0.0,
        avg_max_wind_speed=10.0,
        max_wind_speed=10.0,
        windiest_month=None,
        calmest_month=None,
        monthly_stats=[],
        windy_days=[],
    )
    analyze_mock = MagicMock(return_value=domain_result)
    original = wind_analysis_service.analyze_wind_patterns
    wind_analysis_service.analyze_wind_patterns = analyze_mock

    try:
        dto = WindAnalysisService.analyze(
            weather_data,
            location_name="Budapest",
            threshold_kmh=50.0,
        )
    finally:
        wind_analysis_service.analyze_wind_patterns = original

    analyze_mock.assert_called_once_with(
        weather_data=weather_data,
        location_name="Budapest",
        threshold_kmh=50.0,
    )
    assert dto.location_name == "Budapest"


def test_get_windy_day_threshold_returns_domain_constant() -> None:
    """The service should expose the configured default threshold."""
    assert (
        WindAnalysisService.get_windy_day_threshold()
        == wind_analysis_service.WINDY_DAY_THRESHOLD_KMH
    )
