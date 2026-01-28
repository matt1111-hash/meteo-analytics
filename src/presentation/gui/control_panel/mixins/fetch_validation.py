#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Control Panel - Fetch Validation Mixin
Fetch button validation logic and state management.
"""


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
            # Analysis type check
            analysis_type = self.analysis_type_widget.get_current_type()
            if not analysis_type:
                print("❌ DEBUG: No analysis type selected")
                return False

            # Location/Multi-city check analysis type szerint
            if analysis_type == "single_location":
                # Single location validation
                location_valid = self.location_widget.is_valid()
                if not location_valid:
                    print("❌ DEBUG: Location not valid in single_location mode")
                    return False

                # További location ellenőrzések
                location_state = self.location_widget.get_state()
                if not location_state.get("has_location", False):
                    print("❌ DEBUG: No location selected in single_location mode")
                    return False

                city_data = location_state.get("current_city_data")
                if not city_data or not all(
                    key in city_data for key in ["latitude", "longitude"]
                ):
                    print("❌ DEBUG: Invalid city data in single_location mode")
                    return False

            elif analysis_type in ["region", "county"]:
                # 🏙️ Multi-city validation
                multi_city_valid = self.multi_city_widget.is_valid()
                if not multi_city_valid:
                    print(f"❌ DEBUG: Multi-city selection not valid in {analysis_type} mode")
                    return False

                # További multi-city ellenőrzések
                multi_city_state = self.multi_city_widget.get_state()
                if multi_city_state.get("selection_count", 0) == 0:
                    print(f"❌ DEBUG: No {analysis_type} selected in multi-city mode")
                    return False

                print(f"✅ DEBUG: Multi-city validation passed for {analysis_type}")

            # Date range check
            date_valid = self.date_range_widget.is_valid()
            if not date_valid:
                print("❌ DEBUG: Date range not valid")
                return False

            # API settings check
            api_valid = self.api_settings_widget.is_valid()
            if not api_valid:
                print("❌ DEBUG: API settings not valid")
                return False

            # Provider check
            provider_valid = self.provider_widget.is_valid()
            if not provider_valid:
                print("❌ DEBUG: Provider not valid")
                return False

            # Fetching state check
            not_fetching = not self.query_control_widget._is_fetching
            if not not_fetching:
                print("❌ DEBUG: Fetch already in progress")
                return False

            print(f"✅ DEBUG: Comprehensive validation passed for {analysis_type}")
            return True

        except Exception as e:
            print(f"❌ DEBUG: Error during comprehensive fetch validation: {e}")
            return False

    def force_fetch_button_update(self) -> None:
        """Fetch button állapot kényszerített frissítése."""
        self._update_fetch_button_state_comprehensive()
