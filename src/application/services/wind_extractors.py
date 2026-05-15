"""Wind analysis extraction and classification helpers."""

from __future__ import annotations

import logging

import pandas as pd
from src.domain.analytics.wind_models import WINDY_DAY_THRESHOLD_KMH

logger = logging.getLogger(__name__)


def _empty_wind_dataframe() -> pd.DataFrame:
    """Return an empty normalized wind dataframe."""
    return pd.DataFrame(columns=["date", "max_wind_speed_kmh"])


def _select_wind_column(weather_data: pd.DataFrame) -> str | None:
    """Resolve the preferred wind column from incoming weather data."""
    if "wind_gusts_max" in weather_data.columns:
        logger.info("Using wind_gusts_max for wind analysis")
        return "wind_gusts_max"
    if "wind_speed" in weather_data.columns:
        logger.warning("Falling back to wind_speed for wind analysis")
        return "wind_speed"
    if "windspeed_10m_max" in weather_data.columns:
        logger.warning("Using legacy windspeed_10m_max for wind analysis")
        return "windspeed_10m_max"
    logger.error("No supported wind speed column found: %s", list(weather_data.columns))
    return None


def _prepare_wind_source_frame(weather_data: pd.DataFrame, wind_column: str) -> pd.DataFrame:
    """Prepare a normalized wind source frame."""
    df = weather_data.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])
    wind_data = df[["date", wind_column]].copy()
    return wind_data.rename(columns={wind_column: "wind_speed"})


def _clean_wind_data(wind_data: pd.DataFrame) -> pd.DataFrame:
    """Drop invalid wind values and log cleanup counts."""
    original_count = len(wind_data)
    cleaned = wind_data.dropna(subset=["wind_speed"])
    cleaned = cleaned[cleaned["wind_speed"] >= 0]
    cleaned_count = len(cleaned)
    if original_count > cleaned_count:
        logger.warning("Removed %s invalid wind speed records", original_count - cleaned_count)
    return cleaned


def _aggregate_daily_wind(wind_data: pd.DataFrame) -> pd.DataFrame:
    """Aggregate max daily wind speed values."""
    daily_wind = (
        wind_data.groupby(wind_data["date"].dt.date).agg({"wind_speed": "max"}).reset_index()
    )
    daily_wind.columns = ["date", "max_wind_speed_kmh"]
    daily_wind["max_wind_speed_kmh"] = daily_wind["max_wind_speed_kmh"].fillna(0.0)
    return daily_wind


def _log_daily_wind_stats(daily_wind: pd.DataFrame, wind_column: str) -> None:
    """Log summary statistics for daily wind data."""
    valid_days = len(daily_wind[daily_wind["max_wind_speed_kmh"] > 0])
    max_speed = daily_wind["max_wind_speed_kmh"].max() if not daily_wind.empty else 0
    logger.info("Processed %s daily wind records", len(daily_wind))
    logger.info("Valid wind days: %s/%s", valid_days, len(daily_wind))
    logger.info("Maximum wind speed: %.1f km/h from %s", max_speed, wind_column)


def extract_daily_wind_data(weather_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract daily maximum wind data using the best available wind column.

    Args:
        weather_data: Weather dataframe.

    Returns:
        Dataframe with date and max_wind_speed_kmh columns.
    """
    try:
        wind_column = _select_wind_column(weather_data)
        if wind_column is None:
            return _empty_wind_dataframe()
        if "date" not in weather_data.columns:
            logger.error("No date column found in weather data")
            return _empty_wind_dataframe()

        wind_data = _prepare_wind_source_frame(weather_data, wind_column)
        daily_wind = _aggregate_daily_wind(_clean_wind_data(wind_data))
        _log_daily_wind_stats(daily_wind, wind_column)
        return daily_wind
    except Exception:
        logger.exception("Failed to extract daily wind data")
        return _empty_wind_dataframe()


def identify_windy_days(
    daily_wind_data: pd.DataFrame, threshold_kmh: float = WINDY_DAY_THRESHOLD_KMH
) -> pd.DataFrame:
    """
    Mark windy days using the supplied threshold.

    Args:
        daily_wind_data: Daily wind dataframe.
        threshold_kmh: Wind speed threshold in km/h.

    Returns:
        Dataframe with an is_windy column.
    """
    try:
        if daily_wind_data.empty:
            logger.warning("Daily wind data is empty")
            return pd.DataFrame(columns=["date", "max_wind_speed_kmh", "is_windy"])

        df = daily_wind_data.copy()
        df["is_windy"] = df["max_wind_speed_kmh"] > threshold_kmh

        windy_count = df["is_windy"].sum()
        total_count = len(df)
        logger.info(
            "Identified windy days: %s/%s (%.1f%%) at %.1f km/h",
            windy_count,
            total_count,
            windy_count / total_count * 100,
            threshold_kmh,
        )
        return df
    except Exception:
        logger.exception("Failed to identify windy days")
        return pd.DataFrame(columns=["date", "max_wind_speed_kmh", "is_windy"])


__all__ = ["extract_daily_wind_data", "identify_windy_days"]
