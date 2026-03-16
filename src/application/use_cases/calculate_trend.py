# mypy: ignore-errors
"""Use case for trend analysis calculation.

Orchestrates weather data fetching and trend calculation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.api.dto.trend_request import TrendAnalysisRequest
from src.domain.analytics.services.trend_calculator import TrendCalculator
from src.domain.entities.trend_result import TrendAnalysisResult
from src.domain.ports import CityManagerPort, WeatherClientPort

logger = logging.getLogger(__name__)


class CalculateTrendUseCase:
    """Calculate climate trends for a location over multiple time periods."""

    def __init__(
        self,
        weather_client: WeatherClientPort,
        city_manager: CityManagerPort,
        trend_calculator: Optional[TrendCalculator] = None,
    ) -> None:
        """Initialize the use case with dependencies.

        Args:
            weather_client: Weather client for fetching data
            city_manager: City manager for location lookup
            trend_calculator: Trend calculator (default: new instance)
        """
        self._weather_client = weather_client
        self._city_manager = city_manager
        self._trend_calculator = trend_calculator or TrendCalculator()

    def execute(self, request: TrendAnalysisRequest) -> TrendAnalysisResult:
        """Execute trend analysis for the given request.

        Args:
            request: Trend analysis request with location, metric, and time periods

        Returns:
            TrendAnalysisResult with trend statistics for each time period

        Raises:
            ValueError: If location coordinates cannot be found
        """
        # Get location coordinates
        coordinates = self._get_coordinates(request.location)
        if not coordinates:
            raise ValueError(f"Location not found: {request.location}")

        lat, lon = coordinates

        # Determine date range
        max_period = max(request.time_periods) if request.time_periods else 55
        end_date = self._parse_date(request.end_date) or datetime.now()
        start_date = self._parse_date(request.start_date) or (
            end_date - timedelta(days=max_period * 365)
        )

        # Fetch weather data
        weather_data = self._fetch_weather_data(
            lat=lat,
            lon=lon,
            start_date=start_date,
            end_date=end_date,
        )

        if not weather_data:
            logger.warning("No weather data returned for %s", request.location)
            return self._empty_result(request)

        # Calculate trends for all periods
        result = self._trend_calculator.calculate_multiple_periods(
            weather_data=weather_data,
            metric=request.metric,
            location_name=request.location,
            time_periods=request.time_periods,
            end_date=end_date.strftime("%Y-%m-%d") if request.end_date else None,
        )

        return result

    def _get_coordinates(self, location: str) -> Optional[tuple[float, float]]:
        """Get coordinates for a location.

        Uses the city manager to find coordinates by name.
        """
        try:
            coords = self._city_manager.find_city_by_name(location)
            return coords
        except Exception as e:
            logger.error("Error finding coordinates for %s: %s", location, e)
            return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            logger.error("Invalid date format %s: %s", date_str, e)
            return None

    def _fetch_weather_data(
        self,
        lat: float,
        lon: float,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, Any]]:
        """Fetch weather data for the given location and date range.

        Uses batch fetching for long date ranges.
        """
        all_data = []
        current_start = start_date

        # Fetch in yearly batches
        while current_start < end_date:
            current_end = min(current_start + timedelta(days=365), end_date)

            try:
                batch_data = self._weather_client.get_weather_data(
                    lat=lat,
                    lon=lon,
                    start_date=current_start.strftime("%Y-%m-%d"),
                    end_date=current_end.strftime("%Y-%m-%d"),
                )

                if isinstance(batch_data, tuple):
                    batch_data, _ = batch_data

                if batch_data:
                    all_data.extend(batch_data)

            except Exception as e:
                logger.error("Error fetching weather data batch: %s", e)

            current_start = current_end + timedelta(days=1)

        logger.info("Fetched %d weather records for trend analysis", len(all_data))
        return all_data

    def _empty_result(self, request: TrendAnalysisRequest) -> TrendAnalysisResult:
        """Return empty result when no data is available."""
        return TrendAnalysisResult(
            location_name=request.location,
            metric=request.metric,
            periods=[],
            execution_time=0.0,
            total_data_points=0,
            date_range=("", ""),
            data_quality_score=0.0,
            completeness_ratio=0.0,
        )


__all__ = ["CalculateTrendUseCase"]
