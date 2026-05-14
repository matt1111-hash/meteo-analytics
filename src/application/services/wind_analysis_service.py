#!/usr/bin/env python3
"""
Wind Analysis Application Service.

This service provides a stable API for wind analysis operations,
wrapping domain services for use by the presentation layer.
"""

from dataclasses import dataclass

import pandas as pd
from src.domain.analytics.wind_models import WINDY_DAY_THRESHOLD_KMH, WindAnalysisResult
from src.infrastructure.analytics.wind_analysis_service import (
    analyze_wind_patterns as _analyze_wind_patterns_impl,
)

# Re-export for presentation layer — keeps dependency rule intact
analyze_wind_patterns = _analyze_wind_patterns_impl


@dataclass
class WindyDayDTO:
    """DTO for a windy day result."""

    date: str
    max_wind_speed_kmh: float
    avg_wind_speed_kmh: float | None
    direction: str | None
    is_windy: bool


@dataclass
class MonthlyWindStatsDTO:
    """DTO for monthly wind statistics."""

    month: str
    windy_days_count: int
    total_days: int
    windy_percentage: float
    avg_wind_speed: float
    max_wind_speed: float


@dataclass
class WindAnalysisResultDTO:
    """DTO for complete wind analysis result."""

    location_name: str
    threshold_kmh: float
    total_days: int
    total_windy_days: int
    overall_windy_percentage: float
    avg_wind_speed: float
    max_wind_speed: float
    windiest_month: str | None
    calmest_month: str | None
    monthly_stats: list[MonthlyWindStatsDTO]
    windy_days: list[str]

    @classmethod
    def from_domain(cls, result: WindAnalysisResult) -> "WindAnalysisResultDTO":
        """Create DTO from domain entity."""
        avg_ws = sum(s.avg_wind_speed for s in result.monthly_stats) / max(
            len(result.monthly_stats), 1
        )
        max_ws = max((s.max_wind_speed for s in result.monthly_stats), default=0.0)
        all_windy_dates = [
            d.isoformat() for stat in result.monthly_stats for d in stat.windy_days_list
        ]

        return cls(
            location_name=result.location_name,
            threshold_kmh=result.threshold_kmh,
            total_days=result.total_days,
            total_windy_days=result.total_windy_days,
            overall_windy_percentage=result.overall_windy_percentage,
            avg_wind_speed=avg_ws,
            max_wind_speed=max_ws,
            windiest_month=result.windiest_month.month_name if result.windiest_month else None,
            calmest_month=result.calmest_month.month_name if result.calmest_month else None,
            monthly_stats=[
                MonthlyWindStatsDTO(
                    month=stat.month_name,
                    windy_days_count=stat.windy_days_count,
                    total_days=stat.total_days,
                    windy_percentage=stat.windy_percentage,
                    avg_wind_speed=stat.avg_wind_speed,
                    max_wind_speed=stat.max_wind_speed,
                )
                for stat in result.monthly_stats
            ],
            windy_days=all_windy_dates,
        )


class WindAnalysisService:
    """
    Application service for wind analysis operations.

    This service wraps domain wind analysis functions and provides
    a stable API for the presentation layer.
    """

    @staticmethod
    def analyze(
        weather_data: pd.DataFrame,
        location_name: str = "Ismeretlen helyszín",
        threshold_kmh: float = WINDY_DAY_THRESHOLD_KMH,
    ) -> WindAnalysisResultDTO:
        """
        Analyze wind patterns in weather data.

        Args:
            weather_data: DataFrame with weather data
            location_name: Name of the location
            threshold_kmh: Wind speed threshold for windy days

        Returns:
            WindAnalysisResultDTO with analysis results
        """
        result = analyze_wind_patterns(
            weather_data=weather_data,
            location_name=location_name,
            threshold_kmh=threshold_kmh,
        )
        return WindAnalysisResultDTO.from_domain(result)

    @staticmethod
    def get_windy_day_threshold() -> float:
        """Get the default windy day threshold in km/h."""
        return WINDY_DAY_THRESHOLD_KMH


__all__ = [
    "MonthlyWindStatsDTO",
    "WindAnalysisResultDTO",
    "WindAnalysisService",
    "WindyDayDTO",
    "analyze_wind_patterns",
]
