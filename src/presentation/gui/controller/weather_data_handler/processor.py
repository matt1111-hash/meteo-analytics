"""Weather data processing module."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from src.presentation.gui.controller.weather_data_handler.constants import (
    OPTIONAL_DAILY_FIELDS,
    REQUIRED_DAILY_FIELDS,
    WIND_DIRECTION_MAPPING,
)


def process_weather_data(
    raw_data: Dict[str, Any],
    current_city_data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Process weather data with complete wind data support.

    Args:
        raw_data: Raw API data
        current_city_data: Current city data

    Returns:
        Processed data or None
    """
    logger = logging.getLogger(__name__)

    try:
        if not raw_data or 'daily' not in raw_data:
            logger.warning("Invalid weather data structure")
            return None

        daily_data = raw_data['daily']
        hourly_data = raw_data.get('hourly', {})

        # Validate required fields
        for field in REQUIRED_DAILY_FIELDS:
            if field not in daily_data or not daily_data[field]:
                logger.warning(f"Missing field: {field}")
                return None

        record_count = len(daily_data['time'])
        logger.info(f"Weather data valid - {record_count} records")

        # Build processed data structure
        processed = {
            'daily': {},
            'hourly': hourly_data,
            'latitude': raw_data.get('latitude'),
            'longitude': raw_data.get('longitude'),
            'timezone': raw_data.get('timezone', 'UTC'),
            'elevation': raw_data.get('elevation'),
            'data_source': raw_data.get('provider', 'unknown'),
            'source_type': raw_data.get('provider', 'unknown'),
            'provider': raw_data.get('provider', 'unknown'),
            'processed_at': datetime.now().isoformat(),
            'city_data': current_city_data.copy() if current_city_data else None,
            'record_count': record_count
        }

        # Copy required fields
        for field in REQUIRED_DAILY_FIELDS:
            if field in daily_data:
                processed['daily'][field] = daily_data[field]
                logger.debug(f"Copied field: {field}")

        # Copy optional fields
        for field in OPTIONAL_DAILY_FIELDS:
            if field in daily_data:
                processed['daily'][field] = daily_data[field]
                if field == 'wind_gusts_10m_max':
                    logger.info(f"🌪️ Wind gusts data copied: {len(daily_data[field])} values")
                logger.debug(f"Copied optional field: {field}")

        # Wind direction compatibility fix
        for src_field, dst_field in WIND_DIRECTION_MAPPING.items():
            if src_field in daily_data:
                processed['daily'][dst_field] = daily_data[src_field]
                logger.info("Wind direction data mapped for WindRoseChart compatibility.")

        logger.info(f"Processed {record_count} records successfully")
        return processed

    except Exception as e:
        logger.error(f"Weather data processing error: {e}")
        return None


def calculate_daily_max_wind_gusts(
    hourly_gusts: List[float],
    hourly_times: List[str],
    daily_times: List[str]
) -> List[float]:
    """
    Calculate daily maximum wind gusts from hourly data.

    Args:
        hourly_gusts: Hourly wind gusts (km/h)
        hourly_times: Hourly timestamps (ISO format)
        daily_times: Daily timestamps (YYYY-MM-DD format)

    Returns:
        List of daily maximum wind gusts
    """
    logger = logging.getLogger(__name__)

    try:
        if not hourly_gusts or not hourly_times or not daily_times:
            logger.warning("Missing data for wind gusts calculation")
            return []

        hourly_df = pd.DataFrame({
            'time': pd.to_datetime(hourly_times),
            'wind_gusts': hourly_gusts
        })
        hourly_df['date'] = hourly_df['time'].dt.date

        daily_max_gusts = []

        for daily_time in daily_times:
            try:
                daily_date = pd.to_datetime(daily_time).date()
                day_gusts = hourly_df[hourly_df['date'] == daily_date]['wind_gusts']

                if not day_gusts.empty:
                    valid_gusts = day_gusts.dropna()
                    if not valid_gusts.empty:
                        daily_max_gusts.append(valid_gusts.max())
                    else:
                        daily_max_gusts.append(None)
                else:
                    daily_max_gusts.append(None)
            except Exception:
                daily_max_gusts.append(None)

        # Validation summary
        valid_gusts = [g for g in daily_max_gusts if g is not None and g > 0]
        if valid_gusts:
            logger.info(f"Daily wind gusts: {len(valid_gusts)}/{len(daily_max_gusts)} valid days, "
                       f"max: {max(valid_gusts):.1f} km/h")

        return daily_max_gusts

    except Exception as e:
        logger.error(f"Daily wind gusts calculation error: {e}")
        return []
