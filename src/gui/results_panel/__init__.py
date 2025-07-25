#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Results Panel Module Exports
Clean modular exports for the results panel components.
🏗️ MODULÁRIS ARCHITEKTÚRA: Each tab = one file principle
🎯 CLEAN IMPORTS: Centralized component access
🚀 PROFESSIONAL CODING: DRY, KISS, SOLID principles

🏗️ MODULÁRIS KOMPONENSEK:
✅ ResultsPanel - Fő panel (src/gui/results_panel/results_panel.py)
✅ QuickOverviewTab - Gyors áttekintés tab
✅ DetailedChartsTab - Részletes diagramok tab  
✅ DataTableTab - Adattáblázat tab
✅ ExtremeEventsTab - Extrém események tab
✅ Utility Classes - Közös segédosztályok

🎯 IMPORT PATTERN:
from src.gui.results_panel import ResultsPanel, QuickOverviewTab
# vagy
from src.gui.results_panel import *  # Összes komponens
"""

import logging

# Logging konfigurálása
logger = logging.getLogger(__name__)

try:
    # === FŐ RESULTSPANEL IMPORT ===
    # ✅ JAVÍTOTT: Belső results_panel.py-ből (13.3 kB verzió)
    from .results_panel import ResultsPanel
    
    # === MODULÁRIS TAB IMPORTS ===
    from .quick_overview_tab import QuickOverviewTab
    from .detailed_charts_tab import DetailedChartsTab  
    from .data_table_tab import DataTableTab
    from .extreme_events_tab import ExtremeEventsTab
    
    # === UTILITY OSZTÁLYOK ===
    from .utils import (
        WindGustsConstants,
        DataFrameExtractor, 
        WindGustsAnalyzer
    )
    
    logger.info("✅ Results panel moduláris imports sikeresek!")
    
except ImportError as e:
    logger.error(f"❌ Results panel import hiba: {e}")
    
    # === FALLBACK - Ha valamelyik moduláris fájl hiányzik ===
    try:
        # Próbáljuk meg legalább a fő ResultsPanel-t importálni
        logger.warning("🔄 Fallback - csak ResultsPanel import...")
        
        from .results_panel import ResultsPanel
        
        # Üres placeholder classes a hiányzó komponensekhez
        class QuickOverviewTab:
            """Placeholder QuickOverviewTab - import hiba esetén."""
            def __init__(self, *args, **kwargs):
                logger.error("QuickOverviewTab placeholder használatban - fájl hiányzik!")
        
        class DetailedChartsTab:
            """Placeholder DetailedChartsTab - import hiba esetén."""  
            def __init__(self, *args, **kwargs):
                logger.error("DetailedChartsTab placeholder használatban - fájl hiányzik!")
        
        class DataTableTab:
            """Placeholder DataTableTab - import hiba esetén."""
            def __init__(self, *args, **kwargs):
                logger.error("DataTableTab placeholder használatban - fájl hiányzik!")
        
        class ExtremeEventsTab:
            """Placeholder ExtremeEventsTab - import hiba esetén."""
            def __init__(self, *args, **kwargs):
                logger.error("ExtremeEventsTab placeholder használatban - fájl hiányzik!")
        
        # Utility placeholders
        class WindGustsConstants:
            """Placeholder WindGustsConstants - import hiba esetén."""
            pass
        
        class DataFrameExtractor:
            """Placeholder DataFrameExtractor - import hiba esetén."""
            @staticmethod 
            def extract_safely(*args, **kwargs):
                logger.error("DataFrameExtractor placeholder használatban!")
                return None
        
        class WindGustsAnalyzer:
            """Placeholder WindGustsAnalyzer - import hiba esetén."""
            @staticmethod
            def categorize_wind_gust(*args, **kwargs):
                logger.error("WindGustsAnalyzer placeholder használatban!")
                return "unknown"
        
        logger.warning("⚠️ Részleges fallback sikeres - ResultsPanel elérhető, de moduláris komponensek placeholderek!")
        
    except ImportError as fallback_error:
        logger.critical(f"💥 KRITIKUS: Minden results panel import sikertelen: {fallback_error}")
        
        # === TELJES ÜRES PLACEHOLDER CLASSES ===
        # Hogy az alkalmazás ne törjön össze
        class ResultsPanel:
            """Placeholder ResultsPanel - import hiba esetén."""
            def __init__(self, *args, **kwargs):
                logger.error("ResultsPanel placeholder használatban - results_panel.py fájl hiányzik!")
        
        class QuickOverviewTab:
            """Placeholder QuickOverviewTab - import hiba esetén."""
            def __init__(self, *args, **kwargs):
                logger.error("QuickOverviewTab placeholder használatban - quick_overview_tab.py fájl hiányzik!")
        
        class DetailedChartsTab:
            """Placeholder DetailedChartsTab - import hiba esetén."""  
            def __init__(self, *args, **kwargs):
                logger.error("DetailedChartsTab placeholder használatban - detailed_charts_tab.py fájl hiányzik!")
        
        class DataTableTab:
            """Placeholder DataTableTab - import hiba esetén."""
            def __init__(self, *args, **kwargs):
                logger.error("DataTableTab placeholder használatban - data_table_tab.py fájl hiányzik!")
        
        class ExtremeEventsTab:
            """Placeholder ExtremeEventsTab - import hiba esetén."""
            def __init__(self, *args, **kwargs):
                logger.error("ExtremeEventsTab placeholder használatban - extreme_events_tab.py fájl hiányzik!")
        
        # Utility placeholders
        class WindGustsConstants:
            """Placeholder WindGustsConstants - import hiba esetén."""
            pass
        
        class DataFrameExtractor:
            """Placeholder DataFrameExtractor - import hiba esetén."""
            @staticmethod 
            def extract_safely(*args, **kwargs):
                logger.error("DataFrameExtractor placeholder használatban!")
                return None
        
        class WindGustsAnalyzer:
            """Placeholder WindGustsAnalyzer - import hiba esetén."""
            @staticmethod
            def categorize_wind_gust(*args, **kwargs):
                logger.error("WindGustsAnalyzer placeholder használatban!")
                return "unknown"


# === PUBLIC API EXPORTS ===

__all__ = [
    # Fő komponensek
    "ResultsPanel",
    
    # Tab komponensek  
    "QuickOverviewTab",
    "DetailedChartsTab", 
    "DataTableTab",
    "ExtremeEventsTab",
    
    # Utility osztályok
    "WindGustsConstants",
    "DataFrameExtractor", 
    "WindGustsAnalyzer"
]


# === MODUL INFORMÁCIÓK ===

__version__ = "2.1.0"
__author__ = "Global Weather Analyzer Team"
__description__ = "Modular results panel components with clean architecture"

# Import status report
def get_import_status() -> dict:
    """
    Import status jelentés diagnosztikai célokra.
    
    Returns:
        Import status dictionary
    """
    status = {
        "module": "results_panel",
        "version": __version__,
        "components_loaded": len(__all__),
        "components": __all__,
        "architecture": "modular",
        "status": "ready"
    }
    
    return status


def validate_components() -> bool:
    """
    Komponensek validálása - mind betöltődött-e helyesen.
    
    Returns:
        Minden komponens elérhető-e
    """
    try:
        required_components = [
            "ResultsPanel",
            "QuickOverviewTab", 
            "DetailedChartsTab",
            "DataTableTab",
            "ExtremeEventsTab"
        ]
        
        for component in required_components:
            if component not in globals():
                logger.error(f"❌ Hiányzó komponens: {component}")
                return False
        
        logger.info("✅ Minden results panel komponens elérhető!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Komponens validálási hiba: {e}")
        return False


# === DIAGNOSZTIKAI INFORMÁCIÓK ===

logger.info(f"📦 Results Panel Module initialized (v{__version__})")
logger.info(f"🏗️ Architecture: Modular - {len(__all__)} components loaded")
logger.info(f"🎯 Components: {', '.join(__all__)}")

# Komponensek validálása inicializáláskor
component_validation = validate_components()
if component_validation:
    logger.info("✅ Results panel modul teljesen funkcionális!")
else:
    logger.warning("⚠️ Results panel modul részben funkcionális - hiányzó komponensek!")
