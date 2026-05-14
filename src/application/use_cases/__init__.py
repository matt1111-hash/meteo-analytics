"""Application use cases."""

from __future__ import annotations

from .analyze_multi_city import AnalyzeMultiCityUseCase
from .detect_anomalies import DetectAnomaliesUseCase
from .use_case_result import ErrorCategory, ResultStatus, UseCaseResult

__all__ = [
    "AnalyzeMultiCityUseCase",
    "DetectAnomaliesUseCase",
    "ErrorCategory",
    "ResultStatus",
    "UseCaseResult",
]
