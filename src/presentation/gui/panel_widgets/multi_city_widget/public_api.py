#!/usr/bin/env python3
# mypy: ignore-errors

"""
Multi-City Widget - Public API

📤 Publikus interface metódusok

Képességek:
- State management (get_state, set_state)
- Validation
- City queries
- Selection summary

Fájl: src/presentation/gui/panel_widgets/multi_city_widget/public_api.py
"""

from typing import Any

from PySide6.QtWidgets import QComboBox, QGroupBox, QPushButton

from .regional_data import get_counties_for_region


class MultiCityWidgetPublicAPI:
    """
    Publikus interface metódusok delegeálása.

    Ez a mixin osztály tartalmazza a publikus metódusokat,
    amiket a MultiCityWidget 提供.
    """

    # State
    _current_mode: str
    _selected_region: str | None
    _selected_county: str | None
    _updating_state: bool

    # Widgets
    group: QGroupBox
    combo_box: QComboBox
    clear_btn: QPushButton

    # Dependencies
    city_manager: Any  # CityManager

    def get_state(self) -> dict[str, Any]:
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
            "selection_text": self._get_selection_display_text(),
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

            # Mode beállítása
            mode = state.get("mode", "region")
            if mode != self._current_mode:
                self.set_analysis_mode(mode)

            # Selections restoration
            if "selected_region" in state:
                self._selected_region = state["selected_region"]

            if "selected_county" in state:
                self._selected_county = state["selected_county"]

            # UI frissítése
            self._combo_handler.restore_selection(
                self._current_mode, self._selected_region, self._selected_county
            )
            self._combo_handler.update_info_label(self._current_mode, self._get_current_selection())
            self._update_clear_button()

            print("✅ DEBUG: MultiCityWidget state restored successfully")
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

    def get_selected_cities(self) -> list[dict[str, Any]]:
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
                counties = get_counties_for_region(current_selection)
                for county in counties:
                    county_cities = self.city_manager.get_hungarian_settlements_by_county(
                        county, limit=50
                    )
                    cities.extend([city.to_dict() for city in county_cities])

            else:
                # Megye esetén közvetlenül
                county_cities = self.city_manager.get_hungarian_settlements_by_county(
                    current_selection, limit=50
                )
                cities.extend([city.to_dict() for city in county_cities])

            print(
                f"🏙️ DEBUG: Kiválasztott városok: {len(cities)} db ({self._current_mode}: {current_selection})"
            )
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
            counties = get_counties_for_region(current_selection)
            return f"Régió: {current_selection} ({len(counties)} megye)"
        else:
            return f"Megye: {current_selection}"

    def clear_selection(self) -> None:
        """Kiválasztás törlése."""
        self._clear_selection()

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

    # === HELPER METHODS ===

    def _get_current_selection(self) -> str | None:
        """Aktuális kiválasztás lekérdezése mode szerint."""
        if self._current_mode == "region":
            return self._selected_region
        else:
            return self._selected_county

    def _get_selection_display_text(self) -> str:
        """Kiválasztás megjelenítési szövege."""
        if self._current_mode == "region" and self._selected_region:
            counties = get_counties_for_region(self._selected_region)
            return f"{self._selected_region} ({len(counties)} megye)"
        elif self._current_mode == "county" and self._selected_county:
            return f"{self._selected_county} megye"
        else:
            return ""

    def _update_clear_button(self) -> None:
        """Clear button állapot frissítése."""
        has_selection = self._get_current_selection() is not None
        self.clear_btn.setEnabled(has_selection)
