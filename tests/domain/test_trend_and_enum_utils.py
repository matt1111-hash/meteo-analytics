"""Tests for trend result entities and enum utility helpers."""

from datetime import datetime

from src.domain.entities.trend_result import TrendAnalysisResult, TrendPeriodResult
from src.domain.value_objects.enum_utils import (
    get_analysis_type_display_name,
    get_available_metrics_for_question_type,
    get_data_provider_display_name,
    get_metric_display_name,
    get_metric_unit,
    get_question_type_display_name,
    get_region_scope_display_name,
    get_severity_color,
    validate_analysis_type,
    validate_analytics_metric,
    validate_data_provider,
    validate_region_scope,
)
from src.domain.value_objects.enums import (
    AnalysisType,
    AnalyticsMetric,
    AnomalySeverity,
    DataProvider,
    QuestionType,
    RegionScope,
)


def _build_period(
    years: int, direction: str, significance: str, slope: float
) -> TrendPeriodResult:
    """Create a reusable trend period result."""
    return TrendPeriodResult(
        time_period=years,
        years=[2020, 2021, 2022],
        slope=slope,
        slope_per_decade=slope * 10,
        r_squared=0.8,
        p_value=0.03,
        trend_direction=direction,
        confidence_interval=(slope - 0.1, slope + 0.1),
        significance=significance,
        yearly_means=[1.0, 2.0, 3.0],
        yearly_dates=["2020-01-01", "2021-01-01", "2022-01-01"],
        intercept=1.5,
        std_error=0.2,
        sample_size=30,
    )


def test_trend_period_result_to_dict_serializes_all_fields() -> None:
    """TrendPeriodResult converts tuple and scalar fields for API use."""
    period = _build_period(10, "increasing", "significant", 0.2)

    serialized = period.to_dict()

    assert serialized["time_period"] == 10
    assert serialized["confidence_interval"] == [0.1, 0.30000000000000004]
    assert serialized["intercept"] == 1.5
    assert serialized["sample_size"] == 30


def test_trend_analysis_result_helpers_cover_summary_chart_and_empty_paths() -> None:
    """TrendAnalysisResult handles empty, lookup, summary, chart, and serialization cases."""
    first = _build_period(10, "increasing", "significant", 0.2)
    second = _build_period(30, "stable", "not_significant", 0.0)
    result = TrendAnalysisResult(
        location_name="Budapest",
        metric=AnalyticsMetric.TEMPERATURE_2M_MEAN,
        periods=[first, second],
        execution_time=1.25,
        total_data_points=365,
        date_range=("2020-01-01", "2022-12-31"),
        created_at=datetime(2024, 2, 3, 4, 5, 6),
    )
    empty = TrendAnalysisResult(
        location_name="Empty",
        metric=AnalyticsMetric.PRECIPITATION_SUM,
        periods=[],
    )

    summary = result.get_summary()
    chart = result.get_chart_data(10)
    serialized = result.to_dict()

    assert len(result) == 2
    assert result.get_period(10) is first
    assert result.get_period(999) is None
    assert summary["total_periods"] == 2
    assert summary["trend_directions"]["increasing"] == 1
    assert summary["significant_periods"] == 1
    assert chart["trend_line"] == [1.5, 1.7, 1.9]
    assert chart["trend_direction"] == "increasing"
    assert result.get_chart_data(999) == {}
    assert serialized["metric"] == AnalyticsMetric.TEMPERATURE_2M_MEAN.value
    assert serialized["created_at"] == "2024-02-03T04:05:06"
    assert serialized["summary"]["location_name"] == "Budapest"
    assert empty.get_summary() == {}


def test_enum_utils_display_validation_and_metric_mapping_helpers() -> None:
    """Enum helpers cover known values, fallbacks, validation, and question mappings."""
    assert get_analysis_type_display_name(AnalysisType.TREND) == "Trend elemzés"
    assert get_data_provider_display_name(DataProvider.OPENWEATHER) == "OpenWeatherMap"
    assert (
        get_metric_display_name(AnalyticsMetric.PRECIPITATION_SUM) == "Csapadékösszeg"
    )
    assert get_metric_unit(AnalyticsMetric.UV_INDEX_MAX) == ""
    assert get_region_scope_display_name(RegionScope.GLOBAL) == "Globális"
    assert get_question_type_display_name(QuestionType.WIND_MAX) == "Legerősebb szél"
    assert get_severity_color(AnomalySeverity.EXTREME) == "#dc2626"

    assert validate_analysis_type("trend") is True
    assert validate_analysis_type("unknown") is False
    assert validate_data_provider("meteostat") is True
    assert validate_data_provider("bad-provider") is False
    assert validate_analytics_metric("temperature_2m_max") is True
    assert validate_analytics_metric("bad-metric") is False
    assert validate_region_scope("country") is True
    assert validate_region_scope("galaxy") is False

    assert get_available_metrics_for_question_type(QuestionType.TEMPERATURE_MAX) == [
        AnalyticsMetric.TEMPERATURE_2M_MAX,
        AnalyticsMetric.APPARENT_TEMPERATURE_MAX,
    ]
    assert get_available_metrics_for_question_type(QuestionType.PRECIPITATION_MAX) == [
        AnalyticsMetric.PRECIPITATION_SUM,
        AnalyticsMetric.RAIN_SUM,
        AnalyticsMetric.SNOWFALL_SUM,
    ]
    assert get_available_metrics_for_question_type(QuestionType.CLIMATE_RANKING) == []
