#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provider Widget - Core

🔧 ProviderWidget main class

Képességek:
- Main ProviderWidget class
- Signal definíciók
- Inicializáció
- Event handler metódusok

Fájl: src/presentation/gui/panel_widgets/provider_widget/core.py
"""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QLabel, QProgressBar, QTextEdit, QWidget

from src.presentation.gui.theme_manager import register_widget_for_theming
from .monitoring import _update_usage_display
from .provider_data import get_default_warning_thresholds, get_status_messages

# Import functions as methods
from .public_api import (
    cleanup,
    closeEvent,
    get_current_provider,
    get_state,
    get_usage_summary,
    is_valid,
    refresh_usage_display,
    set_enabled,
    set_provider,
    set_state,
    start_monitoring,
    stop_monitoring,
    update_usage_stats,
)
from .ui_builder import setup_provider_ui


class ProviderWidget(QWidget):
    """
    🔧 COMPLETE Provider Widget - Selection & Monitoring

    🎯 ALAPÉRTELMEZETT: OPEN-METEO (INGYENES) - AUTO ROUTING LETILTVA!

    FUNKCIONALITÁS:
    - Provider kiválasztás dropdown
    - Usage statistics megjelenítés
    - Cost monitoring
    - Real-time updates
    - Warning notifications
    - Clean signal architecture
    """

    # Signals
    provider_changed = Signal(str)  # provider_name
    usage_warning = Signal(str, int)  # provider_name, usage_percent
    cost_warning = Signal(str, float)  # provider_name, estimated_cost

    def __init__(self, parent=None):
        """Provider Widget inicializálása - OPEN-METEO ALAPÉRTELMEZETT."""
        super().__init__(parent)

        print("🌍 DEBUG: ProviderWidget inicializálva - OPEN-METEO ALAPÉRTELMEZETT")

        # Widget téma regisztráció
        register_widget_for_theming(self, "container")

        # === ADATOK INICIALIZÁLÁSA ===

        # 🎯 KRITIKUS VÁLTOZÁS: Open-Meteo alapértelmezett (ingyenes)
        self.current_provider = "open-meteo"  # AUTO HELYETT OPEN-METEO!

        self.usage_stats = {}
        self.cost_estimates = {}
        self.warning_thresholds = get_default_warning_thresholds()

        # === UI KOMPONENSEK ===

        self.provider_combo: Optional[QComboBox] = None
        self.status_label: Optional[QLabel] = None
        self.usage_progress: Optional[QProgressBar] = None
        self.usage_label: Optional[QLabel] = None
        self.cost_label: Optional[QLabel] = None
        self.details_text: Optional[QTextEdit] = None

        # === TIMER SETUP ===

        from PySide6.QtCore import QTimer
        self.usage_timer = QTimer()
        self.usage_timer.setInterval(5000)  # 5 seconds
        self.usage_timer.timeout.connect(lambda: _update_usage_display(self))

        # === UI INICIALIZÁLÁS ===

        setup_provider_ui(self)
        self._setup_signals()
        self.usage_timer.start()

        print("✅ DEBUG: ProviderWidget initialized - OPEN-METEO ALAPÉRTELMEZETT")

    def _setup_signals(self) -> None:
        """Signal connections beállítása."""
        # Provider selection change
        self.provider_combo.currentTextChanged.connect(self._on_provider_selection_changed)

        print("✅ DEBUG: ProviderWidget signals connected")

    def _on_provider_selection_changed(self) -> None:
        """Provider kiválasztás változás kezelése."""
        try:
            current_data = self.provider_combo.currentData()
            if current_data:
                old_provider = self.current_provider
                self.current_provider = current_data

                print(f"🌍 DEBUG: Provider changed: {old_provider} → {self.current_provider}")

                # Status update
                status_messages = get_status_messages()
                status = status_messages.get(self.current_provider, f"📡 {self.current_provider} aktív")
                self.status_label.setText(status)

                # Signal emission
                self.provider_changed.emit(self.current_provider)

        except Exception as e:
            print(f"❌ DEBUG: Provider selection change error: {e}")

    # Public API methods
    def set_provider(self, provider_name: str) -> None:
        set_provider(self, provider_name)

    def get_current_provider(self) -> str:
        return get_current_provider(self)

    def update_usage_stats(self, stats: dict) -> None:
        update_usage_stats(self, stats)

    def get_usage_summary(self) -> dict:
        return get_usage_summary(self)

    def stop_monitoring(self) -> None:
        stop_monitoring(self)

    def start_monitoring(self) -> None:
        start_monitoring(self)

    def get_state(self) -> dict:
        return get_state(self)

    def set_state(self, state: dict) -> bool:
        return set_state(self, state)

    def is_valid(self) -> bool:
        return is_valid(self)

    def set_enabled(self, enabled: bool) -> None:
        set_enabled(self, enabled)

    def refresh_usage_display(self) -> None:
        refresh_usage_display(self)

    def cleanup(self) -> None:
        cleanup(self)

    def closeEvent(self, event) -> None:
        closeEvent(self, event)
