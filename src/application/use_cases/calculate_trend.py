# mypy: ignore-errors
"""Use case for trend analysis calculation.

Orchestrates weather data fetching and trend calculation.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any

from src.application.commands.trend_command import TrendAnalysisCommand
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
        trend_calculator: TrendCalculator | None = None,
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

    def execute(self, request: TrendAnalysisCommand) -> TrendAnalysisResult:
        """Execute trend analysis for the given request.

        Args:
            request: Trend analysis command with location, metric, and time periods

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

    def _get_coordinates(self, location: str) -> tuple[float, float] | None:
        """Get coordinates for a location.

        Uses the city manager to find coordinates by name.
        """
        try:
            coords = self._city_manager.find_city_by_name(location)
            return coords
        except Exception as e:
            logger.error("Error finding coordinates for %s: %s", location, e)
            return None

    def _parse_date(self, date_str: str | None) -> datetime | None:
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
    ) -> list[dict[str, Any]]:
        """Fetch weather data for the given location and date range.

        Uses parallel yearly batch fetching for long date ranges.
        """
        year_batches = self._build_year_batches(start_date, end_date)
        if not year_batches:
            return []

        all_data: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self._fetch_batch, lat, lon, s, e): (s, e) for s, e in year_batches
            }
            for future in as_completed(futures):
                batch_data = future.result()
                if batch_data:
                    all_data.extend(batch_data)

        logger.info("Fetched %d weather records for trend analysis", len(all_data))
        return all_data

    @staticmethod
    def _build_year_batches(
        start_date: datetime,
        end_date: datetime,
    ) -> list[tuple[datetime, datetime]]:
        """Split date range into yearly (≤365 day) batches."""
        batches: list[tuple[datetime, datetime]] = []
        current = start_date
        while current < end_date:
            batch_end = min(current + timedelta(days=365), end_date)
            batches.append((current, batch_end))
            current = batch_end + timedelta(days=1)
        return batches

    def _fetch_batch(
        self,
        lat: float,
        lon: float,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        """Fetch a single yearly batch, returning an empty list on failure."""
        try:
            batch_data = self._weather_client.get_weather_data(
                latitude=lat,
                longitude=lon,
                start_date=start.strftime("%Y-%m-%d"),
                end_date=end.strftime("%Y-%m-%d"),
            )
            if isinstance(batch_data, tuple):
                batch_data, _ = batch_data
            return batch_data or []
        except Exception as e:
            logger.error("Error fetching weather data batch: %s", e)
            return []

    def _empty_result(self, request: TrendAnalysisCommand) -> TrendAnalysisResult:
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
