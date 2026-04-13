"""
Global Weather Analyzer - Data Enums (Legacy Export Module)
🎯 CLEAN ARCHITECTURE MIGRATION - This file now re-exports from Domain layer.

Usage (Legacy - still works):
from src.data.enums import AnalyticsMetric  # Works

Recommended new usage:
from src.domain.value_objects.enums import AnalyticsMetric
"""

# Re-export from Domain Layer
from src.domain.value_objects.enums import (
    AnalysisType,
    AnalyticsMetric,
    AnalyticsMode,
    AnomalySeverity,
    AnomalyType,
    DataProvider,
    DataSource,
    QuestionType,
    RegionScope,
    RegionType,
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

# Export all symbols
__all__ = [
    "AnalysisType",
    "AnalyticsMetric",
    "AnalyticsMode",
    "AnomalySeverity",
    "AnomalyType",
    "DataProvider",
    "DataSource",
    "QuestionType",
    "RegionScope",
    "RegionType",
    "get_analysis_type_display_name",
    "get_available_metrics_for_question_type",
    "get_data_provider_display_name",
    "get_metric_display_name",
    "get_metric_unit",
    "get_question_type_display_name",
    "get_region_scope_display_name",
    "get_severity_color",
    "validate_analysis_type",
    "validate_analytics_metric",
    "validate_data_provider",
    "validate_region_scope",
]
