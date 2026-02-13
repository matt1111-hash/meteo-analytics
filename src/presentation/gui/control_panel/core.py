#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Control Panel Core (CLEAN ARCHITECTURE)
SIGNAL AGGREGATOR PATTERN - FETCH_BUTTON FIX BEFEJEZVE!

🎯 CLEAN ARCHITECTURE + FETCH_BUTTON FIX:
- Single Responsibility: Widget aggregáció és egyetlen signal routing
- Signal Aggregation: CSAK analysis_requested = Signal(dict) - FŐCSATORNA
- Widget Composition: 7 specializált widget komponens (+ MultiCityWidget)
- State Management: get_current_state() minden widget-ből
- 🔧 FETCH_BUTTON FIX: fetch_button → query_button minden előfordulásban
- 🏙️ MULTI-CITY WIDGET INTEGRÁCIÓ: Régió/megye választás támogatás
- 📡 SIGNAL ROUTING: Multi-city selection_changed signal kezelés

🔧 KRITIKUS JAVÍTÁSOK BEFEJEZVE:
✅ _update_fetch_button_state_comprehensive() - fetch_button → query_button
✅ _preserve_widget_states() - State megőrzés analysis type váltás előtt
✅ _restore_widget_states() - State visszaállítás analysis type váltás után
✅ _force_widget_refresh() - Widget belső állapot refresh
✅ _comprehensive_fetch_validation() - Robusztus fetch button logic
✅ Debug logging minden kritikus pontra
✅ 🏙️ MultiCityWidget integráció analysis_type alapú mode váltással
✅ 📡 Multi-city selection signal routing
✅ 🚨 DATE RANGE FIX: AppController kompatibilis formátum
✅ 🚨 VALIDATION FIX: location_data objektum alatt keresi lat/lon kulcsokat
✅ 🔧 FETCH_BUTTON ATTRIBUTE FIX: Minden query_button.setEnabled() javítva
✅ 🔥 PROGRESS TEXT FIX: set_progress_text → update_progress
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from src.domain.ports import CityManagerPort
from src.infrastructure.container import get_city_manager_port

# Refaktorált widget komponensek
from ..panel_widgets.analysis_type_widget import AnalysisTypeWidget
from ..panel_widgets.api_settings_widget import ApiSettingsWidget
from ..panel_widgets.date_range_widget import DateRangeWidget
from ..panel_widgets.location_widget import LocationWidget
from ..panel_widgets.multi_city_widget import MultiCityWidget  # 🏙️ ÚJ: Multi-City Widget
from ..panel_widgets.provider_widget import ProviderWidget
from ..panel_widgets.query_control_widget import QueryControlWidget
from ..theme_manager import get_theme_manager
from ..workers import WorkerManager

# Mixins
from .mixins import (
    ExternalHandlersMixin,
    FetchValidationMixin,
    PublicAPIMixin,
    RequestBuilderMixin,
    SignalHandlersMixin,
    UIManagerMixin,
)


class ControlPanel(
    SignalHandlersMixin,
    UIManagerMixin,
    FetchValidationMixin,
    RequestBuilderMixin,
    PublicAPIMixin,
    ExternalHandlersMixin,
    QWidget,
):
    """
    🎯 CLEAN ARCHITECTURE CONTROL PANEL - FETCH_BUTTON FIX BEFEJEZVE!

    WIDGET HIERARCHIA:
    - AnalysisTypeWidget: Egyedi/Régió/Megye választó
    - LocationWidget: UniversalLocationSelector wrapper (single_location módban) ✅
    - MultiCityWidget: Magyar régiók/megyék checkbox lista (region/county módban) ✅ ÚJ
    - DateRangeWidget: Multi-year + Manual dátum választó
    - ProviderWidget: API provider + usage tracking
    - ApiSettingsWidget: Timeout, cache, timezone beállítások
    - QueryControlWidget: Fetch/cancel gombok + progress

    CLEAN SIGNAL FLOW:
    🎯 analysis_requested(dict) ← EGYETLEN KIMENŐ SIGNAL
    ├── Widget events aggregálás
    ├── Comprehensive analysis request building
    └── AppController delegálás

    🏙️ MULTI-CITY WIDGET INTEGRÁCIÓ:
    ✅ Analysis type alapú widget váltás (LocationWidget ↔ MultiCityWidget)
    ✅ Régió/megye selection signal routing
    ✅ State preservation multi-city módban
    ✅ Comprehensive fetch validation multi-city támogatással
    ✅ Debug logging minden kritikus pont
    """

    # === CLEAN ARCHITECTURE - EGYETLEN KIMENŐ SIGNAL ===
    analysis_requested = Signal(dict)  # Comprehensive analysis request

    # === MINIMÁLIS KOMPATIBILITÁSI SIGNALOK ===
    search_requested = Signal(str)  # LocationWidget geocoding
    city_selected = Signal(str, float, float, dict)  # LocationWidget selection
    local_error_occurred = Signal(str)  # Error handling

    def __init__(self, worker_manager: WorkerManager, parent: Optional[QWidget] = None):
        """
        Clean ControlPanel inicializálása.

        Args:
            worker_manager: Worker manager (kompatibilitás)
            parent: Szülő widget
        """
        super().__init__(parent)

        # Dependencies (CA compliant - uses port)
        self.worker_manager = worker_manager
        self.city_manager: CityManagerPort = get_city_manager_port()
        self.theme_manager = get_theme_manager()

        # 🔧 WIDGET STATE PRESERVATION
        self._preserved_states: dict = {}
        self._last_analysis_type = "single_location"

        # UI init
        self._init_ui()
        self._connect_widget_signals()
        self._setup_theme()

        print(
            "🎯 ControlPanel CLEAN ARCHITECTURE + MULTI-CITY WIDGET - Widget Aggregator Pattern initialized"
        )

    def _init_ui(self) -> None:
        """UI struktúra létrehozása scroll area-val."""
        # Panel size policy
        self.setMinimumWidth(320)
        self.setMaximumWidth(450)
        self.setMinimumHeight(700)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # Scroll area wrapper
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Scroll content widget
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        # Content layout
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(16)

        # === WIDGET KOMPONENSEK LÉTREHOZÁSA ===

        # 1. Analysis Type Widget
        self.analysis_type_widget = AnalysisTypeWidget()
        content_layout.addWidget(self.analysis_type_widget)

        # 2. Location Widget (single_location módban)
        self.location_widget = LocationWidget(self.city_manager)
        content_layout.addWidget(self.location_widget)

        # 🏙️ 3. Multi-City Widget (region/county módban) - ÚJ WIDGET
        self.multi_city_widget = MultiCityWidget(self.city_manager)
        content_layout.addWidget(self.multi_city_widget)

        print("🏙️ DEBUG: MultiCityWidget létrehozva és hozzáadva a layout-hoz")

        # 4. Date Range Widget
        self.date_range_widget = DateRangeWidget()
        content_layout.addWidget(self.date_range_widget)

        # 5. Provider Widget
        self.provider_widget = ProviderWidget()
        content_layout.addWidget(self.provider_widget)

        # 6. API Settings Widget
        self.api_settings_widget = ApiSettingsWidget()
        content_layout.addWidget(self.api_settings_widget)

        # 7. Query Control Widget
        self.query_control_widget = QueryControlWidget()
        content_layout.addWidget(self.query_control_widget)

        # Stretch a végén
        content_layout.addStretch()

        # 🚨 KRITIKUS: Kezdeti UI állapot beállítása MULTI-CITY TÁMOGATÁSSAL
        self._update_ui_for_analysis_type_fixed("single_location")

        print("✅ DEBUG: ControlPanel UI setup complete - MULTI-CITY WIDGET INTEGRÁLVA")

    def _setup_theme(self) -> None:
        """Theme setup - minden widget már regisztrálva van saját magában."""
        if hasattr(self.theme_manager, "theme_changed"):
            self.theme_manager.theme_changed.connect(self._on_theme_changed)

        print("🎨 Theme setup completed for clean ControlPanel + MultiCityWidget")
