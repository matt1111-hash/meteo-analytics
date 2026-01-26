#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Results Panel - Clean Architecture Refactor

A fő ResultsPanel osztály, ami moduláris felépítésű,
külön komponensekre bontva a funkcionális területek szerint.
"""

import logging
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton
)
from PySide6.QtCore import QSize, QTimer, Signal
from PySide6.QtGui import QFont

from ..theme_manager import get_theme_manager
from .progress_manager import ProgressManagerWithTimeout
from .tab_manager import TabManager
from .data_processor import DataProcessor


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
        self._init_ui()
        self._connect_signals()

        # === THEMEMANAGER REGISZTRÁCIÓ ===
        if self.theme_manager:
            self._register_widgets_for_theming()

        # 🚨 CRITICAL FIX: Minimum size beállítása
        self.setMinimumSize(QSize(450, 400))

        logger.info("✅ ResultsPanel inicializálva (REFACTORED)")

    def _init_ui(self) -> None:
        """UI elemek inicializálása."""
        logger.debug("ResultsPanel._init_ui() START")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # === FŐCÍM + PROGRESS INDICATOR ===
        title_layout = QHBoxLayout()

        self.title_label = QLabel("📊 Időjárási Adatok Elemzése")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        title_layout.addWidget(self.title_label)

        # Progress indicator
        self.progress_indicator = QLabel("")
        self.progress_indicator.setStyleSheet("""
            QLabel {
                color: #2563eb;
                font-size: 12px;
                font-style: italic;
                padding: 5px 10px;
            }
        """)
        self.progress_indicator.setVisible(False)
        title_layout.addWidget(self.progress_indicator)

        title_layout.addStretch()

        # Export gomb
        self.global_export_btn = QPushButton("💾 Export")
        self.global_export_btn.clicked.connect(lambda: self.export_requested.emit("csv"))
        title_layout.addWidget(self.global_export_btn)

        # Extreme weather gomb
        self.extreme_weather_btn = QPushButton("⚡ Extrém Időjárás")
        self.extreme_weather_btn.clicked.connect(self._on_extreme_weather_clicked)
        title_layout.addWidget(self.extreme_weather_btn)

        layout.addLayout(title_layout)

        # === TAB WIDGET LÉTREHOZÁSA ===
        self.tab_widget = self.tab_manager.initialize()
        layout.addWidget(self.tab_widget)

        # Progress manager inicializálása
        self.progress_manager.initialize(self.progress_indicator)

        logger.debug("ResultsPanel._init_ui() BEFEJEZVE")

    def _connect_signals(self) -> None:
        """Belső signal kapcsolatok beállítása."""
        # Progress manager signalok
        self.progress_manager.timeout_occurred.connect(self._on_loading_timeout)
        self.progress_manager.loading_state_changed.connect(self._on_loading_state_changed)

        # WindyDaysTab signal kapcsolatok
        windy_days_tab = self.tab_manager.get_windy_days_tab()
        if windy_days_tab:
            try:
                if hasattr(windy_days_tab, 'analysis_completed'):
                    windy_days_tab.analysis_completed.connect(self._on_windy_days_analysis_completed)
                if hasattr(windy_days_tab, 'error_occurred'):
                    windy_days_tab.error_occurred.connect(self._on_windy_days_error)
                if hasattr(windy_days_tab, 'export_requested'):
                    windy_days_tab.export_requested.connect(self._on_windy_days_export_requested)
                logger.debug("✅ WindyDaysTab signal kapcsolatok beállítva")
            except Exception as e:
                logger.warning(f"⚠️ WindyDaysTab signal kapcsolat hiba: {e}")

    def _register_widgets_for_theming(self) -> None:
        """Widget-ek regisztrálása theme manager-hez."""
        if self.theme_manager:
            # Register widgets for theming
            pass

    # === PROGRESS API ===

    def show_loading_indicator(self, message: str = "⏳ Adatok betöltése...") -> None:
        """Loading indicator megjelenítése."""
        self.progress_manager.show_loading(message)

    def hide_loading_indicator(self) -> None:
        """Loading indicator elrejtése."""
        self.progress_manager.hide_loading()

    def update_loading_progress(self, message: str) -> None:
        """Loading progress frissítése."""
        self.progress_manager.update_progress(message)

    def force_hide_loading(self) -> None:
        """Loading indicator kényszerített elrejtése."""
        self.progress_manager.force_hide()

    def is_loading(self) -> bool:
        """Loading állapot lekérdezése."""
        return self.progress_manager.is_loading()

    def _on_loading_timeout(self) -> None:
        """Loading timeout kezelése."""
        logger.warning("ResultsPanel loading timeout - handled by ProgressManager")

        # Error message a title-ben
        original_text = self.title_label.text()
        self.title_label.setText("⚠️ Időtúllépés - próbálja újra")

        # Reset after 5 seconds
        QTimer.singleShot(5000, lambda: self.title_label.setText(original_text))

    def _on_loading_state_changed(self, is_loading: bool) -> None:
        """Loading állapot változás kezelése."""
        # Tab-ok engedélyezése/letiltása
        if self.tab_widget:
            self.tab_widget.setEnabled(not is_loading)

        # Gombok engedélyezése/letiltása
        self.global_export_btn.setEnabled(not is_loading)
        self.extreme_weather_btn.setEnabled(not is_loading)

    # === TAB API ===

    def switch_to_tab(self, tab_name: str) -> None:
        """Specifikus tab-ra váltás."""
        self.tab_manager.switch_to_tab(tab_name)

    def get_current_tab(self) -> str:
        """Jelenlegi aktív tab nevének lekérdezése."""
        return self.tab_manager.get_current_tab()

    def switch_to_windy_days_tab(self) -> None:
        """Szeles napok tab-ra váltás."""
        self.switch_to_tab("windy_days")

    def get_windy_days_tab(self):
        """WindyDaysTab referencia lekérdezése."""
        return self.tab_manager.get_windy_days_tab()

    def trigger_windy_days_analysis(self) -> None:
        """Szeles napok analízis programatikus triggerelése."""
        windy_days_tab = self.get_windy_days_tab()
        if windy_days_tab and hasattr(windy_days_tab, '_start_analysis'):
            windy_days_tab._start_analysis()
            logger.info("🌪️ WindyDaysTab analízis programatikusan triggerelve")

    # === DATA UPDATE API ===

    def update_data(self, data: Dict[str, Any], city_name: str) -> None:
        """
        Adatok frissítése.

        Args:
            data: OpenMeteo API válasz
            city_name: Város neve
        """
        logger.info(f"ResultsPanel.update_data() - City: {city_name} (REFACTORED)")

        try:
            # Loading elrejtése ha aktív
            if self.is_loading():
                self.hide_loading_indicator()

            # Állapot mentése
            self.current_data = data
            self.current_city = city_name
            self._update_title(city_name)

            # Szabványos tabok frissítése
            self.tab_manager.update_standard_tabs(data, city_name)

            # WindyDaysTab frissítése
            self._update_windy_days_tab(data, city_name)

            # Signal küldése
            self.data_updated.emit(data, city_name)
            logger.info("ResultsPanel.update_data() SIKERES!")

        except Exception as e:
            logger.error(f"ResultsPanel adatfrissítési hiba: {e}")
            import traceback
            traceback.print_exc()

            # Error esetén is hide loading
            if self.is_loading():
                self.hide_loading_indicator()

            # Error message megjelenítése
            self.title_label.setText(f"❌ Adatfrissítési hiba: {str(e)[:50]}...")
            self.clear_data()

    def _update_title(self, city_name: str) -> None:
        """Title frissítése város névvel."""
        self.title_label.setText(f"📊 Időjárási Adatok - {city_name}")

    def _update_windy_days_tab(self, data: Dict[str, Any], city_name: str) -> None:
        """WindyDaysTab frissítése."""
        logger.info("🌪️ WindyDaysTab frissítése STARTED (REFACTORED)...")

        try:
            # DataFrame konverzió
            weather_df = self.data_processor.convert_data_to_dataframe(data)
            logger.info("🚨 DEBUG: _convert_data_to_dataframe() HÍVÁS SIKERES")

            # Adatok kézbesítése
            self.data_processor.process_windy_days_data(
                weather_df,
                city_name,
                lambda df, city: self.tab_manager.update_windy_days_tab(data, city, df)
            )

        except Exception as convert_error:
            logger.error(f"🚨 DEBUG: _convert_data_to_dataframe() HIBA: {convert_error}")
            import traceback
            traceback.print_exc()
            empty_df = self.data_processor._empty_dataframe_fallback()
            self.tab_manager.update_windy_days_tab(data, city_name, empty_df)

    def clear_data(self) -> None:
        """Adatok törlése."""
        logger.debug("ResultsPanel.clear_data() MEGHÍVVA")

        # Loading elrejtése
        if self.is_loading():
            self.hide_loading_indicator()

        # Állapot törlése
        self.current_data = None
        self.current_city = None

        # Title reset
        self.title_label.setText("📊 Időjárási Adatok Elemzése")

        # Tabok törlése
        self.tab_manager.clear_all_tabs()

        logger.debug("ResultsPanel.clear_data() BEFEJEZVE")

    # === EXTREME WEATHER SIGNAL ===

    def _on_extreme_weather_clicked(self) -> None:
        """Extreme weather gomb kattintás kezelése."""
        logger.info("🔥 Extreme weather button clicked - emitting signal")
        self.extreme_weather_requested.emit()

        # Tab váltás
        self.switch_to_tab("extreme")

    def trigger_extreme_weather_analysis(self) -> None:
        """Programmatic extreme weather trigger."""
        logger.info("🔥 Programmatic extreme weather analysis triggered")
        self.extreme_weather_requested.emit()

    # === WINDY DAYS SIGNAL KEZELŐK ===

    def _on_windy_days_analysis_completed(self, result: Dict[str, Any]) -> None:
        """WindyDaysTab analízis befejezés kezelése."""
        logger.info("🌪️ WindyDaysTab analízis befejezve")

    def _on_windy_days_error(self, error_message: str) -> None:
        """WindyDaysTab hiba kezelése."""
        logger.error(f"🌪️ WindyDaysTab hiba: {error_message}")

        # Hiba megjelenítése
        original_text = self.title_label.text()
        self.title_label.setText(f"⚠️ Szeles napok hiba: {error_message[:30]}...")

        # Reset 5 másodperc után
        QTimer.singleShot(5000, lambda: self.title_label.setText(original_text))

    def _on_windy_days_export_requested(self, file_type: str, file_path: str) -> None:
        """WindyDaysTab export kérés kezelése."""
        logger.info(f"🌪️ WindyDaysTab export kérés: {file_type} -> {file_path}")
        self.export_requested.emit(file_type)

    # === TÉMA KEZELÉS ===

    def apply_theme(self, dark_theme: bool) -> None:
        """
        Téma alkalmazása.

        Args:
            dark_theme: Sötét téma engedélyezve
        """
        logger.debug(f"ResultsPanel.apply_theme({dark_theme}) MEGHÍVVA")
        self.tab_manager.apply_theme(dark_theme)
        logger.debug("ResultsPanel.apply_theme() BEFEJEZVE")

    # === PUBLIKUS GETTEREK ===

    def get_charts_container(self):
        """Charts container referenciájának lekérdezése."""
        return self.tab_manager.get_charts_container()

    def get_data_table(self):
        """Data table referenciájának lekérdezése."""
        return self.tab_manager.get_data_table()

    # === THEMEMANAGER API ===

    def apply_theme_by_name(self, theme_name: str) -> None:
        """Téma alkalmazása név alapján."""
        if self.theme_manager:
            success = self.theme_manager.set_theme(theme_name)
            if success:
                logger.info(f"ResultsPanel téma alkalmazva: {theme_name}")
            else:
                logger.error(f"ResultsPanel téma alkalmazás sikertelen: {theme_name}")

    def get_current_theme_name(self) -> str:
        """Jelenlegi téma nevének lekérdezése."""
        if self.theme_manager:
            return self.theme_manager.get_current_theme()
        return "default"

    # === STATE MANAGEMENT ===

    def get_state(self) -> Dict[str, Any]:
        """ResultsPanel állapot lekérdezése."""
        return {
            "is_loading": self.is_loading(),
            "current_city": self.current_city,
            "has_data": self.current_data is not None,
            "current_tab": self.get_current_tab(),
            "progress_visible": self.progress_indicator.isVisible(),
            "pandas_available": True,
            "dataframe_extractor_available": self.data_processor._dataframe_extractor_available,
            "is_valid": True
        }

    def set_state(self, state: Dict[str, Any]) -> bool:
        """ResultsPanel állapot beállítása."""
        try:
            if state.get("is_loading"):
                self.show_loading_indicator()
            elif "is_loading" in state:
                self.hide_loading_indicator()

            if "current_tab" in state:
                self.switch_to_tab(state["current_tab"])

            logger.debug("ResultsPanel state set successfully")
            return True
        except Exception as e:
            logger.error(f"ResultsPanel state set failed: {e}")
            return False

    def is_valid(self) -> bool:
        """ResultsPanel validálása."""
        return True

    def set_enabled(self, enabled: bool) -> None:
        """ResultsPanel engedélyezése/letiltása."""
        if self.tab_widget:
            self.tab_widget.setEnabled(enabled)
        self.global_export_btn.setEnabled(enabled)
        self.extreme_weather_btn.setEnabled(enabled)
        logger.debug(f"ResultsPanel enabled state: {enabled}")

    # === EMERGENCY CONTROLS ===

    def emergency_reset(self) -> None:
        """Emergency reset - teljes panel visszaállítása."""
        logger.warning("ResultsPanel emergency reset triggered")

        # Loading reset
        self.force_hide_loading()

        # Data clear
        self.clear_data()

        # UI reset
        self.title_label.setText("📊 Időjárási Adatok Elemzése")
        self.switch_to_tab("overview")

        logger.warning("ResultsPanel emergency reset completed")

    def get_loading_status(self) -> Dict[str, Any]:
        """Loading állapot részletes lekérdezése."""
        return {
            "is_loading": self.is_loading(),
            "progress_text": self.progress_manager.get_progress_text(),
            "progress_visible": self.progress_indicator.isVisible(),
        }

    # === CLEANUP ===

    def cleanup(self) -> None:
        """ResultsPanel cleanup."""
        # Progress manager cleanup
        self.progress_manager.cleanup()

        # Tab cleanup
        self.tab_manager.cleanup()

        logger.debug("ResultsPanel cleanup completed")

    def closeEvent(self, event) -> None:
        """Widget bezárása - cleanup hívás."""
        self.cleanup()
        super().closeEvent(event)

    def __del__(self):
        """Destruktor - cleanup."""
        try:
            self.cleanup()
        except Exception:
            logger.exception("ResultsPanel cleanup during destruction failed")
