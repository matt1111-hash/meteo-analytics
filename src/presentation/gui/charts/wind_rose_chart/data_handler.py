# mypy: ignore-errors
"""Wind rose data extraction."""

from typing import Any, Dict

import pandas as pd


def _get_winddirection_data(daily_data: Dict[str, Any]) -> list:
    """Return available wind direction series."""
    return daily_data.get("winddirection_10m_dominant", []) or daily_data.get(
        "wind_direction_10m_dominant", []
    )


def _has_valid_data(data_list: list) -> bool:
    """Check whether a sequence contains valid numeric values."""
    return any(
        value is not None and isinstance(value, (int, float)) for value in data_list
    )


def _get_preferred_windspeed_data(
    daily_data: Dict[str, Any], dates: list
) -> tuple[list, str]:
    """Select preferred windspeed source and label."""
    candidates = [
        (
            daily_data.get("windgusts_10m_max", [])
            or daily_data.get("wind_gusts_max", []),
            "wind_gusts_max",
        ),
        (
            daily_data.get("windspeed_10m_max", [])
            or daily_data.get("wind_speed_max", []),
            "windspeed_10m_max",
        ),
    ]
    for data_list, label in candidates:
        if data_list and len(data_list) == len(dates) and _has_valid_data(data_list):
            return data_list, label
    return [], ""


def extract_wind_data(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Széllökés adatok kinyerése rózsadiagramhoz.

    PRIORITÁS RENDSZER:
    1. wind_gusts_max + winddirection_10m_dominant
    2. windspeed_10m_max + winddirection_10m_dominant
    """
    daily_data = data.get("daily", {})
    dates = daily_data.get("time", []) or daily_data.get("date", [])
    winddirection = _get_winddirection_data(daily_data)
    if not dates or not winddirection:
        return pd.DataFrame()

    windspeed_data, data_source = _get_preferred_windspeed_data(daily_data, dates)
    if not windspeed_data:
        return pd.DataFrame()

    df = pd.DataFrame(
        {
            "date": pd.to_datetime(dates),
            "windspeed": windspeed_data,
            "winddirection": winddirection,
            "_data_source": data_source,
        }
    )
    df = df.dropna()
    valid_direction_mask = (df["winddirection"] >= 0) & (df["winddirection"] <= 360)
    return df[valid_direction_mask]
