"""Regression tests for extreme-event pressure records."""

from __future__ import annotations

from src.presentation.gui.results_panel.extreme.category_calculators import (
    CategoryCalculators,
)


def test_pressure_records_prefer_msl_pressure() -> None:
    """Pressure records should use sea-level pressure when available."""
    calculators = CategoryCalculators()
    daily_data = {
        "pressure_msl_max": [1032.0, 1042.4, 1038.1],
        "pressure_msl_min": [1018.0, 1024.5, 1020.2],
        "surface_pressure_max": [1018.0, 1027.7, 1024.0],
        "surface_pressure_min": [1005.0, 1011.1, 1007.9],
    }
    dates = ["2025-01-01", "2025-01-02", "2025-01-03"]

    records = calculators.calculate_pressure_records(daily_data, dates)

    assert [record.value for record in records] == ["1042hPa", "1018hPa"]
    assert [record.date for record in records] == ["2025-01-02", "2025-01-01"]


def test_pressure_records_fall_back_to_surface_pressure() -> None:
    """Surface pressure should still work when MSL fields are absent."""
    calculators = CategoryCalculators()
    daily_data = {
        "surface_pressure_max": [1015.0, 1020.0, 1018.0],
        "surface_pressure_min": [995.0, 1001.0, 999.0],
    }
    dates = ["2025-01-01", "2025-01-02", "2025-01-03"]

    records = calculators.calculate_pressure_records(daily_data, dates)

    assert [record.value for record in records] == ["1020hPa", "995hPa"]
    assert [record.date for record in records] == ["2025-01-02", "2025-01-01"]
