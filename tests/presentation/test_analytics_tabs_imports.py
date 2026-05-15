"""Regression tests for GUI analytics tab imports."""

from __future__ import annotations

from src.presentation.gui.analytics.analytics_tabs_part3 import ClimateTabWidget


def test_climate_tab_imports_without_missing_split_module() -> None:
    """ClimateTabWidget should import from the existing split modules."""
    assert ClimateTabWidget.__name__ == "ClimateTabWidget"
