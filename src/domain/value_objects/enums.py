#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Domain Value Objects - Enums
🎯 CLEAN ARCHITECTURE - Domain layer enum definitions

This file contains all enum definitions that belong to the domain layer.
Moved from src.data.enums as part of Clean Architecture refactoring.
"""

from enum import Enum


class AnalysisType(Enum):
    """
    Analysis type enum.

    For defining analytics and trend analysis types.
    """
    SINGLE_CITY = "single_city"
    MULTI_CITY = "multi_city"
    REGIONAL = "regional"
    COMPARATIVE = "comparative"
    TREND = "trend"
    STATISTICAL = "statistical"
    ANOMALY = "anomaly"
    CLIMATE = "climate"


class RegionScope(Enum):
    """
    Region scope enum.

    For defining geographic scope of analytics queries.
    """
    COUNTRY = "country"
    CONTINENT = "continent"
    GLOBAL = "global"
    REGION = "region"
    CUSTOM = "custom"


class AnalyticsMetric(Enum):
    """
    Analytics metric enum.

    Standardized names for weather parameters.
    """
    # Temperature metrics
    TEMPERATURE_2M_MAX = "temperature_2m_max"
    TEMPERATURE_2M_MIN = "temperature_2m_min"
    TEMPERATURE_2M_MEAN = "temperature_2m_mean"
    APPARENT_TEMPERATURE_MAX = "apparent_temperature_max"
    APPARENT_TEMPERATURE_MIN = "apparent_temperature_min"

    # Precipitation metrics
    PRECIPITATION_SUM = "precipitation_sum"
    PRECIPITATION_HOURS = "precipitation_hours"
    RAIN_SUM = "rain_sum"
    SNOWFALL_SUM = "snowfall_sum"
    SHOWERS_SUM = "showers_sum"

    # Wind metrics
    WINDSPEED_10M_MAX = "windspeed_10m_max"
    WINDGUSTS_10M_MAX = "windgusts_10m_max"
    WINDDIRECTION_10M_DOMINANT = "winddirection_10m_dominant"

    # Atmospheric metrics
    PRESSURE_MSL_MIN = "pressure_msl_min"
    PRESSURE_MSL_MAX = "pressure_msl_max"
    CLOUDCOVER_MEAN = "cloudcover_mean"
    HUMIDITY_2M_MEAN = "relative_humidity_2m"

    # UV and sunshine
    UV_INDEX_MAX = "uv_index_max"
    SUNSHINE_DURATION = "sunshine_duration"

    # Derived metrics
    TEMPERATURE_RANGE = "temperature_range"
    WIND_CHILL = "wind_chill"
    HEAT_INDEX = "heat_index"


class QuestionType(Enum):
    """
    Analytics question type enum.

    For categorizing multi-city analytics questions.
    """
    # Temperature questions
    TEMPERATURE_MAX = "temperature_max"
    TEMPERATURE_MIN = "temperature_min"
    TEMPERATURE_RANGE = "temperature_range"
    HEAT_WAVE = "heat_wave"
    COLD_SNAP = "cold_snap"

    # Precipitation questions
    PRECIPITATION_MAX = "precipitation_max"
    PRECIPITATION_TOTAL = "precipitation_total"
    DROUGHT_ANALYSIS = "drought_analysis"
    FLOOD_RISK = "flood_risk"

    # Wind questions
    WIND_MAX = "wind_max"
    STORM_ANALYSIS = "storm_analysis"
    CALM_WEATHER = "calm_weather"

    # Combined questions
    EXTREME_WEATHER = "extreme_weather"
    WEATHER_COMPARISON = "weather_comparison"
    SEASONAL_ANALYSIS = "seasonal_analysis"
    CLIMATE_RANKING = "climate_ranking"

    # Special questions
    COMFORT_INDEX = "comfort_index"
    TOURISM_WEATHER = "tourism_weather"
    AGRICULTURE_ANALYSIS = "agriculture_analysis"


class AnomalySeverity(Enum):
    """
    Anomaly severity enum.

    For classifying weather anomalies.
    """
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"
    RECORD = "record"


class AnomalyType(Enum):
    """
    Anomaly type enum.

    For determining anomaly direction.
    """
    HIGH = "high"
    LOW = "low"
    BOTH = "both"


class DataProvider(Enum):
    """
    Data provider enum.

    For identifying weather API providers.
    """
    OPEN_METEO = "open-meteo"
    METEOSTAT = "meteostat"
    WEATHERAPI = "weatherapi"
    OPENWEATHER = "openweather"
    ECMWF = "ecmwf"
    NOAA = "noaa"
    AUTO = "auto"


class DataSource(Enum):
    """
    Data source enum.

    For distinguishing weather API sources.
    """
    OPEN_METEO = "open-meteo"
    METEOSTAT = "meteostat"
    ECMWF = "ecmwf"
    NOAA = "noaa"
    AUTO = "auto"


class RegionType(Enum):
    """
    Region type enum.

    For City Manager database queries.
    """
    COUNTRY = "country"
    CONTINENT = "continent"
    ADMINISTRATIVE = "administrative"
    METROPOLITAN = "metropolitan"
    CUSTOM = "custom"


class AnalyticsMode(Enum):
    """
    Analytics mode enum.

    For distinguishing GUI analytics panel modes.
    """
    SINGLE_CITY = "single_city"
    MULTI_CITY = "multi_city"
    PARAMETER_BASED = "parameter_based"


# Re-export utility functions for backward compatibility
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

# EXPORT API
__all__ = [
    'AnalysisType',
    'DataProvider',
    'RegionScope',
    'AnalyticsMetric',
    'QuestionType',
    'AnomalySeverity',
    'AnomalyType',
    'DataSource',
    'RegionType',
    'AnalyticsMode',
    'get_analysis_type_display_name',
    'get_data_provider_display_name',
    'get_metric_display_name',
    'get_metric_unit',
    'get_region_scope_display_name',
    'get_question_type_display_name',
    'get_severity_color',
    'validate_analysis_type',
    'validate_data_provider',
    'validate_analytics_metric',
    'validate_region_scope',
    'get_available_metrics_for_question_type'
]
