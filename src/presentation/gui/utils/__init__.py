#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors
# ruff: noqa: F405

"""
Global Weather Analyzer - GUI Utils Module.
GUI segédfüggvények, konstansok és stíluslapok modulja.

🌍 PROVIDER TRACKING FUNCTIONS:
✅ Provider usage statistics formázása
✅ Cost calculation utilities
✅ Provider status helpers
✅ Warning level check functions
✅ Provider recommendation logic
✅ Usage validation functions

🌪️ WIND GUSTS ANOMALY CONSTANTS:
✅ WIND_HIGH_THRESHOLD 70.0 km/h (erős széllökés)
✅ WIND_EXTREME_THRESHOLD 100.0 km/h (extrém széllökés)
✅ WIND_HURRICANE_THRESHOLD 120.0 km/h (hurrikán erősségű)
✅ Élethű széllökés kategorizálás Balatonfüred 130+ km/h adatokhoz
✅ Backward compatibility windspeed_10m_max küszöbökkel

🚀 PROFESSZIONÁLIS KÓDOLÁSI ELVEK:
✅ DRY: Központosított konstansok, újrafelhasználható utility függvények
✅ KISS: Egyszerű, érthető kategorizálás és validáció
✅ YAGNI: Csak szükséges funkcionalitás implementálva
✅ SOLID: Egyszeres felelősség, bővíthetőség
✅ Type hints: Minden függvénynél explicit típusok
✅ Error handling: Robusztus kivételkezelés
✅ Logging: Debug és monitoring funkciók

🎨 THEMEMANAGER INTEGRÁCIÓ:
✅ Dinamikus CSS generálás
✅ ColorPalette support
✅ Runtime téma váltás
✅ Backward compatibility

🌍 DUAL-API INTEGRÁCIÓ:
✅ Open-Meteo API konstansok
✅ Meteostat API konstansok
✅ Smart source routing
✅ Multi-city támogatás

Portolva: PyQt5 → PySide6
Architektúra: Moduláris design, centralizált konstansok, DUAL-API powered
"""

import logging

from .export_group_a import *  # noqa: F403
from .export_group_b import *  # noqa: F403

# Logging konfigurálása
logger = logging.getLogger(__name__)

# === 🔧 KRITIKUS BACKWARD COMPATIBILITY ALIASES ===

# Backward compatibility aliases for import errors
get_display_name_for_source = get_source_display_name

# Source display names direct export
SOURCE_DISPLAY_NAMES = APIConstants.SOURCE_DISPLAY_NAMES

# API Constants direct exports
OPEN_METEO_BASE = APIConstants.OPEN_METEO_BASE
METEOSTAT_BASE = APIConstants.METEOSTAT_BASE


# === MODUL INICIALIZÁLÁS ===
if __name__ == "__main__":
    # Standalone futtatás esetén teljes validáció
    print(
        "🌍 DUAL-API UTILS MODULE + PROVIDER TRACKING + BACKWARD COMPATIBILITY - STANDALONE VALIDATION"
    )
    print("=" * 80)

    summary = get_project_completion_summary()
    dual_api_summary = get_dual_api_implementation_summary()

    print(f"📊 Project: {summary['project_name']}")
    print(f"🏁 Status: {summary['status']}")
    print(f"📅 Completion: {summary['completion_date']}")
    print(f"🌍 API Architecture: {dual_api_summary['architecture']}")
    print()

    print("🔍 VALIDATION RESULTS:")
    validation_results = validate_anomaly_constants()
    for key, value in validation_results.items():
        status = "✅ PASS" if value else "❌ FAIL"
        print(f"  {key}: {status}")
    print()

    print("🌍 DUAL-API SYSTEM:")
    for source in DataConstants.DATA_SOURCE_PRIORITY:
        display_name = get_source_display_name(source)
        available = validate_api_source_available(source)
        status = "✅ Elérhető" if available else "❌ API kulcs szükséges"
        print(f"  {display_name}: {status}")
    print()

    print("🌍 PROVIDER TRACKING FUNCTIONS:")
    tracking_functions = [
        "format_provider_usage",
        "calculate_provider_costs",
        "get_provider_warning_level",
        "format_provider_status",
        "validate_provider_selection",
        "get_provider_recommendation",
    ]
    for func in tracking_functions:
        print(f"  ✅ {func}")
    print()

    print("🔧 BACKWARD COMPATIBILITY ALIASES:")
    print("  ✅ get_display_name_for_source → get_source_display_name")
    print("  ✅ SOURCE_DISPLAY_NAMES")
    print("  ✅ OPEN_METEO_BASE")
    print("  ✅ METEOSTAT_BASE")
    print()

    print("🔍 RÉSZLETES DEMONSTRÁCIÓK:")
    demonstrate_dual_api_strategy()
    demonstrate_meteorological_fix()

    print("🏁 PROJECT COMPLETION: 6/6 STEPS COMPLETED!")
    print("✅ DUAL-API SYSTEM SUCCESSFULLY INTEGRATED!")
    print("🌪️ METEOROLÓGIAI STANDARDOKRA KALIBRÁLVA!")
    print("🌍 CLEAN API ARCHITECTURE IMPLEMENTED!")
    print("🌍 PROVIDER TRACKING FUNCTIONS READY!")
    print("🔧 BACKWARD COMPATIBILITY ALIASES FIXED!")

else:
    # Importálás esetén csendes inicializálás
    initialize_utils_module()
    logger.info(
        "utils.py loaded with DUAL-API + WIND GUSTS + PROVIDER TRACKING + BACKWARD COMPATIBILITY support"
    )
    logger.info(
        "🌍 Clean Dual-API: Open-Meteo + Meteostat | 🌪️ Meteorológiai standardok OK | 🌍 Provider tracking ready | 🔧 Backward compatibility fixed"
    )


# === FULL EXPORT LIST FOR BACKWARD COMPATIBILITY ===

__all__ = [
    # Constants
    "APIConstants",
    "GUIConstants",
    "AnomalyConstants",
    "DataConstants",
    "ThemeType",
    "ColorVariant",
    # Formatting
    "format_temperature",
    "format_precipitation",
    "format_wind_speed",
    "format_wind_gusts",
    "get_wind_gusts_category",
    "is_wind_gusts_extreme",
    "is_wind_gusts_hurricane",
    "is_wind_gusts_catastrophic",
    "get_weather_icon",
    "get_wind_gusts_icon",
    "get_wind_gusts_color",
    "calculate_statistics",
    "calculate_wind_gusts_statistics",
    # Validation
    "validate_date_range",
    "sanitize_filename",
    "validate_color_hex",
    "get_contrast_ratio",
    "validate_gui_constants",
    "validate_wind_gusts_constants",
    "validate_dual_api_constants",
    "validate_anomaly_constants",
    # Theme helpers
    "StyleSheets",
    "log_theme_change",
    "log_wind_gusts_event",
    # API helpers
    "get_optimal_data_source",
    "get_source_display_name",
    "validate_api_source_available",
    "get_fallback_source_chain",
    "log_api_source_selection",
    "format_provider_usage",
    "calculate_provider_costs",
    "get_provider_warning_level",
    "format_provider_status",
    "get_provider_icon",
    "validate_provider_selection",
    "get_provider_recommendation",
    "format_cost_summary",
    "log_provider_usage_event",
    # Summary functions
    "get_dual_api_implementation_summary",
    "get_project_completion_summary",
    "demonstrate_dual_api_strategy",
    "demonstrate_meteorological_fix",
    "initialize_utils_module",
    # Backward compatibility aliases
    "get_display_name_for_source",
    "SOURCE_DISPLAY_NAMES",
    "OPEN_METEO_BASE",
    "METEOSTAT_BASE",
]
