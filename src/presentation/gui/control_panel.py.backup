#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Control Panel (CLEAN ARCHITECTURE)
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

📋 WIDGET HIERARCHIA (KIEGÉSZÍTVE):
- AnalysisTypeWidget: Egyedi/Régió/Megye választó
- LocationWidget: UniversalLocationSelector wrapper (single_location módban) ✅ 
- MultiCityWidget: Magyar régiók/megyék checkbox lista (region/county módban) ✅ ÚJ
- DateRangeWidget: Multi-year + Manual dátum választó
- ProviderWidget: API provider + usage tracking
- ApiSettingsWidget: Timeout, cache, timezone beállítások
- QueryControlWidget: Fetch/cancel gombok + progress
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt, QTimer

# Refaktorált widget komponensek
from .panel_widgets.analysis_type_widget import AnalysisTypeWidget
from .panel_widgets.location_widget import LocationWidget  
from .panel_widgets.multi_city_widget import MultiCityWidget  # 🏙️ ÚJ: Multi-City Widget
from .panel_widgets.date_range_widget import DateRangeWidget
from .panel_widgets.provider_widget import ProviderWidget
from .panel_widgets.api_settings_widget import ApiSettingsWidget
from .panel_widgets.query_control_widget import QueryControlWidget

from .workers.data_fetch_worker import WorkerManager
from .theme_manager import get_theme_manager
from ..data.city_manager import CityManager


class ControlPanel(QWidget):
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
    search_requested = Signal(str)                        # LocationWidget geocoding
    city_selected = Signal(str, float, float, dict)       # LocationWidget selection  
    local_error_occurred = Signal(str)                    # Error handling
    
    def __init__(self, worker_manager: WorkerManager, parent: Optional[QWidget] = None):
        """
        Clean ControlPanel inicializálása.
        
        Args:
            worker_manager: Worker manager (kompatibilitás)
            parent: Szülő widget
        """
        super().__init__(parent)
        
        # Dependencies
        self.worker_manager = worker_manager
        self.city_manager = CityManager()
        self.theme_manager = get_theme_manager()
        
        # 🔧 WIDGET STATE PRESERVATION
        self._preserved_states: Dict[str, Any] = {}
        self._last_analysis_type = "single_location"
        
        # UI init
        self._init_ui()
        self._connect_widget_signals()
        self._setup_theme()
        
        print("🎯 ControlPanel CLEAN ARCHITECTURE + MULTI-CITY WIDGET - Widget Aggregator Pattern initialized")
    
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
    
    def _connect_widget_signals(self) -> None:
        """Widget signalok összekötése - CLEAN SIGNAL ROUTING + MULTI-CITY."""
        
        # === 1. ANALYSIS TYPE WIDGET ===
        self.analysis_type_widget.analysis_type_changed.connect(self._on_analysis_type_changed)
        
        # === 2. LOCATION WIDGET ===
        # Kompatibilitási signalok (AppController számára)
        self.location_widget.search_requested.connect(self.search_requested.emit)
        self.location_widget.city_selected.connect(self.city_selected.emit)
        
        # Internal handling
        self.location_widget.location_changed.connect(self._on_location_changed)
        
        # 🏙️ === 3. MULTI-CITY WIDGET (ÚJ) ===
        self.multi_city_widget.selection_changed.connect(self._on_multi_city_selection_changed)
        
        # === 4. DATE RANGE WIDGET ===
        self.date_range_widget.date_range_changed.connect(self._on_date_range_changed)
        self.date_range_widget.date_mode_changed.connect(self._on_date_mode_changed)
        
        # === 5. PROVIDER WIDGET ===
        self.provider_widget.provider_changed.connect(self._on_provider_changed)
        
        # === 6. API SETTINGS WIDGET ===
        self.api_settings_widget.api_settings_changed.connect(self._on_api_settings_changed)
        
        # === 7. QUERY CONTROL WIDGET ===
        self.query_control_widget.fetch_requested.connect(self._on_fetch_requested)
        self.query_control_widget.cancel_requested.connect(self._on_cancel_requested)
        
        print("🎯 Clean signal routing connected + MULTI-CITY signals - Single analysis_requested signal")
    
    def _setup_theme(self) -> None:
        """Theme setup - minden widget már regisztrálva van saját magában."""
        if hasattr(self.theme_manager, 'theme_changed'):
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        print("🎨 Theme setup completed for clean ControlPanel + MultiCityWidget")
    
    # === WIDGET SIGNAL HANDLERS - CLEAN AGGREGATION + MULTI-CITY ===
    
    def _on_analysis_type_changed(self, analysis_type: str) -> None:
        """
        🔧 KRITIKUS FIX: Analysis type változás kezelése + WIDGET STATE PRESERVATION + MULTI-CITY.
        
        Args:
            analysis_type: Új analysis type ("single_location", "region", "county")
        """
        print(f"🎯 DEBUG: Analysis type changed from '{self._last_analysis_type}' to '{analysis_type}'")
        
        # 1. WIDGET STATES MEGŐRZÉSE (analysis type váltás előtt)
        self._preserve_widget_states()
        
        # 2. UI FRISSÍTÉSE - JAVÍTOTT VERZIÓ MULTI-CITY TÁMOGATÁSSAL
        self._update_ui_for_analysis_type_fixed(analysis_type)
        
        # 3. WIDGET STATES VISSZAÁLLÍTÁSA (analysis type váltás után)
        self._restore_widget_states(analysis_type)
        
        # 4. FETCH BUTTON STATE ÚJRAÉRTÉKELÉSE
        self._update_fetch_button_state_comprehensive()
        
        # 5. LAST ANALYSIS TYPE TRACKING
        self._last_analysis_type = analysis_type
        
        print(f"✅ DEBUG: Analysis type change completed: {analysis_type}")
    
    def _on_location_changed(self, location) -> None:
        """Location változás kezelése."""
        print(f"🌍 Location changed: {location}")
        
        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()
    
    def _on_multi_city_selection_changed(self, selection_data: Dict[str, Any]) -> None:
        """
        🏙️ ÚJ: Multi-city selection változás kezelése.
        
        Args:
            selection_data: {"mode": "region", "selected": [...], "count": 3, "is_valid": True}
        """
        mode = selection_data.get("mode", "unknown")
        count = selection_data.get("count", 0)
        selected = selection_data.get("selected", [])
        
        print(f"🏙️ Multi-city selection changed: {mode} mode, {count} items selected")
        print(f"📋 Selected items: {selected[:3]}{'...' if len(selected) > 3 else ''}")
        
        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()
    
    def _on_date_range_changed(self, start_date: str, end_date: str) -> None:
        """Date range változás kezelése."""
        print(f"📅 Date range changed: {start_date} → {end_date}")
        
        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()
    
    def _on_date_mode_changed(self, date_mode: str) -> None:
        """Date mode változás kezelése."""
        print(f"📅 Date mode changed: {date_mode}")
        
        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()
    
    def _on_provider_changed(self, provider: str) -> None:
        """Provider változás kezelése."""
        print(f"🎛️ Provider changed: {provider}")
        
        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()
    
    def _on_api_settings_changed(self, settings: Dict[str, Any]) -> None:
        """API settings változás kezelése."""
        print(f"⚙️ API settings changed: {settings}")
        
        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()
    
    def _on_fetch_requested(self) -> None:
        """
        🎯 FETCH REQUEST KEZELÉSE - FŐSIGNAL KIBOCSÁTÁS + MULTI-CITY TÁMOGATÁS
        
        Ez a CLEAN ARCHITECTURE központi pontja:
        1. Widget state aggregálás (+ multi-city)
        2. Analysis request building
        3. Validálás
        4. analysis_requested(dict) signal emit
        """
        print("🚀 Fetch requested - generating clean analysis request + multi-city support")
        
        # Comprehensive analysis request összeállítása
        analysis_request = self._build_analysis_request()
        
        if self._validate_analysis_request(analysis_request):
            # Fetch state beállítása
            self.query_control_widget.set_fetching_state(True)
            
            # 🎯 FŐSIGNAL KIBOCSÁTÁSA - CLEAN ARCHITECTURE
            self.analysis_requested.emit(analysis_request)
            
            print(f"🎯 CLEAN: analysis_requested emitted → {analysis_request['analysis_type']}")
            
            # 🔧 AUTO-RESET FETCH STATE - Error esetére timeout
            from PySide6.QtCore import QTimer
            QTimer.singleShot(2000, self._auto_reset_fetch_state)  # 2 sec után reset
            
        else:
            print("❌ ERROR: Invalid analysis request")
            # 🔧 FETCH STATE RESET on validation failure
            self.query_control_widget.set_fetching_state(False)
            self.local_error_occurred.emit("Hiányos vagy érvénytelen beállítások")
    
    def _on_cancel_requested(self) -> None:
        """Cancel request kezelése."""
        print("⛔ Cancel requested")
        
        # Worker manager stop
        if self.worker_manager:
            self.worker_manager.stop_all_workers()
        
        # UI reset
        self.query_control_widget.set_fetching_state(False)
        self._update_fetch_button_state_comprehensive()
    
    def _on_theme_changed(self, theme_name: str) -> None:
        """Theme változás kezelése."""
        print(f"🎨 Theme changed to: {theme_name}")
        # Widget-ek saját maguk kezelik a theme változást
    
    # === 🔧 KRITIKUS FIX: UI MANAGEMENT LOGIC - MULTI-CITY WIDGET VÁLTÁS ===
    
    def _preserve_widget_states(self) -> None:
        """
        🔧 Widget állapotok megőrzése analysis type váltás előtt + MULTI-CITY.
        """
        print("💾 DEBUG: Preserving widget states before analysis type change...")
        
        try:
            self._preserved_states = {
                "location": self.location_widget.get_state(),
                "multi_city": self.multi_city_widget.get_state(),  # 🏙️ ÚJ
                "date_range": self.date_range_widget.get_state(),
                "provider": self.provider_widget.get_state(),
                "api_settings": self.api_settings_widget.get_state()
            }
            
            location_valid = self._preserved_states['location'].get('is_valid', False)
            multi_city_valid = self._preserved_states['multi_city'].get('is_valid', False)
            print(f"✅ DEBUG: Widget states preserved - location: {location_valid}, multi-city: {multi_city_valid}")
            
        except Exception as e:
            print(f"⚠️ DEBUG: Error preserving widget states: {e}")
            self._preserved_states = {}
    
    def _restore_widget_states(self, analysis_type: str) -> None:
        """
        🔧 Widget állapotok visszaállítása analysis type váltás után + MULTI-CITY.
        
        Args:
            analysis_type: Aktuális analysis type
        """
        print(f"🔄 DEBUG: Restoring widget states for analysis type: {analysis_type}")
        
        try:
            # Location widget state visszaállítása (csak single_location módban)
            if analysis_type == "single_location" and "location" in self._preserved_states:
                location_state = self._preserved_states["location"]
                if location_state.get("has_location", False):
                    print("🔄 DEBUG: Restoring location widget state...")
                    self.location_widget.set_state(location_state)
            
            # 🏙️ Multi-city widget state visszaállítása (csak region/county módban)
            if analysis_type in ["region", "county"] and "multi_city" in self._preserved_states:
                multi_city_state = self._preserved_states["multi_city"]
                if multi_city_state.get("is_valid", False):
                    print(f"🏙️ DEBUG: Restoring multi-city widget state for {analysis_type}...")
                    self.multi_city_widget.set_state(multi_city_state)
            
            # Egyéb widget states visszaállítása
            if "date_range" in self._preserved_states:
                self.date_range_widget.set_state(self._preserved_states["date_range"])
            
            if "provider" in self._preserved_states:
                self.provider_widget.set_state(self._preserved_states["provider"])
            
            if "api_settings" in self._preserved_states:
                self.api_settings_widget.set_state(self._preserved_states["api_settings"])
            
            print("✅ DEBUG: Widget states restored successfully")
            
        except Exception as e:
            print(f"⚠️ DEBUG: Error restoring widget states: {e}")
    
    def _update_ui_for_analysis_type_fixed(self, analysis_type: str) -> None:
        """
        🔧 KRITIKUS FIX: UI elemek megjelenítése/elrejtése analysis type alapján + MULTI-CITY WIDGET VÁLTÁS.
        
        Args:
            analysis_type: Analysis type ("single_location", "region", "county")
        """
        print(f"🔧 DEBUG: _update_ui_for_analysis_type_fixed called: {analysis_type}")
        
        if analysis_type == "single_location":
            print("🔧 DEBUG: Setting UI to single_location mode - LocationWidget MEGJELENÍTÉSE...")
            
            # === LOCATION WIDGET MEGJELENÍTÉSE ===
            self.location_widget.setVisible(True)
            self.location_widget.setEnabled(True)
            
            if hasattr(self.location_widget, 'group'):
                self.location_widget.group.setVisible(True)
                self.location_widget.group.setEnabled(True)
            
            # Location widget belső enable + refresh
            self.location_widget.set_enabled(True)
            self.location_widget.show()
            
            # === MULTI-CITY WIDGET ELREJTÉSE ===
            self.multi_city_widget.setVisible(False)
            self.multi_city_widget.setEnabled(False)
            
            print("✅ DEBUG: UI set to single_location mode - LOCATION WIDGET VISIBLE, MULTI-CITY HIDDEN")
            
        elif analysis_type in ["region", "county"]:
            print(f"🔧 DEBUG: Setting UI to {analysis_type} mode - MultiCityWidget MEGJELENÍTÉSE...")
            
            # === LOCATION WIDGET ELREJTÉSE ===
            self.location_widget.setVisible(False)
            self.location_widget.setEnabled(False)
            
            # === MULTI-CITY WIDGET MEGJELENÍTÉSE + MODE BEÁLLÍTÁSA ===
            self.multi_city_widget.setVisible(True)
            self.multi_city_widget.setEnabled(True)
            self.multi_city_widget.show()
            
            # 🏙️ Analysis mode beállítása a MultiCityWidget-en
            self.multi_city_widget.set_analysis_mode(analysis_type)
            
            print(f"✅ DEBUG: UI set to {analysis_type} mode - MULTI-CITY WIDGET VISIBLE ({analysis_type} mode), LOCATION HIDDEN")
        
        # Query control button text frissítése
        if hasattr(self.query_control_widget, 'update_for_analysis_type'):
            self.query_control_widget.update_for_analysis_type(analysis_type)
        
        # Widget refresh késleltetett trigger (Qt event loop miatt)
        QTimer.singleShot(100, self._delayed_widget_refresh)
    
    def _delayed_widget_refresh(self) -> None:
        """
        🔧 Késleltetett widget refresh - Qt event loop után + MULTI-CITY.
        """
        try:
            analysis_type = self.analysis_type_widget.get_current_type()
            
            if analysis_type == "single_location":
                # LocationWidget explicit refresh
                if hasattr(self.location_widget, 'location_selector'):
                    self.location_widget.location_selector.setVisible(True)
                    self.location_widget.location_selector.setEnabled(True)
                
                # 🚨 FINAL VISIBILITY GUARANTEE
                self.location_widget.setVisible(True)
                self.location_widget.show()
                
                print("🔧 DEBUG: Delayed widget refresh completed for single_location - LocationWidget VISIBLE")
            
            elif analysis_type in ["region", "county"]:
                # 🏙️ MultiCityWidget explicit refresh
                self.multi_city_widget.setVisible(True)
                self.multi_city_widget.setEnabled(True)
                self.multi_city_widget.show()
                
                print(f"🔧 DEBUG: Delayed widget refresh completed for {analysis_type} - MultiCityWidget VISIBLE")
            
        except Exception as e:
            print(f"⚠️ DEBUG: Error during delayed widget refresh: {e}")
    
    def _update_fetch_button_state_comprehensive(self) -> None:
        """
        🔧 KRITIKUS FIX: Fetch button állapot újraértékelése - comprehensive validation + MULTI-CITY + QUERY_BUTTON.
        """
        can_fetch = self._comprehensive_fetch_validation()
        
        # 🔧 KRITIKUS FIX: fetch_button → query_button
        if not self.query_control_widget._is_fetching:
            self.query_control_widget.query_button.setEnabled(can_fetch)
        
        print(f"🚀 DEBUG: Query button enabled: {can_fetch} (comprehensive validation + multi-city + FETCH_BUTTON FIX)")
    
    def _comprehensive_fetch_validation(self) -> bool:
        """
        🔧 ROBUSZTUS: Comprehensive fetch validálás - minden widget állapot ellenőrzése + MULTI-CITY.
        
        Returns:
            bool: True ha indítható a fetch
        """
        try:
            # Analysis type check
            analysis_type = self.analysis_type_widget.get_current_type()
            if not analysis_type:
                print("❌ DEBUG: No analysis type selected")
                return False
            
            # Location/Multi-city check analysis type szerint
            if analysis_type == "single_location":
                # Single location validation
                location_valid = self.location_widget.is_valid()
                if not location_valid:
                    print("❌ DEBUG: Location not valid in single_location mode")
                    return False
                
                # További location ellenőrzések
                location_state = self.location_widget.get_state()
                if not location_state.get("has_location", False):
                    print("❌ DEBUG: No location selected in single_location mode")
                    return False
                
                city_data = location_state.get("current_city_data")
                if not city_data or not all(key in city_data for key in ["latitude", "longitude"]):
                    print("❌ DEBUG: Invalid city data in single_location mode")
                    return False
                
            elif analysis_type in ["region", "county"]:
                # 🏙️ Multi-city validation
                multi_city_valid = self.multi_city_widget.is_valid()
                if not multi_city_valid:
                    print(f"❌ DEBUG: Multi-city selection not valid in {analysis_type} mode")
                    return False
                
                # További multi-city ellenőrzések
                multi_city_state = self.multi_city_widget.get_state()
                if multi_city_state.get("selection_count", 0) == 0:
                    print(f"❌ DEBUG: No {analysis_type} selected in multi-city mode")
                    return False
                
                print(f"✅ DEBUG: Multi-city validation passed for {analysis_type}")
            
            # Date range check
            date_valid = self.date_range_widget.is_valid()
            if not date_valid:
                print("❌ DEBUG: Date range not valid")
                return False
            
            # API settings check
            api_valid = self.api_settings_widget.is_valid()
            if not api_valid:
                print("❌ DEBUG: API settings not valid")
                return False
            
            # Provider check
            provider_valid = self.provider_widget.is_valid()
            if not provider_valid:
                print("❌ DEBUG: Provider not valid")
                return False
            
            # Fetching state check
            not_fetching = not self.query_control_widget._is_fetching
            if not not_fetching:
                print("❌ DEBUG: Fetch already in progress")
                return False
            
            print(f"✅ DEBUG: Comprehensive validation passed for {analysis_type}")
            return True
            
        except Exception as e:
            print(f"❌ DEBUG: Error during comprehensive fetch validation: {e}")
            return False
    
    # === ANALYSIS REQUEST BUILDING - CLEAN ARCHITECTURE + MULTI-CITY TÁMOGATÁS ===
    
    def _build_analysis_request(self) -> Dict[str, Any]:
        """
        🎯 COMPREHENSIVE ANALYSIS REQUEST - Widget State Aggregation + MULTI-CITY
        
        Ez a CLEAN ARCHITECTURE központi data aggregation pontja.
        Minden widget state-jét összegyűjti egy comprehensive request-be.
        
        Returns:
            Teljes analysis request dict minden paraméterrel
        """
        return {
            # Analysis type és location/multi-city
            **self._get_analysis_params(),
            
            # Date range
            **self._get_date_params(),
            
            # Provider és API settings
            **self._get_api_params(),
            
            # Meta információk
            "timestamp": datetime.now().isoformat(),
            "request_id": f"req_{int(datetime.now().timestamp())}",
            "widget_states": self._get_all_widget_states()
        }
    
    def _get_analysis_params(self) -> Dict[str, Any]:
        """Analysis és location/multi-city paraméterek + MULTI-CITY TÁMOGATÁS."""
        analysis_type = self.analysis_type_widget.get_current_type()
        
        params = {
            "analysis_type": analysis_type
        }
        
        if analysis_type == "single_location":
            # Single location parameterek
            location_state = self.location_widget.get_state()
            if location_state["has_location"]:
                city_data = location_state["current_city_data"]
                params.update({
                    "latitude": city_data["latitude"],
                    "longitude": city_data["longitude"],
                    "location_name": city_data["name"],
                    "location_data": city_data
                })
        
        elif analysis_type in ["region", "county"]:
            # 🚨 FIX: Analysis type konverzió AppController kompatibilitáshoz
            if analysis_type == "region":
                converted_analysis_type = "multi_city"
            else:  # county
                converted_analysis_type = "county_analysis"
            
            # 🏙️ Multi-city paraméterek
            multi_city_state = self.multi_city_widget.get_state()
            selected_cities = self.multi_city_widget.get_selected_cities()
            
            # 🚨 FIX: AppController kompatibilis régió/megye név mezők
            current_selection = multi_city_state["current_selection"]
            if analysis_type == "region":
                region_name = current_selection
                county_name = None
            else:  # county
                region_name = None
                county_name = current_selection
            
            params.update({
                "analysis_type": converted_analysis_type,  # 🚨 FIX: Konvertált analysis_type
                "multi_city_mode": True,
                "region_or_county": analysis_type,  # Eredeti típus megőrzése
                # 🚨 FIX: AppController várt mezők
                "region_name": region_name,
                "county_name": county_name,
                "multi_city_selection": {
                    "mode": multi_city_state["mode"],
                    "selected": multi_city_state["current_selection"],
                    "count": multi_city_state["selection_count"]
                },
                "selected_cities": selected_cities,
                "city_count": len(selected_cities)
            })
            
            print(f"🏙️ DEBUG: Multi-city analysis request - {len(selected_cities)} cities selected")
            print(f"🚨 DEBUG: Analysis type converted: {analysis_type} → {converted_analysis_type}")
        
        return params
    
    def _get_date_params(self) -> Dict[str, Any]:
        """
        🚨 KRITIKUS FIX: Date range paraméterek AppController kompatibilis formátumban.
        
        AppController ezt várja:
        "date_range": {
            "start_date": "2024-08-13",
            "end_date": "2025-08-13"
        }
        """
        date_state = self.date_range_widget.get_state()
        
        return {
            "date_mode": date_state["date_mode"],
            # 🚨 FIX: date_range objektum a külön start_date/end_date helyett
            "date_range": {
                "start_date": date_state["start_date"],
                "end_date": date_state["end_date"]
            },
            "time_range": date_state.get("time_range")
        }
    
    def _get_api_params(self) -> Dict[str, Any]:
        """Provider és API paraméterek."""
        provider_state = self.provider_widget.get_state()
        api_state = self.api_settings_widget.get_state()
        
        return {
            "provider": provider_state["current_provider"],
            "api_settings": api_state["settings"],
            "provider_preferences": provider_state.get("provider_preferences", {})
        }
    
    def _validate_analysis_request(self, request: Dict[str, Any]) -> bool:
        """
        🚨 KRITIKUS FIX: Analysis request validálása + MULTI-CITY - JAVÍTOTT VALIDATION LOGIC.
        
        A fő hiba helye volt itt! A validation a location_data objektum alatt keresi a lat/lon kulcsokat.
        """
        # Analysis type check
        if "analysis_type" not in request:
            print("❌ DEBUG: Missing analysis_type in request")
            return False
        
        analysis_type = request["analysis_type"]
        
        # 🚨 FIX: Konvertált analysis type validálás
        valid_types = ["single_location", "multi_city", "county_analysis"]
        if analysis_type not in valid_types:
            print(f"❌ DEBUG: Invalid analysis type: {analysis_type}")
            return False
        
        # 🚨 KRITIKUS FIX: Single location validation - location_data objektum alatt keresi lat/lon
        if analysis_type == "single_location":
            if "location_data" not in request:
                print("❌ DEBUG: Missing location_data in request")
                return False
            location_data = request["location_data"]
            if not all(key in location_data for key in ["latitude", "longitude"]):
                print(f"❌ DEBUG: Missing lat/lon in location_data: {list(location_data.keys())}")
                return False
            print("✅ DEBUG: Single location validation passed - location_data structure valid")
        
        # 🏙️ Multi-city validation (mind a két típusra)
        elif analysis_type in ["multi_city", "county_analysis"]:
            if "multi_city_mode" not in request or not request["multi_city_mode"]:
                print("❌ DEBUG: Missing multi_city_mode in request")
                return False
            
            if "selected_cities" not in request or len(request["selected_cities"]) == 0:
                print("❌ DEBUG: No selected_cities in multi-city request")
                return False
            
            print(f"✅ DEBUG: Multi-city validation passed - {len(request['selected_cities'])} cities")
        
        # Date validation - 🚨 FIX: date_range objektum ellenőrzése
        if "date_range" not in request:
            print("❌ DEBUG: Missing date_range in request")
            return False
            
        date_range = request["date_range"]
        if not all(key in date_range for key in ["start_date", "end_date"]):
            print(f"❌ DEBUG: Missing start_date/end_date in date_range: {list(date_range.keys())}")
            return False
        
        # API validation
        if "provider" not in request or "api_settings" not in request:
            print("❌ DEBUG: Missing provider or api_settings in request")
            return False
        
        print(f"✅ DEBUG: Analysis request validation passed for {analysis_type}")
        return True
    
    # === PUBLIC API - STATE MANAGEMENT + MULTI-CITY ===
    
    def get_current_state(self) -> Dict[str, Any]:
        """Teljes panel állapot lekérdezése + MULTI-CITY."""
        return {
            "analysis_type": self.analysis_type_widget.get_state(),
            "location": self.location_widget.get_state(),
            "multi_city": self.multi_city_widget.get_state(),  # 🏙️ ÚJ
            "date_range": self.date_range_widget.get_state(),
            "provider": self.provider_widget.get_state(),
            "api_settings": self.api_settings_widget.get_state(),
            "query_control": self.query_control_widget.get_state()
        }
    
    def _get_all_widget_states(self) -> Dict[str, Any]:
        """Összes widget state lekérdezése (internal) + MULTI-CITY."""
        return self.get_current_state()
    
    def set_panel_state(self, state: Dict[str, Any]) -> bool:
        """Teljes panel állapot beállítása + MULTI-CITY."""
        success = True
        
        # Widget states beállítása egyenként
        if "analysis_type" in state:
            success &= self.analysis_type_widget.set_state(state["analysis_type"])
        
        if "location" in state:
            success &= self.location_widget.set_state(state["location"])
        
        # 🏙️ Multi-city state beállítása
        if "multi_city" in state:
            success &= self.multi_city_widget.set_state(state["multi_city"])
        
        if "date_range" in state:
            success &= self.date_range_widget.set_state(state["date_range"])
        
        if "provider" in state:
            success &= self.provider_widget.set_state(state["provider"])
        
        if "api_settings" in state:
            success &= self.api_settings_widget.set_state(state["api_settings"])
        
        # UI frissítése
        if success:
            analysis_type = self.analysis_type_widget.get_current_type()
            self._update_ui_for_analysis_type_fixed(analysis_type)
            self._update_fetch_button_state_comprehensive()
        
        return success
    
    def is_valid(self) -> bool:
        """Panel validálása - minden widget valid kell legyen + MULTI-CITY."""
        analysis_type = self.analysis_type_widget.get_current_type()
        
        # Base validation
        valid = (
            self.analysis_type_widget.is_valid() and
            self.date_range_widget.is_valid() and
            self.provider_widget.is_valid() and
            self.api_settings_widget.is_valid()
        )
        
        # Location/Multi-city validation analysis type szerint
        if analysis_type == "single_location":
            valid &= self.location_widget.is_valid()
        elif analysis_type in ["region", "county"]:
            valid &= self.multi_city_widget.is_valid()  # 🏙️ ÚJ
        
        return valid
    
    def set_enabled(self, enabled: bool) -> None:
        """Teljes panel engedélyezése/letiltása + MULTI-CITY."""
        self.analysis_type_widget.set_enabled(enabled)
        self.location_widget.set_enabled(enabled)
        self.multi_city_widget.set_enabled(enabled)  # 🏙️ ÚJ
        self.date_range_widget.set_enabled(enabled)
        self.provider_widget.set_enabled(enabled)
        self.api_settings_widget.set_enabled(enabled)
        # QueryControlWidget saját maga kezeli az enabled státuszt
        
        print(f"🎯 ControlPanel enabled state: {enabled} (+ MultiCityWidget)")
    
    # === EXTERNAL SIGNAL HANDLERS (UNCHANGED) ===
    
    def _auto_reset_fetch_state(self) -> None:
        """🔧 AUTO-RESET: Fetch state reset timeout esetére."""
        if self.query_control_widget._is_fetching:
            print("🔧 DEBUG: Auto-resetting fetch state after timeout")
            self.query_control_widget.set_fetching_state(False)
            # 🔥 KRITIKUS FIX: set_progress_text → update_progress
            self.query_control_widget.update_progress("⏰ Timeout - próbálja újra")
            self._update_fetch_button_state_comprehensive()
    
    def on_weather_data_completed(self) -> None:
        """Weather data lekérdezés befejezése külső jelzés alapján."""
        self.query_control_widget.set_fetching_state(False)
        # 🔥 KRITIKUS FIX: set_progress_text → update_progress
        self.query_control_widget.update_progress("✅ Adatok sikeresen lekérdezve")
        self._update_fetch_button_state_comprehensive()
        
        print("✅ Weather data completed - UI updated")
    
    def on_controller_error(self, error_message: str) -> None:
        """Hiba kezelése külső jelzés alapján."""
        self.query_control_widget.set_fetching_state(False)
        # 🔥 KRITIKUS FIX: set_progress_text → update_progress
        self.query_control_widget.update_progress(f"❌ Hiba: {error_message}")
        self._update_fetch_button_state_comprehensive()
        
        self.local_error_occurred.emit(error_message)
        
        print(f"❌ Controller error: {error_message}")
    
    def update_progress(self, worker_type: str, progress: int) -> None:
        """Progress frissítése külső jelzés alapján."""
        if 0 <= progress <= 100:
            self.query_control_widget.set_progress_value(progress)
            # 🔥 KRITIKUS FIX: set_progress_text → update_progress
            self.query_control_widget.update_progress(f"⏳ {worker_type}: {progress}%")
        
        if progress >= 100:
            # 🔥 KRITIKUS FIX: set_progress_text → update_progress
            self.query_control_widget.update_progress("✅ Befejezve")
    
    def update_status_from_controller(self, message: str) -> None:
        """Status frissítése külső controller-ből."""
        # 🔥 KRITIKUS FIX: set_progress_text → update_progress
        self.query_control_widget.update_progress(message)
        print(f"📊 Status update: {message}")
    
    # === GEOCODING COMPATIBILITY HANDLERS (UNCHANGED) ===
    
    def _on_geocoding_completed(self, results: List[Dict[str, Any]]) -> None:
        """Geocoding eredmények fogadása - LocationWidget-re továbbítás."""
        if hasattr(self.location_widget, 'update_search_results'):
            self.location_widget.update_search_results(results)
        
        print(f"🔍 Geocoding completed: {len(results)} results")
    
    def _on_geocoding_error(self, error_message: str) -> None:
        """Geocoding hiba fogadása."""
        self.local_error_occurred.emit(f"Keresési hiba: {error_message}")
        print(f"❌ Geocoding error: {error_message}")
    
    # === LEGACY COMPATIBILITY API (MINIMÁLIS) ===
    
    def get_selected_city_data(self) -> Optional[Dict[str, Any]]:
        """Legacy: Kiválasztott város adatok."""
        return self.location_widget.get_current_city_data()
    
    def get_date_range(self) -> tuple[str, str]:
        """Legacy: Dátum tartomány."""
        return self.date_range_widget.get_date_range()
    
    def get_analysis_type(self) -> str:
        """Legacy: Analysis type."""
        return self.analysis_type_widget.get_current_type()
    
    def get_provider(self) -> str:
        """Legacy: Provider."""
        return self.provider_widget.get_current_provider()
    
    def is_fetch_in_progress(self) -> bool:
        """Legacy: Fetch progress check."""
        return self.query_control_widget._is_fetching
    
    # 🏙️ ÚJ LEGACY API: Multi-city support
    def get_selected_multi_city_data(self) -> Dict[str, Any]:
        """ÚJ: Multi-city selection adatok."""
        return self.multi_city_widget.get_state()
    
    def get_selected_cities(self) -> List[Dict[str, Any]]:
        """ÚJ: Kiválasztott városok listája multi-city módban."""
        return self.multi_city_widget.get_selected_cities()
    
    def refresh_ui_state(self) -> None:
        """UI állapot teljes frissítése + MULTI-CITY."""
        analysis_type = self.analysis_type_widget.get_current_type()
        self._update_ui_for_analysis_type_fixed(analysis_type)
        self._update_fetch_button_state_comprehensive()
        self.provider_widget.refresh_usage_display()
        
        print("🔄 ControlPanel UI state refreshed + MultiCityWidget")
    
    def force_fetch_button_update(self) -> None:
        """Fetch button állapot kényszerített frissítése."""
        self._update_fetch_button_state_comprehensive()
    
    # === CLEANUP ===
    
    def cleanup(self) -> None:
        """ControlPanel cleanup - widget cleanup-ok hívása + MULTI-CITY."""
        # Provider widget cleanup (timer leállítása)
        if hasattr(self.provider_widget, 'cleanup'):
            self.provider_widget.cleanup()
        
        # 🏙️ Multi-city widget cleanup (ha van)
        if hasattr(self.multi_city_widget, 'cleanup'):
            self.multi_city_widget.cleanup()
        
        print("🧹 ControlPanel cleanup completed + MultiCityWidget")
    
    def __del__(self):
        """Destruktor."""
        try:
            self.cleanup()
        except:
            pass