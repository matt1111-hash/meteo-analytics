#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validation - Constants validators for GUI, wind gusts, dual-API.
"""

import logging
from typing import Dict

from ..constants import AnomalyConstants, APIConstants, DataConstants, GUIConstants
from .validators import validate_color_hex

logger = logging.getLogger(__name__)


def validate_gui_constants() -> Dict[str, bool]:
    """
    GUI konstansok validálása rendszerindításkor.

    Returns:
        Validációs eredmények
    """
    try:
        validations = {
            "window_size_valid": GUIConstants.MAIN_WINDOW_WIDTH >= GUIConstants.MAIN_WINDOW_MIN_WIDTH,
            "panel_size_valid": GUIConstants.CONTROL_PANEL_MIN_WIDTH <= GUIConstants.CONTROL_PANEL_MAX_WIDTH,
            "splitter_size_valid": GUIConstants.SPLITTER_HANDLE_WIDTH > 0,
            "colors_valid": all(validate_color_hex(color) for color in [
                GUIConstants.PRIMARY_COLOR,
                GUIConstants.SUCCESS_COLOR,
                GUIConstants.WARNING_COLOR,
                GUIConstants.ERROR_COLOR
            ]),
            # 🌪️ KRITIKUS JAVÍTÁS: Wind gusts küszöbök validálása
            "wind_gusts_thresholds_valid": (
                AnomalyConstants.WIND_GUSTS_STRONG > AnomalyConstants.WIND_GUSTS_MODERATE and
                AnomalyConstants.WIND_GUSTS_EXTREME > AnomalyConstants.WIND_GUSTS_STRONG and
                AnomalyConstants.WIND_GUSTS_HURRICANE > AnomalyConstants.WIND_GUSTS_EXTREME
            ),
            # ✅ ÚJ: Dual-API validáció
            "dual_api_sources_valid": len(DataConstants.DATA_SOURCE_PRIORITY) >= 2,
            "api_capabilities_defined": all(
                source in DataConstants.SOURCE_CAPABILITIES
                for source in DataConstants.DATA_SOURCE_PRIORITY
            )
        }

        return validations

    except Exception as e:
        logger.error(f"GUI konstansok validálási hiba: {e}")
        return {"validation_failed": True}


def validate_wind_gusts_constants() -> Dict[str, bool]:
    """
    🌪️ KRITIKUS JAVÍTÁS: Wind gusts konstansok validálása.

    Returns:
        Validációs eredmények
    """
    try:
        validations = {
            "thresholds_ascending": (
                AnomalyConstants.WIND_HIGH_THRESHOLD > 0 and
                AnomalyConstants.WIND_EXTREME_THRESHOLD > AnomalyConstants.WIND_HIGH_THRESHOLD and
                AnomalyConstants.WIND_HURRICANE_THRESHOLD > AnomalyConstants.WIND_EXTREME_THRESHOLD
            ),
            "categories_complete": len(AnomalyConstants.WIND_GUSTS_CATEGORIES) >= 7,  # 7 kategória már (STORMY hozzáadva)
            "colors_valid": all(
                validate_color_hex(color) for color in AnomalyConstants.WIND_GUSTS_COLORS.values()
            ),
            "gusts_vs_windspeed_valid": (
                AnomalyConstants.WIND_GUSTS_STRONG >= AnomalyConstants.WINDSPEED_HIGH_THRESHOLD and
                AnomalyConstants.WIND_GUSTS_EXTREME >= AnomalyConstants.WINDSPEED_EXTREME_THRESHOLD
            ),
            # 🌪️ KRITIKUS JAVÍTÁS: Meteorológiai standard validálás
            "beaufort_scale_compliant": (
                AnomalyConstants.WIND_GUSTS_MODERATE == 30.0 and    # Beaufort 4-5
                AnomalyConstants.WIND_GUSTS_STRONG == 50.0 and      # Beaufort 7-8
                AnomalyConstants.WIND_GUSTS_STORMY == 70.0          # Beaufort 8-9
            )
        }

        return validations

    except Exception as e:
        logger.error(f"Wind gusts konstansok validálási hiba: {e}")
        return {"validation_failed": True}


def validate_dual_api_constants() -> Dict[str, bool]:
    """
    🌍 ÚJ: Dual-API konstansok validálása.

    Returns:
        Dual-API validációs eredmények
    """
    try:
        validations = {
            "source_priority_valid": len(DataConstants.DATA_SOURCE_PRIORITY) >= 2,
            "use_case_mapping_complete": all(
                use_case in DataConstants.USE_CASE_SOURCE_MAPPING
                for use_case in ["single_city", "multi_city", "historical_deep"]
            ),
            "source_capabilities_complete": all(
                source in DataConstants.SOURCE_CAPABILITIES
                for source in DataConstants.DATA_SOURCE_PRIORITY
            ),
            "display_names_available": all(
                source in APIConstants.SOURCE_DISPLAY_NAMES
                for source in DataConstants.DATA_SOURCE_PRIORITY
            ),
            "api_endpoints_defined": (
                bool(APIConstants.OPEN_METEO_BASE) and
                bool(APIConstants.METEOSTAT_BASE)
            )
        }

        return validations

    except Exception as e:
        logger.error(f"Dual-API konstansok validálási hiba: {e}")
        return {"validation_failed": True}


def validate_anomaly_constants() -> Dict[str, bool]:
    """
    🌪️ KRITIKUS JAVÍTÁS: Összes anomália konstans validálása.

    Returns:
        Teljes validációs eredmények
    """
    try:
        gui_validation = validate_gui_constants()
        wind_validation = validate_wind_gusts_constants()
        dual_api_validation = validate_dual_api_constants()

        # Hőmérséklet validálás
        temp_validation = {
            "temp_thresholds_valid": (
                AnomalyConstants.TEMP_EXTREME_HOT > AnomalyConstants.TEMP_HOT_THRESHOLD and
                AnomalyConstants.TEMP_COLD_THRESHOLD > AnomalyConstants.TEMP_EXTREME_COLD
            )
        }

        # Csapadék validálás
        precip_validation = {
            "precip_thresholds_valid": (
                AnomalyConstants.PRECIP_EXTREME_HIGH > AnomalyConstants.PRECIP_HIGH_THRESHOLD and
                AnomalyConstants.PRECIP_HIGH_THRESHOLD > AnomalyConstants.PRECIP_LOW_THRESHOLD
            )
        }

        # Összesített validáció
        all_validations = {
            **gui_validation,
            **wind_validation,
            **dual_api_validation,
            **temp_validation,
            **precip_validation
        }

        return all_validations

    except Exception as e:
        logger.error(f"Teljes anomália konstansok validálási hiba: {e}")
        return {"validation_failed": True}


__all__ = [
    "validate_gui_constants",
    "validate_wind_gusts_constants",
    "validate_dual_api_constants",
    "validate_anomaly_constants",
]
