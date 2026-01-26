#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Analysis Type Widget
Elemzési típus választó widget (Egyedi/Régió/Megye)

🎯 CLEAN ARCHITECTURE REFAKTOR - 1. LÉPÉS
Felelősség: CSAK az elemzési típus választás kezelése
- Single Responsibility: Csak analysis type selection
- Clean Interface: get_state(), set_state(), analysis_type_changed signal
- No Business Logic: Csak UI state management
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Signal

from ..theme_manager import get_theme_manager, register_widget_for_theming


class AnalysisTypeWidget(QWidget):
    """
    🎯 ELEMZÉSI TÍPUS VÁLASZTÓ WIDGET - CLEAN ARCHITECTURE
    
    Felelősség:
    - Analysis type radio buttonok (single_location/region/county)
    - State management és validation
    - Clean signal emission
    
    Interface:
    - analysis_type_changed = Signal(str) - kimenő signal
    - get_state() -> dict - aktuális állapot lekérdezése  
    - set_state(dict) - állapot beállítása
    - is_valid() -> bool - validáció
    """
    
    # === KIMENŐ SIGNAL ===
    analysis_type_changed = Signal(str)  # "single_location", "region", "county"
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        AnalysisTypeWidget inicializálása.
        
        Args:
            parent: Szülő widget
        """
        super().__init__(parent)
        
        # Theme manager
        self.theme_manager = get_theme_manager()
        
        # State
        self._current_type = "single_location"
        self._updating_state = False  # Signal loop prevention
        
        # UI init
        self._init_ui()
        self._connect_signals()
        self._register_for_theming()
        
        print("🎯 DEBUG: AnalysisTypeWidget inicializálva - Clean Architecture")
    
    def _init_ui(self) -> None:
        """UI elemek létrehozása."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Group box
        self.group = QGroupBox("🎯 Elemzési Típus")
        group_layout = QVBoxLayout(self.group)
        group_layout.setContentsMargins(12, 16, 12, 12)
        group_layout.setSpacing(12)
        
        # Radio button group
        self.button_group = QButtonGroup()
        
        # Single location radio
        self.single_location_radio = QRadioButton("📍 Egyedi lokáció elemzés")
        self.single_location_radio.setChecked(True)
        self.single_location_radio.setToolTip("Egy konkrét település részletes időjárási elemzése")
        self.single_location_radio.setMinimumHeight(24)
        self.button_group.addButton(self.single_location_radio, 0)
        group_layout.addWidget(self.single_location_radio)
        
        # Region radio
        self.region_radio = QRadioButton("🏞️ Régió elemzés (Multi-City)")
        self.region_radio.setToolTip("Magyar statisztikai régiók összehasonlító elemzése")
        self.region_radio.setMinimumHeight(24)
        self.button_group.addButton(self.region_radio, 1)
        group_layout.addWidget(self.region_radio)
        
        # County radio
        self.county_radio = QRadioButton("🏛️ Megye elemzés (Multi-City)")
        self.county_radio.setToolTip("Magyar megyék összehasonlító elemzése")
        self.county_radio.setMinimumHeight(24)
        self.button_group.addButton(self.county_radio, 2)
        group_layout.addWidget(self.county_radio)
        
        # Size constraints
        self.group.setMinimumHeight(110)
        self.group.setMaximumHeight(130)
        
        layout.addWidget(self.group)
    
    def _connect_signals(self) -> None:
        """Signal-slot kapcsolatok."""
        self.button_group.buttonClicked.connect(self._on_button_clicked)
    
    def _register_for_theming(self) -> None:
        """Theme manager regisztráció."""
        register_widget_for_theming(self, "container")
        register_widget_for_theming(self.group, "container")
        register_widget_for_theming(self.single_location_radio, "input")
        register_widget_for_theming(self.region_radio, "input")
        register_widget_for_theming(self.county_radio, "input")
    
    def _on_button_clicked(self, button) -> None:
        """Radio button click kezelése."""
        if self._updating_state:
            return
        
        # Új típus meghatározása
        if button == self.single_location_radio:
            new_type = "single_location"
        elif button == self.region_radio:
            new_type = "region" 
        elif button == self.county_radio:
            new_type = "county"
        else:
            return
        
        # State frissítése ha változott
        if new_type != self._current_type:
            old_type = self._current_type
            self._current_type = new_type
            
            print(f"🎯 DEBUG: Analysis type changed: {old_type} → {new_type}")
            
            # Signal kibocsátása
            self.analysis_type_changed.emit(new_type)
    
    # === PUBLIKUS INTERFACE ===
    
    def get_state(self) -> Dict[str, Any]:
        """
        Aktuális állapot lekérdezése.
        
        Returns:
            Dict az aktuális állapottal
        """
        return {
            "analysis_type": self._current_type,
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
        analysis_type = state.get("analysis_type")
        if not analysis_type or analysis_type not in ["single_location", "region", "county"]:
            print(f"❌ ERROR: Invalid analysis type in state: {analysis_type}")
            return False
        
        try:
            # Signal loop prevention
            self._updating_state = True
            
            # Radio button beállítása
            if analysis_type == "single_location":
                self.single_location_radio.setChecked(True)
            elif analysis_type == "region":
                self.region_radio.setChecked(True)
            elif analysis_type == "county":
                self.county_radio.setChecked(True)
            
            # State frissítése
            old_type = self._current_type
            self._current_type = analysis_type
            
            print(f"🎯 DEBUG: Analysis type set programmatically: {old_type} → {analysis_type}")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to set analysis type state: {e}")
            return False
        finally:
            self._updating_state = False
    
    def is_valid(self) -> bool:
        """
        Validáció - analysis type widget mindig valid.
        
        Returns:
            bool: Mindig True (valamelyik radio mindig be van jelölve)
        """
        return True
    
    def get_current_type(self) -> str:
        """
        Aktuális elemzési típus lekérdezése.
        
        Returns:
            str: "single_location", "region", vagy "county"
        """
        return self._current_type
    
    def set_current_type(self, analysis_type: str) -> bool:
        """
        Elemzési típus programozott beállítása.
        
        Args:
            analysis_type: Beállítandó típus
            
        Returns:
            bool: Sikeres volt-e
        """
        return self.set_state({"analysis_type": analysis_type})
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Widget engedélyezése/letiltása.
        
        Args:
            enabled: Engedélyezett állapot
        """
        self.group.setEnabled(enabled)
        self.single_location_radio.setEnabled(enabled)
        self.region_radio.setEnabled(enabled)
        self.county_radio.setEnabled(enabled)
        
        print(f"🎯 DEBUG: AnalysisTypeWidget enabled state: {enabled}")
    
    # === SIZE HINT ===
    
    def sizeHint(self):
        """Preferált méret."""
        return self.group.sizeHint()
    
    def minimumSizeHint(self):
        """Minimum méret."""
        return self.group.minimumSizeHint()