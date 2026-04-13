"""Tests for time range, query entities, and analysis factories."""

from datetime import date, datetime

from src.domain.entities.analysis_factories import (
    create_analytics_question,
    create_universal_query,
    create_universal_time_range,
)
from src.domain.entities.analysis_type import AnalysisType
from src.domain.entities.location_types import LocationType
from src.domain.entities.time_granularity import TimeGranularity
from src.domain.entities.universal_location import UniversalLocation
from src.domain.entities.universal_query import UniversalQuery
from src.domain.entities.universal_time_range import UniversalTimeRange
from src.domain.value_objects.enums import (
    AnalyticsMetric,
    DataSource,
    QuestionType,
    RegionScope,
)


def _build_location(
    name: str, *, location_type: LocationType = LocationType.CITY
) -> UniversalLocation:
    """Create a compact reusable test location."""
    return UniversalLocation(
        type=location_type,
        identifier=name.lower(),
        display_name=name,
        coordinates=(47.0, 19.0),
    )


def test_universal_time_range_generates_description_and_helpers() -> None:
    """Time range derives descriptions, months, years, and overlap flags."""
    single_day = UniversalTimeRange(
        start_date=date(2020, 1, 2),
        end_date=date(2020, 1, 2),
        granularity=TimeGranularity.DAILY,
    )
    weekly = UniversalTimeRange(
        start_date=date(2020, 1, 1),
        end_date=date(2020, 1, 7),
        granularity=TimeGranularity.WEEKLY,
    )
    monthly = UniversalTimeRange(
        start_date=date(2020, 1, 1),
        end_date=date(2020, 1, 31),
        granularity=TimeGranularity.MONTHLY,
    )
    yearly = UniversalTimeRange(
        start_date=date(2020, 1, 1),
        end_date=date(2020, 12, 31),
        granularity=TimeGranularity.YEARLY,
    )
    multi_year = UniversalTimeRange(
        start_date=date(2020, 12, 20),
        end_date=date(2021, 1, 10),
        granularity=TimeGranularity.DAILY,
        exclude_weekends=True,
        seasonal_filter=["winter"],
    )

    assert "Egy nap" in single_day.description
    assert "7 nap" in weekly.description
    assert "~4 hét" in monthly.description
    assert "~1 év" in yearly.description
    assert str(single_day).endswith("[daily]")
    assert multi_year.total_days == 22
    assert multi_year.is_historical is True
    assert multi_year.is_future is False
    assert multi_year.overlaps_with(yearly) is True
    assert multi_year.contains_date(date(2020, 12, 31)) is True
    assert multi_year.get_months_list() == ["2020-12", "2021-01"]
    assert multi_year.get_years_list() == [2020, 2021]
    assert multi_year.to_dict()["seasonal_filter"] == ["winter"]


def test_universal_time_range_split_by_years_handles_single_and_multi_year_ranges() -> None:
    """Year splitting returns unchanged single-year ranges and segmented multi-year ranges."""
    single_year = UniversalTimeRange(
        start_date=date(2021, 2, 1),
        end_date=date(2021, 2, 28),
        granularity=TimeGranularity.MONTHLY,
    )
    split = UniversalTimeRange(
        start_date=date(2021, 12, 15),
        end_date=date(2023, 1, 15),
        granularity=TimeGranularity.DAILY,
    ).split_by_years()

    assert single_year.split_by_years() == [single_year]
    assert [item.start_date for item in split] == [
        date(2021, 12, 15),
        date(2022, 1, 1),
        date(2023, 1, 1),
    ]
    assert [item.end_date for item in split] == [
        date(2021, 12, 31),
        date(2022, 12, 31),
        date(2023, 1, 15),
    ]
    assert all(item.granularity is TimeGranularity.YEARLY for item in split)


def test_analysis_factories_convert_strings_and_build_entities() -> None:
    """Factories accept string inputs and create fully wired entities."""
    time_range = create_universal_time_range(
        "2022-01-01",
        "2022-12-31",
        "monthly",
        exclude_weekends=True,
    )
    query = create_universal_query(
        locations=[_build_location("Budapest"), _build_location("Szeged")],
        time_range=time_range,
        parameters=["temperature_2m_mean"],
        analysis_type="trend_analysis",
        created_by="tester",
        tags=["coverage"],
    )
    question = create_analytics_question(
        "Hol a legmelegebb?",
        QuestionType.TEMPERATURE_MAX,
        RegionScope.COUNTRY,
        AnalyticsMetric.TEMPERATURE_2M_MAX,
    )

    assert time_range.granularity is TimeGranularity.MONTHLY
    assert time_range.exclude_weekends is True
    assert query.analysis_type is AnalysisType.TREND_ANALYSIS
    assert query.created_by == "tester"
    assert query.comparative_mode is True
    assert question.question_text == "Hol a legmelegebb?"
    assert question.metric is AnalyticsMetric.TEMPERATURE_2M_MAX


def test_universal_query_description_complexity_validation_and_serialization() -> None:
    """UniversalQuery derives descriptions, complexity, and validation errors."""
    multi_location = UniversalLocation(
        type=LocationType.MULTIPLE,
        identifier=["Budapest", "Szeged"],
        display_name="Pair",
        child_locations=[_build_location("Budapest"), _build_location("Szeged")],
    )
    historical_range = UniversalTimeRange(
        start_date=date(2020, 1, 1),
        end_date=date(2021, 12, 31),
        granularity=TimeGranularity.MONTHLY,
        description="Historic period",
    )
    query = UniversalQuery(
        locations=[_build_location("Budapest"), multi_location],
        time_range=historical_range,
        parameters=["temperature_2m_mean", "precipitation_sum"],
        analysis_type=AnalysisType.TREND_ANALYSIS,
        anomaly_detection=True,
        anomaly_threshold_override=-1.0,
        max_results_per_location=50,
        data_sources=[DataSource.OPEN_METEO],
        created_by="qa",
        created_at=datetime(2024, 1, 2, 3, 4, 5),
        tags=["one", "two"],
    )

    valid, errors = query.validate()
    serialized = query.to_dict()

    assert "Budapest vs Pair" in query.user_description
    assert str(query).startswith("UniversalQuery[")
    assert query.get_total_locations() == 3
    assert query.get_all_coordinates() == [(47.0, 19.0), (47.0, 19.0), (47.0, 19.0)]
    assert query.is_multi_location_query() is True
    assert query.is_long_term_analysis() is True
    assert query.is_historical_query() is True
    assert query.get_estimated_complexity() == "complex"
    assert valid is False
    assert any("Anomália küszöb pozitív szám" in error for error in errors)
    assert serialized["data_sources"] == ["open-meteo"]
    assert serialized["created_at"] == "2024-01-02T03:04:05"
    assert serialized["estimated_complexity"] == "complex"
    assert serialized["is_long_term"] is True


def test_universal_query_validation_covers_empty_and_very_complex_cases() -> None:
    """Validation reports missing inputs and too-small limits for very complex queries."""
    huge_range = UniversalTimeRange(
        start_date=date(2020, 1, 1),
        end_date=date(2026, 12, 31),
        granularity=TimeGranularity.MONTHLY,
    )
    huge_locations = [_build_location(f"City{i}") for i in range(10)]
    huge_query = UniversalQuery(
        locations=huge_locations,
        time_range=huge_range,
        parameters=["temperature_2m_mean", "precipitation_sum", "windgusts_10m_max"],
        analysis_type=AnalysisType.FORECAST,
        max_results_per_location=99,
    )
    invalid_range_query = UniversalQuery(
        locations=[],
        time_range=UniversalTimeRange(
            start_date=date(2022, 2, 1),
            end_date=date(2022, 1, 1),
            granularity=TimeGranularity.DAILY,
        ),
        parameters=[],
        analysis_type=AnalysisType.CUSTOM,
        anomaly_detection=True,
        anomaly_threshold_override=-0.1,
    )

    huge_valid, huge_errors = huge_query.validate()
    invalid_valid, invalid_errors = invalid_range_query.validate()

    assert huge_query.get_estimated_complexity() == "very_complex"
    assert huge_valid is False
    assert any("max_results_per_location" in error for error in huge_errors)
    assert invalid_valid is False
    assert len(invalid_range_query.data_sources) == 1
    assert invalid_range_query.data_sources[0] is DataSource.AUTO
    assert any("Legalább egy lokáció" in error for error in invalid_errors)
    assert any("Legalább egy paraméter" in error for error in invalid_errors)
    assert any("kezdő dátum" in error for error in invalid_errors)
    assert any("Anomália küszöb pozitív szám" in error for error in invalid_errors)
