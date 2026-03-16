# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from calculation.py."""

from __future__ import annotations

from .calculation_support import *


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
