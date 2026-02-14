"""Trend calculator service for climate trend analysis.

Provides statistical trend calculation with confidence intervals and significance testing.
Extracted from GUI layer for API reuse.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.domain.entities.trend_result import TrendAnalysisResult, TrendPeriodResult
from src.domain.value_objects.enums import AnalyticsMetric

from .trend_data_processor import TrendDataProcessor
from .trend_statistics import TrendStatisticsCalculator

logger = logging.getLogger(__name__)


class TrendCalculator:
    """
    Statistical trend calculator for climate data.

    Calculates linear regression trends with:
    - Slope (change per year/decade)
    - R² (coefficient of determination)
    - p-value (statistical significance)
    - Confidence intervals
    - Trend direction classification
    """

    # Significance thresholds
    HIGHLY_SIGNIFICANT = 0.001
    SIGNIFICANT = 0.01
    MODERATELY_SIGNIFICANT = 0.05

    # Minimum data requirements
    MIN_DAILY_RECORDS = 30
    MIN_MONTHLY_POINTS = 6

    def __init__(self) -> None:
        """Initialize the trend calculator."""
        self.metric_field_map = {
            AnalyticsMetric.TEMPERATURE_2M_MAX: "temperature_2m_max",
            AnalyticsMetric.TEMPERATURE_2M_MIN: "temperature_2m_min",
            AnalyticsMetric.TEMPERATURE_2M_MEAN: "temperature_2m_mean",
            AnalyticsMetric.PRECIPITATION_SUM: "precipitation_sum",
            AnalyticsMetric.WINDSPEED_10M_MAX: "windspeed_10m_max",
            AnalyticsMetric.WINDGUSTS_10M_MAX: "windgusts_10m_max",
            AnalyticsMetric.TEMPERATURE_RANGE: "temperature_range",
        }
        self.data_processor = TrendDataProcessor()
        self.stats_calculator = TrendStatisticsCalculator()

    def calculate_trend(
        self,
        weather_data: List[Dict[str, Any]],
        metric: AnalyticsMetric,
        _location_name: str,
        time_period_years: int,
    ) -> Optional[TrendPeriodResult]:
        """Calculate trend statistics for a single time period."""
        if not weather_data:
            logger.warning("No weather data provided for trend calculation")
            return None

        api_field = self._get_api_field(metric)
        if not api_field:
            logger.error("Unknown metric: %s", metric)
            return None

        # Prepare data
        df = self.data_processor.prepare_dataframe(weather_data, api_field)
        if df is None or len(df) < self.MIN_DAILY_RECORDS:
            logger.warning(
                "Insufficient data: %d records", len(df) if df is not None else 0
            )
            return None

        # Monthly aggregation
        monthly_df = self.data_processor.aggregate_monthly(df)
        if monthly_df is None or len(monthly_df) < self.MIN_MONTHLY_POINTS:
            n_points = len(monthly_df) if monthly_df is not None else 0
            logger.warning("Insufficient monthly data points: %d", n_points)
            return None

        # Linear regression
        trend_stats = self.stats_calculator.calculate_linear_regression(monthly_df)
        if not trend_stats:
            return None

        # Extract years from dates
        years = self.data_processor.extract_years(monthly_df)

        # Classify trend direction
        trend_direction = self._classify_trend_direction(
            trend_stats["slope"], trend_stats["p_value"]
        )

        # Assess significance
        significance = self._assess_significance(trend_stats["p_value"])

        # Create result
        return TrendPeriodResult(
            time_period=time_period_years,
            years=years,
            slope=float(trend_stats["slope"]),
            slope_per_decade=float(trend_stats["slope_per_decade"]),
            r_squared=float(trend_stats["r_squared"]),
            p_value=float(trend_stats["p_value"]),
            trend_direction=trend_direction,
            confidence_interval=trend_stats["confidence_interval"],
            significance=significance,
            yearly_means=self.data_processor.calculate_yearly_means(monthly_df),
            yearly_dates=self.data_processor.calculate_yearly_dates(monthly_df),
            intercept=float(trend_stats["intercept"]),
            std_error=float(trend_stats["std_error"]),
            sample_size=len(monthly_df),
        )

    def calculate_multiple_periods(
        self,
        weather_data: List[Dict[str, Any]],
        metric: AnalyticsMetric,
        location_name: str,
        time_periods: List[int],
        end_date: Optional[str] = None,
    ) -> TrendAnalysisResult:
        """Calculate trends for multiple time periods."""
        start_time = time.time()

        # Sort data by date
        sorted_data = sorted(weather_data, key=lambda x: x.get("date", ""))

        # Determine end date
        if end_date:
            try:
                calculated_end = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                calculated_end = datetime.now()
        else:
            calculated_end = datetime.now()

        # Get date range
        start_date_str = sorted_data[0].get("date", "") if sorted_data else ""
        end_date_str = sorted_data[-1].get("date", "") if sorted_data else ""

        # Calculate for each period
        periods: List[TrendPeriodResult] = []
        for period_years in sorted(time_periods):
            period_start = calculated_end.replace(
                year=calculated_end.year - period_years
            )
            period_start_str = period_start.strftime("%Y-%m-%d")

            period_data = [
                d
                for d in sorted_data
                if period_start_str
                <= d.get("date", "")
                <= calculated_end.strftime("%Y-%m-%d")
            ]

            if period_data:
                result = self.calculate_trend(
                    period_data, metric, location_name, period_years
                )
                if result:
                    periods.append(result)

        execution_time = time.time() - start_time

        return TrendAnalysisResult(
            location_name=location_name,
            metric=metric,
            periods=periods,
            execution_time=execution_time,
            total_data_points=len(weather_data),
            date_range=(start_date_str, end_date_str),
        )

    def _get_api_field(self, metric: AnalyticsMetric) -> Optional[str]:
        """Get API field name from AnalyticsMetric enum."""
        return self.metric_field_map.get(metric)

    def _classify_trend_direction(self, slope: float, p_value: float) -> str:
        """Classify trend direction: 'increasing', 'decreasing', or 'stable'."""
        if p_value >= self.MODERATELY_SIGNIFICANT:
            return "stable"
        return "increasing" if slope > 0 else "decreasing"

    def _assess_significance(self, p_value: float) -> str:
        """Assess statistical significance level."""
        if p_value < self.HIGHLY_SIGNIFICANT:
            return "highly_significant"
        if p_value < self.SIGNIFICANT:
            return "significant"
        if p_value < self.MODERATELY_SIGNIFICANT:
            return "moderately_significant"
        return "not_significant"


__all__ = ["TrendCalculator"]
