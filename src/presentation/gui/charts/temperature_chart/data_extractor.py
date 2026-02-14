#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        daily_data = data.get("daily", {})
        dates = daily_data.get("time", [])
        temp_max = daily_data.get("temperature_2m_max", [])
        temp_min = daily_data.get("temperature_2m_min", [])
        temp_mean = daily_data.get("temperature_2m_mean", [])

        # 🚨 KRITIKUS: CSAK VALÓDI API ADATOK! Számított átlag TILOS!
        if not dates or not temp_max or not temp_min or not temp_mean:
            print("⚠️ DEBUG: Hiányzó hőmérséklet adatok - chart nem jeleníthető meg")
            return pd.DataFrame()

        # Adatstruktúra hosszak ellenőrzése
        if (
            len(dates) != len(temp_max)
            or len(dates) != len(temp_min)
            or len(dates) != len(temp_mean)
        ):
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
