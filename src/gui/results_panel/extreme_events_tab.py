#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Extreme Events Tab Module (FACADE PATTERN - FINAL)
🗃️ FACADE PATTERN: UI koordináció és delegálás specialized modulokhoz
🎯 FINAL CLEANUP: ~400 LOC tiszta UI koordináció
🔥 BACKWARD COMPATIBILITY: Minden public API és signal változatlan marad!
🚨 IMPORT FIX: Relative import problémák javítva

📋 REFAKTORING VÁLTOZÁSOK:
✅ Anomália detektálás → AnomalyDetector modul
✅ Rekordok számítása → ExtremeCalculator modul  
✅ UI CSAK koordináció és delegálás
✅ Redundáns kódok TÖRÖLVE
❌ ZERO BREAKING CHANGES: Minden import és API ugyanaz!

🚀 CLEAN CODE ELVEK:
✅ FACADE PATTERN: UI koordináció
✅ COMPOSITION: Aggregáció öröklés helyett
✅ SOLID: Single Responsibility megvalósítva
✅ DRY: Logika specialized modulokban
✅ Type hints: Explicit típusok
✅ Error handling: Robusztus kivételkezelés
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QTextEdit, QButtonGroup, QRadioButton, 
    QHeaderView, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# 🚨 IMPORT FIX: Absolute importok relative helyett
try:
    from src.config import GUIConfig
except ImportError:
    # Fallback ha nincs GUIConfig
    class GUIConfig:
        pass

# 🚨 IMPORT FIX: Safe imports minden dependency-hez
try:
    from ..utils import GUIConstants, AnomalyConstants
except ImportError:
    # Fallback constants
    class GUIConstants:
        pass
    class AnomalyConstants:
        pass

try:
    from ..theme_manager import get_theme_manager, register_widget_for_theming
except ImportError:
    # Fallback theme functions
    def get_theme_manager():
        return None
    def register_widget_for_theming(*args, **kwargs):
        pass

# 🗃️ REFAKTORING: Új modulok importálása SAFE módon
try:
    from .anomaly_detector import AnomalyDetector, AnomalyResult, create_anomaly_detector_with_settings
    _anomaly_detector_available = True
except ImportError as e:
    logging.warning(f"AnomalyDetector import hiba: {e}")
    _anomaly_detector_available = False

try:
    from .extreme_calculator import ExtremeCalculator, ExtremeRecord, RecordsTextSummary
    _extreme_calculator_available = True
except ImportError as e:
    logging.warning(f"ExtremeCalculator import hiba: {e}")
    _extreme_calculator_available = False

try:
    from ..dialogs.anomaly_settings_dialog import AnomalySettingsDialog
    _anomaly_dialog_available = True
except ImportError as e:
    logging.warning(f"AnomalySettingsDialog import hiba: {e}")
    _anomaly_dialog_available = False

try:
    from src.data.anomaly_profile_manager import AnomalyProfileManager
    _profile_manager_available = True
except ImportError as e:
    logging.warning(f"AnomalyProfileManager import hiba: {e}")
    _profile_manager_available = False

# Logging konfigurálása
logger = logging.getLogger(__name__)


class ExtremeEventsTab(QWidget):
    """
    🗃️ FACADE PATTERN: Extrém Események Tab UI Koordinátor
    🚨 IMPORT FIX: Safe import fallback system
    
    🎯 CLEAN RESPONSIBILITIES:
    ✅ UI építés és layout menedzsment
    ✅ Delegálás AnomalyDetector-hoz (ha elérhető)
    ✅ Delegálás ExtremeCalculator-hoz (ha elérhető)
    ✅ Eredmények megjelenítése UI-ban
    ✅ Eseménykezelés koordinálása
    ✅ Graceful fallback ha modulok hiányoznak
    
    🔥 BACKWARD COMPATIBILITY:
    ❌ ZERO BREAKING CHANGES
    ✅ Minden public API változatlan marad
    ✅ Signals ugyanazok
    ✅ Constructor signature ugyanaz
    ✅ Minden import és használat változatlan marad!
    """
    
    # 🔥 BACKWARD COMPATIBILITY: Signals változatlanok!
    extreme_weather_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """🗃️ FACADE PATTERN konstruktor SAFE IMPORTS-tal."""
        super().__init__(parent)
        
        self.theme_manager = get_theme_manager()
        
        # 🗃️ REFAKTORING: Specialized modulok kompozíciója SAFE módon
        if _profile_manager_available:
            self.profile_manager = AnomalyProfileManager()
        else:
            self.profile_manager = None
        
        # Dinamikus beállításokkal anomaly detector létrehozása
        if _anomaly_detector_available and self.profile_manager:
            try:
                current_settings = self.profile_manager.get_current_settings()
                self.anomaly_detector = create_anomaly_detector_with_settings(current_settings)
            except Exception as e:
                logger.warning(f"AnomalyDetector létrehozási hiba: {e}")
                self.anomaly_detector = None
        else:
            self.anomaly_detector = None
        
        if _extreme_calculator_available:
            try:
                self.extreme_calculator = ExtremeCalculator()
            except Exception as e:
                logger.warning(f"ExtremeCalculator létrehozási hiba: {e}")
                self.extreme_calculator = None
        else:
            self.extreme_calculator = None
        
        # Settings dialog tárolása
        self.settings_dialog: Optional[object] = None
        
        # Legacy UI komponensek referenciák (backward compatibility)
        self.current_data: Optional[Dict[str, Any]] = None
        self.temp_anomaly: Optional[QLabel] = None
        self.precip_anomaly: Optional[QLabel] = None
        self.wind_anomaly: Optional[QLabel] = None
        self.records_text: Optional[QTextEdit] = None
        self.extreme_table: Optional[QTableWidget] = None
        self.period_type: str = "daily"
        
        # UI építés
        self._init_ui()
        self._register_widgets_for_theming()
        
        logger.info("🗃️ ExtremeEventsTab FACADE PATTERN inicializálva - SAFE IMPORTS")
    
    def _init_ui(self) -> None:
        """🎨 UI inicializál