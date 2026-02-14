#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Control Panel - Request Builder Mixin
Analysis request building and validation logic.
"""

from datetime import datetime
from typing import Any, Dict


class RequestBuilderMixin:
    """
    Request builder mixin a ControlPanel számára.
    Összeállítja és validálja az analysis requestet.
    """

    def _build_analysis_request(self) -> Dict[str, Any]:
        """
        🎯 COMPREHENSIVE ANALYSIS REQUEST - Widget State Aggregation + MULTI-CITY

        Ez a CLEAN ARCHITECTURE központi data aggregation pontja.
        Minden widget state-jét összegyűjti egy comprehensive request-be.

        Returns:
            Teljes analysis request dict minden paraméterrel
        """
        return {
            # Analysis type és location/multi-city
            **self._get_analysis_params(),
            # Date range
            **self._get_date_params(),
            # Provider és API settings
            **self._get_api_params(),
            # Meta információk
            "timestamp": datetime.now().isoformat(),
            "request_id": f"req_{int(datetime.now().timestamp())}",
            "widget_states": self._get_all_widget_states(),
        }

    def _get_analysis_params(self) -> Dict[str, Any]:
        """Analysis és location/multi-city paraméterek + MULTI-CITY TÁMOGATÁS."""
        analysis_type = self.analysis_type_widget.get_current_type()

        params = {"analysis_type": analysis_type}

        if analysis_type == "single_location":
            # Single location parameterek
            location_state = self.location_widget.get_state()
            if location_state["has_location"]:
                city_data = location_state["current_city_data"]
                print(
                    f"🚨 DEBUG: _get_analysis_params - city_data keys: {list(city_data.keys())}"
                )
                print(f"🚨 DEBUG: _get_analysis_params - city_data: {city_data}")
                params.update(
                    {
                        "latitude": city_data["latitude"],
                        "longitude": city_data["longitude"],
                        "location_name": city_data["name"],
                        "location_data": city_data,
                    }
                )
                print(
                    f"🚨 DEBUG: _get_analysis_params - params['location_data'] keys: {list(params['location_data'].keys())}"
                )

        elif analysis_type in ["region", "county"]:
            # 🚨 FIX: Analysis type konverzió AppController kompatibilitáshoz
            if analysis_type == "region":
                converted_analysis_type = "multi_city"
            else:  # county
                converted_analysis_type = "county_analysis"

            # 🏙️ Multi-city paraméterek
            multi_city_state = self.multi_city_widget.get_state()
            selected_cities = self.multi_city_widget.get_selected_cities()

            # 🚨 FIX: AppController kompatibilis régió/megye név mezők
            current_selection = multi_city_state["current_selection"]
            if analysis_type == "region":
                region_name = current_selection
                county_name = None
            else:  # county
                region_name = None
                county_name = current_selection

            params.update(
                {
                    "analysis_type": converted_analysis_type,  # 🚨 FIX: Konvertált analysis_type
                    "multi_city_mode": True,
                    "region_or_county": analysis_type,  # Eredeti típus megőrzése
                    # 🚨 FIX: AppController várt mezők
                    "region_name": region_name,
                    "county_name": county_name,
                    "multi_city_selection": {
                        "mode": multi_city_state["mode"],
                        "selected": multi_city_state["current_selection"],
                        "count": multi_city_state["selection_count"],
                    },
                    "selected_cities": selected_cities,
                    "city_count": len(selected_cities),
                }
            )

            print(
                f"🏙️ DEBUG: Multi-city analysis request - {len(selected_cities)} cities selected"
            )
            print(
                f"🚨 DEBUG: Analysis type converted: {analysis_type} → {converted_analysis_type}"
            )

        return params

    def _get_date_params(self) -> Dict[str, Any]:
        """
        🚨 KRITIKUS FIX: Date range paraméterek AppController kompatibilis formátumban.

        AppController ezt várja:
        "date_range": {
            "start_date": "2024-08-13",
            "end_date": "2025-08-13"
        }
        """
        date_state = self.date_range_widget.get_state()

        return {
            "date_mode": date_state["date_mode"],
            # 🚨 FIX: date_range objektum a külön start_date/end_date helyett
            "date_range": {
                "start_date": date_state["start_date"],
                "end_date": date_state["end_date"],
            },
            "time_range": date_state.get("time_range"),
        }

    def _get_api_params(self) -> Dict[str, Any]:
        """Provider és API paraméterek."""
        provider_state = self.provider_widget.get_state()
        api_state = self.api_settings_widget.get_state()

        return {
            "provider": provider_state["current_provider"],
            "api_settings": api_state["settings"],
            "provider_preferences": provider_state.get("provider_preferences", {}),
        }

    def _validate_analysis_request(self, request: Dict[str, Any]) -> bool:
        """
        🚨 KRITIKUS FIX: Analysis request validálása + MULTI-CITY - JAVÍTOTT VALIDATION LOGIC.

        A fő hiba helye volt itt! A validation a location_data objektum alatt keresi a lat/lon kulcsokat.
        """
        # Analysis type check
        if "analysis_type" not in request:
            print("❌ DEBUG: Missing analysis_type in request")
            return False

        analysis_type = request["analysis_type"]

        # 🚨 FIX: Konvertált analysis type validálás
        valid_types = ["single_location", "multi_city", "county_analysis"]
        if analysis_type not in valid_types:
            print(f"❌ DEBUG: Invalid analysis type: {analysis_type}")
            return False

        # 🚨 KRITIKUS FIX: Single location validation - location_data objektum alatt keresi lat/lon
        if analysis_type == "single_location":
            if "location_data" not in request:
                print("❌ DEBUG: Missing location_data in request")
                return False
            location_data = request["location_data"]
            if not all(key in location_data for key in ["latitude", "longitude"]):
                print(
                    f"❌ DEBUG: Missing lat/lon in location_data: {list(location_data.keys())}"
                )
                return False
            print(
                "✅ DEBUG: Single location validation passed - location_data structure valid"
            )

        # 🏙️ Multi-city validation (mind a két típusra)
        elif analysis_type in ["multi_city", "county_analysis"]:
            if "multi_city_mode" not in request or not request["multi_city_mode"]:
                print("❌ DEBUG: Missing multi_city_mode in request")
                return False

            if "selected_cities" not in request or len(request["selected_cities"]) == 0:
                print("❌ DEBUG: No selected_cities in multi-city request")
                return False

            print(
                f"✅ DEBUG: Multi-city validation passed - {len(request['selected_cities'])} cities"
            )

        # Date validation - 🚨 FIX: date_range objektum ellenőrzése
        if "date_range" not in request:
            print("❌ DEBUG: Missing date_range in request")
            return False

        date_range = request["date_range"]
        if not all(key in date_range for key in ["start_date", "end_date"]):
            print(
                f"❌ DEBUG: Missing start_date/end_date in date_range: {list(date_range.keys())}"
            )
            return False

        # API validation
        if "provider" not in request or "api_settings" not in request:
            print("❌ DEBUG: Missing provider or api_settings in request")
            return False

        print(f"✅ DEBUG: Analysis request validation passed for {analysis_type}")
        return True
