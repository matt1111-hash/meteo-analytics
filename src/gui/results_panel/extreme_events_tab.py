#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Extreme Events Tab Module (FACADE PATTERN - FINAL)
"""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QTextEdit, QButtonGroup, QRadioButton, 
    QHeaderView, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Application imports
from src.application.use_cases.detect_anomalies import DetectAnomaliesUseCase

# Absolute imports
try:
    from src.config import GUIConfig
except ImportError:
    class GUIConfig:
        pass

try:
    from ..utils import GUIConstants, AnomalyConstants
except ImportError:
    class GUIConstants:
        pass
    class AnomalyConstants:
        pass

try:
    from ..theme_manager import get_theme_manager, register_widget_for_theming
except ImportError:
    def get_theme_manager():
        return None
    def register_widget_for_theming(*args, **kwargs):
        pass

try:
    from src.data.anomaly_profile_manager import AnomalyProfileManager
    _profile_manager_available = True
except ImportError:
    _profile_manager_available = False

try:
    from .extreme_calculator import ExtremeCalculator
    _extreme_calculator_available = True
except ImportError:
    _extreme_calculator_available = False

# Logging
logger = logging.getLogger(__name__)

@dataclass
class AnomalyResult:
    """GUI-barát eredmény az anomália detektáláshoz."""
    category: str
    message: str
    status: str  # 'success' | 'warning' | 'error' | 'disabled'
    value: Optional[float] = None
    threshold: Optional[float] = None
    details: Optional[str] = None

class ExtremeEventsTab(QWidget):
    """
    ⚡ Extrém Események Tab.
    Közvetlenül használja az Application Use Case-t az anomáliák kimutatásához.
    """
    
    extreme_weather_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.theme_manager = get_theme_manager()
        self.profile_manager = AnomalyProfileManager() if _profile_manager_available else None
        self.use_case = DetectAnomaliesUseCase()
        self.extreme_calculator = ExtremeCalculator() if _extreme_calculator_available else None
        
        self.current_data: Optional[Dict[str, Any]] = None
        self.period_type: str = "daily"
        
        # UI komponensek
        self.temp_anomaly: Optional[QLabel] = None
        self.precip_anomaly: Optional[QLabel] = None
        self.wind_anomaly: Optional[QLabel] = None
        self.records_text: Optional[QTextEdit] = None
        self.extreme_table: Optional[QTableWidget] = None
        
        self._init_ui()
        self._register_widgets_for_theming()
        
        logger.info("ExtremeEventsTab inicializálva (Clean Architecture)")

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
        
        # Anomália beállítások gomb
        self.settings_btn = QPushButton("⚙️ ANOMÁLIA BEÁLLÍTÁSOK MEGNYITÁSA")
        self.settings_btn.setMinimumHeight(40)
        self.settings_btn.clicked.connect(self._on_anomaly_settings_clicked)
        layout.addWidget(self.settings_btn)
        
        # Anomália szekció
        self.anomaly_section = self._create_anomaly_section()
        layout.addWidget(self.anomaly_section)
        
        # Rekordok szekció
        self.records_section = self._create_records_section()
        layout.addWidget(self.records_section)
        
        # Akciók
        self.detailed_btn = QPushButton("🔍 Részletes Extrém Elemzés")
        self.detailed_btn.clicked.connect(self._on_detailed_analysis_clicked)
        layout.addWidget(self.detailed_btn)
        
        layout.addStretch()

    def _create_anomaly_section(self) -> QGroupBox:
        section = QGroupBox("🔍 Anomália Detektálás")
        layout = QGridLayout(section)
        
        self.temp_anomaly = QLabel("🌡️ Hőmérséklet: -")
        self.precip_anomaly = QLabel("🌧️ Csapadék: -")
        self.wind_anomaly = QLabel("🌪️ Szél: -")
        
        layout.addWidget(self.temp_anomaly, 0, 0)
        layout.addWidget(self.precip_anomaly, 0, 1)
        layout.addWidget(self.wind_anomaly, 0, 2)
        
        return section

    def _create_records_section(self) -> QGroupBox:
        section = QGroupBox("🏆 Rekordok és Szélsőértékek")
        layout = QVBoxLayout(section)
        
        # Periódus választó
        period_layout = QHBoxLayout()
        self.period_group = QButtonGroup(self)
        
        self.daily_radio = QRadioButton("Napi")
        self.monthly_radio = QRadioButton("Havi")
        self.yearly_radio = QRadioButton("Éves")
        
        self.daily_radio.setChecked(True)
        for rb in [self.daily_radio, self.monthly_radio, self.yearly_radio]:
            self.period_group.addButton(rb)
            period_layout.addWidget(rb)
            rb.toggled.connect(self._on_period_type_changed)
            
        layout.addLayout(period_layout)
        
        self.extreme_table = QTableWidget()
        self.extreme_table.setColumnCount(4)
        self.extreme_table.setHorizontalHeaderLabels(["Kategória", "Típus", "Érték", "Dátum"])
        self.extreme_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.extreme_table)
        
        return section

    def update_data(self, data: Dict[str, Any], city_name: str = "") -> None:
        """📊 Adatok frissítése."""
        if not data:
            return
        self.current_data = data
        
        # Use Case hívása
        try:
            thresholds = self._get_thresholds()
            daily_data = data.get("daily", data)
            anomalies = self.use_case.execute(daily_data, thresholds, city_name)
            self._display_anomalies(anomalies)
        except Exception as e:
            logger.error(f"Hiba az anomália detektálás során: {e}")

        # Rekordok
        if self.extreme_calculator:
            records = self.extreme_calculator.calculate_records_by_period(daily_data, self.period_type)
            self._display_records(records)

    def _get_thresholds(self) -> Dict[str, float]:
        """Beállítások lekérése a profil menedzsertől."""
        if self.profile_manager:
            return self.profile_manager.get_current_settings()
        
        # Fallback
        return {
            "temp_hot": 35.0, "temp_cold": -10.0,
            "precip_high": 50.0, "precip_low": 5.0,
            "wind_normal": 40.0, "wind_strong": 60.0,
            "wind_extreme": 90.0, "wind_hurricane": 110.0
        }

    def _display_anomalies(self, anomalies: Dict[str, Any]) -> None:
        """Eredmények megjelenítése a UI-n."""
        mapping = {
            "temperature": self.temp_anomaly,
            "precipitation": self.precip_anomaly,
            "wind": self.wind_anomaly
        }
        
        for cat, label in mapping.items():
            anomaly = anomalies.get(cat)
            if not anomaly:
                self._update_label(label, f"{cat.capitalize()}: Normális", "success")
            else:
                self._update_label(label, anomaly.message, anomaly.severity)

    def _update_label(self, label: Optional[QLabel], text: str, status: str) -> None:
        if not label:
            return
        label.setText(text)
        colors = {"success": "#10b981", "warning": "#f59e0b", "danger": "#ef4444", "error": "#ef4444"}
        color = colors.get(status, "#9ca3af")
        label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _display_records(self, records: List[Any]) -> None:
        if not self.extreme_table:
            return
        self.extreme_table.setRowCount(0)
        for i, rec in enumerate(records):
            self.extreme_table.insertRow(i)
            self.extreme_table.setItem(i, 0, QTableWidgetItem(str(rec.category)))
            self.extreme_table.setItem(i, 1, QTableWidgetItem(str(rec.record_type)))
            self.extreme_table.setItem(i, 2, QTableWidgetItem(str(rec.value)))
            self.extreme_table.setItem(i, 3, QTableWidgetItem(str(rec.date)))

    def _on_anomaly_settings_clicked(self) -> None:
        try:
            from src.gui.dialogs.anomaly_settings_dialog import AnomalySettingsDialog
            dialog = AnomalySettingsDialog(self)
            if dialog.exec():
                if self.current_data:
                    self.update_data(self.current_data)
        except Exception as e:
            logger.error(f"Settings dialog error: {e}")

    def _on_period_type_changed(self) -> None:
        if self.daily_radio.isChecked(): self.period_type = "daily"
        elif self.monthly_radio.isChecked(): self.period_type = "monthly"
        else: self.period_type = "yearly"
        if self.current_data:
            self.update_data(self.current_data)

    def _on_detailed_analysis_clicked(self) -> None:
        QMessageBox.information(self, "Info", "Részletes elemzés hamarosan...")

    def _register_widgets_for_theming(self) -> None:
        try:
            register_widget_for_theming(self, "container")
            register_widget_for_theming(self.title_label, "text")
        except:
            pass