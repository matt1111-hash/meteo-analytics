#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Control Panel - Fetch Validation Mixin
Fetch button validation logic and state management.
"""


def _validate_single_location(control_panel) -> bool:
    """Validate single-location fetch state."""
    if not control_panel.location_widget.is_valid():
        print("❌ DEBUG: Location not valid in single_location mode")
        return False
    location_state = control_panel.location_widget.get_state()
    if not location_state.get("has_location", False):
        print("❌ DEBUG: No location selected in single_location mode")
        return False
    city_data = location_state.get("current_city_data")
    if not city_data or not all(key in city_data for key in ["latitude", "longitude"]):
        print("❌ DEBUG: Invalid city data in single_location mode")
        return False
    return True


def _validate_multi_city(control_panel, analysis_type: str) -> bool:
    """Validate multi-city fetch state."""
    if not control_panel.multi_city_widget.is_valid():
        print(f"❌ DEBUG: Multi-city selection not valid in {analysis_type} mode")
        return False
    multi_city_state = control_panel.multi_city_widget.get_state()
    if multi_city_state.get("selection_count", 0) == 0:
        print(f"❌ DEBUG: No {analysis_type} selected in multi-city mode")
        return False
    print(f"✅ DEBUG: Multi-city validation passed for {analysis_type}")
    return True


def _validate_analysis_scope(control_panel, analysis_type: str) -> bool:
    """Validate the active analysis scope."""
    if analysis_type == "single_location":
        return _validate_single_location(control_panel)
    if analysis_type in ["region", "county"]:
        return _validate_multi_city(control_panel, analysis_type)
    return True


def _validate_shared_dependencies(control_panel) -> bool:
    """Validate shared fetch dependencies."""
    checks = [
        (control_panel.date_range_widget.is_valid(), "❌ DEBUG: Date range not valid"),
        (
            control_panel.api_settings_widget.is_valid(),
            "❌ DEBUG: API settings not valid",
        ),
        (control_panel.provider_widget.is_valid(), "❌ DEBUG: Provider not valid"),
        (
            not control_panel.query_control_widget._is_fetching,
            "❌ DEBUG: Fetch already in progress",
        ),
    ]
    for is_valid, message in checks:
        if not is_valid:
            print(message)
            return False
    return True


class FetchValidationMixin:
    """
    Fetch validation mixin a ControlPanel számára.
    Kezeli a fetch button állapotát és validációját.
    """

    def _update_fetch_button_state_comprehensive(self) -> None:
        """
        🔧 KRITIKUS FIX: Fetch button állapot újraértékelése - comprehensive validation + MULTI-CITY + QUERY_BUTTON.
        """
        can_fetch = self._comprehensive_fetch_validation()

        # 🔧 KRITIKUS FIX: fetch_button → query_button
        if not self.query_control_widget._is_fetching:
            self.query_control_widget.query_button.setEnabled(can_fetch)

        print(
            f"🚀 DEBUG: Query button enabled: {can_fetch} (comprehensive validation + multi-city + FETCH_BUTTON FIX)"
        )

    def _comprehensive_fetch_validation(self) -> bool:
        """
        🔧 ROBUSZTUS: Comprehensive fetch validálás - minden widget állapot ellenőrzése + MULTI-CITY.

        Returns:
            bool: True ha indítható a fetch
        """
        try:
            analysis_type = self.analysis_type_widget.get_current_type()
            if not analysis_type:
                print("❌ DEBUG: No analysis type selected")
                return False

            if not _validate_analysis_scope(self, analysis_type):
                return False
            if not _validate_shared_dependencies(self):
                return False
            print(f"✅ DEBUG: Comprehensive validation passed for {analysis_type}")
            return True

        except Exception as e:
            print(f"❌ DEBUG: Error during comprehensive fetch validation: {e}")
            return False

    def force_fetch_button_update(self) -> None:
        """Fetch button állapot kényszerített frissítése."""
        self._update_fetch_button_state_comprehensive()
