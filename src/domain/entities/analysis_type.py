"""Analysis type enum for analytics."""
from enum import Enum


class AnalysisType(Enum):
    """Analysis types for user analytics freedom."""
    CURRENT_CONDITIONS = "current_conditions"
    TREND_ANALYSIS = "trend_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    COMPARATIVE = "comparative"
    STATISTICAL = "statistical"
    PATTERN_RECOGNITION = "pattern_recognition"
    FORECAST = "forecast"
    CUSTOM = "custom"


__all__ = ['AnalysisType']
