#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Location Widget
Lokáció választó widget (UniversalLocationSelector wrapper)

🎯 CLEAN ARCHITECTURE REFAKTOR - 2. LÉPÉS
Felelősség: CSAK a lokáció választás kezelése single_location módban
- Single Responsibility: Csak location selection
- Clean Interface: get_state(), set_state(), location_changed signal
- UniversalLocationSelector wrapper funkcionalitás
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

# 🔧 JAVÍTOTT IMPORT - Helyes útvonal!
from ..universal_location_selector import UniversalLocationSelector
from ..theme_manager import get_theme_manager, register_widget_for_theming
from ...data.city_manager import CityManager
from ...data.models import UniversalLocation


class LocationWidget(QWidget):
    """
    🌍 LOKÁCIÓ VÁLASZTÓ WIDGET - CLEAN ARCHITECTURE
    
    Felelősség:
    - UniversalLocationSelector wrapper
    - Current location state management
    - Search és selection signal továbbítása
    - Location info display és clear funkcionalitás
    
    Interface:
    - search_requested = Signal(str) - keresési kérés
    - location_changed = Signal(object) - UniversalLocation változás
    - city_selected = Signal(str, float, float, dict) - compatibility signal
    - get_state() -> dict - aktuális állapot
    - set_state(dict) - állapot beállítása
    - is_valid() -> bool - van-e kiválasztott lokáció
    """
    
    # === KIMENŐ SIGNALOK ===
    search_requested = Signal(str)  # search_query
    location_changed = Signal(object)  # UniversalLocation object
    city_selected = Signal(str, float, float, dict)  # name, lat, lon, metadata (compatibility)
    
    def __init__(self, city_manager: CityManager, parent: Optional[QWidget] = None):
        """
        LocationWidget inicializálása.
        
        Args:
            city_manager: CityManager instance
            parent: Szülő widget
        """
        super().__init__(parent)
        
        # Dependencies
        self.city_manager = city_manager
        self.theme_manager = get_theme_manager()
        
        # State
        self.current_location: Optional[UniversalLocation] = None
        self.current_city_data: Optional[Dict[str, Any]] = None
        self._updating_state = False
        
        # UI init
        self._init_ui()
        self._connect_signals()
        self._register_for_theming()
        
        print("🌍 DEBUG: LocationWidget inicializálva - Clean Architecture")
    
    def _init_ui(self) -> None:
        """UI elemek létrehozása."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Group box
        self.group = QGroupBox("🌍 Lokáció Választó")
        group_layout = QVBoxLayout(self.group)
        group_layout.setContentsMargins(12, 16, 12, 12)
        group_layout.setSpacing(12)
        
        # UniversalLocationSelector
        self.location_selector = UniversalLocationSelector(self.city_manager, self)
        self.location_selector.setMinimumHeight(420)
        self.location_selector.setMaximumHeight(500)
        group_layout.addWidget(self.location_selector)
        
        # Location info és clear gomb
        info_layout = QHBoxLayout()
        info_layout.setSpacing(8)
        
        # Info label
        self.info_label = QLabel("Válasszon lokációt...")
        self.info_label.setWordWrap(True)
        self.info_label.setMinimumHeight(40)
        info_layout.addWidget(self.info_label)
        
        # Clear button
        self.clear_btn = QPushButton("🗑️")
        self.clear_btn.clicked.connect(self._clear_location)
        self.clear_btn.setEnabled(False)
        self.clear_btn.setFixedSize(32, 32)
        self.clear_btn.setToolTip("Lokáció törlése")
        info_layout.addWidget(self.clear_btn)
        
        group_layout.addLayout(info_layout)
        
        # Size constraints
        self.group.setMinimumHeight(500)
        self.group.setMaximumHeight(580)
        
        layout.addWidget(self.group)
    
    def _connect_signals(self) -> None:
        """Signal-slot kapcsolatok."""
        # UniversalLocationSelector signalok
        self.location_selector.search_requested.connect(self._on_search_requested)
        self.location_selector.city_selected.connect(self._on_city_selected)
        self.location_selector.location_changed.connect(self._on_location_changed)
    
    def _register_for_theming(self) -> None:
        """Theme manager regisztráció."""
        register_widget_for_theming(self, "container")
        register_widget_for_theming(self.group, "container")
        register_widget_for_theming(self.location_selector, "container")
        register_widget_for_theming(self.clear_btn, "button")
        
        # Info label styling
        self._apply_label_styling(self.info_label, "secondary")
    
    def _apply_label_styling(self, label: QLabel, style_type: str) -> None:
        """Label styling alkalmazása."""
        color_palette = self.theme_manager.get_color_scheme()
        if not color_palette:
            return
        
        if style_type == "secondary":
            color = color_palette.get_color("info", "light") or "#9ca3af"
            font_size = "11px"
        elif style_type == "primary":
            color = color_palette.get_color("primary", "base") or "#2563eb"
            font_size = "12px"
        else:
            return
        
        css = f"QLabel {{ color: {color}; font-size: {font_size}; }}"
        label.setStyleSheet(css)
        
        register_widget_for_theming(label, "text")
    
    # === SIGNAL HANDLERS ===
    
    def _on_search_requested(self, query: str) -> None:
        """Keresési kérés továbbítása."""
        print(f"🔍 DEBUG: LocationWidget search requested: {query}")
        self.search_requested.emit(query)
    
    def _on_city_selected(self, name: str, lat: float, lon: float, data: Dict[str, Any]) -> None:
        """City selection kezelése."""
        if self._updating_state:
            return
        
        try:
            print(f"🏙️ DEBUG: LocationWidget city selected: {name} [{lat:.4f}, {lon:.4f}]")
            
            # State frissítése
            self.current_city_data = {
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "display_name": name,
                **data
            }
            
            # UI frissítése
            self._update_location_info(name, lat, lon)
            self.clear_btn.setEnabled(True)
            
            # Signal továbbítása (compatibility)
            self.city_selected.emit(name, lat, lon, data)
            
            print(f"✅ DEBUG: LocationWidget city selection processed: {name}")
            
        except Exception as e:
            print(f"❌ ERROR: LocationWidget city selection error: {e}")
    
    def _on_location_changed(self, location: UniversalLocation) -> None:
        """UniversalLocation változás kezelése."""
        if self._updating_state:
            return
        
        try:
            print(f"🌍 DEBUG: LocationWidget location changed: {location}")
            
            # State frissítése
            self.current_location = location
            
            # current_city_data frissítése UniversalLocation-ből
            if hasattr(location, 'identifier') and hasattr(location, 'coordinates'):
                self.current_city_data = {
                    "name": location.identifier,
                    "latitude": location.coordinates[0],
                    "longitude": location.coordinates[1],
                    "display_name": getattr(location, 'display_name', location.identifier),
                    "location_type": getattr(location, 'type', 'city'),
                    "country": getattr(location, 'country', ''),
                    "region": getattr(location, 'region', '')
                }
                
                # UI frissítése
                self._update_location_info(
                    location.identifier, 
                    location.coordinates[0], 
                    location.coordinates[1]
                )
                self.clear_btn.setEnabled(True)
            
            # Signal továbbítása
            self.location_changed.emit(location)
            
            print(f"✅ DEBUG: LocationWidget location change processed: {location.identifier}")
            
        except Exception as e:
            print(f"❌ ERROR: LocationWidget location change error: {e}")
    
    def _clear_location(self) -> None:
        """Lokáció törlése."""
        if self._updating_state:
            return
        
        try:
            print("🗑️ DEBUG: LocationWidget clear location")
            
            # UniversalLocationSelector törlése
            self.location_selector.clear_selection()
            
            # State törlése
            self.current_location = None
            self.current_city_data = None
            
            # UI reset
            self.info_label.setText("Válasszon lokációt...")
            self._apply_label_styling(self.info_label, "secondary")
            self.clear_btn.setEnabled(False)
            
            print("✅ DEBUG: LocationWidget location cleared")
            
        except Exception as e:
            print(f"❌ ERROR: LocationWidget clear error: {e}")
    
    def _update_location_info(self, name: str, lat: float, lon: float) -> None:
        """Lokáció info frissítése."""
        info_text = f"🏙️ {name}\n🗺️ Koordináták: [{lat:.4f}, {lon:.4f}]"
        self.info_label.setText(info_text)
        self._apply_label_styling(self.info_label, "primary")
    
    # === 🔧 REFRESH/REAKTIVÁLÁS METÓDUSOK ===
    
    def refresh_ui(self) -> None:
        """UI teljes frissítése - REAKTIVÁLÁS TÁMOGATÁS."""
        print("🔄 DEBUG: LocationWidget refresh_ui() called")
        
        try:
            # Widget enabled state check
            self.group.setEnabled(True)
            self.location_selector.setEnabled(True)
            
            # UniversalLocationSelector refresh
            if hasattr(self.location_selector, 'refresh_ui'):
                self.location_selector.refresh_ui()
            
            # State validation
            if self.current_city_data:
                name = self.current_city_data.get("name", "Unknown")
                lat = self.current_city_data.get("latitude", 0.0)
                lon = self.current_city_data.get("longitude", 0.0)
                self._update_location_info(name, lat, lon)
                self.clear_btn.setEnabled(True)
            else:
                self.info_label.setText("Válasszon lokációt...")
                self._apply_label_styling(self.info_label, "secondary")
                self.clear_btn.setEnabled(False)
            
            print("✅ DEBUG: LocationWidget refresh_ui() completed")
            
        except Exception as e:
            print(f"❌ ERROR: LocationWidget refresh_ui() error: {e}")
    
    def force_refresh(self) -> None:
        """Kényszerített refresh - WIDGET REAKTIVÁLÁS."""
        print("⚡ DEBUG: LocationWidget force_refresh() called")
        
        try:
            # Explicit enable cascade
            self.setEnabled(True)
            self.group.setEnabled(True)
            
            # UniversalLocationSelector force refresh
            if hasattr(self.location_selector, 'force_refresh'):
                self.location_selector.force_refresh()
            elif hasattr(self.location_selector, 'refresh_ui'):
                self.location_selector.refresh_ui()
            
            # Layout frissítés
            self.updateGeometry()
            self.update()
            
            print("✅ DEBUG: LocationWidget force_refresh() completed")
            
        except Exception as e:
            print(f"❌ ERROR: LocationWidget force_refresh() error: {e}")
    
    # === PUBLIKUS INTERFACE ===
    
    def get_state(self) -> Dict[str, Any]:
        """
        Aktuális állapot lekérdezése.
        
        Returns:
            Dict az aktuális állapottal
        """
        return {
            "current_location": self.current_location,
            "current_city_data": self.current_city_data,
            "has_location": self.current_city_data is not None,
            "is_valid": self.is_valid()
        }
    
    def set_state(self, state: Dict[str, Any]) -> bool:
        """
        Állapot beállítása.
        
        Args:
            state: Beállítandó állapot dict
            
        Returns:
            bool: Sikeres volt-e a beállítás
        """
        try:
            self._updating_state = True
            
            # Location data beállítása
            city_data = state.get("current_city_data")
            if city_data:
                self.current_city_data = city_data
                self._update_location_info(
                    city_data.get("name", "Unknown"),
                    city_data.get("latitude", 0.0),
                    city_data.get("longitude", 0.0)
                )
                self.clear_btn.setEnabled(True)
            else:
                self.current_city_data = None
                self.info_label.setText("Válasszon lokációt...")
                self._apply_label_styling(self.info_label, "secondary")
                self.clear_btn.setEnabled(False)
            
            # UniversalLocation beállítása
            location = state.get("current_location")
            if location:
                self.current_location = location
            
            print(f"✅ DEBUG: LocationWidget state set successfully")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to set LocationWidget state: {e}")
            return False
        finally:
            self._updating_state = False
    
    def is_valid(self) -> bool:
        """
        Validáció - van-e kiválasztott lokáció.
        
        Returns:
            bool: True ha van kiválasztott lokáció
        """
        return self.current_city_data is not None
    
    def clear_selection(self) -> None:
        """Lokáció kiválasztás törlése."""
        self._clear_location()
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Widget engedélyezése/letiltása.
        
        Args:
            enabled: Engedélyezett állapot
        """
        self.group.setEnabled(enabled)
        self.location_selector.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled and self.current_city_data is not None)
        
        print(f"🌍 DEBUG: LocationWidget enabled state: {enabled}")
    
    def get_current_city_data(self) -> Optional[Dict[str, Any]]:
        """Aktuális city data lekérdezése (compatibility)."""
        return self.current_city_data
    
    def get_current_location(self) -> Optional[UniversalLocation]:
        """Aktuális UniversalLocation lekérdezése."""
        return self.current_location
    
    def update_search_results(self, results) -> None:
        """Search results frissítése (compatibility)."""
        if hasattr(self.location_selector, 'update_search_results'):
            self.location_selector.update_search_results(results)
    
    # === SIZE HINT ===
    
    def sizeHint(self):
        """Preferált méret."""
        return self.group.sizeHint()
    
    def minimumSizeHint(self):
        """Minimum méret."""
        return self.group.minimumSizeHint()