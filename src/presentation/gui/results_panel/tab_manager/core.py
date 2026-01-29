"""Tab Manager Core - initialization and tab creation."""
import logging
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget


class TabManager(QObject):
    """Tab management kezelése."""

    tab_changed = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)

        self.tab_widget: Optional[QTabWidget] = None
        self.overview_tab: Optional[QWidget] = None
        self.charts_tab: Optional[QWidget] = None
        self.table_tab: Optional[QWidget] = None
        self.extreme_tab: Optional[QWidget] = None
        self.windy_days_tab: Optional[QWidget] = None

        self._overview_available = False
        self._charts_available = False
        self._table_available = False
        self._extreme_available = False
        self._windy_days_available = False

    def initialize(self) -> QTabWidget:
        """Tab manager inicializálása."""
        self.tab_widget = QTabWidget()
        self._create_tabs()
        return self.tab_widget

    def _create_tabs(self) -> None:
        """Tabok létrehozása importokkal."""
        self._logger.info("Tab availability check started...")

        # QuickOverviewTab
        try:
            from .quick_overview_tab import QuickOverviewTab
            self.overview_tab = QuickOverviewTab()
            self.tab_widget.addTab(self.overview_tab, "📊 Gyors Áttekintés")
            self._overview_available = True
        except ImportError as e:
            self._logger.warning(f"QuickOverviewTab import failed: {e}")
            self.overview_tab = self._create_fallback_tab("📊 Gyors Áttekintés (Fallback)")
            self.tab_widget.addTab(self.overview_tab, "📊 Gyors Áttekintés")

        # DetailedChartsTab
        try:
            from .detailed_charts_tab import DetailedChartsTab
            self.charts_tab = DetailedChartsTab()
            self.tab_widget.addTab(self.charts_tab, "📈 Részletes Diagramok")
            self._charts_available = True
        except ImportError as e:
            self._logger.warning(f"DetailedChartsTab import failed: {e}")
            self.charts_tab = self._create_fallback_tab("📈 Részletes Diagramok (Fallback)")
            self.tab_widget.addTab(self.charts_tab, "📈 Részletes Diagramok")

        # DataTableTab
        try:
            from .data_table_tab import DataTableTab
            self.table_tab = DataTableTab()
            self.tab_widget.addTab(self.table_tab, "📋 Adattáblázat")
            self._table_available = True
        except ImportError as e:
            self._logger.warning(f"DataTableTab import failed: {e}")
            self.table_tab = self._create_fallback_tab("📋 Adattáblázat (Fallback)")
            self.tab_widget.addTab(self.table_tab, "📋 Adattáblázat")

        # ExtremeEventsTab
        try:
            from .extreme_events_tab import ExtremeEventsTab
            self.extreme_tab = ExtremeEventsTab()
            self.tab_widget.addTab(self.extreme_tab, "⚡ Extrém Események")
            self._extreme_available = True
        except ImportError as e:
            self._logger.warning(f"ExtremeEventsTab import failed: {e}")
            self.extreme_tab = self._create_fallback_tab("⚡ Extrém Események (Fallback)")
            self.tab_widget.addTab(self.extreme_tab, "⚡ Extrém Események")

        # WindyDaysTab
        try:
            from .windy_days_tab import WindyDaysTab
            self.windy_days_tab = WindyDaysTab()
            self.tab_widget.addTab(self.windy_days_tab, "🌪️ Szeles Napok")
            self._windy_days_available = True
        except ImportError as e:
            self._logger.warning(f"WindyDaysTab import failed: {e}")
            self.windy_days_tab = self._create_fallback_tab("🌪️ Szeles Napok (Fallback)")
            self.tab_widget.addTab(self.windy_days_tab, "🌪️ Szeles Napok (Fallback)")

    def _create_fallback_tab(self, title: str) -> QWidget:
        """Fallback tab létrehozása."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(title)
        layout.addWidget(label)
        return widget

    def switch_to_tab(self, tab_name: str) -> None:
        """Specifikus tab-ra váltás."""
        if not self.tab_widget:
            return

        tab_indices = {
            "overview": 0, "charts": 1, "table": 2, "extreme": 3, "windy_days": 4
        }

        if tab_name in tab_indices:
            self.tab_widget.setCurrentIndex(tab_indices[tab_name])
            self.tab_changed.emit(tab_name)

    def get_current_tab(self) -> str:
        """Jelenlegi aktív tab neve."""
        if not self.tab_widget:
            return "overview"

        current_index = self.tab_widget.currentIndex()
        tab_names = ["overview", "charts", "table", "extreme", "windy_days"]

        if 0 <= current_index < len(tab_names):
            return tab_names[current_index]
        return "overview"
