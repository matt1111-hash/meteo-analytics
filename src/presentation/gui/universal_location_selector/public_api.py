#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Location Selector - Public API

📤 Publikus interface metódusok

Képességek:
- Location query és beállítás
- Selection törlés
- Search fókusz
- Current location getter

Fájl: src/presentation/gui/universal_location_selector/public_api.py
"""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QLineEdit, QListWidget, QPushButton

from src.data.models import UniversalLocation

from .location_card import LocationCard


class UniversalLocationSelectorPublicAPI:
    """
    Publikus interface metódusok delegeálása.

    Ez a mixin osztály tartalmazza a publikus metódusokat,
    amiket a UniversalLocationSelector 提供.
    """

    # Signalok (delegált)
    search_requested: Signal
    city_selected: Signal
    location_changed: Signal

    # State
    current_location: Optional[UniversalLocation]

    # Widgets
    search_input: QLineEdit
    results_list: QListWidget
    location_card: LocationCard
    confirm_button: QPushButton
    status_label: QLabel

    def get_current_location(self) -> Optional[UniversalLocation]:
        """Jelenlegi lokáció lekérdezése"""
        return self.current_location

    def set_current_location(self, location: UniversalLocation) -> None:
        """
        Lokáció programmatic beállítása

        Args:
            location: UniversalLocation objektum
        """
        self.current_location = location
        self.location_changed.emit(location)

        # UI frissítése
        if location:
            lat, lon = location.coordinates
            details = f"Koordináták: [{lat:.4f}, {lon:.4f}]"
            self.location_card.set_location(location.display_name, details)
            self.confirm_button.setEnabled(True)

    def clear_selection(self) -> None:
        """Kiválasztás törlése"""
        self.current_location = None
        self.search_input.clear()
        self.results_list.clear()
        self.location_card.clear()
        self.confirm_button.setEnabled(False)
        self.status_label.setText("💡 Kezdj el gépelni a kereséshez...")

    def focus_search(self) -> None:
        """Fókusz a keresőmezőre"""
        self.search_input.setFocus()
        self.search_input.selectAll()

    def get_search_text(self) -> str:
        """Jelenlegi keresés szöveg"""
        return self.search_input.text()

    def set_search_text(self, text: str) -> None:
        """
        Keresés szöveg beállítása

        Args:
            text: Új kereső szöveg
        """
        self.search_input.setText(text)
