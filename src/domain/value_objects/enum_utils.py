"""Utility functions for domain enums."""

from typing import List

from src.domain.value_objects.enums import (
    AnalysisType,
    AnalyticsMetric,
    AnomalySeverity,
    DataProvider,
    QuestionType,
    RegionScope,
)


def get_analysis_type_display_name(analysis_type: AnalysisType) -> str:
    """Get AnalysisType display name."""
    display_names = {
        AnalysisType.SINGLE_CITY: "Egyváros elemzés",
        AnalysisType.MULTI_CITY: "Többváros elemzés",
        AnalysisType.REGIONAL: "Regionális elemzés",
        AnalysisType.COMPARATIVE: "Összehasonlító elemzés",
        AnalysisType.TREND: "Trend elemzés",
        AnalysisType.STATISTICAL: "Statisztikai elemzés",
        AnalysisType.ANOMALY: "Anomália elemzés",
        AnalysisType.CLIMATE: "Klíma elemzés",
    }
    return display_names.get(analysis_type, analysis_type.value)


def get_data_provider_display_name(provider: DataProvider) -> str:
    """Get DataProvider display name."""
    display_names = {
        DataProvider.OPEN_METEO: "Open-Meteo",
        DataProvider.METEOSTAT: "Meteostat",
        DataProvider.WEATHERAPI: "WeatherAPI",
        DataProvider.OPENWEATHER: "OpenWeatherMap",
        DataProvider.ECMWF: "ECMWF",
        DataProvider.NOAA: "NOAA",
        DataProvider.AUTO: "Automatikus",
    }
    return display_names.get(provider, provider.value)


def validate_data_provider(provider_str: str) -> bool:
    """Validate DataProvider."""
    return provider_str in [p.value for p in DataProvider]


def get_metric_display_name(metric: AnalyticsMetric) -> str:
    """Get metric display name."""
    display_names = {
        AnalyticsMetric.TEMPERATURE_2M_MAX: "Maximum hőmérséklet",
        AnalyticsMetric.TEMPERATURE_2M_MIN: "Minimum hőmérséklet",
        AnalyticsMetric.TEMPERATURE_2M_MEAN: "Átlagos hőmérséklet",
        AnalyticsMetric.PRECIPITATION_SUM: "Csapadékösszeg",
        AnalyticsMetric.WINDSPEED_10M_MAX: "Maximum szélsebesség",
        AnalyticsMetric.WINDGUSTS_10M_MAX: "Maximum széllökés",
        AnalyticsMetric.PRESSURE_MSL_MIN: "Minimum légnyomás",
        AnalyticsMetric.HUMIDITY_2M_MEAN: "Átlagos páratartalom",
        AnalyticsMetric.UV_INDEX_MAX: "Maximum UV index",
        AnalyticsMetric.SUNSHINE_DURATION: "Napsütés időtartama",
    }
    return display_names.get(metric, metric.value)


def get_metric_unit(metric: AnalyticsMetric) -> str:
    """Get metric unit."""
    units = {
        AnalyticsMetric.TEMPERATURE_2M_MAX: "°C",
        AnalyticsMetric.TEMPERATURE_2M_MIN: "°C",
        AnalyticsMetric.TEMPERATURE_2M_MEAN: "°C",
        AnalyticsMetric.PRECIPITATION_SUM: "mm",
        AnalyticsMetric.WINDSPEED_10M_MAX: "km/h",
        AnalyticsMetric.WINDGUSTS_10M_MAX: "km/h",
        AnalyticsMetric.PRESSURE_MSL_MIN: "hPa",
        AnalyticsMetric.HUMIDITY_2M_MEAN: "%",
        AnalyticsMetric.UV_INDEX_MAX: "",
        AnalyticsMetric.SUNSHINE_DURATION: "h",
    }
    return units.get(metric, "")


def get_region_scope_display_name(scope: RegionScope) -> str:
    """Get RegionScope display name."""
    display_names = {
        RegionScope.COUNTRY: "Ország",
        RegionScope.CONTINENT: "Kontinens",
        RegionScope.GLOBAL: "Globális",
        RegionScope.REGION: "Régió",
        RegionScope.CUSTOM: "Egyedi",
    }
    return display_names.get(scope, scope.value)


def get_question_type_display_name(question_type: QuestionType) -> str:
    """Get QuestionType display name."""
    display_names = {
        QuestionType.TEMPERATURE_MAX: "Legmagasabb hőmérséklet",
        QuestionType.TEMPERATURE_MIN: "Legalacsonyabb hőmérséklet",
        QuestionType.PRECIPITATION_MAX: "Legtöbb csapadék",
        QuestionType.WIND_MAX: "Legerősebb szél",
        QuestionType.EXTREME_WEATHER: "Szélsőséges időjárás",
        QuestionType.WEATHER_COMPARISON: "Időjárás összehasonlítás",
    }
    return display_names.get(question_type, question_type.value)


def get_severity_color(severity: AnomalySeverity) -> str:
    """Get anomaly severity color code."""
    colors = {
        AnomalySeverity.LOW: "#fbbf24",
        AnomalySeverity.MODERATE: "#f97316",
        AnomalySeverity.HIGH: "#ef4444",
        AnomalySeverity.EXTREME: "#dc2626",
        AnomalySeverity.RECORD: "#7c2d12",
    }
    return colors.get(severity, "#6b7280")


def validate_analysis_type(analysis_type_str: str) -> bool:
    """Validate AnalysisType."""
    return analysis_type_str in [a.value for a in AnalysisType]


def validate_analytics_metric(metric_str: str) -> bool:
    """Validate analytics metric."""
    return metric_str in [m.value for m in AnalyticsMetric]


def validate_region_scope(scope_str: str) -> bool:
    """Validate RegionScope."""
    return scope_str in [s.value for s in RegionScope]


def get_available_metrics_for_question_type(
    question_type: QuestionType,
) -> List[AnalyticsMetric]:
    """Get available metrics for a question type."""
    metric_mapping = {
        QuestionType.TEMPERATURE_MAX: [
            AnalyticsMetric.TEMPERATURE_2M_MAX,
            AnalyticsMetric.APPARENT_TEMPERATURE_MAX,
        ],
        QuestionType.TEMPERATURE_MIN: [
            AnalyticsMetric.TEMPERATURE_2M_MIN,
            AnalyticsMetric.APPARENT_TEMPERATURE_MIN,
        ],
        QuestionType.PRECIPITATION_MAX: [
            AnalyticsMetric.PRECIPITATION_SUM,
            AnalyticsMetric.RAIN_SUM,
            AnalyticsMetric.SNOWFALL_SUM,
        ],
        QuestionType.WIND_MAX: [
            AnalyticsMetric.WINDSPEED_10M_MAX,
            AnalyticsMetric.WINDGUSTS_10M_MAX,
        ],
    }
    return metric_mapping.get(question_type, [])


__all__ = [
    "get_analysis_type_display_name",
    "get_data_provider_display_name",
    "get_metric_display_name",
    "get_metric_unit",
    "get_region_scope_display_name",
    "get_question_type_display_name",
    "get_severity_color",
    "validate_analysis_type",
    "validate_data_provider",
    "validate_analytics_metric",
    "validate_region_scope",
    "get_available_metrics_for_question_type",
]
