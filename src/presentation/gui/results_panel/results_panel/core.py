#!/usr/bin/env python3
# mypy: ignore-errors

"""
Results Panel - Core

🎯 ResultsPanel main class

Képességek:
- Main ResultsPanel class
- Initialization
- Signal definíciók
- Komponens integráció

Fájl: src/presentation/gui/results_panel/results_panel/core.py
"""

import logging
from typing import Any

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QWidget
from src.presentation.gui.theme_manager import get_theme_manager

from ..data_processor import DataProcessor
from ..progress_manager import ProgressManagerWithTimeout
from ..tab_manager import TabManager
from .public_api import (
    apply_theme,
    apply_theme_by_name,
    clear_data,
    force_hide_loading,
    get_charts_container,
    get_current_tab,
    get_current_theme_name,
    get_data_table,
    get_loading_status,
    get_windy_days_tab,
    hide_loading_indicator,
    is_loading,
    show_loading_indicator,
    switch_to_tab,
    switch_to_windy_days_tab,
    trigger_extreme_weather_analysis,
    trigger_windy_days_analysis,
    update_data,
    update_loading_progress,
)
from .signal_handlers import connect_signals
from .state_management import (
    __del__,
    cleanup,
    closeEvent,
    emergency_reset,
    get_state,
    is_valid,
    set_enabled,
    set_state,
)
from .ui_builder import init_ui

logger = logging.getLogger(__name__)


class ResultsPanel(QWidget):
    """
    Results Panel - Refactored moduláris struktúrával.

    Fő funkciók:
    - Progress tracking (ProgressManager)
    - Tab management (TabManager)
    - Data processing (DataProcessor)
    - External API: AppController integration
    - Emergency controls: force reset capabilities

    Signals:
        export_requested: Export kérés (str format)
        data_updated: Adat frissítés (dict data, str city_name)
        extreme_weather_requested: Extrém időjárás kérés
    """

    # Signals
    export_requested = Signal(str)
    data_updated = Signal(dict, str)
    extreme_weather_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        """ResultsPanel inicializálása."""
        super().__init__(parent)

        logger.info("🎯 ResultsPanel inicializálása (REFACTORED)")

        # === KOMPONENSEK ===
        self.theme_manager = get_theme_manager()
        self.progress_manager = ProgressManagerWithTimeout(self)
        self.tab_manager = TabManager(self)
        self.data_processor = DataProcessor(self)

        # === ÁLLAPOT VÁLTOZÓK ===
        self.current_data: dict[str, Any] | None = None
        self.current_city: str | None = None

        # === UI INICIALIZÁLÁSA ===
        init_ui(self)
        connect_signals(self)

        # === THEMEMANAGER REGISZTRÁCIÓ ===
        if self.theme_manager:
            self._register_widgets_for_theming()

        # 🚨 CRITICAL FIX: Minimum size beállítása
        self.setMinimumSize(QSize(450, 400))

        logger.info("✅ ResultsPanel inicializálva (REFACTORED)")

    def _register_widgets_for_theming(self) -> None:
        """Widget-ek regisztrálása theme manager-hez."""
        if self.theme_manager:
            # Register widgets for theming
            pass

    # Public API methods
    def show_loading_indicator(self, message: str = "⏳ Adatok betöltése...") -> None:  # noqa: D102
        show_loading_indicator(self, message)

    def hide_loading_indicator(self) -> None:  # noqa: D102
        hide_loading_indicator(self)

    def update_loading_progress(self, message: str) -> None:  # noqa: D102
        update_loading_progress(self, message)

    def force_hide_loading(self) -> None:  # noqa: D102
        force_hide_loading(self)

    def is_loading(self) -> bool:  # noqa: D102
        return is_loading(self)

    def get_loading_status(self) -> dict[str, Any]:  # noqa: D102
        return get_loading_status(self)

    def switch_to_tab(self, tab_name: str) -> None:  # noqa: D102
        switch_to_tab(self, tab_name)

    def get_current_tab(self) -> str:  # noqa: D102
        return get_current_tab(self)

    def switch_to_windy_days_tab(self) -> None:  # noqa: D102
        switch_to_windy_days_tab(self)

    def get_windy_days_tab(self):  # noqa: D102
        return get_windy_days_tab(self)

    def trigger_windy_days_analysis(self) -> None:  # noqa: D102
        trigger_windy_days_analysis(self)

    def update_data(self, data: dict[str, Any], city_name: str) -> None:  # noqa: D102
        update_data(self, data, city_name)

    def clear_data(self) -> None:  # noqa: D102
        clear_data(self)

    def trigger_extreme_weather_analysis(self) -> None:  # noqa: D102
        trigger_extreme_weather_analysis(self)

    def get_charts_container(self):  # noqa: D102
        return get_charts_container(self)

    def get_data_table(self):  # noqa: D102
        return get_data_table(self)

    def apply_theme(self, dark_theme: bool) -> None:  # noqa: D102
        apply_theme(self, dark_theme)

    def apply_theme_by_name(self, theme_name: str) -> None:  # noqa: D102
        apply_theme_by_name(self, theme_name)

    def get_current_theme_name(self) -> str:  # noqa: D102
        return get_current_theme_name(self)

    def get_state(self) -> dict[str, Any]:  # noqa: D102
        return get_state(self)

    def set_state(self, state: dict[str, Any]) -> bool:  # noqa: D102
        return set_state(self, state)

    def is_valid(self) -> bool:  # noqa: D102
        return is_valid(self)

    def set_enabled(self, enabled: bool) -> None:  # noqa: D102
        set_enabled(self, enabled)

    def emergency_reset(self) -> None:  # noqa: D102
        emergency_reset(self)

    def cleanup(self) -> None:  # noqa: D102
        cleanup(self)

    def closeEvent(self, event) -> None:  # noqa: D102
        closeEvent(self, event)

    def __del__(self):
        __del__(self)
