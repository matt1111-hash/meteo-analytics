# mypy: ignore-errors
"""Weather data processing module."""

import logging
from datetime import datetime
from typing import Any

import pandas as pd
from src.presentation.gui.controller.weather_data_handler.constants import (
    OPTIONAL_DAILY_FIELDS,
    REQUIRED_DAILY_FIELDS,
    WIND_DIRECTION_MAPPING,
)


def process_weather_data(
    raw_data: dict[str, Any], current_city_data: dict[str, Any] | None = None
) -> dict[str, Any] | None:
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
        if not _has_valid_daily_payload(raw_data, logger):
            return None

        daily_data = raw_data["daily"]
        hourly_data = raw_data.get("hourly", {})
        record_count = len(daily_data["time"])
        logger.info(f"Weather data valid - {record_count} records")

        processed = _build_processed_payload(
            raw_data=raw_data,
            hourly_data=hourly_data,
            current_city_data=current_city_data,
            record_count=record_count,
        )
        _copy_daily_fields(processed["daily"], daily_data, logger)
        _copy_wind_direction_fields(processed["daily"], daily_data, logger)

        logger.info(f"Processed {record_count} records successfully")
        return processed

    except Exception as e:
        logger.error(f"Weather data processing error: {e}")
        return None


def calculate_daily_max_wind_gusts(
    hourly_gusts: list[float], hourly_times: list[str], daily_times: list[str]
) -> list[float]:
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

        hourly_df = _build_hourly_gust_dataframe(hourly_gusts, hourly_times)
        hourly_df["date"] = hourly_df["time"].dt.date

        daily_max_gusts = [
            _extract_daily_max_gust(hourly_df, daily_time) for daily_time in daily_times
        ]
        _log_gust_summary(daily_max_gusts, logger)

        return daily_max_gusts

    except Exception as e:
        logger.error(f"Daily wind gusts calculation error: {e}")
        return []


def _has_valid_daily_payload(raw_data: dict[str, Any], logger: logging.Logger) -> bool:
    """Validate daily weather payload structure."""
    if not raw_data or "daily" not in raw_data:
        logger.warning("Invalid weather data structure")
        return False

    daily_data = raw_data["daily"]
    for field in REQUIRED_DAILY_FIELDS:
        if field not in daily_data or not daily_data[field]:
            logger.warning(f"Missing field: {field}")
            return False
    return True


def _build_processed_payload(
    raw_data: dict[str, Any],
    hourly_data: dict[str, Any],
    current_city_data: dict[str, Any] | None,
    record_count: int,
) -> dict[str, Any]:
    """Build processed weather payload metadata shell."""
    provider = raw_data.get("provider", "unknown")
    return {
        "daily": {},
        "hourly": hourly_data,
        "latitude": raw_data.get("latitude"),
        "longitude": raw_data.get("longitude"),
        "timezone": raw_data.get("timezone", "UTC"),
        "elevation": raw_data.get("elevation"),
        "data_source": provider,
        "source_type": provider,
        "provider": provider,
        "processed_at": datetime.now().isoformat(),
        "city_data": current_city_data.copy() if current_city_data else None,
        "record_count": record_count,
    }


def _copy_daily_fields(
    processed_daily: dict[str, Any],
    daily_data: dict[str, Any],
    logger: logging.Logger,
) -> None:
    """Copy required and optional daily fields."""
    for field in REQUIRED_DAILY_FIELDS:
        processed_daily[field] = daily_data[field]
        logger.debug(f"Copied field: {field}")

    for field in OPTIONAL_DAILY_FIELDS:
        if field not in daily_data:
            continue
        processed_daily[field] = daily_data[field]
        if field == "wind_gusts_10m_max":
            logger.info(f"🌪️ Wind gusts data copied: {len(daily_data[field])} values")
        logger.debug(f"Copied optional field: {field}")


def _copy_wind_direction_fields(
    processed_daily: dict[str, Any],
    daily_data: dict[str, Any],
    logger: logging.Logger,
) -> None:
    """Map wind direction aliases for chart compatibility."""
    for src_field, dst_field in WIND_DIRECTION_MAPPING.items():
        if src_field not in daily_data:
            continue
        processed_daily[dst_field] = daily_data[src_field]
        logger.info("Wind direction data mapped for WindRoseChart compatibility.")


def _build_hourly_gust_dataframe(
    hourly_gusts: list[float], hourly_times: list[str]
) -> pd.DataFrame:
    """Build hourly gust dataframe for daily aggregation."""
    return pd.DataFrame({"time": pd.to_datetime(hourly_times), "wind_gusts": hourly_gusts})


def _extract_daily_max_gust(hourly_df: pd.DataFrame, daily_time: str) -> Any:
    """Extract maximum valid gust for a single day."""
    try:
        daily_date = pd.to_datetime(daily_time).date()
        day_gusts = hourly_df[hourly_df["date"] == daily_date]["wind_gusts"]
        if day_gusts.empty:
            return None

        valid_gusts = day_gusts.dropna()
        if valid_gusts.empty:
            return None
        return valid_gusts.max()
    except Exception:
        return None


def _log_gust_summary(daily_max_gusts: list[Any], logger: logging.Logger) -> None:
    """Log summary for extracted daily wind gusts."""
    valid_gusts = [gust for gust in daily_max_gusts if gust is not None and gust > 0]
    if not valid_gusts:
        return
    logger.info(
        "Daily wind gusts: %d/%d valid days, max: %.1f km/h",
        len(valid_gusts),
        len(daily_max_gusts),
        max(valid_gusts),
    )
