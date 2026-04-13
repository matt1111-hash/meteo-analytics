#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Control Panel - UI Manager Mixin
UI state management, visibility control, mode switching.
"""

from PySide6.QtCore import QTimer


def _restore_single_location_state(control_panel) -> None:
    """Restore preserved single-location state when available."""
    if "location" not in control_panel._preserved_states:
        return
    location_state = control_panel._preserved_states["location"]
    if location_state.get("has_location", False):
        print("🔄 DEBUG: Restoring location widget state...")
        control_panel.location_widget.set_state(location_state)


def _restore_multi_city_state(control_panel, analysis_type: str) -> None:
    """Restore preserved multi-city state when available."""
    if "multi_city" not in control_panel._preserved_states:
        return
    multi_city_state = control_panel._preserved_states["multi_city"]
    if multi_city_state.get("is_valid", False):
        print(f"🏙️ DEBUG: Restoring multi-city widget state for {analysis_type}...")
        control_panel.multi_city_widget.set_state(multi_city_state)


def _restore_shared_widget_states(control_panel) -> None:
    """Restore shared widget states after analysis type changes."""
    if "date_range" in control_panel._preserved_states:
        control_panel.date_range_widget.set_state(control_panel._preserved_states["date_range"])
    if "provider" in control_panel._preserved_states:
        control_panel.provider_widget.set_state(control_panel._preserved_states["provider"])
    if "api_settings" in control_panel._preserved_states:
        control_panel.api_settings_widget.set_state(control_panel._preserved_states["api_settings"])


class UIManagerMixin:
    """
    UI management mixin a ControlPanel számára.
    Kezeli a widgetek megjelenését, elrejtését és state preservation-t.
    """

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
                "api_settings": self.api_settings_widget.get_state(),
            }

            location_valid = self._preserved_states["location"].get("is_valid", False)
            multi_city_valid = self._preserved_states["multi_city"].get("is_valid", False)
            print(
                f"✅ DEBUG: Widget states preserved - location: {location_valid}, multi-city: {multi_city_valid}"
            )

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
            if analysis_type == "single_location":
                _restore_single_location_state(self)
            if analysis_type in ["region", "county"]:
                _restore_multi_city_state(self, analysis_type)
            _restore_shared_widget_states(self)
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

            if hasattr(self.location_widget, "group"):
                self.location_widget.group.setVisible(True)
                self.location_widget.group.setEnabled(True)

            # Location widget belső enable + refresh
            self.location_widget.set_enabled(True)
            self.location_widget.show()

            # === MULTI-CITY WIDGET ELREJTÉSE ===
            self.multi_city_widget.setVisible(False)
            self.multi_city_widget.setEnabled(False)

            print(
                "✅ DEBUG: UI set to single_location mode - LOCATION WIDGET VISIBLE, MULTI-CITY HIDDEN"
            )

        elif analysis_type in ["region", "county"]:
            print(
                f"🔧 DEBUG: Setting UI to {analysis_type} mode - MultiCityWidget MEGJELENÍTÉSE..."
            )

            # === LOCATION WIDGET ELREJTÉSE ===
            self.location_widget.setVisible(False)
            self.location_widget.setEnabled(False)

            # === MULTI-CITY WIDGET MEGJELENÍTÉSE + MODE BEÁLLÍTÁSA ===
            self.multi_city_widget.setVisible(True)
            self.multi_city_widget.setEnabled(True)
            self.multi_city_widget.show()

            # 🏙️ Analysis mode beállítása a MultiCityWidget-en
            self.multi_city_widget.set_analysis_mode(analysis_type)

            print(
                f"✅ DEBUG: UI set to {analysis_type} mode - MULTI-CITY WIDGET VISIBLE ({analysis_type} mode), LOCATION HIDDEN"
            )

        # Query control button text frissítése
        if hasattr(self.query_control_widget, "update_for_analysis_type"):
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
                if hasattr(self.location_widget, "location_selector"):
                    self.location_widget.location_selector.setVisible(True)
                    self.location_widget.location_selector.setEnabled(True)

                # 🚨 FINAL VISIBILITY GUARANTEE
                self.location_widget.setVisible(True)
                self.location_widget.show()

                print(
                    "🔧 DEBUG: Delayed widget refresh completed for single_location - LocationWidget VISIBLE"
                )

            elif analysis_type in ["region", "county"]:
                # 🏙️ MultiCityWidget explicit refresh
                self.multi_city_widget.setVisible(True)
                self.multi_city_widget.setEnabled(True)
                self.multi_city_widget.show()

                print(
                    f"🔧 DEBUG: Delayed widget refresh completed for {analysis_type} - MultiCityWidget VISIBLE"
                )

        except Exception as e:
            print(f"⚠️ DEBUG: Error during delayed widget refresh: {e}")

    def refresh_ui_state(self) -> None:
        """UI állapot teljes frissítése + MULTI-CITY."""
        analysis_type = self.analysis_type_widget.get_current_type()
        self._update_ui_for_analysis_type_fixed(analysis_type)
        self._update_fetch_button_state_comprehensive()
        self.provider_widget.refresh_usage_display()

        print("🔄 ControlPanel UI state refreshed + MultiCityWidget")
