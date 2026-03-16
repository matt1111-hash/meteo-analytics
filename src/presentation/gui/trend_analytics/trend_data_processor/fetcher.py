# mypy: ignore-errors
"""Trend data fetching module."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from src.presentation.gui.trend_analytics.trend_data_processor.constants import (
    TIME_RANGES,
    TREND_PARAMETERS,
)

logger = logging.getLogger(__name__)


def fetch_trend_data_batch(
    weather_client: object,
    lat: float,
    lon: float,
    start_date: datetime,
    end_date: datetime,
    progress_callback=None,
) -> List[Dict]:
    """
    Multi-year API fetch with batching.

    Args:
        weather_client: WeatherClient instance
        lat, lon: Coordinates
        start_date, end_date: Date range
        progress_callback: Optional progress callback

    Returns:
        List of daily weather records
    """
    weather_data = []
    current_start = start_date
    batch_count = 0
    total_batches = (end_date - start_date).days // 365 + 1

    while current_start < end_date:
        current_end = min(current_start + timedelta(days=365), end_date)

        try:
            yearly_data = weather_client.get_weather_data(
                lat,
                lon,
                current_start.strftime("%Y-%m-%d"),
                current_end.strftime("%Y-%m-%d"),
            )

            if yearly_data:
                weather_data.extend(yearly_data)
                logger.info(f"Batch {batch_count + 1}: {len(yearly_data)} days")

        except Exception as batch_error:
            logger.error(f"Batch {batch_count + 1} error: {batch_error}")

        current_start = current_end + timedelta(days=1)
        batch_count += 1

        if progress_callback:
            progress = 30 + int((batch_count / total_batches) * 30)
            progress_callback(progress)

    return weather_data


def get_settlement_coordinates(
    city_manager: object, settlement_name: str
) -> Optional[Tuple[float, float]]:
    """
    Get settlement coordinates from CityManager.

    Args:
        city_manager: CityManager instance
        settlement_name: Settlement name

    Returns:
        (lat, lon) tuple or None
    """
    try:
        coordinates = city_manager.find_city_by_name(settlement_name)
        if coordinates:
            return coordinates
        return None
    except Exception as e:
        logger.error(f"Coordinate lookup error: {e}")
        return None


def calculate_date_range(time_range: str) -> Tuple[datetime, datetime]:
    """Calculate start/end dates from time range string."""
    years = TIME_RANGES.get(time_range, 5)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=years * 365)
    return start_date, end_date


def get_api_field(parameter: str) -> Optional[str]:
    """Get API field name from parameter display name."""
    return TREND_PARAMETERS.get(parameter)
