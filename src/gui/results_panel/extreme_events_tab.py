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
        """🎨 UI inicializálása."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Cím
        self.title_label = QLabel("⚡ Extrém Időjárási Események")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 🔥 KRITIKUS: Anomália beállítások gomb mindig elérhető!
        self.settings_btn = QPushButton("⚙️ ANOMÁLIA BEÁLLÍTÁSOK MEGNYITÁSA")
        self.settings_btn.setMinimumHeight(50)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        self.settings_btn.clicked.connect(self._on_anomaly_settings_clicked)
        layout.addWidget(self.settings_btn)
        
        # Anomália szekció
        self.anomaly_section = self._create_anomaly_section()
        layout.addWidget(self.anomaly_section)
        
        # Rekordok szekció
        self.records_section = self._create_records_section()
        layout.addWidget(self.records_section)
        
        # Akciók szekció
        actions_section = self._create_actions_section()
        layout.addWidget(actions_section)
        
        layout.addStretch()
    
    def _create_anomaly_section(self) -> QGroupBox:
        """🔍 Anomália detektálás szekció UI."""
        section = QGroupBox("🔍 Anomália Detektálás")
        layout = QVBoxLayout(section)
        
        indicators_layout = QGridLayout()
        
        self.temp_anomaly = QLabel("🌡️ Hőmérséklet: Normális")
        indicators_layout.addWidget(self.temp_anomaly, 0, 0)
        
        self.precip_anomaly = QLabel("🌧️ Csapadék: Normális")
        indicators_layout.addWidget(self.precip_anomaly, 0, 1)
        
        self.wind_anomaly = QLabel("🌪️ Szél: Normális")
        indicators_layout.addWidget(self.wind_anomaly, 0, 2)
        
        layout.addLayout(indicators_layout)
        
        # Inicializálás ColorPalette API-val
        self._set_anomaly_status_with_theme(self.temp_anomaly, "🌡️ Hőmérséklet: Normális", "success")
        self._set_anomaly_status_with_theme(self.precip_anomaly, "🌧️ Csapadék: Normális", "success")
        self._set_anomaly_status_with_theme(self.wind_anomaly, " tornado Szél: Normális", "success")
        
        return section
    
    def _create_records_section(self) -> QGroupBox:
        """🏆 Rekordok kimutatása szekció UI."""
        section = QGroupBox("🏆 Rekordok és Szélsőértékek")
        layout = QVBoxLayout(section)
        
        # Periódus választó
        period_group = self._create_period_selection_group()
        layout.addWidget(period_group)
        
        # Extrém értékek táblázata
        self.extreme_table = self._create_extreme_table()
        layout.addWidget(self.extreme_table)
        
        # Szöveges összefoglaló
        self.records_text = QTextEdit()
        self.records_text.setMaximumHeight(80)
        self.records_text.setReadOnly(True)
        layout.addWidget(self.records_text)
        
        return section
    
    def _create_period_selection_group(self) -> QGroupBox:
        """📅 Periódus választó widget."""
        period_group = QGroupBox("📅 Időszak típusa")
        period_layout = QHBoxLayout(period_group)
        
        # Radio button group
        self.period_type_group = QButtonGroup()
        
        self.daily_radio = QRadioButton("📊 Napi rekordok")
        self.monthly_radio = QRadioButton("📅 Havi rekordok") 
        self.yearly_radio = QRadioButton("🗓️ Éves rekordok")
        
        self.daily_radio.setChecked(True)
        self.period_type = "daily"
        
        self.period_type_group.addButton(self.daily_radio)
        self.period_type_group.addButton(self.monthly_radio)
        self.period_type_group.addButton(self.yearly_radio)
        
        period_layout.addWidget(self.daily_radio)
        period_layout.addWidget(self.monthly_radio)
        period_layout.addWidget(self.yearly_radio)
        period_layout.addStretch()
        
        # Eseménykezelők
        self.daily_radio.toggled.connect(self._on_period_type_changed)
        self.monthly_radio.toggled.connect(self._on_period_type_changed)
        self.yearly_radio.toggled.connect(self._on_period_type_changed)
        
        return period_group
    
    def _create_extreme_table(self) -> QTableWidget:
        """📊 Extrém értékek táblázat UI."""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["📊 Kategória", "🏆 Rekord típus", "📈 Érték", "📅 Dátum"])
        
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.verticalHeader().setVisible(False)
        
        # Oszlop szélességek
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        table.setMinimumHeight(200)
        return table
    
    def _create_actions_section(self) -> QWidget:
        """⚙️ Akciók szekció UI."""
        container = QWidget()
        layout = QHBoxLayout(container)
        
        self.detailed_btn = QPushButton("🔍 Részletes Extrém Elemzés")
        self.detailed_btn.clicked.connect(self._on_detailed_analysis_clicked)
        layout.addWidget(self.detailed_btn)
        
        layout.addStretch()
        return container
    
    def _register_widgets_for_theming(self) -> None:
        """🎨 Widget-ek regisztrálása ThemeManager-hez."""
        try:
            register_widget_for_theming(self, "container")
            register_widget_for_theming(self.anomaly_section, "container")
            register_widget_for_theming(self.records_section, "container")
            register_widget_for_theming(self.title_label, "text")
            register_widget_for_theming(self.records_text, "input")
            register_widget_for_theming(self.detailed_btn, "button")
            register_widget_for_theming(self.settings_btn, "button")
            
            if self.extreme_table:
                register_widget_for_theming(self.extreme_table, "table")
            
            register_widget_for_theming(self.daily_radio, "chart")
            register_widget_for_theming(self.monthly_radio, "chart")
            register_widget_for_theming(self.yearly_radio, "chart")
            
            logger.debug("ExtremeEventsTab - Widgets regisztrál