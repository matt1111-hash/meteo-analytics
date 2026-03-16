# mypy: ignore-errors
"""UI Builder - re-export for backward compatibility."""

from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.buttons import (
    create_buttons_section,
)
from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.categories import (
    create_categories_grid,
    create_categories_tab,
)
from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.header import (
    create_header_section,
    create_profile_section,
)
from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.preview import (
    create_preview_tab,
    create_test_section,
)
from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.thresholds import (
    create_precipitation_section,
    create_temperature_section,
    create_thresholds_tab,
    create_wind_section,
)

__all__ = [
    "create_header_section",
    "create_profile_section",
    "create_thresholds_tab",
    "create_temperature_section",
    "create_precipitation_section",
    "create_wind_section",
    "create_categories_tab",
    "create_categories_grid",
    "create_preview_tab",
    "create_test_section",
    "create_buttons_section",
]
