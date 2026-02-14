"""Trend analysis domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.domain.value_objects.enums import AnalyticsMetric


@dataclass
class TrendPeriodResult:
    """Single time period trend result."""

    time_period: int  # years
    years: List[int]  # actual years in the period
    slope: float  # change per year
    slope_per_decade: float  # slope * 10
    r_squared: float  # coefficient of determination
    p_value: float  # statistical significance
    trend_direction: str  # "increasing", "decreasing", "stable"
    confidence_interval: Tuple[float, float]  # 95% CI for slope
    significance: str  # "significant", "not_significant", "highly_significant"

    # Raw data
    yearly_means: List[float]  # mean value per year
    yearly_dates: List[str]  # ISO dates for each year

    # Additional statistics
    intercept: float = 0.0
    std_error: float = 0.0
    sample_size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "time_period": self.time_period,
            "years": self.years,
            "slope": self.slope,
            "slope_per_decade": self.slope_per_decade,
            "r_squared": self.r_squared,
            "p_value": self.p_value,
            "trend_direction": self.trend_direction,
            "confidence_interval": list(self.confidence_interval),
            "significance": self.significance,
            "yearly_means": self.yearly_means,
            "yearly_dates": self.yearly_dates,
            "intercept": self.intercept,
            "std_error": self.std_error,
            "sample_size": self.sample_size,
        }


@dataclass
class TrendAnalysisResult:
    """
    Trend analysis result for a location and metric.

    Contains trend calculations for multiple time periods.
    """

    location_name: str
    metric: AnalyticsMetric
    periods: List[TrendPeriodResult]

    # Execution metadata
    execution_time: float = 0.0
    total_data_points: int = 0
    date_range: Tuple[str, str] = ("", "")  # (start_date, end_date)

    # Quality metrics
    data_quality_score: float = 1.0
    completeness_ratio: float = 1.0  # actual_data / expected_data

    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)

    def __len__(self) -> int:
        """Number of period results."""
        return len(self.periods)

    def get_period(self, years: int) -> Optional[TrendPeriodResult]:
        """Get result for specific time period."""
        for period in self.periods:
            if period.time_period == years:
                return period
        return None

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.periods:
            return {}

        directions = [p.trend_direction for p in self.periods]
        direction_counts = {
            "increasing": directions.count("increasing"),
            "decreasing": directions.count("decreasing"),
            "stable": directions.count("stable"),
        }

        return {
            "total_periods": len(self.periods),
            "trend_directions": direction_counts,
            "avg_r_squared": sum(p.r_squared for p in self.periods) / len(self.periods),
            "significant_periods": sum(
                1
                for p in self.periods
                if p.significance in ("significant", "highly_significant")
            ),
            "location_name": self.location_name,
            "metric": self.metric.value,
        }

    def get_chart_data(self, period_years: int) -> Dict[str, Any]:
        """Get data formatted for charting."""
        period = self.get_period(period_years)
        if not period:
            return {}

        # Generate trend line points
        x_values = list(range(len(period.years)))
        y_trend = [period.intercept + period.slope * i for i in x_values]

        return {
            "years": period.years,
            "values": period.yearly_means,
            "trend_line": y_trend,
            "slope_per_decade": period.slope_per_decade,
            "r_squared": period.r_squared,
            "p_value": period.p_value,
            "trend_direction": period.trend_direction,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "location_name": self.location_name,
            "metric": self.metric.value,
            "periods": [p.to_dict() for p in self.periods],
            "execution_time": self.execution_time,
            "total_data_points": self.total_data_points,
            "date_range": list(self.date_range),
            "data_quality_score": self.data_quality_score,
            "completeness_ratio": self.completeness_ratio,
            "created_at": self.created_at.isoformat(),
            "summary": self.get_summary(),
        }


__all__ = ["TrendPeriodResult", "TrendAnalysisResult"]
