# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from calculation.py."""

from __future__ import annotations

from .calculation_support import *


def _calculate_monthly_extremes(self, df: pd.DataFrame) -> List[Dict[str, str]]:  # noqa: ARG001
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
