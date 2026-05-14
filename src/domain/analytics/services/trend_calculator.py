"""Domain port for trend calculation — implementation lives in infrastructure."""

from __future__ import annotations

from typing import Protocol

from src.domain.entities.trend_result import TrendAnalysisResult, TrendPeriodResult
from src.domain.value_objects.enums import AnalyticsMetric


class TrendCalculatorPort(Protocol):
    """Interface for statistical trend calculation."""

    def calculate_trend(  # noqa: D102
        self,
        weather_data: list[dict[str, object]],
        metric: AnalyticsMetric,
        _location_name: str,
        time_period_years: int,
    ) -> TrendPeriodResult | None: ...

    def calculate_multiple_periods(  # noqa: D102
        self,
        weather_data: list[dict[str, object]],
        metric: AnalyticsMetric,
        location_name: str,
        time_periods: list[int],
        end_date: str | None = None,
    ) -> TrendAnalysisResult: ...


__all__ = ["TrendCalculatorPort"]
