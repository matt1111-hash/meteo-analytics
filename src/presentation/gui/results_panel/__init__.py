#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Results Panel Module Exports
Clean modular exports for the results panel components.
🏗️ MODULÁRIS ARCHITEKTÚRA: Each tab = one file principle
🎯 CLEAN IMPORTS: Centralized component access
🚀 PROFESSIONAL CODING: DRY, KISS, SOLID principles
🚨 CRITICAL FIX: Fallback import logika javítva - nincs felesleges placeholder aktiválás

🏗️ MODULÁRIS KOMPONENSEK:
✅ ResultsPanel - Fő panel (src/gui/results_panel/results_panel.py)
✅ QuickOverviewTab - Gyors áttekintés tab
✅ DetailedChartsTab - Részletes diagramok tab  
✅ DataTableTab - Adattáblázat tab
✅ ExtremeEventsTab - Extrém események tab
✅ WindyDaysTab - Szeles napok analízis tab (ÚJ!)
✅ Utility Classes - Közös segédosztályok

🎯 IMPORT PATTERN:
from src.presentation.gui.results_panel import ResultsPanel, QuickOverviewTab, WindyDaysTab
# vagy
from src.presentation.gui.results_panel import *  # Összes komponens
"""

import logging

# Logging konfigurálása
logger = logging.getLogger(__name__)

# === 🚨 CRITICAL FIX: STEP-BY-STEP IMPORT - NO MASS FALLBACK ===

# 1. FŐ RESULTSPANEL IMPORT (PRIORITÁS!)
try:
    from .results_panel import ResultsPanel
    logger.info("✅ ResultsPanel import SIKERES!")
    _results_panel_loaded = True
except ImportError as e:
    logger.error(f"❌ KRITIKUS: ResultsPanel import hiba: {e}")
    
    # EMERGENCY PLACEHOLDER CSAK HA VALÓBAN HIÁNYZIK
    class ResultsPanel:
        """Emergency placeholder ResultsPanel - csak akkor ha valóban hiányzik."""
        def __init__(self, *args, **kwargs):
            logger.error("❌ EMERGENCY: ResultsPanel placeholder használatban - results_panel.py valóban hiányzik!")
            raise ImportError("ResultsPanel module not found!")
    
    _results_panel_loaded = False

# 2. MODULÁRIS TAB IMPORTS (EGYENKÉNT!)
try:
    from .quick_overview_tab import QuickOverviewTab
    logger.debug("✅ QuickOverviewTab import sikeres")
    _quick_overview_loaded = True
except ImportError as e:
    logger.warning(f"⚠️ QuickOverviewTab import hiba: {e}")
    
    class QuickOverviewTab:
        """Fallback QuickOverviewTab."""
        def __init__(self, *args, **kwargs):
            logger.warning("⚠️ QuickOverviewTab fallback használatban")
    
    _quick_overview_loaded = False

try:
    from .detailed_charts_tab import DetailedChartsTab
    logger.debug("✅ DetailedChartsTab import sikeres")
    _detailed_charts_loaded = True
except ImportError as e:
    logger.warning(f"⚠️ DetailedChartsTab import hiba: {e}")
    
    class DetailedChartsTab:
        """Fallback DetailedChartsTab."""  
        def __init__(self, *args, **kwargs):
            logger.warning("⚠️ DetailedChartsTab fallback használatban")
    
    _detailed_charts_loaded = False

try:
    from .data_table_tab import DataTableTab
    logger.debug("✅ DataTableTab import sikeres")
    _data_table_loaded = True
except ImportError as e:
    logger.warning(f"⚠️ DataTableTab import hiba: {e}")
    
    class DataTableTab:
        """Fallback DataTableTab."""
        def __init__(self, *args, **kwargs):
            logger.warning("⚠️ DataTableTab fallback használatban")
    
    _data_table_loaded = False

try:
    from .extreme_events_tab import ExtremeEventsTab
    logger.debug("✅ ExtremeEventsTab import sikeres")
    _extreme_events_loaded = True
except ImportError as e:
    logger.warning(f"⚠️ ExtremeEventsTab import hiba: {e}")
    
    class ExtremeEventsTab:
        """Fallback ExtremeEventsTab."""
        def __init__(self, *args, **kwargs):
            logger.warning("⚠️ ExtremeEventsTab fallback használatban")
    
    _extreme_events_loaded = False

# 🌪️ ÚJ: WINDY DAYS TAB IMPORT
try:
    from .windy_days_tab import WindyDaysTab
    logger.debug("✅ WindyDaysTab import sikeres")
    _windy_days_loaded = True
except ImportError as e:
    logger.warning(f"⚠️ WindyDaysTab import hiba: {e}")
    
    class WindyDaysTab:
        """Fallback WindyDaysTab."""
        def __init__(self, *args, **kwargs):
            logger.warning("⚠️ WindyDaysTab fallback használatban - windy_days_tab.py hiányzik")
    
    _windy_days_loaded = False

# 3. UTILITY OSZTÁLYOK (OPCIONÁLIS)
try:
    from .utils import (
        WindGustsConstants,
        DataFrameExtractor, 
        WindGustsAnalyzer
    )
    logger.debug("✅ Utility osztályok import sikeres")
    _utils_loaded = True
except ImportError as e:
    logger.warning(f"⚠️ Utils import hiba: {e}")
    
    # Minimal utility placeholders
    class WindGustsConstants:
        """Placeholder WindGustsConstants."""
    
    class DataFrameExtractor:
        """Placeholder DataFrameExtractor."""
        @staticmethod 
        def extract_safely(*args, **kwargs):
            logger.warning("⚠️ DataFrameExtractor placeholder használatban!")
            return None
    
    class WindGustsAnalyzer:
        """Placeholder WindGustsAnalyzer."""
        @staticmethod
        def categorize_wind_gust(*args, **kwargs):
            logger.warning("⚠️ WindGustsAnalyzer placeholder használatban!")
            return "unknown"
    
    _utils_loaded = False

# === IMPORT STATUS REPORT ===
_import_summary = {
    "results_panel": _results_panel_loaded,
    "quick_overview": _quick_overview_loaded,
    "detailed_charts": _detailed_charts_loaded,
    "data_table": _data_table_loaded,
    "extreme_events": _extreme_events_loaded,
    "windy_days": _windy_days_loaded,  # ÚJ
    "utils": _utils_loaded
}

_loaded_count = sum(_import_summary.values())
_total_count = len(_import_summary)

logger.info(f"📊 Results Panel Import Summary: {_loaded_count}/{_total_count} komponens betöltve")

if _results_panel_loaded:
    logger.info("🎯 KRITIKUS: ResultsPanel SIKERESEN BETÖLTVE - setMinimumWidth elérhető!")
else:
    logger.error("💥 KRITIKUS: ResultsPanel BETÖLTÉS SIKERTELEN - setMinimumWidth AttributeError várható!")

# WindyDaysTab status
if _windy_days_loaded:
    logger.info("🌪️ ÚJ: WindyDaysTab SIKERESEN BETÖLTVE!")
else:
    logger.warning("⚠️ ÚJ: WindyDaysTab BETÖLTÉS SIKERTELEN - fallback használatban")

if _loaded_count == _total_count:
    logger.info("✅ TELJES results panel modul betöltés SIKERES!")
elif _loaded_count >= 4:  # Ha ResultsPanel + legalább 3 tab működik
    logger.info("✅ ALAPVETŐ results panel modul betöltés SIKERES!")
else:
    logger.warning("⚠️ RÉSZLEGES results panel modul betöltés!")

# === PUBLIC API EXPORTS ===

__all__ = [
    # Fő komponensek
    "ResultsPanel",
    
    # Tab komponensek  
    "QuickOverviewTab",
    "DetailedChartsTab", 
    "DataTableTab",
    "ExtremeEventsTab",
    "WindyDaysTab",  # ÚJ
    
    # Utility osztályok
    "WindGustsConstants",
    "DataFrameExtractor", 
    "WindGustsAnalyzer"
]

# === MODUL INFORMÁCIÓK ===

__version__ = "2.2.0"  # WindyDaysTab hozzáadása miatt verzió növelés
__author__ = "Global Weather Analyzer Team"
__description__ = "Modular results panel components with WindyDaysTab integration"

# Import status report function
def get_import_status() -> dict:
    """
    Import status jelentés diagnosztikai célokra.
    
    Returns:
        Import status dictionary
    """
    status = {
        "module": "results_panel",
        "version": __version__,
        "components_total": _total_count,
        "components_loaded": _loaded_count,
        "components_success_rate": f"{(_loaded_count/_total_count)*100:.1f}%",
        "critical_component_loaded": _results_panel_loaded,
        "windy_days_component_loaded": _windy_days_loaded,  # ÚJ
        "detailed_status": _import_summary,
        "components": __all__,
        "architecture": "modular",
        "status": "ready" if _results_panel_loaded else "degraded"
    }
    
    return status

def validate_components() -> bool:
    """
    Komponensek validálása - legalább a kritikus komponens betöltődött-e.
    
    Returns:
        ResultsPanel elérhető-e (minimum követelmény)
    """
    try:
        # KRITIKUS: ResultsPanel KÖTELEZŐ
        if not _results_panel_loaded:
            logger.error("❌ KRITIKUS HIBA: ResultsPanel nem elérhető!")
            return False
        
        # ResultsPanel létezik-e és van-e setMinimumWidth metódusa?
        if hasattr(ResultsPanel, '__init__') and hasattr(ResultsPanel, 'setMinimumWidth'):
            logger.info("✅ ResultsPanel validálás sikeres - setMinimumWidth elérhető!")
            return True
        else:
            logger.error("❌ ResultsPanel validálás sikertelen - hiányzó metódusok!")
            return False
        
    except Exception as e:
        logger.error(f"❌ Komponens validálási hiba: {e}")
        return False

def validate_windy_days_tab() -> bool:
    """
    WindyDaysTab komponens validálása.
    
    Returns:
        WindyDaysTab elérhető és működőképes-e
    """
    try:
        if not _windy_days_loaded:
            logger.warning("⚠️ WindyDaysTab nem betöltött")
            return False
        
        # WindyDaysTab alapvető metódusainak ellenőrzése
        if hasattr(WindyDaysTab, '__init__') and hasattr(WindyDaysTab, 'update_data'):
            logger.info("✅ WindyDaysTab validálás sikeres!")
            return True
        else:
            logger.warning("⚠️ WindyDaysTab validálás sikertelen - hiányzó metódusok")
            return False
        
    except Exception as e:
        logger.error(f"❌ WindyDaysTab validálási hiba: {e}")
        return False

# === INICIALIZÁLÁSI VALIDÁCIÓ ===

logger.info(f"📦 Results Panel Module initialized (v{__version__})")
logger.info(f"🏗️ Architecture: Modular - {_loaded_count}/{_total_count} components loaded")

# Komponensek validálása inicializáláskor
component_validation = validate_components()
if component_validation:
    logger.info("🎯 SIKERES: Results panel modul TELJESEN MŰKÖDŐKÉPES - ResultsPanel.setMinimumWidth elérhető!")
else:
    logger.error("💥 HIBA: Results panel modul NEM MŰKÖDŐKÉPES - ResultsPanel hibák várhatók!")

# WindyDaysTab validálása
windy_days_validation = validate_windy_days_tab()
if windy_days_validation:
    logger.info("🌪️ SIKERES: WindyDaysTab TELJESEN MŰKÖDŐKÉPES!")
else:
    logger.warning("⚠️ FIGYELEM: WindyDaysTab nem működőképes - fallback használatban")

# 🚨 CRITICAL SUCCESS INDICATOR
if _results_panel_loaded:
    logger.info("🚀 MAIN_WINDOW KOMPATIBILITÁS: ResultsPanel.setMinimumWidth() HASZNÁLHATÓ!")
else:
    logger.error("🛑 MAIN_WINDOW INKOMPATIBILITÁS: ResultsPanel.setMinimumWidth() AttributeError!")

# 🌪️ WINDY DAYS SUCCESS INDICATOR  
if _windy_days_loaded:
    logger.info("🌪️ WINDY DAYS INTEGRÁCIÓ: WindyDaysTab HASZNÁLHATÓ a results_panel-ben!")
else:
    logger.warning("⚠️ WINDY DAYS FIGYELEM: WindyDaysTab fallback használatban!")
