#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tab Manager - Tab management és frissítés kezelése

Kezeli a tabok létrehozását, frissítését, váltását
és a tematizálást.
"""

import logging
from typing import Dict, Any, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTabWidget, QLabel, QPushButton, QWidget


class TabManager(QObject):
    """
    Tab management kezelése.

    Felelőségek:
    - Tab widget inicializálása
    - Tabok létrehozása (QuickOverview, DetailedCharts, DataTable, ExtremeEvents, WindyDays)
    - Tab váltás
    - Tab frissítés adatokkal
    - Tab tematizálás
    """

    # Signalok
    tab_changed = Signal(str)  # tab név változás

    def __init__(self, parent=None):
        """
        TabManager inicializálása.

        Args:
            parent: Szülő QObject
        """
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)

        # Tab referenciák
        self.tab_widget: Optional[QTabWidget] = None
        self.overview_tab: Optional[QWidget] = None
        self.charts_tab: Optional[QWidget] = None
        self.table_tab: Optional[QWidget] = None
        self.extreme_tab: Optional[QWidget] = None
        self.windy_days_tab: Optional[QWidget] = None

        # Tab elérhetőség flag-ek
        self._overview_available = False
        self._charts_available = False
        self._table_available = False
        self._extreme_available = False
        self._windy_days_available = False

    def initialize(self) -> QTabWidget:
        """
        Tab manager inicializálása és a tab widget létrehozása.

        Returns:
            QTabWidget: A létrehozott tab widget
        """
        self.tab_widget = QTabWidget()
        self._create_tabs()
        return self.tab_widget

    def _create_tabs(self) -> None:
        """Tabok létrehozása importokkal."""
        self._logger.info("📊 Tab availability check started...")

        # QuickOverviewTab import
        try:
            from .quick_overview_tab import QuickOverviewTab
            self.overview_tab = QuickOverviewTab()
            self.tab_widget.addTab(self.overview_tab, "📊 Gyors Áttekintés")
            self._overview_available = True
            self._logger.debug("✅ QuickOverviewTab import successful")
        except ImportError as e:
            self._logger.warning(f"⚠️ QuickOverviewTab import failed: {e}")
            self._overview_tab = self._create_fallback_tab("📊 Gyors Áttekintés (Fallback)")
            self.tab_widget.addTab(self.overview_tab, "📊 Gyors Áttekintés")

        # DetailedChartsTab import
        try:
            from .detailed_charts_tab import DetailedChartsTab
            self.charts_tab = DetailedChartsTab()
            self.tab_widget.addTab(self.charts_tab, "📈 Részletes Diagramok")
            self._charts_available = True
            self._logger.debug("✅ DetailedChartsTab import successful")
        except ImportError as e:
            self._logger.warning(f"⚠️ DetailedChartsTab import failed: {e}")
            self.charts_tab = self._create_fallback_tab("📈 Részletes Diagramok (Fallback)")
            self.tab_widget.addTab(self.charts_tab, "📈 Részletes Diagramok")

        # DataTableTab import
        try:
            from .data_table_tab import DataTableTab
            self.table_tab = DataTableTab()
            self.tab_widget.addTab(self.table_tab, "📋 Adattáblázat")
            self._table_available = True
            self._logger.debug("✅ DataTableTab import successful")
        except ImportError as e:
            self._logger.warning(f"⚠️ DataTableTab import failed: {e}")
            self.table_tab = self._create_fallback_tab("📋 Adattáblázat (Fallback)")
            self.tab_widget.addTab(self.table_tab, "📋 Adattáblázat")

        # ExtremeEventsTab import
        try:
            from .extreme_events_tab import ExtremeEventsTab
            self.extreme_tab = ExtremeEventsTab()
            self.tab_widget.addTab(self.extreme_tab, "⚡ Extrém Események")
            self._extreme_available = True
            self._logger.debug("✅ ExtremeEventsTab import successful")
        except ImportError as e:
            self._logger.warning(f"⚠️ ExtremeEventsTab import failed: {e}")
            self.extreme_tab = self._create_fallback_tab("⚡ Extrém Események (Fallback)")
            self.tab_widget.addTab(self.extreme_tab, "⚡ Extrém Események")

        # WindyDaysTab import
        try:
            from .windy_days_tab import WindyDaysTab
            self.windy_days_tab = WindyDaysTab()
            self.tab_widget.addTab(self.windy_days_tab, "🌪️ Szeles Napok")
            self._windy_days_available = True
            self._logger.info("✅ WindyDaysTab sikeresen hozzáadva")
        except ImportError as e:
            self._logger.warning(f"⚠️ WindyDaysTab import failed: {e}")
            self.windy_days_tab = self._create_fallback_tab("🌪️ Szeles Napok (Fallback)")
            self.tab_widget.addTab(self.windy_days_tab, "🌪️ Szeles Napok (Fallback)")

        self._logger.info(f"📊 Tab availability: overview={self._overview_available}, "
                         f"charts={self._charts_available}, table={self._table_available}, "
                         f"extreme={self._extreme_available}, windy_days={self._windy_days_available}")

    def _create_fallback_tab(self, title: str) -> QWidget:
        """
        Fallback tab létrehozása ha az import sikertelen.

        Args:
            title: Tab címe

        Returns:
            QWidget: Egyszerű fallback widget
        """
        from PySide6.QtWidgets import QVBoxLayout

        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel(title)
        layout.addWidget(label)

        return widget

    def update_standard_tabs(self, data: Dict[str, Any], city_name: str) -> None:
        """
        Szabványos tabok frissítése adatokkal.

        Args:
            data: Időjárási adatok
            city_name: Város neve
        """
        # QuickOverviewTab frissítése
        if self.overview_tab and self._overview_available:
            self._logger.debug("QuickOverviewTab frissítése...")
            self.overview_tab.update_data(data, city_name)

        # DetailedChartsTab frissítése
        if self.charts_tab and self._charts_available:
            self._logger.debug("DetailedChartsTab frissítése...")
            self.charts_tab.update_data(data)

        # DataTableTab frissítése
        if self.table_tab and self._table_available:
            self._logger.debug("DataTableTab frissítése...")
            self.table_tab.update_data(data)

        # ExtremeEventsTab frissítése
        if self.extreme_tab and self._extreme_available:
            self._logger.debug("ExtremeEventsTab frissítése...")
            self.extreme_tab.update_data(data)

    def update_windy_days_tab(self, data: Any, city_name: str, weather_df: Any) -> None:
        """
        WindyDaysTab frissítése adatokkal.

        Args:
            data: Időjárási adatok
            city_name: Város neve
            weather_df: DataFrame adatok
        """
        if not self.windy_days_tab:
            self._logger.error("❌ WindyDaysTab nem elérhető!")
            return
        if not self._windy_days_available:
            self._logger.warning("⚠️ WindyDaysTab fallback frissítése...")
            return

        self._logger.info("🌪️ WindyDaysTab frissítése STARTED...")
        if not hasattr(self.windy_days_tab, 'update_data'):
            self._logger.error("❌ WindyDaysTab.update_data metódus nem elérhető")
            return

        try:
            self.windy_days_tab.update_data(weather_df, city_name)
            self._logger.info("✅ WindyDaysTab.update_data() SIKERES!")
        except Exception as e:
            self._logger.error(f"❌ WindyDaysTab frissítési hiba: {e}")

    def switch_to_tab(self, tab_name: str) -> None:
        """
        Specifikus tab-ra váltás.

        Args:
            tab_name: Tab neve ("overview", "charts", "table", "extreme", "windy_days")
        """
        if not self.tab_widget:
            return

        tab_indices = {
            "overview": 0,
            "charts": 1,
            "table": 2,
            "extreme": 3,
            "windy_days": 4
        }

        if tab_name in tab_indices:
            self.tab_widget.setCurrentIndex(tab_indices[tab_name])
            self.tab_changed.emit(tab_name)
            self._logger.debug(f"📊 DEBUG: Switched to tab: {tab_name}")

    def get_current_tab(self) -> str:
        """
        Jelenlegi aktív tab nevének lekérdezése.

        Returns:
            str: Aktív tab neve
        """
        if not self.tab_widget:
            return "overview"

        current_index = self.tab_widget.currentIndex()
        tab_names = ["overview", "charts", "table", "extreme", "windy_days"]

        if 0 <= current_index < len(tab_names):
            return tab_names[current_index]
        return "overview"

    def get_windy_days_tab(self) -> Optional[QWidget]:
        """
        WindyDaysTab referencia lekérdezése.

        Returns:
            WindyDaysTab vagy None
        """
        return self.windy_days_tab if self._windy_days_available else None

    def get_charts_container(self) -> Optional[object]:
        """
        Charts container referenciájának lekérdezése.

        Returns:
            Charts container vagy None
        """
        if self.charts_tab and hasattr(self.charts_tab, 'charts_container'):
            return self.charts_tab.charts_container
        return None

    def get_data_table(self) -> Optional[object]:
        """
        Data table referenciájának lekérdezése.

        Returns:
            Data table vagy None
        """
        if self.table_tab and hasattr(self.table_tab, 'data_table'):
            return self.table_tab.data_table
        return None

    def apply_theme(self, dark_theme: bool) -> None:
        """
        Téma alkalmazása az összes tab-ra.

        Args:
            dark_theme: Sötét téma engedélyezve
        """
        # Charts tab theme
        if self.charts_tab and hasattr(self.charts_tab, 'apply_theme'):
            self.charts_tab.apply_theme(dark_theme)

        # Table tab theme
        if self.table_tab and hasattr(self.table_tab, 'apply_theme'):
            self.table_tab.apply_theme(dark_theme)

        # WindyDaysTab theme
        if self.windy_days_tab and hasattr(self.windy_days_tab, '_on_theme_changed'):
            theme_name = "dark" if dark_theme else "light"
            self.windy_days_tab._on_theme_changed(theme_name)

    def clear_all_tabs(self) -> None:
        """Minden tab adatainak törlése."""
        if self.overview_tab and hasattr(self.overview_tab, '_clear_stats'):
            self.overview_tab._clear_stats()

        if self.charts_tab and hasattr(self.charts_tab, 'clear_data'):
            self.charts_tab.clear_data()

        if self.table_tab and hasattr(self.table_tab, 'clear_data'):
            self.table_tab.clear_data()

        if self.extreme_tab and hasattr(self.extreme_tab, '_clear_extremes'):
            self.extreme_tab._clear_extremes()

        if self.windy_days_tab and hasattr(self.windy_days_tab, 'clear_data'):
            self.windy_days_tab.clear_data()

    def cleanup(self) -> None:
        """Tabok cleanup-ja."""
        if self.overview_tab and hasattr(self.overview_tab, 'cleanup'):
            self.overview_tab.cleanup()

        if self.charts_tab and hasattr(self.charts_tab, 'cleanup'):
            self.charts_tab.cleanup()

        if self.table_tab and hasattr(self.table_tab, 'cleanup'):
            self.table_tab.cleanup()

        if self.extreme_tab and hasattr(self.extreme_tab, 'cleanup'):
            self.extreme_tab.cleanup()

        if self.windy_days_tab and hasattr(self.windy_days_tab, 'cleanup'):
            self.windy_days_tab.cleanup()

        self._logger.debug("Tab cleanup completed")
