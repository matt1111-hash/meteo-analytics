#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Location Widget - Signal handlers.
"""

from typing import Any, Dict

from src.domain.entities.universal_location import UniversalLocation


class SignalHandlers:
    """Signal handler a LocationWidget számára."""

    def __init__(self, widget: 'LocationWidget'):
        """
        SignalHandlers inicializálása.

        Args:
            widget: LocationWidget instance
        """
        self.widget = widget

    def connect(self) -> None:
        """Signal-slot kapcsolatok."""
        # UniversalLocationSelector signalok
        self.widget.ui.location_selector.search_requested.connect(self._on_search_requested)
        self.widget.ui.location_selector.city_selected.connect(self._on_city_selected)
        self.widget.ui.location_selector.location_changed.connect(self._on_location_changed)

    def _on_search_requested(self, query: str) -> None:
        """Keresési kérés továbbítása."""
        print(f"🔍 DEBUG: LocationWidget search requested: {query}")
        self.widget.search_requested.emit(query)

    def _on_city_selected(self, name: str, lat: float, lon: float, data: Dict[str, Any]) -> None:
        """City selection kezelése."""
        if self.widget._updating_state:
            return

        try:
            print(f"🏙️ DEBUG: LocationWidget city selected: {name} [{lat:.4f}, {lon:.4f}]")

            # State frissítése
            self.widget.current_city_data = {
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "display_name": name,
                **data
            }

            # UI frissítése
            self._update_location_info(name, lat, lon)
            self.widget.ui.clear_btn.setEnabled(True)

            # Signal továbbítása (compatibility)
            self.widget.city_selected.emit(name, lat, lon, data)

            print(f"✅ DEBUG: LocationWidget city selection processed: {name}")

        except Exception as e:
            print(f"❌ ERROR: LocationWidget city selection error: {e}")

    def _on_location_changed(self, location: UniversalLocation) -> None:
        """UniversalLocation változás kezelése."""
        if self.widget._updating_state:
            return

        try:
            print(f"🌍 DEBUG: LocationWidget location changed: {location}")

            # State frissítése
            self.widget.current_location = location

            # current_city_data frissítése UniversalLocation-ből
            if hasattr(location, 'identifier') and hasattr(location, 'coordinates'):
                self.widget.current_city_data = {
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
                self.widget.ui.clear_btn.setEnabled(True)

            # Signal továbbítása
            self.widget.location_changed.emit(location)

            print(f"✅ DEBUG: LocationWidget location change processed: {location.identifier}")

        except Exception as e:
            print(f"❌ ERROR: LocationWidget location change error: {e}")

    def _clear_location(self) -> None:
        """Lokáció törlése."""
        if self.widget._updating_state:
            return

        try:
            print("🗑️ DEBUG: LocationWidget clear location")

            # UniversalLocationSelector törlése
            self.widget.ui.location_selector.clear_selection()

            # State törlése
            self.widget.current_location = None
            self.widget.current_city_data = None

            # UI reset
            self.widget.ui.info_label.setText("Válasszon lokációt...")
            self.widget.theme._apply_label_styling(self.widget.ui.info_label, "secondary")
            self.widget.ui.clear_btn.setEnabled(False)

            print("✅ DEBUG: LocationWidget location cleared")

        except Exception as e:
            print(f"❌ ERROR: LocationWidget clear error: {e}")

    def _update_location_info(self, name: str, lat: float, lon: float) -> None:
        """Lokáció info frissítése."""
        info_text = f"🏙️ {name}\n🗺️ Koordináták: [{lat:.4f}, {lon:.4f}]"
        self.widget.ui.info_label.setText(info_text)
        self.widget.theme._apply_label_styling(self.widget.ui.info_label, "primary")
