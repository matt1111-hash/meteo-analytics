#!/usr/bin/env python3
# mypy: ignore-errors

"""
Heatmap Chart - Data Extractor

📊 Adatok kinyerése és aggregálása

Képességek:
- Daily data kinyerés
- 365 konstans aggregáció
- Date range analízis

Fájl: src/presentation/gui/charts/heatmap_chart/data_extractor.py
"""

import logging
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _resolve_parameter_values(self, daily_data: dict[str, Any]) -> list[Any]:
    """Resolve requested parameter values, adding temperature mean fallback."""
    parameter_values = daily_data.get(self.parameter, [])
    if parameter_values or self.parameter != "temperature_2m_mean":
        return parameter_values

    temp_max = daily_data.get("temperature_2m_max", [])
    temp_min = daily_data.get("temperature_2m_min", [])
    if not temp_max or not temp_min or len(temp_max) != len(temp_min):
        return []

    logger.info("⚠️ temperature_2m_mean hiányzik, fallback számításra...")
    return [
        round((t_max + t_min) / 2, 1) if t_max is not None and t_min is not None else None
        for t_max, t_min in zip(temp_max, temp_min, strict=False)
    ]


def _empty_or_short_period(values: list, total_days: int) -> np.ndarray | None:
    """Return original values when aggregation is unnecessary."""
    if total_days > 365:  # noqa: PLR2004
        return None
    logger.debug(f"📊 Rövid időszak: {len(values)} nap, nincs aggregáció.")
    return np.array(values)


def _resolve_clean_bin_values(values: list, start_idx: int, end_idx: int) -> list[Any]:
    """Return cleaned values for one aggregation bin."""
    bin_values = values[start_idx : min(end_idx, len(values))]
    return [value for value in bin_values if value is not None and not np.isnan(value)]


def _aggregate_bin_values(parameter: str, clean_values: list[Any]) -> float:
    """Aggregate a bin based on parameter family."""
    if "temperature" in parameter:
        return float(np.mean(clean_values))
    if "precipitation" in parameter:
        return float(np.sum(clean_values))
    if "wind" in parameter:
        return float(np.max(clean_values))
    return float(np.mean(clean_values))


def extract_daily_data(self, data: dict[str, Any]) -> pd.DataFrame:
    """
    Extract daily data for parameter.

    Args:
        self: HeatmapCalendarChart instance
        data: API válasz dictionary

    Returns:
        pd.DataFrame: Dátum és értékek oszlopokkal
    """
    daily_data = data.get("daily", {})
    dates = daily_data.get("time", [])
    parameter_values = _resolve_parameter_values(self, daily_data)

    logger.debug(f"🔍 Paraméter keresése: {self.parameter}")
    logger.debug(f"  📊 Dates: {len(dates)} elem")
    logger.debug(f"  📈 Values: {len(parameter_values)} elem")

    if not dates or not parameter_values:
        logger.warning(f"⚠️ Hiányzó {self.parameter} adatok")
        return pd.DataFrame()

    if len(dates) != len(parameter_values):
        logger.error(f"❌ Eltérő hosszúságú {self.parameter} adatok")
        return pd.DataFrame()

    df = pd.DataFrame({"date": pd.to_datetime(dates), self.parameter: parameter_values})

    df = df.dropna()

    if df.empty:
        logger.warning(f"⚠️ Nincs érvényes {self.parameter} adat")
    else:
        logger.info(f"✅ {len(df)} érvényes {self.parameter} adat betöltve")

    return df


def aggregate_to_365(self, values: list, total_days: int) -> np.ndarray:
    """
    Aggregate any timespan to 365 values.

    Args:
        self: HeatmapCalendarChart instance
        values: Értékek listája
        total_days: Összes napok száma

    Returns:
        np.ndarray: 365 elemű tömb aggregált értékekkel
    """
    short_period_result = _empty_or_short_period(values, total_days)
    if short_period_result is not None:
        return short_period_result

    # Hosszú időszak esetén aggregálunk
    bin_size = total_days / 365.0
    aggregated = np.full(365, np.nan)

    for index in range(365):
        start_idx = int(index * bin_size)
        end_idx = int((index + 1) * bin_size)
        if start_idx < len(values):
            clean_values = _resolve_clean_bin_values(values, start_idx, end_idx)
            if clean_values:
                aggregated[index] = _aggregate_bin_values(self.parameter, clean_values)

    logger.debug(f"📊 Hosszú aggregáció: {total_days} nap → 365 bin")
    return aggregated
