#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Multi-City Widget
Magyar Régiók és Megyék választó widget (Analysis type alapú) - DROPDOWN verzió

🎯 CLEAN ARCHITECTURE REFAKTOR - MULTI-CITY TÁMOGATÁS - DROPDOWN UI
Felelősség: CSAK a régió/megye választás kezelése multi-city módban
- Single Responsibility: Csak multi-city location selection
- Clean Interface: get_state(), set_state(), selection_changed signal
- Analysis type alapú mode váltás (region vs county)
- DROPDOWN UI: QComboBox egyszerű választással
- 🚨 FIX: ComboBox inicializálási probléma javítva
"""

from typing import Optional, Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, 
    QPushButton, QLabel
)
from PySide6.QtCore import Signal, Qt

from ..theme_manager import get_theme_manager, register_widget_for_theming
from src.data.city_manager import CityManager


class MultiCityWidget(QWidget):
    """
    🏙️ MULTI-CITY VÁLASZTÓ WIDGET - DROPDOWN VERSION
    
    Felelősség:
    - Magyar régiók/megyék dropdown választás (QComboBox)
    - Analysis type alapú mode váltás (region vs county)
    - Single selection state management
    - Selection info display (pl. "Közép-Magyarország (2 megye)")
    
    Interface:
    - selection_changed = Signal(dict) - kiválasztás változás
    - get_state() -> dict - aktuális állapot
    - set_state(dict) - állapot beállítása
    - is_valid() -> bool - van-e kiválasztás
    - set_analysis_mode(str) - "region" vagy "county" mode
    """
    
    # === KIMENŐ SIGNAL ===
    selection_changed = Signal(dict)  # {"mode": "region", "selected": "Közép-Magyarország", "is_valid": True}
    
    def __init__(self, city_manager: CityManager, parent: Optional[QWidget] = None):
        """
        MultiCityWidget inicializálása.
        
        Args:
            city_manager: CityManager instance (magyar adatok lekérdezéshez)
            parent: Szülő widget
        """
        super().__init__(parent)
        
        # Dependencies
        self.city_manager = city_manager
        self.theme_manager = get_theme_manager()
        
        # State
        self._current_mode = "region"  # "region" vagy "county"
        self._selected_region: Optional[str] = None
        self._selected_county: Optional[str] = None
        self._updating_state = False
        
        # Data sources
        self._available_regions = self._get_hungarian_regions()
        self._available_counties = []  # Betöltjük később
        
        # UI init
        self._init_ui()
        self._load_data()
        self._connect_signals()
        self._register_for_theming()
        
        # 🚨 KRITIKUS FIX: ComboBox inicializálása RÖGTÖN!
        self._populate_combo_box()
        self._update_group_title()
        self._update_info_label()
        
        print("🏙️ DEBUG: MultiCityWidget (DROPDOWN) inicializálva - Clean Architecture + COMBO FIX")
    
    def _init_ui(self) -> None:
        """UI elemek létrehozása - DROPDOWN VERSION."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Group box
        self.group = QGroupBox("🏙️ Multi-City Választó")
        group_layout = QVBoxLayout(self.group)
        group_layout.setContentsMargins(12, 16, 12, 12)
        group_layout.setSpacing(12)
        
        # Dropdown combo box
        self.combo_box = QComboBox()
        self.combo_box.setMinimumHeight(35)
        self.combo_box.setEditable(False)
        # 🚨 FIX: ComboBox ENABLED állapotban kell legyen!
        self.combo_box.setEnabled(True)
        group_layout.addWidget(self.combo_box)
        
        # Selection info label
        self.info_label = QLabel("Válasszon régiót vagy megyét...")
        self.info_label.setWordWrap(True)
        self.info_label.setMinimumHeight(40)
        group_layout.addWidget(self.info_label)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)
        
        self.clear_btn = QPushButton("❌ Választás törlése")
        self.clear_btn.clicked.connect(self._clear_selection)
        self.clear_btn.setEnabled(False)
        control_layout.addWidget(self.clear_btn)
        
        # Spacer
        control_layout.addStretch()
        
        group_layout.addLayout(control_layout)
        
        # Size constraints
        self.group.setMinimumHeight(150)
        self.group.setMaximumHeight(180)
        
        layout.addWidget(self.group)
    
    def _load_data(self) -> None:
        """Magyar régiók és megyék adatainak betöltése."""
        try:
            # Megyék betöltése city_manager-ből
            self._available_counties = self.city_manager.get_hungarian_counties()
            print(f"🏛️ DEBUG: Betöltött megyék: {len(self._available_counties)} db")
            print(f"📋 DEBUG: Megyék listája: {self._available_counties[:5]}...")  # Első 5
            
        except Exception as e:
            print(f"❌ ERROR: Adatok betöltési hiba: {e}")
            self._available_counties = []
    
    def _get_hungarian_regions(self) -> List[str]:
        """
        Magyar NUTS régiók listája (hungarian_settlements_importer.py alapján).
        
        Returns:
            7 magyar statisztikai régió listája
        """
        return [
            "Közép-Magyarország",     # Budapest + Pest
            "Közép-Dunántúl",         # Fejér + Komárom-Esztergom + Veszprém
            "Nyugat-Dunántúl",        # Győr-Moson-Sopron + Vas + Zala
            "Dél-Dunántúl",           # Baranya + Somogy + Tolna
            "Észak-Magyarország",     # Borsod-Abaúj-Zemplén + Heves + Nógrád
            "Észak-Alföld",           # Hajdú-Bihar + Jász-Nagykun-Szolnok + Szabolcs-Szatmár-Bereg
            "Dél-Alföld"              # Bács-Kiskun + Békés + Csongrád-Csanád
        ]
    
    def _get_counties_for_region(self, region: str) -> List[str]:
        """
        Régióhoz tartozó megyék listája (hungarian_settlements_importer.py alapján).
        
        Args:
            region: Régió neve
            
        Returns:
            Megyék listája
        """
        region_county_mapping = {
            "Közép-Magyarország": ["Budapest", "Pest"],
            "Közép-Dunántúl": ["Fejér", "Komárom-Esztergom", "Veszprém"],
            "Nyugat-Dunántúl": ["Győr-Moson-Sopron", "Vas", "Zala"],
            "Dél-Dunántúl": ["Baranya", "Somogy", "Tolna"],
            "Észak-Magyarország": ["Borsod-Abaúj-Zemplén", "Heves", "Nógrád"],
            "Észak-Alföld": ["Hajdú-Bihar", "Jász-Nagykun-Szolnok", "Szabolcs-Szatmár-Bereg"],
            "Dél-Alföld": ["Bács-Kiskun", "Békés", "Csongrád-Csanád"]
        }
        
        return region_county_mapping.get(region, [])
    
    def _connect_signals(self) -> None:
        """Signal-slot kapcsolatok."""
        self.combo_box.currentTextChanged.connect(self._on_combo_selection_changed)
    
    def _register_for_theming(self) -> None:
        """Theme manager regisztráció."""
        register_widget_for_theming(self, "container")
        register_widget_for_theming(self.group, "container")
        register_widget_for_theming(self.combo_box, "input")
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
    
    # === ANALYSIS MODE MANAGEMENT ===
    
    def set_analysis_mode(self, mode: str) -> None:
        """
        Analysis mode beállítása.
        
        Args:
            mode: "region" vagy "county"
        """
        if mode not in ["region", "county"]:
            print(f"❌ ERROR: Invalid analysis mode: {mode}")
            return
        
        if mode == self._current_mode:
            print(f"🔄 DEBUG: Mode already set to {mode}, skipping...")
            return  # Nincs változás
        
        print(f"🔄 DEBUG: Analysis mode váltás: {self._current_mode} → {mode}")
        
        self._current_mode = mode
        self._populate_combo_box()
        self._update_group_title()
        self._update_info_label()
        
        print(f"✅ DEBUG: Analysis mode váltás befejezve: {mode}")
    
    def _populate_combo_box(self) -> None:
        """
        🚨 KRITIKUS FIX: ComboBox feltöltése aktuális mode alapján.
        Most már biztosan hívódik inicializáláskor is!
        """
        print(f"🔄 DEBUG: _populate_combo_box() started - mode: {self._current_mode}")
        
        self._updating_state = True
        
        try:
            self.combo_box.clear()
            
            # Első elem: placeholder
            if self._current_mode == "region":
                self.combo_box.addItem("-- Válasszon régiót --")
                
                # Régiók hozzáadása
                for region in self._available_regions:
                    counties = self._get_counties_for_region(region)
                    item_text = f"{region} ({len(counties)} megye)"
                    self.combo_box.addItem(item_text, region)  # userData = region név
                
                print(f"🏞️ DEBUG: ComboBox feltöltve {len(self._available_regions)} régióval")
                
            elif self._current_mode == "county":
                self.combo_box.addItem("-- Válasszon megyét --")
                
                # Megyék hozzáadása
                for county in self._available_counties:
                    item_text = f"{county} megye"
                    self.combo_box.addItem(item_text, county)  # userData = county név
                
                print(f"🏛️ DEBUG: ComboBox feltöltve {len(self._available_counties)} megyével")
            
            # 🚨 KRITIKUS FIX: ComboBox ENABLED állapot biztosítása
            self.combo_box.setEnabled(True)
            print(f"✅ DEBUG: ComboBox enabled state: {self.combo_box.isEnabled()}")
            
            # State restoration
            self._restore_selection_after_populate()
            
        except Exception as e:
            print(f"❌ ERROR: ComboBox populate hiba: {e}")
        finally:
            self._updating_state = False
            print(f"✅ DEBUG: _populate_combo_box() completed")
    
    def _restore_selection_after_populate(self) -> None:
        """Selection visszaállítása combo box populate után."""
        if self._current_mode == "region" and self._selected_region:
            # Régió keresése és beállítása
            for i in range(1, self.combo_box.count()):  # Skip placeholder (index 0)
                if self.combo_box.itemData(i) == self._selected_region:
                    self.combo_box.setCurrentIndex(i)
                    print(f"🔄 DEBUG: Régió visszaállítva: {self._selected_region}")
                    break
        
        elif self._current_mode == "county" and self._selected_county:
            # Megye keresése és beállítása
            for i in range(1, self.combo_box.count()):  # Skip placeholder (index 0)
                if self.combo_box.itemData(i) == self._selected_county:
                    self.combo_box.setCurrentIndex(i)
                    print(f"🔄 DEBUG: Megye visszaállítva: {self._selected_county}")
                    break
    
    def _update_group_title(self) -> None:
        """Group box title frissítése mode szerint."""
        if self._current_mode == "region":
            self.group.setTitle("🏞️ Régió Választó (Multi-City)")
        else:
            self.group.setTitle("🏛️ Megye Választó (Multi-City)")
    
    # === COMBO BOX SIGNAL HANDLER ===
    
    def _on_combo_selection_changed(self, text: str) -> None:
        """ComboBox selection változás kezelése."""
        if self._updating_state:
            print(f"⏸️ DEBUG: Skipping combo change (updating state): {text}")
            return
        
        current_index = self.combo_box.currentIndex()
        print(f"🔄 DEBUG: Combo selection changed - index: {current_index}, text: '{text}'")
        
        # Placeholder választás (index 0) - törlés
        if current_index == 0:
            print(f"🔄 DEBUG: Placeholder selected - clearing selection")
            self._clear_current_selection()
            return
        
        # Érvényes választás
        selected_data = self.combo_box.currentData()
        print(f"✅ DEBUG: Valid selection - data: {selected_data}")
        
        if self._current_mode == "region":
            self._selected_region = selected_data
            self._selected_county = None  # Clear other mode
            print(f"🏞️ DEBUG: Régió kiválasztva: {self._selected_region}")
            
        elif self._current_mode == "county":
            self._selected_county = selected_data
            self._selected_region = None  # Clear other mode
            print(f"🏛️ DEBUG: Megye kiválasztva: {self._selected_county}")
        
        self._update_info_label()
        self._update_clear_button()
        self._emit_selection_changed()
    
    def _clear_current_selection(self) -> None:
        """Aktuális mode selection törlése."""
        if self._current_mode == "region":
            self._selected_region = None
            print(f"🏞️ DEBUG: Régió selection törölve")
        else:
            self._selected_county = None
            print(f"🏛️ DEBUG: Megye selection törölve")
        
        self._update_info_label()
        self._update_clear_button()
        self._emit_selection_changed()
    
    def _emit_selection_changed(self) -> None:
        """Selection changed signal kibocsátása."""
        current_selection = self._get_current_selection()
        
        selection_data = {
            "mode": self._current_mode,
            "selected": current_selection,
            "is_valid": self.is_valid(),
            "selection_text": self._get_selection_display_text()
        }
        
        self.selection_changed.emit(selection_data)
        print(f"📡 DEBUG: selection_changed signal emitted: {selection_data}")
    
    def _get_current_selection(self) -> Optional[str]:
        """Aktuális kiválasztás lekérdezése mode szerint."""
        if self._current_mode == "region":
            return self._selected_region
        else:
            return self._selected_county
    
    def _get_selection_display_text(self) -> str:
        """Kiválasztás megjelenítési szövege."""
        if self._current_mode == "region" and self._selected_region:
            counties = self._get_counties_for_region(self._selected_region)
            return f"{self._selected_region} ({len(counties)} megye)"
        elif self._current_mode == "county" and self._selected_county:
            return f"{self._selected_county} megye"
        else:
            return ""
    
    def _update_info_label(self) -> None:
        """Info label frissítése."""
        current_selection = self._get_current_selection()
        
        if not current_selection:
            if self._current_mode == "region":
                text = "Válasszon régiót az elemzéshez..."
            else:
                text = "Válasszon megyét az elemzéshez..."
            self._apply_label_styling(self.info_label, "secondary")
        else:
            display_text = self._get_selection_display_text()
            
            if self._current_mode == "region":
                text = f"🏞️ Kiválasztott régió: {display_text}"
            else:
                text = f"🏛️ Kiválasztott megye: {display_text}"
            
            self._apply_label_styling(self.info_label, "primary")
        
        self.info_label.setText(text)
    
    def _update_clear_button(self) -> None:
        """Clear button állapot frissítése."""
        has_selection = self._get_current_selection() is not None
        self.clear_btn.setEnabled(has_selection)
    
    # === CONTROL BUTTON HANDLERS ===
    
    def _clear_selection(self) -> None:
        """Kiválasztás törlése."""
        if self._updating_state:
            return
        
        print(f"❌ DEBUG: Selection törlése - {self._current_mode} mode")
        
        self._updating_state = True
        
        try:
            # ComboBox-ot placeholder-re állítás
            self.combo_box.setCurrentIndex(0)
            
            # State törlése
            self._clear_current_selection()
            
        finally:
            self._updating_state = False
    
    # === PUBLIKUS INTERFACE ===
    
    def get_state(self) -> Dict[str, Any]:
        """
        Aktuális állapot lekérdezése.
        
        Returns:
            Dict az aktuális állapottal
        """
        current_selection = self._get_current_selection()
        
        return {
            "mode": self._current_mode,
            "selected_region": self._selected_region,
            "selected_county": self._selected_county,
            "current_selection": current_selection,
            "selection_count": 1 if current_selection else 0,
            "is_valid": self.is_valid(),
            "selection_text": self._get_selection_display_text()
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
            
            # Mode beállítása
            mode = state.get("mode", "region")
            if mode != self._current_mode:
                self.set_analysis_mode(mode)
            
            # Selections restoration
            if "selected_region" in state:
                self._selected_region = state["selected_region"]
            
            if "selected_county" in state:
                self._selected_county = state["selected_county"]
            
            # ComboBox frissítése
            self._restore_selection_after_populate()
            self._update_info_label()
            self._update_clear_button()
            
            print(f"✅ DEBUG: MultiCityWidget state restored successfully")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to set MultiCityWidget state: {e}")
            return False
        finally:
            self._updating_state = False
    
    def is_valid(self) -> bool:
        """
        Validáció - van-e kiválasztás.
        
        Returns:
            bool: True ha van kiválasztás
        """
        return self._get_current_selection() is not None
    
    def clear_selection(self) -> None:
        """Kiválasztás törlése."""
        self._clear_selection()
    
    def get_selected_cities(self) -> List[Dict[str, Any]]:
        """
        Kiválasztott régió/megye városainak lekérdezése.
        
        Returns:
            Városok listája koordinátákkal
        """
        cities = []
        current_selection = self._get_current_selection()
        
        if not current_selection:
            return cities
        
        try:
            if self._current_mode == "region":
                # Régió esetén a régióhoz tartozó megyék városai
                counties = self._get_counties_for_region(current_selection)
                for county in counties:
                    county_cities = self.city_manager.get_hungarian_settlements_by_county(county, limit=50)
                    cities.extend([city.to_dict() for city in county_cities])
            
            else:
                # Megye esetén közvetlenül
                county_cities = self.city_manager.get_hungarian_settlements_by_county(current_selection, limit=50)
                cities.extend([city.to_dict() for city in county_cities])
            
            print(f"🏙️ DEBUG: Kiválasztott városok: {len(cities)} db ({self._current_mode}: {current_selection})")
            return cities
            
        except Exception as e:
            print(f"❌ ERROR: Cities lekérdezési hiba: {e}")
            return []
    
    def get_current_mode(self) -> str:
        """Aktuális mode lekérdezése."""
        return self._current_mode
    
    def get_selection_summary(self) -> str:
        """Kiválasztás összefoglalása string formában."""
        current_selection = self._get_current_selection()
        
        if not current_selection:
            return "Nincs kiválasztás"
        elif self._current_mode == "region":
            counties = self._get_counties_for_region(current_selection)
            return f"Régió: {current_selection} ({len(counties)} megye)"
        else:
            return f"Megye: {current_selection}"
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Widget engedélyezése/letiltása.
        
        Args:
            enabled: Engedélyezett állapot
        """
        self.group.setEnabled(enabled)
        self.combo_box.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled and self.is_valid())
        
        print(f"🏙️ DEBUG: MultiCityWidget enabled state: {enabled}")
        print(f"🔧 DEBUG: ComboBox enabled after set_enabled: {self.combo_box.isEnabled()}")
    
    # === SIZE HINT ===
    
    def sizeHint(self):
        """Preferált méret."""
        return self.group.sizeHint()
    
    def minimumSizeHint(self):
        """Minimum méret."""
        return self.group.minimumSizeHint()