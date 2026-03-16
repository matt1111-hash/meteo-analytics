# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from yearly_calculator.py."""

from __future__ import annotations

from .yearly_calculator_support import *


def _resolve_temperature_trend_column(df) -> str | None:
    """Resolve or build temperature column for trend calculation."""
    if "temperature_2m_mean" in df.columns:
        return "temperature_2m_mean"
    if "temperature_2m_max" in df.columns and "temperature_2m_min" in df.columns:
        df["temp_calculated_mean"] = (
            df["temperature_2m_max"] + df["temperature_2m_min"]
        ) / 2
        return "temp_calculated_mean"
    return None


def _build_temperature_trend_record(
    temp_trend: float, years: List[int]
) -> ExtremeRecord:
    """Build climate trend record for the given delta."""
    if temp_trend > 0.5:
        return ExtremeRecord(
            category="🌡️ Trend",
            record_type="🔥 Felmelegedés trend",
            value=f"+{temp_trend:.1f}°C",
            date=f"{years[0]}-{years[-1]}",
            raw_value=float(temp_trend),
        )
    if temp_trend < -0.5:
        return ExtremeRecord(
            category="🌡️ Trend",
            record_type="🧊 Lehűlés trend",
            value=f"{temp_trend:.1f}°C",
            date=f"{years[0]}-{years[-1]}",
            raw_value=float(temp_trend),
        )
    return ExtremeRecord(
        category="🌡️ Trend",
        record_type="📊 Stabil hőmérséklet",
        value=f"{temp_trend:+.1f}°C",
        date=f"{years[0]}-{years[-1]}",
        raw_value=float(temp_trend),
    )


def _calculate_climate_trends(df, years: List[int]) -> List[ExtremeRecord]:
    """Klímaváltozási trendek számítása 10+ évre."""
    records = []

    try:
        # Egyszerű trend számítás (első 5 év vs utolsó 5 év)
        early_years = years[:5]
        late_years = years[-5:]
        temp_col = _resolve_temperature_trend_column(df)
        if temp_col is not None:
            early_avg = df[df["year"].isin(early_years)][temp_col].mean()
            late_avg = df[df["year"].isin(late_years)][temp_col].mean()
            temp_trend = late_avg - early_avg
            records.append(_build_temperature_trend_record(temp_trend, years))

    except Exception as e:
        logger.error(f"Klíma trend számítási hiba: {e}")

    return records


def _get_wind_column(columns) -> str | None:
    """Széllökés oszlop kiválasztása DataFrame-hez."""
    if "wind_gusts_max" in columns:
        return "wind_gusts_max"
    elif "windspeed_10m_max" in columns:
        return "windspeed_10m_max"
    elif "windspeed" in columns:
        return "windspeed"
    return None
