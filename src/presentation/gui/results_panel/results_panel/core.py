#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from typing import Any, Dict, Optional

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QWidget

from ..data_processor import DataProcessor
from ..progress_manager import ProgressManagerWithTimeout
from ..tab_manager import TabManager
from src.presentation.gui.theme_manager import get_theme_manager
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

    def __init__(self, parent: Optional[QWidget] = None):
        """ResultsPanel inicializálása."""
        super().__init__(parent)

        logger.info("🎯 ResultsPanel inicializálása (REFACTORED)")

        # === KOMPONENSEK ===
        self.theme_manager = get_theme_manager()
        self.progress_manager = ProgressManagerWithTimeout(self)
        self.tab_manager = TabManager(self)
        self.data_processor = DataProcessor(self)

        # === ÁLLAPOT VÁLTOZÓK ===
        self.current_data: Optional[Dict[str, Any]] = None
        self.current_city: Optional[str] = None

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
    def show_loading_indicator(self, message: str = "⏳ Adatok betöltése...") -> None:
        show_loading_indicator(self, message)

    def hide_loading_indicator(self) -> None:
        hide_loading_indicator(self)

    def update_loading_progress(self, message: str) -> None:
        update_loading_progress(self, message)

    def force_hide_loading(self) -> None:
        force_hide_loading(self)

    def is_loading(self) -> bool:
        return is_loading(self)

    def get_loading_status(self) -> Dict[str, Any]:
        return get_loading_status(self)

    def switch_to_tab(self, tab_name: str) -> None:
        switch_to_tab(self, tab_name)

    def get_current_tab(self) -> str:
        return get_current_tab(self)

    def switch_to_windy_days_tab(self) -> None:
        switch_to_windy_days_tab(self)

    def get_windy_days_tab(self):
        return get_windy_days_tab(self)

    def trigger_windy_days_analysis(self) -> None:
        trigger_windy_days_analysis(self)

    def update_data(self, data: Dict[str, Any], city_name: str) -> None:
        update_data(self, data, city_name)

    def clear_data(self) -> None:
        clear_data(self)

    def trigger_extreme_weather_analysis(self) -> None:
        trigger_extreme_weather_analysis(self)

    def get_charts_container(self):
        return get_charts_container(self)

    def get_data_table(self):
        return get_data_table(self)

    def apply_theme(self, dark_theme: bool) -> None:
        apply_theme(self, dark_theme)

    def apply_theme_by_name(self, theme_name: str) -> None:
        apply_theme_by_name(self, theme_name)

    def get_current_theme_name(self) -> str:
        return get_current_theme_name(self)

    def get_state(self) -> Dict[str, Any]:
        return get_state(self)

    def set_state(self, state: Dict[str, Any]) -> bool:
        return set_state(self, state)

    def is_valid(self) -> bool:
        return is_valid(self)

    def set_enabled(self, enabled: bool) -> None:
        set_enabled(self, enabled)

    def emergency_reset(self) -> None:
        emergency_reset(self)

    def cleanup(self) -> None:
        cleanup(self)

    def closeEvent(self, event) -> None:
        closeEvent(self, event)

    def __del__(self):
        __del__(self)
