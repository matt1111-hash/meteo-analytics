#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Control Panel - Public API Mixin
Public API methods and legacy compatibility.
"""

from typing import Any, Dict, List, Optional


class PublicAPIMixin:
    """
    Public API mixin a ControlPanel számára.
    Nyilvános API metódusok és legacy kompatibilitás.
    """

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
            "query_control": self.query_control_widget.get_state(),
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
            self.analysis_type_widget.is_valid()
            and self.date_range_widget.is_valid()
            and self.provider_widget.is_valid()
            and self.api_settings_widget.is_valid()
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
