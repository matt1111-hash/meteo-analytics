#!/usr/bin/env python3
# mypy: ignore-errors

"""
Location Widget - Core class with state and public interface.
"""

from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from src.domain.entities.universal_location import UniversalLocation
from src.domain.ports import CityManagerPort
from src.presentation.gui.theme_manager import get_theme_manager


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

    def __init__(self, city_manager: CityManagerPort, parent: QWidget | None = None):
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
        self.current_location: UniversalLocation | None = None
        self.current_city_data: dict[str, Any] | None = None
        self._updating_state = False

        # UI init
        from .refresh_handler import RefreshHandler  # noqa: PLC0415
        from .signal_handlers import SignalHandlers  # noqa: PLC0415
        from .theme_handler import ThemeHandler  # noqa: PLC0415
        from .ui_builder import UIInitializer  # noqa: PLC0415

        self.ui = UIInitializer(self)
        self.signals = SignalHandlers(self)
        self.refresh = RefreshHandler(self)
        self.theme = ThemeHandler(self)

        self.ui.build()
        self.signals.connect()
        self.theme.apply()

        print("🌍 DEBUG: LocationWidget inicializálva - Clean Architecture")

    # === PUBLIKUS INTERFACE ===

    def get_state(self) -> dict[str, Any]:
        """
        Aktuális állapot lekérdezése.

        Returns:
            Dict az aktuális állapottal
        """
        return {
            "current_location": self.current_location,
            "current_city_data": self.current_city_data,
            "has_location": self.current_city_data is not None,
            "is_valid": self.is_valid(),
        }

    def set_state(self, state: dict[str, Any]) -> bool:
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
                self.signals._update_location_info(
                    city_data.get("name", "Unknown"),
                    city_data.get("latitude", 0.0),
                    city_data.get("longitude", 0.0),
                )
                self.ui.clear_btn.setEnabled(True)
            else:
                self.current_city_data = None
                self.ui.info_label.setText("Válasszon lokációt...")
                self.theme._apply_label_styling(self.ui.info_label, "secondary")
                self.ui.clear_btn.setEnabled(False)

            # UniversalLocation beállítása
            location = state.get("current_location")
            if location:
                self.current_location = location

            print("✅ DEBUG: LocationWidget state set successfully")
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
        self.signals._clear_location()

    def set_enabled(self, enabled: bool) -> None:
        """
        Widget engedélyezése/letiltása.

        Args:
            enabled: Engedélyezett állapot
        """
        self.ui.group.setEnabled(enabled)
        self.ui.location_selector.setEnabled(enabled)
        self.ui.clear_btn.setEnabled(enabled and self.current_city_data is not None)

        print(f"🌍 DEBUG: LocationWidget enabled state: {enabled}")

    def get_current_city_data(self) -> dict[str, Any] | None:
        """Aktuális city data lekérdezése (compatibility)."""
        return self.current_city_data

    def get_current_location(self) -> UniversalLocation | None:
        """Aktuális UniversalLocation lekérdezése."""
        return self.current_location

    def update_search_results(self, results) -> None:
        """Search results frissítése (compatibility)."""
        if hasattr(self.ui.location_selector, "update_search_results"):
            self.ui.location_selector.update_search_results(results)

    def refresh_ui(self) -> None:
        """UI teljes frissítése - REAKTIVÁLÁS TÁMOGATÁS."""
        self.refresh.refresh_ui()

    def force_refresh(self) -> None:
        """Kényszerített refresh - WIDGET REAKTIVÁLÁS."""
        self.refresh.force_refresh()

    # === SIZE HINT ===

    def sizeHint(self):
        """Preferált méret."""
        return self.ui.group.sizeHint()

    def minimumSizeHint(self):
        """Minimum méret."""
        return self.ui.group.minimumSizeHint()
