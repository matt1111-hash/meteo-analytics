#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialogs - Calculation

📊 Extrém értékek számítása

Képességek:
- Adatkinyerés
- Napi/havi extrém értékek számítása

Fájl: src/presentation/gui/dialogs/calculation.py
"""

from typing import TYPE_CHECKING, Dict, List

import pandas as pd

if TYPE_CHECKING:
    pass

from .table_handler import (
    _populate_extreme_table,
    _show_calculation_error,
    _show_no_data_message,
)


def _calculate_extremes(self) -> None:
    """
    Extrém időjárási értékek kiszámítása és táblázat frissítése.
    Delegálja a számítást a megfelelő privát metódushoz.

    Args:
        self: ExtremeWeatherDialog instance
    """
    try:
        # Alapadatok kinyerése
        df = _extract_weather_dataframe(self)
        if df.empty:
            _show_no_data_message(self)
            return

        # Extrém értékek számítása a kiválasztott periódus alapján
        if self.period_type == "monthly":
            extremes = _calculate_monthly_extremes(self, df)
        else:
            extremes = _calculate_daily_extremes(self, df)

        # Táblázat feltöltése
        _populate_extreme_table(self, extremes)

    except Exception as e:
        print(f"Hiba az extrém értékek kiszámítása közben: {e}")
        _show_calculation_error(self)


def _extract_weather_dataframe(self) -> pd.DataFrame:
    """
    Időjárási adatok kinyerése a raw API válaszból DataFrame formába.

    Args:
        self: ExtremeWeatherDialog instance

    Returns:
        Feldolgozott DataFrame vagy üres DataFrame hiba esetén
    """
    try:
        daily_data = self.data.get("daily", {})

        # Alapadatok kinyerése
        dates = daily_data.get("time", [])
        temp_max = daily_data.get("temperature_2m_max", [])
        temp_min = daily_data.get("temperature_2m_min", [])
        precip = daily_data.get("precipitation_sum", [])
        windspeed = daily_data.get("windspeed_10m_max", [])

        # DataFrame létrehozása
        df = pd.DataFrame(
            {
                "date": dates,
                "temp_max": temp_max,
                "temp_min": temp_min,
                "precipitation": precip,
                "windspeed": windspeed if windspeed else [None] * len(dates),
            }
        )

        # Dátum oszlop konvertálása
        df["date_obj"] = pd.to_datetime(df["date"])
        df["year"] = df["date_obj"].dt.year
        df["month"] = df["date_obj"].dt.month
        df["formatted_date"] = df["date_obj"].dt.strftime("%Y-%m-%d")

        return df

    except Exception as e:
        print(f"Hiba az adatok kinyerése közben: {e}")
        return pd.DataFrame()


def _calculate_daily_extremes(self, df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Napi extrém értékek számítása.

    Args:
        self: ExtremeWeatherDialog instance
        df: Időjárási adatok DataFrame

    Returns:
        Lista az extrém értékekről
    """
    extremes = []

    # Legmelegebb nap
    max_temp_idx = df["temp_max"].idxmax()
    extremes.append(
        {
            "category": "Legmelegebb nap",
            "value": f"{df.iloc[max_temp_idx]['temp_max']:.1f} °C",
            "date": df.iloc[max_temp_idx]["formatted_date"],
        }
    )

    # Leghidegebb nap
    min_temp_idx = df["temp_min"].idxmin()
    extremes.append(
        {
            "category": "Leghidegebb nap",
            "value": f"{df.iloc[min_temp_idx]['temp_min']:.1f} °C",
            "date": df.iloc[min_temp_idx]["formatted_date"],
        }
    )

    # Legnagyobb napi hőingás
    df["temp_range"] = df["temp_max"] - df["temp_min"]
    max_range_idx = df["temp_range"].idxmax()
    extremes.append(
        {
            "category": "Legnagyobb napi hőingás",
            "value": f"{df.iloc[max_range_idx]['temp_range']:.1f} °C",
            "date": df.iloc[max_range_idx]["formatted_date"],
        }
    )

    # Legcsapadékosabb nap
    max_precip_idx = df["precipitation"].idxmax()
    extremes.append(
        {
            "category": "Legcsapadékosabb nap",
            "value": f"{df.iloc[max_precip_idx]['precipitation']:.1f} mm",
            "date": df.iloc[max_precip_idx]["formatted_date"],
        }
    )

    # Legszelesebb nap (ha van adat)
    if not df["windspeed"].isna().all():
        max_wind_idx = df["windspeed"].idxmax()
        extremes.append(
            {
                "category": "Legszelesebb nap",
                "value": f"{df.iloc[max_wind_idx]['windspeed']:.1f} km/h",
                "date": df.iloc[max_wind_idx]["formatted_date"],
            }
        )

    # Időszak átlaghőmérséklete
    avg_temp = (df["temp_max"].mean() + df["temp_min"].mean()) / 2
    extremes.append(
        {
            "category": "Időszak átlaghőmérséklete",
            "value": f"{avg_temp:.1f} °C",
            "date": "-",
        }
    )

    return extremes


def _calculate_monthly_extremes(self, df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Havi extrém értékek számítása.

    Args:
        self: ExtremeWeatherDialog instance
        df: Időjárási adatok DataFrame

    Returns:
        Lista az extrém értékekről
    """
    extremes = []

    # Havi aggregáció
    monthly_data = (
        df.groupby(["year", "month"])
        .agg(
            {
                "temp_max": "max",
                "temp_min": "min",
                "precipitation": "sum",
                "windspeed": "max" if not df["windspeed"].isna().all() else "mean",
            }
        )
        .reset_index()
    )

    # Hónap nevek
    month_names = {
        1: "Január",
        2: "Február",
        3: "Március",
        4: "Április",
        5: "Május",
        6: "Június",
        7: "Július",
        8: "Augusztus",
        9: "Szeptember",
        10: "Október",
        11: "November",
        12: "December",
    }

    monthly_data["month_name"] = monthly_data["month"].map(month_names)

    # Legmelegebb hónap (max hőmérséklet alapján)
    max_temp_idx = monthly_data["temp_max"].idxmax()
    extremes.append(
        {
            "category": "Legmelegebb hónap (max)",
            "value": f"{monthly_data.iloc[max_temp_idx]['temp_max']:.1f} °C",
            "date": f"{monthly_data.iloc[max_temp_idx]['month_name']} {monthly_data.iloc[max_temp_idx]['year']}",
        }
    )

    # Leghidegebb hónap
    min_temp_idx = monthly_data["temp_min"].idxmin()
    extremes.append(
        {
            "category": "Leghidegebb hónap",
            "value": f"{monthly_data.iloc[min_temp_idx]['temp_min']:.1f} °C",
            "date": f"{monthly_data.iloc[min_temp_idx]['month_name']} {monthly_data.iloc[min_temp_idx]['year']}",
        }
    )

    # Legcsapadékosabb hónap
    max_precip_idx = monthly_data["precipitation"].idxmax()
    extremes.append(
        {
            "category": "Legcsapadékosabb hónap",
            "value": f"{monthly_data.iloc[max_precip_idx]['precipitation']:.1f} mm",
            "date": f"{monthly_data.iloc[max_precip_idx]['month_name']} {monthly_data.iloc[max_precip_idx]['year']}",
        }
    )

    # Legszelesebb hónap (ha van adat)
    if not df["windspeed"].isna().all():
        max_wind_idx = monthly_data["windspeed"].idxmax()
        extremes.append(
            {
                "category": "Legszelesebb hónap",
                "value": f"{monthly_data.iloc[max_wind_idx]['windspeed']:.1f} km/h",
                "date": f"{monthly_data.iloc[max_wind_idx]['month_name']} {monthly_data.iloc[max_wind_idx]['year']}",
            }
        )

    # Időszak átlaghőmérséklete
    avg_temp = (df["temp_max"].mean() + df["temp_min"].mean()) / 2
    extremes.append(
        {
            "category": "Időszak átlaghőmérséklete",
            "value": f"{avg_temp:.1f} °C",
            "date": "-",
        }
    )

    return extremes
