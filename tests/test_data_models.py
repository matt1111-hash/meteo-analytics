"""Adatmodell funkciók regressziós tesztjei."""

from __future__ import annotations

from datetime import date, datetime
from typing import List

import pytest

from src.data.enums import AnalyticsMetric, DataSource, QuestionType, RegionScope
from src.data.models import (
    AnalyticsQuestion,
    AnalyticsResult,
    CityWeatherResult,
    Location,
    LocationType,
)


def test_location_to_universal_location_preserves_metadata() -> None:
    """Megye metaadatból micro-régió típusú UniversalLocation keletkezzen."""
    location = Location(
        identifier="budapest",
        display_name="Budapest",
        latitude=47.4979,
        longitude=19.0402,
        metadata={"county": "Budapest", "climate_zone": "continental"},
    )
    # Convert Location to UniversalLocation using factory function
    from src.domain.entities.location_factories import create_universal_location
    converted = create_universal_location(
        location_type=LocationType.MICRO_REGION,
        identifier=location.identifier,
        display_name=location.display_name,
        coordinates=(location.latitude, location.longitude),
        climate_zone=location.metadata.get("climate_zone")
    )
    assert converted.type == LocationType.MICRO_REGION
    assert converted.coordinates == (47.4979, 19.0402)
    assert converted.climate_zone == "continental"


def test_analytics_question_validate_collects_all_errors() -> None:
    """Érvénytelen mezők esetén több hibaüzenet is visszatérjen."""
    question = AnalyticsQuestion(
        question_text=" ",
        question_type=QuestionType.CLIMATE_RANKING,
        region_scope=RegionScope.COUNTRY,
        metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
        max_cities=0,
    )
    is_valid, errors = question.validate()
    assert not is_valid
    assert "Kérdés szövege nem lehet üres" in errors
    assert "Maximum városok száma pozitív kell legyen" in errors
    assert any("country scope esetén region_value kötelező" in err for err in errors)


def test_analytics_result_statistics_summary_aggregates_metrics() -> None:
    """Statisztikai összegzés helyes min/max/átlag értékeket adjon."""
    base_kwargs = {
        "city_name": "City",
        "country": "HU",
        "country_code": "HU",
        "latitude": 47.0,
        "longitude": 19.0,
        "metric": AnalyticsMetric.TEMPERATURE_2M_MAX,
        "date": date(2024, 1, 1),
    }
    results: List[CityWeatherResult] = [
        CityWeatherResult(value=10.0, **base_kwargs),
        CityWeatherResult(value=20.0, **base_kwargs),
        CityWeatherResult(value=30.0, **base_kwargs),
    ]
    question = AnalyticsQuestion(
        question_text="Hol a legmelegebb?",
        question_type=QuestionType.CLIMATE_RANKING,
        region_scope=RegionScope.GLOBAL,
        metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
    )
    analytics_result = AnalyticsResult(
        question=question,
        city_results=results,
        execution_time=0.1,
        total_cities_found=3,
        data_sources_used=[DataSource.OPEN_METEO],
        statistics={},
        provider_statistics={},
        average_quality_score=0.9,
        average_confidence=0.95,
        created_at=datetime(2024, 1, 1, 0, 0, 0),
    )
    summary = analytics_result.get_statistics_summary()
    assert summary["count"] == 3
    assert summary["min"] == 10.0
    assert summary["max"] == 30.0
    assert summary["mean"] == pytest.approx(20.0)
    assert summary["median"] == 20.0
    assert summary["stdev"] == pytest.approx(10.0)
    assert summary["range"] == 20.0
