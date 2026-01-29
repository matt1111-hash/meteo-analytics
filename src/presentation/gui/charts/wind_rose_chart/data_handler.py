"""Wind rose data extraction."""
from typing import Any, Dict

import pandas as pd


def extract_wind_data(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Széllökés adatok kinyerése rózsadiagramhoz.

    PRIORITÁS RENDSZER:
    1. wind_gusts_max + winddirection_10m_dominant
    2. windspeed_10m_max + winddirection_10m_dominant
    """
    daily_data = data.get("daily", {})

    dates = daily_data.get("time", [])
    winddirection = daily_data.get("wind_direction_10m_dominant", [])

    # Alapadatok ellenőrzése
    if not dates or not winddirection:
        return pd.DataFrame()

    wind_gusts_max = daily_data.get("wind_gusts_max", [])
    windspeed_10m_max = daily_data.get("windspeed_10m_max", [])

    def has_valid_data(data_list: list) -> bool:
        """Van-e valódi szám adat a listában."""
        return any(x is not None and isinstance(x, (int, float)) for x in data_list)

    # PRIORITÁS KIÉRTÉKELÉS
    windspeed_data = []
    data_source = ""

    if wind_gusts_max and len(wind_gusts_max) == len(dates) and has_valid_data(wind_gusts_max):
        windspeed_data = wind_gusts_max
        data_source = "wind_gusts_max"
    elif windspeed_10m_max and len(windspeed_10m_max) == len(dates) and has_valid_data(windspeed_10m_max):
        windspeed_data = windspeed_10m_max
        data_source = "windspeed_10m_max"
    else:
        return pd.DataFrame()

    # DataFrame létrehozása
    df = pd.DataFrame({
        'date': pd.to_datetime(dates),
        'windspeed': windspeed_data,
        'winddirection': winddirection,
        '_data_source': data_source
    })

    # NaN értékek eltávolítása
    df = df.dropna()

    # Szélirány érték tartomány ellenőrzése (0-360 fok)
    valid_direction_mask = (df['winddirection'] >= 0) & (df['winddirection'] <= 360)
    df = df[valid_direction_mask]

    return df
