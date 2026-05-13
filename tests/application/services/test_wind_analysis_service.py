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
    """Domain WindAnalysisResult should be converted into DTO values."""
    result = SimpleNamespace(
        location_name="Budapest",
        threshold_kmh=42.0,
        total_days=3,
        total_windy_days=1,
        overall_windy_percentage=33.3,
        windiest_month=SimpleNamespace(
            year=2026,
            month=3,
            month_name="March",
            windy_days_count=1,
            total_days=3,
            windy_percentage=33.3,
            max_wind_speed=60.0,
            avg_wind_speed=25.0,
            windy_days_list=[],
        ),
        calmest_month=SimpleNamespace(
            year=2026,
            month=4,
            month_name="April",
            windy_days_count=0,
            total_days=3,
            windy_percentage=0.0,
            max_wind_speed=10.0,
            avg_wind_speed=5.0,
            windy_days_list=[],
        ),
        monthly_stats=[
            SimpleNamespace(
                year=2026,
                month=3,
                month_name="March",
                windy_days_count=1,
                total_days=3,
                windy_percentage=33.3,
                max_wind_speed=60.0,
                avg_wind_speed=25.0,
                windy_days_list=[],
            )
        ],
    )

    dto = WindAnalysisResultDTO.from_domain(result)

    assert dto.location_name == "Budapest"
    assert dto.monthly_stats[0].month == "March"
    assert dto.windiest_month == "March"
    assert dto.calmest_month == "April"
    assert dto.avg_wind_speed == 25.0
    assert dto.max_wind_speed == 60.0


def test_result_dto_from_domain_handles_none_months() -> None:
    """DTO conversion should handle None windiest/calmest month."""
    result = SimpleNamespace(
        location_name="Budapest",
        threshold_kmh=42.0,
        total_days=1,
        total_windy_days=0,
        overall_windy_percentage=0.0,
        windiest_month=None,
        calmest_month=None,
        monthly_stats=[],
    )

    dto = WindAnalysisResultDTO.from_domain(result)

    assert dto.windiest_month is None
    assert dto.calmest_month is None
    assert dto.avg_wind_speed == 0.0
    assert dto.max_wind_speed == 0.0


def test_analyze_delegates_to_domain_service_and_wraps_result() -> None:
    """Application service should delegate to the domain service."""
    weather_data = pd.DataFrame({"wind_gusts_max": [10.0]})
    domain_result = SimpleNamespace(
        location_name="Budapest",
        threshold_kmh=43.0,
        total_days=1,
        total_windy_days=0,
        overall_windy_percentage=0.0,
        windiest_month=None,
        calmest_month=None,
        monthly_stats=[],
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
