#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multi-City Widget - Core

🏙️ Multi-City választó widget fő osztálya

Képességek:
- Magyar régiók/megyék dropdown választás
- Analysis type alapú mode váltás (region vs county)
- Selection state management
- Signal kibocsátás selection változáskor

Fájl: src/presentation/gui/panel_widgets/multi_city_widget/core.py
"""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from src.domain.ports import CityManagerPort
from src.presentation.gui.theme_manager import get_theme_manager

from .combo_handler import ComboHandler
from .public_api import MultiCityWidgetPublicAPI
from .regional_data import get_hungarian_regions
from .ui_builder import (
    apply_label_styling,
    create_multi_city_ui,
    register_widget_for_theming,
)


class MultiCityWidget(QWidget, MultiCityWidgetPublicAPI):
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
    selection_changed = Signal(
        dict
    )  # {"mode": "region", "selected": "Közép-Magyarország", "is_valid": True}

    def __init__(self, city_manager: CityManagerPort, parent: Optional[QWidget] = None):
        """
        MultiCityWidget inicializálása (CA compliant - uses CityManagerPort).

        Args:
            city_manager: CityManagerPort instance (magyar adatok lekérdezéshez)
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
        self._available_regions = get_hungarian_regions()
        self._available_counties = []  # Betöltjük később

        # UI init
        self._init_ui()
        self._load_data()
        self._connect_signals()
        self._register_for_theming()

        # ComboBox inicializálása
        self._combo_handler.populate_combo_box(
            self._current_mode,
            self._available_regions,
            self._available_counties,
            self._selected_region,
            self._selected_county,
        )
        self._combo_handler.update_group_title(self._current_mode)
        self._combo_handler.update_info_label(
            self._current_mode, self._get_current_selection()
        )

        print(
            "🏙️ DEBUG: MultiCityWidget (DROPDOWN) inicializálva - Clean Architecture + COMBO FIX"
        )

    def _init_ui(self) -> None:
        """UI elemek létrehozása."""
        ui_elements = create_multi_city_ui(self, self.theme_manager)

        self.group = ui_elements["group"]
        self.combo_box = ui_elements["combo_box"]
        self.info_label = ui_elements["info_label"]
        self.clear_btn = ui_elements["clear_btn"]

        # Combo handler inicializálása
        self._combo_handler = ComboHandler(
            self.combo_box,
            self.group,
            self.info_label,
            lambda label, style_type: apply_label_styling(
                label, self.theme_manager, style_type
            ),
        )

    def _load_data(self) -> None:
        """Magyar régiók és megyék adatainak betöltése."""
        try:
            # Megyék betöltése city_manager-ből
            self._available_counties = self.city_manager.get_hungarian_counties()
            print(f"🏛️ DEBUG: Betöltött megyék: {len(self._available_counties)} db")
            print(
                f"📋 DEBUG: Megyék listája: {self._available_counties[:5]}..."
            )  # Első 5

        except Exception as e:
            print(f"❌ ERROR: Adatok betöltési hiba: {e}")
            self._available_counties = []

    def _connect_signals(self) -> None:
        """Signal-slot kapcsolatok."""
        self.combo_box.currentTextChanged.connect(self._on_combo_selection_changed)
        self.clear_btn.clicked.connect(self._clear_selection)

    def _register_for_theming(self) -> None:
        """Theme manager regisztráció."""
        register_widget_for_theming(
            self.theme_manager,
            self,
            self.group,
            self.combo_box,
            self.clear_btn,
            self.info_label,
        )

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

        self._combo_handler.populate_combo_box(
            self._current_mode,
            self._available_regions,
            self._available_counties,
            self._selected_region,
            self._selected_county,
        )
        self._combo_handler.update_group_title(self._current_mode)
        self._combo_handler.update_info_label(
            self._current_mode, self._get_current_selection()
        )

        print(f"✅ DEBUG: Analysis mode váltás befejezve: {mode}")

    # === COMBO BOX SIGNAL HANDLER ===

    def _on_combo_selection_changed(self, text: str) -> None:
        """ComboBox selection változás kezelése."""
        if self._updating_state:
            print(f"⏸️ DEBUG: Skipping combo change (updating state): {text}")
            return

        current_index = self.combo_box.currentIndex()
        print(
            f"🔄 DEBUG: Combo selection changed - index: {current_index}, text: '{text}'"
        )

        # Placeholder választás (index 0) - törlés
        if current_index == 0:
            print("🔄 DEBUG: Placeholder selected - clearing selection")
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

        self._combo_handler.update_info_label(
            self._current_mode, self._get_current_selection()
        )
        self._update_clear_button()
        self._emit_selection_changed()

    def _clear_current_selection(self) -> None:
        """Aktuális mode selection törlése."""
        if self._current_mode == "region":
            self._selected_region = None
            print("🏞️ DEBUG: Régió selection törölve")
        else:
            self._selected_county = None
            print("🏛️ DEBUG: Megye selection törölve")

        self._combo_handler.update_info_label(
            self._current_mode, self._get_current_selection()
        )
        self._update_clear_button()
        self._emit_selection_changed()

    def _emit_selection_changed(self) -> None:
        """Selection changed signal kibocsátása."""
        current_selection = self._get_current_selection()

        selection_data = {
            "mode": self._current_mode,
            "selected": current_selection,
            "is_valid": self.is_valid(),
            "selection_text": self._get_selection_display_text(),
        }

        self.selection_changed.emit(selection_data)
        print(f"📡 DEBUG: selection_changed signal emitted: {selection_data}")

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

    # === SIZE HINT ===

    def sizeHint(self):
        """Preferált méret."""
        return self.group.sizeHint()

    def minimumSizeHint(self):
        """Minimum méret."""
        return self.group.minimumSizeHint()
