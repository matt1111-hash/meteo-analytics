#!/usr/bin/env python3
# mypy: ignore-errors

"""
Quick Overview Tab - Temp Precip Stats

Hőmérséklet és csapadék statisztikák számítása.

Fájl: src/presentation/gui/results_panel/quick_overview_tab/temp_precip_stats.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _resolve_series_mean(series: pd.Series) -> float | None:
    """Resolve mean value for a non-empty series."""
    if series.empty:
        return None
    return float(series.mean())


def _set_label_text(self, label_key: str, value: float | int | None) -> None:
    """Set stat label from optional numeric value."""
    if value is None or not pd.notna(value):
        self._stat_labels[label_key].setText("N/A")
        return
    self._stat_labels[label_key].setText(f"{value:.1f}")


def _set_precipitation_labels(self, precip_series: pd.Series) -> None:
    """Populate precipitation summary labels."""
    _set_label_text(self, "total_precip", precip_series.sum())
    _set_label_text(self, "avg_precip", precip_series.mean())
    _set_label_text(self, "max_precip", precip_series.max())
    rainy_days = len(precip_series[precip_series > 0.1])  # noqa: PLR2004
    self._stat_labels["rainy_days"].setText(f"{rainy_days}")


def _get_non_empty_series(df: pd.DataFrame, column_name: str) -> pd.Series | None:
    """Return cleaned series when the column exists and has values."""
    if column_name not in df.columns:
        return None
    series = df[column_name].dropna()
    return None if series.empty else series


def _is_valid_finite_number(value: float | int | None) -> bool:
    """Return whether numeric value is finite and usable."""
    return (
        value is not None
        and pd.notna(value)
        and value
        not in (
            float("-inf"),
            float("inf"),
        )
    )


def _resolve_average_temperature(df: pd.DataFrame) -> float | None:
    """Resolve average temperature using mean or min/max fallback."""
    mean_series = _get_non_empty_series(df, "temp_mean")
    if mean_series is not None:
        return _resolve_series_mean(mean_series)

    max_series = _get_non_empty_series(df, "temp_max")
    min_series = _get_non_empty_series(df, "temp_min")
    if max_series is not None and min_series is not None:
        return float((max_series.mean() + min_series.mean()) / 2)
    return None


def _resolve_temperature_range(df: pd.DataFrame) -> float | None:
    """Resolve full visible temperature range."""
    max_series = _get_non_empty_series(df, "temp_max")
    min_series = _get_non_empty_series(df, "temp_min")
    if max_series is None or min_series is None:
        return None
    max_val = max_series.max()
    min_val = min_series.min()
    if _is_valid_finite_number(max_val) and _is_valid_finite_number(min_val):
        return float(max_val - min_val)
    return None


def calculate_temperature_stats(self, df: pd.DataFrame) -> None:
    """Hőmérséklet statisztikák számítása."""
    try:
        _set_stat_if_exists(self, df, "temp_max", "max_temp", lambda s: f"{s.max():.1f}")
        _set_stat_if_exists(self, df, "temp_min", "min_temp", lambda s: f"{s.min():.1f}")
        avg_temp = _resolve_average_temperature(df)
        _set_label_text(self, "avg_temp", avg_temp)
        temp_range = _resolve_temperature_range(df)
        _set_label_text(self, "temp_range", temp_range)

    except Exception as e:
        logger.error(f"Hőmérséklet statisztika hiba: {e}")
        _clear_stats_range(self, ["avg_temp", "max_temp", "min_temp", "temp_range"])


def calculate_precipitation_stats(self, df: pd.DataFrame) -> None:
    """Csapadék statisztikák számítása."""
    try:
        if "precipitation" not in df.columns:
            _clear_stats_range(self, ["total_precip", "avg_precip", "max_precip", "rainy_days"])
            return

        precip_series = df["precipitation"].dropna()

        if precip_series.empty:
            _clear_stats_range(self, ["total_precip", "avg_precip", "max_precip"])
            self._stat_labels["rainy_days"].setText("0")
            return

        _set_precipitation_labels(self, precip_series)

    except Exception as e:
        logger.error(f"Csapadék statisztika hiba: {e}")
        _clear_stats_range(self, ["total_precip", "avg_precip", "max_precip", "rainy_days"])


def _set_stat_if_exists(self, df: pd.DataFrame, col: str, label_key: str, formatter) -> None:
    """Statisztika beállítása ha az oszlop létezik."""
    series = _get_non_empty_series(df, col)
    if series is None:
        self._stat_labels[label_key].setText("N/A")
        return

    value = series.max() if "max" in label_key else series.min()
    if _is_valid_finite_number(value):
        self._stat_labels[label_key].setText(formatter(series))
    else:
        self._stat_labels[label_key].setText("N/A")


def _clear_stats_range(self, keys: list) -> None:
    """Statisztika tartomány törlése."""
    for key in keys:
        if key in self._stat_labels:
            self._stat_labels[key].setText("N/A")
