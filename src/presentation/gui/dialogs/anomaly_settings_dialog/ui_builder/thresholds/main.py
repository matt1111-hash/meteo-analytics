"""Main thresholds tab builder."""
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder import (
    create_categories_tab,
    create_preview_tab,
    create_temperature_section,
    create_precipitation_section,
    create_wind_section,
)


def create_main_tabs(dialog: object) -> QTabWidget:
    """Főbb beállítási tab-ok."""
    tabs = QTabWidget()

    thresholds_tab = create_thresholds_tab(dialog)
    tabs.addTab(thresholds_tab, "🌡️ Küszöbértékek")

    categories_tab = create_categories_tab(dialog)
    tabs.addTab(categories_tab, "🏷️ Kategóriák")

    preview_tab = create_preview_tab(dialog)
    tabs.addTab(preview_tab, "👁️ Előnézet")

    return tabs


def create_thresholds_tab(dialog: object) -> QWidget:
    """Küszöbértékek beállítása tab."""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setSpacing(20)

    temp_section = create_temperature_section(dialog)
    layout.addWidget(temp_section)

    precip_section = create_precipitation_section(dialog)
    layout.addWidget(precip_section)

    wind_section = create_wind_section(dialog)
    layout.addWidget(wind_section)

    layout.addStretch()

    return container
