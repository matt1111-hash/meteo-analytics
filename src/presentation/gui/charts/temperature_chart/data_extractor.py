#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Temperature Chart - Data Extractor

🔥 Hőmérséklet adatok kinyerése és validálása

Képességek:
- Adatok kinyerése API válaszból
- Validáció és minőség ellenőrzés
- DataFrame létrehozása

Fájl: src/presentation/gui/charts/temperature_chart/data_extractor.py
"""

from typing import Any, Dict

import pandas as pd


def _extract_daily_temperature_lists(
    data: Dict[str, Any],
) -> tuple[list[Any], list[Any], list[Any], list[Any]]:
    """Extract raw daily temperature arrays from API response."""
    daily_data = data.get("daily", {})
    return (
        daily_data.get("time", []),
        daily_data.get("temperature_2m_max", []),
        daily_data.get("temperature_2m_min", []),
        daily_data.get("temperature_2m_mean", []),
    )


def _has_complete_temperature_payload(
    dates: list[Any], temp_max: list[Any], temp_min: list[Any], temp_mean: list[Any]
) -> bool:
    """Return whether all required temperature arrays are present."""
    return bool(dates and temp_max and temp_min and temp_mean)


def _has_matching_temperature_lengths(
    dates: list[Any], temp_max: list[Any], temp_min: list[Any], temp_mean: list[Any]
) -> bool:
    """Return whether all temperature arrays share the same length."""
    return (
        len(dates) == len(temp_max)
        and len(dates) == len(temp_min)
        and len(dates) == len(temp_mean)
    )


class TemperatureDataExtractor:
    """
    🔥 Hőmérséklet adatok kinyerése és validálása.
    """

    @staticmethod
    def extract_temperature_data(data: Dict[str, Any]) -> pd.DataFrame:
        """
        Hőmérséklet adatok kinyerése - CSAK VALÓDI API ADATOKKAL.

        Args:
            data: OpenMeteo API válasz

        Returns:
            pd.DataFrame: Hőmérséklet adatok date, temp_max, temp_min, temp_mean oszlopokkal
        """
        dates, temp_max, temp_min, temp_mean = _extract_daily_temperature_lists(data)

        # 🚨 KRITIKUS: CSAK VALÓDI API ADATOK! Számított átlag TILOS!
        if not _has_complete_temperature_payload(dates, temp_max, temp_min, temp_mean):
            print("⚠️ DEBUG: Hiányzó hőmérséklet adatok - chart nem jeleníthető meg")
            return pd.DataFrame()

        # Adatstruktúra hosszak ellenőrzése
        if not _has_matching_temperature_lengths(dates, temp_max, temp_min, temp_mean):
            print(
                "❌ DEBUG: Eltérő hosszúságú hőmérséklet adatok - chart nem jeleníthető meg"
            )
            return pd.DataFrame()

        df = pd.DataFrame(
            {
                "date": pd.to_datetime(dates),
                "temp_max": temp_max,
                "temp_min": temp_min,
                "temp_mean": temp_mean,  # CSAK VALÓDI API ADAT!
            }
        )

        # Csak érvényes adatok megtartása
        df = df.dropna()

        if df.empty:
            print(
                "⚠️ DEBUG: Nincs érvényes hőmérséklet adat - chart nem jeleníthető meg"
            )

        return df
