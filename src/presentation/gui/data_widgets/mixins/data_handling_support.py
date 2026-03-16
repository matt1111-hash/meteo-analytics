#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""Support helpers for data handling mixin."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


def normalize_array(arr: List, target_length: int, fill_value: Any = None) -> List:
    """Normalize an array to the requested length."""
    if len(arr) == target_length:
        return arr
    if len(arr) < target_length:
        return arr + [fill_value] * (target_length - len(arr))
    return arr[:target_length]


def build_mean_fallback(temp_max: List, temp_min: List, base_length: int) -> List:
    """Build fallback daily mean temperatures."""
    mean_values: List[Any] = []
    for i in range(base_length):
        if (
            i < len(temp_max)
            and i < len(temp_min)
            and temp_max[i] is not None
            and temp_min[i] is not None
        ):
            mean_values.append(round((temp_max[i] + temp_min[i]) / 2, 1))
        else:
            mean_values.append(None)
    return mean_values


def build_dataframe_payload(
    daily_data: Dict[str, Any], base_length: int
) -> Dict[str, List]:
    """Build normalized dataframe payload from daily data."""
    dates_norm = normalize_array(daily_data.get("time", []), base_length)
    temp_max_norm = normalize_array(
        daily_data.get("temperature_2m_max", []), base_length, None
    )
    temp_min_norm = normalize_array(
        daily_data.get("temperature_2m_min", []), base_length, None
    )
    temp_mean_norm = normalize_array(
        daily_data.get("temperature_2m_mean", []), base_length, None
    )
    precip_norm = normalize_array(
        daily_data.get("precipitation_sum", []), base_length, 0.0
    )
    windspeed_norm = normalize_array(
        daily_data.get("windspeed_10m_max", []), base_length, None
    )
    if not daily_data.get("temperature_2m_mean", []) or all(
        x is None for x in temp_mean_norm
    ):
        temp_mean_norm = build_mean_fallback(temp_max_norm, temp_min_norm, base_length)
    payload = {
        "date": dates_norm,
        "temp_max": temp_max_norm,
        "temp_min": temp_min_norm,
        "temp_mean": temp_mean_norm,
        "precipitation": precip_norm,
    }
    if windspeed_norm and any(x is not None for x in windspeed_norm):
        payload["windspeed"] = windspeed_norm
    return payload


def validate_required_daily_data(dates: List, temp_max: List) -> bool:
    """Validate required daily series before dataframe conversion."""
    if not dates or len(dates) == 0:
        logger.error("❌ Nincs dátum adat!")
        return False
    if not temp_max or len(temp_max) == 0:
        logger.error("❌ Nincs maximum hőmérséklet adat!")
        return False
    return True


def log_mean_source(temp_mean: List, df_data: Dict[str, List]) -> None:
    """Log whether source or fallback mean temperature values are used."""
    if not temp_mean or all(x is None for x in df_data["temp_mean"]):
        logger.warning("⚠️ temperature_2m_mean hiányzik, fallback számításra...")
        logger.info(f"🔄 Fallback számítás kész: {len(df_data['temp_mean'])} érték")
        return
    logger.info(f"✅ temperature_2m_mean használva: {len(df_data['temp_mean'])} érték")


def log_dataframe_summary(df: pd.DataFrame) -> None:
    """Log the created dataframe summary."""
    logger.info("✅ DataFrame sikeresen létrehozva:")
    logger.info(f"   - Sorok: {len(df)}")
    logger.info(f"   - Oszlopok: {len(df.columns)}")
    logger.info(f"   - Oszlopnevek: {list(df.columns)}")
    logger.info(f"   - Első 3 sor dátuma: {list(df['date'].head(3))}")
