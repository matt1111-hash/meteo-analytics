#!/usr/bin/env python3
# mypy: ignore-errors
"""
Wind Analysis Application Service.

This service provides a stable API for wind analysis operations,
wrapping domain services for use by the presentation layer.
"""

from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from src.domain.analytics.wind_analysis_service import analyze_wind_patterns
from src.domain.analytics.wind_models import WINDY_DAY_THRESHOLD_KMH, WindAnalysisResult


@dataclass
class WindyDayDTO:
    """DTO for a windy day result."""

    date: str
    max_wind_speed_kmh: float
    avg_wind_speed_kmh: Optional[float]
    direction: Optional[str]
    is_windy: bool


@dataclass
class MonthlyWindStatsDTO:
    """DTO for monthly wind statistics."""

    month: str
    windy_days_count: int
    total_days: int
    windy_percentage: float
    avg_max_speed: float


@dataclass
class WindAnalysisResultDTO:
    """DTO for complete wind analysis result."""

    location_name: str
    threshold_kmh: float
    total_days: int
    total_windy_days: int
    overall_windy_percentage: float
    avg_max_wind_speed: float
    max_wind_speed: float
    windiest_month: Optional[str]
    calmest_month: Optional[str]
    monthly_stats: List[MonthlyWindStatsDTO]
    windy_days: List[WindyDayDTO]

    @classmethod
    def from_domain(cls, result: WindAnalysisResult) -> "WindAnalysisResultDTO":
        """Create DTO from domain entity."""
        return cls(
            location_name=result.location_name,
            threshold_kmh=result.threshold_kmh,
            total_days=result.total_days,
            total_windy_days=result.total_windy_days,
            overall_windy_percentage=result.overall_windy_percentage,
            avg_max_wind_speed=result.avg_max_wind_speed,
            max_wind_speed=result.max_wind_speed,
            windiest_month=result.windiest_month,
            calmest_month=result.calmest_month,
            monthly_stats=[
                MonthlyWindStatsDTO(
                    month=stat.month,
                    windy_days_count=stat.windy_days_count,
                    total_days=stat.total_days,
                    windy_percentage=stat.windy_percentage,
                    avg_max_speed=stat.avg_max_speed,
                )
                for stat in result.monthly_stats
            ],
            windy_days=[
                WindyDayDTO(
                    date=day.date.isoformat()
                    if hasattr(day.date, "isoformat")
                    else str(day.date),
                    max_wind_speed_kmh=day.max_wind_speed_kmh,
                    avg_wind_speed_kmh=getattr(day, "avg_wind_speed_kmh", None),
                    direction=getattr(day, "direction", None),
                    is_windy=day.is_windy,
                )
                for day in result.windy_days
            ],
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
    "WindAnalysisService",
    "WindAnalysisResultDTO",
    "WindyDayDTO",
    "MonthlyWindStatsDTO",
]
