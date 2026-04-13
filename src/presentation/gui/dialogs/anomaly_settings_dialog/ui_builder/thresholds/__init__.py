# mypy: ignore-errors
"""Threshold sections - re-export."""

from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.thresholds.main import (
    create_main_tabs,
    create_thresholds_tab,
)
from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.thresholds.precipitation import (
    create_precipitation_section,
)
from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.thresholds.temperature import (
    create_temperature_section,
)
from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.thresholds.wind import (
    create_wind_section,
)

__all__ = [
    "create_main_tabs",
    "create_precipitation_section",
    "create_temperature_section",
    "create_thresholds_tab",
    "create_wind_section",
]
