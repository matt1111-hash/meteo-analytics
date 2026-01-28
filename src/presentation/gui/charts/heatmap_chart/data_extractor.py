#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from typing import TYPE_CHECKING, Any, Dict

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def extract_daily_data(self, data: Dict[str, Any]) -> pd.DataFrame:
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
    parameter_values = daily_data.get(self.parameter, [])

    logger.debug(f"🔍 Paraméter keresése: {self.parameter}")
    logger.debug(f"  📊 Dates: {len(dates)} elem")
    logger.debug(f"  📈 Values: {len(parameter_values)} elem")

    if not dates or not parameter_values:
        logger.warning(f"⚠️ Hiányzó {self.parameter} adatok")
        return pd.DataFrame()

    if len(dates) != len(parameter_values):
        logger.error(f"❌ Eltérő hosszúságú {self.parameter} adatok")
        return pd.DataFrame()

    df = pd.DataFrame({
        'date': pd.to_datetime(dates),
        self.parameter: parameter_values
    })

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
    if total_days <= 365:
        # Nincs szükség aggregációra, az eredeti adatokat használjuk
        logger.debug(f"📊 Rövid időszak: {len(values)} nap, nincs aggregáció.")
        return np.array(values)

    # Hosszú időszak esetén aggregálunk
    bin_size = total_days / 365.0
    aggregated = np.full(365, np.nan)

    for i in range(365):
        start_idx = int(i * bin_size)
        end_idx = int((i + 1) * bin_size)

        if start_idx < len(values):
            bin_values = values[start_idx:min(end_idx, len(values))]
            clean_values = [v for v in bin_values if v is not None and not np.isnan(v)]

            if clean_values:
                if 'temperature' in self.parameter:
                    aggregated[i] = np.mean(clean_values)
                elif 'precipitation' in self.parameter:
                    aggregated[i] = np.sum(clean_values)
                elif 'wind' in self.parameter:
                    aggregated[i] = np.max(clean_values)
                else:
                    aggregated[i] = np.mean(clean_values)

    logger.debug(f"📊 Hosszú aggregáció: {total_days} nap → 365 bin")
    return aggregated
