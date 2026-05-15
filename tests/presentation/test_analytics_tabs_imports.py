"""Regression tests for GUI analytics tab imports."""

from __future__ import annotations

import pytest


def test_climate_tab_imports_without_missing_split_module() -> None:
    """ClimateTabWidget should import from the existing split modules."""
    pytest.importorskip(
        "PySide6.QtWidgets",
        reason="Qt system libraries are not available in this environment",
        exc_type=ImportError,
    )

    from src.presentation.gui.analytics.analytics_tabs_part3 import (  # noqa: PLC0415
        ClimateTabWidget,
    )

    assert ClimateTabWidget.__name__ == "ClimateTabWidget"
