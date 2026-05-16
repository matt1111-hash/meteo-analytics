#!/usr/bin/env python3
# mypy: ignore-errors

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

        self.provider_combo: QComboBox | None = None
        self.status_label: QLabel | None = None
        self.usage_progress: QProgressBar | None = None
        self.usage_label: QLabel | None = None
        self.cost_label: QLabel | None = None
        self.details_text: QTextEdit | None = None

        # === TIMER SETUP ===

        from PySide6.QtCore import QTimer  # noqa: PLC0415

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
                status = status_messages.get(
                    self.current_provider, f"📡 {self.current_provider} aktív"
                )
                self.status_label.setText(status)

                # Signal emission
                self.provider_changed.emit(self.current_provider)

        except Exception as e:
            print(f"❌ DEBUG: Provider selection change error: {e}")

    # Public API methods
    def set_provider(self, provider_name: str) -> None:  # noqa: D102
        set_provider(self, provider_name)

    def get_current_provider(self) -> str:  # noqa: D102
        return get_current_provider(self)

    def update_usage_stats(self, stats: dict) -> None:  # noqa: D102
        update_usage_stats(self, stats)

    def get_usage_summary(self) -> dict:  # noqa: D102
        return get_usage_summary(self)

    def stop_monitoring(self) -> None:  # noqa: D102
        stop_monitoring(self)

    def start_monitoring(self) -> None:  # noqa: D102
        start_monitoring(self)

    def get_state(self) -> dict:  # noqa: D102
        return get_state(self)

    def set_state(self, state: dict) -> bool:  # noqa: D102
        return set_state(self, state)

    def is_valid(self) -> bool:  # noqa: D102
        return is_valid(self)

    def set_enabled(self, enabled: bool) -> None:  # noqa: D102
        set_enabled(self, enabled)

    def refresh_usage_display(self) -> None:  # noqa: D102
        refresh_usage_display(self)

    def cleanup(self) -> None:  # noqa: D102
        cleanup(self)

    def closeEvent(self, event) -> None:  # noqa: D102
        closeEvent(self, event)
