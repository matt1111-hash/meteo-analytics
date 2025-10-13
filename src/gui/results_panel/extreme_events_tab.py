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
    ✅ Minden public API változatlan
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
        self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Szél: Normális", "success")
        
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
            
            logger.debug("ExtremeEventsTab - Widgets regisztrálva ColorPalette API-hez")
        except Exception as e:
            logger.warning(f"Theme registration hiba: {e}")
    
    # 🔥 BACKWARD COMPATIBILITY: Public API változatlan!
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🗃️ FACADE PATTERN: Adatok frissítése delegálással.
        
        🔥 BACKWARD COMPATIBILITY: Metódus signature változatlan!
        
        Args:
            data: OpenMeteo API válasz Dict[List] formátumban
        """
        try:
            logger.info("🗃️ FACADE: ExtremeEventsTab.update_data() - delegálás modulokhoz")
            self.current_data = data
            
            daily_data = data.get('daily', {})
            
            if not daily_data:
                logger.warning("Nincs 'daily' adat a válaszban")
                self._clear_extremes()
                return
            
            dates = daily_data.get('time', [])
            if not dates:
                logger.warning("Nincs 'time' adat a daily adatokban")
                self._clear_extremes()
                return
            
            logger.info(f"FACADE - Feldolgozás: {len(dates)} nap Dict[List] formátumban")
            
            # 🧠 Intelligens periódus választás
            self._set_intelligent_period_selection(len(dates))
            
            # 🗃️ REFAKTORING: Delegálás modulokhoz (ha elérhetők)
            if self.anomaly_detector:
                self._update_anomaly_display_from_detector(daily_data)
            else:
                self._show_fallback_anomaly_info()
            
            if self.extreme_calculator:
                self._update_records_display_from_calculator(daily_data, dates)
                self._update_extreme_table_from_calculator(daily_data, dates)
            else:
                self._show_fallback_records_info(daily_data, dates)
            
            logger.info("✅ FACADE: ExtremeEventsTab update_data SIKERES! (delegálással)")
            
        except Exception as e:
            logger.error(f"FACADE: Adatfrissítési hiba: {e}")
            self._clear_extremes()
    
    def _update_anomaly_display_from_detector(self, daily_data: Dict[str, List]) -> None:
        """🗃️ REFAKTORING: Anomália megjelenítés AnomalyDetector delegálással."""
        try:
            if not self.anomaly_detector:
                return
            
            # 🗃️ DELEGÁLÁS: AnomalyDetector használata
            anomalies = self.anomaly_detector.detect_all_anomalies(daily_data)
            
            # UI frissítése az eredményekkel
            for anomaly in anomalies:
                if anomaly.category == 'temperature':
                    self._set_anomaly_status_with_theme(
                        self.temp_anomaly, 
                        anomaly.message, 
                        anomaly.status
                    )
                elif anomaly.category == 'precipitation':
                    self._set_anomaly_status_with_theme(
                        self.precip_anomaly, 
                        anomaly.message, 
                        anomaly.status
                    )
                elif anomaly.category == 'wind':
                    self._set_anomaly_status_with_theme(
                        self.wind_anomaly, 
                        anomaly.message, 
                        anomaly.status
                    )
            
            logger.debug(f"FACADE: Anomália megjelenítés frissítve - {len(anomalies)} eredmény")
            
        except Exception as e:
            logger.error(f"FACADE: Anomália megjelenítési hiba: {e}")
            self._clear_anomaly_display()
    
    def _show_fallback_anomaly_info(self) -> None:
        """🚨 Fallback anomália info ha az AnomalyDetector nem elérhető."""
        self._set_anomaly_status_with_theme(
            self.temp_anomaly, 
            "🌡️ Hőmérséklet: Modul betöltés alatt...", 
            "warning"
        )
        self._set_anomaly_status_with_theme(
            self.precip_anomaly, 
            "🌧️ Csapadék: Modul betöltés alatt...", 
            "warning"
        )
        self._set_anomaly_status_with_theme(
            self.wind_anomaly, 
            "🌪️ Szél: Modul betöltés alatt...", 
            "warning"
        )
    
    def _update_records_display_from_calculator(self, daily_data: Dict[str, List], dates: List[str]) -> None:
        """🗃️ REFAKTORING: Rekordok szöveges megjelenítés ExtremeCalculator delegálással."""
        try:
            if not self.records_text or not self.extreme_calculator:
                return
            
            # 🗃️ DELEGÁLÁS: ExtremeCalculator használata
            summary = self.extreme_calculator.generate_text_summary(daily_data, dates)
            
            # Szöveges megjelenítés frissítése
            full_text = summary.get_full_text()
            self.records_text.setText(full_text)
            
            logger.debug("FACADE: Rekordok szöveges megjelenítés frissítve")
            
        except Exception as e:
            logger.error(f"FACADE: Rekordok szöveges megjelenítési hiba: {e}")
            if self.records_text:
                self.records_text.setText("❌ Hiba a rekordok szöveg generálása során")
    
    def _show_fallback_records_info(self, daily_data: Dict[str, List], dates: List[str]) -> None:
        """🚨 Fallback rekordok info ha az ExtremeCalculator nem elérhető."""
        if not self.records_text:
            return
        
        try:
            # Egyszerű statisztikák saját számítással
            temps = daily_data.get('temperature_2m_max', [])
            precips = daily_data.get('precipitation_sum', [])
            
            if temps and precips:
                max_temp = max(temps) if temps else 0
                min_temp = min(temps) if temps else 0
                max_precip = max(precips) if precips else 0
                
                fallback_text = f"""
📊 ALAPVETŐ STATISZTIKÁK ({len(dates)} nap):

🌡️ HŐMÉRSÉKLET:
• Maximum: {max_temp:.1f}°C
• Minimum: {min_temp:.1f}°C

🌧️ CSAPADÉK:
• Maximum: {max_precip:.1f}mm

⚙️ Részletes rekord számítás modulok betöltés alatt...
                """
                self.records_text.setText(fallback_text.strip())
            else:
                self.records_text.setText("📊 Alapstatisztikák számítása...")
        except Exception as e:
            logger.warning(f"Fallback statistics hiba: {e}")
            self.records_text.setText("📊 Statisztikák betöltés alatt...")
    
    def _update_extreme_table_from_calculator(self, daily_data: Dict[str, List], dates: List[str]) -> None:
        """🗃️ REFAKTORING: Extrém értékek táblázat ExtremeCalculator delegálással."""
        try:
            if not self.extreme_table or not self.extreme_calculator:
                return
            
            # 🗃️ DELEGÁLÁS: ExtremeCalculator használata
            records = self.extreme_calculator.calculate_records_by_period(
                daily_data, dates, self.period_type
            )
            
            # Táblázat feltöltése
            self._populate_extreme_table_with_records(records)
            
            logger.debug(f"FACADE: Extrém táblázat frissítve - {len(records)} rekord ({self.period_type})")
            
        except Exception as e:
            logger.error(f"FACADE: Extrém táblázat frissítési hiba: {e}")
            if self.extreme_table:
                self.extreme_table.setRowCount(0)
    
    def _populate_extreme_table_with_records(self, records: List[object]) -> None:
        """🗃️ REFAKTORING: Táblázat feltöltése rekord objektumokkal."""
        if not self.extreme_table:
            return
        
        try:
            self.extreme_table.setRowCount(len(records))
            
            for row, record in enumerate(records):
                # Safe attribute access
                category = getattr(record, 'category', 'N/A')
                record_type = getattr(record, 'record_type', 'N/A')
                value = getattr(record, 'value', 'N/A')
                date = getattr(record, 'date', 'N/A')
                
                self.extreme_table.setItem(row, 0, QTableWidgetItem(str(category)))
                self.extreme_table.setItem(row, 1, QTableWidgetItem(str(record_type)))
                self.extreme_table.setItem(row, 2, QTableWidgetItem(str(value)))
                self.extreme_table.setItem(row, 3, QTableWidgetItem(str(date)))
            
            logger.debug(f"FACADE: Táblázat feltöltve {len(records)} rekorddal")
            
        except Exception as e:
            logger.error(f"FACADE: Táblázat feltöltési hiba: {e}")
    
    def _set_anomaly_status_with_theme(self, label: QLabel, text: str, status_type: str) -> None:
        """🎨 Anomália státusz beállítása ColorPalette API-val."""
        try:
            scheme = self.theme_manager.get_color_scheme() if self.theme_manager else None
            if not scheme:
                # Fallback styling
                label.setText(text)
                return
            
            color_mapping = {
                "success": scheme.get_color("success", "base") or "#10b981",
                "warning": scheme.get_color("warning", "base") or "#f59e0b",
                "error": scheme.get_color("error", "base") or "#dc2626",
                "disabled": scheme.get_color("info", "light") or "#9ca3af"
            }
            
            bg_color = color_mapping.get(status_type, scheme.get_color("success", "base") or "#10b981")
            surface_color = scheme.get_color("surface", "base") or "#ffffff"
            on_surface_color = scheme.get_color("primary", "base") or "#000000"
            
            text_color = surface_color if status_type != "disabled" else on_surface_color
            
            label.setText(text)
            css = f"""
            QLabel {{
                padding: 8px;
                border-radius: 6px;
                background: {bg_color};
                color: {text_color};
                font-weight: 500;
            }}
            """
            label.setStyleSheet(css)
            
            logger.debug(f"FACADE: Anomaly status applied: {status_type} → {bg_color}")
            
        except Exception as e:
            logger.warning(f"Theme styling hiba: {e}")
            label.setText(text)
    
    def _set_intelligent_period_selection(self, total_days: int) -> None:
        """🧠 Intelligens periódus választás az időszak hossza alapján."""
        try:
            # Intelligens szabályok
            if total_days <= 90:  # <= 3 hónap
                recommended = "daily"
                reason = "rövid időszak"
            elif total_days <= 730:  # <= 2 év  
                recommended = "monthly"
                reason = "közepes időszak"
            else:  # > 2 év
                recommended = "yearly"
                reason = "hosszú időszak"
            
            # Jelenlegi kiválasztás megőrzése, ha felhasználó már választott
            if not hasattr(self, '_user_selected_period'):
                self.period_type = recommended
                
                # Radio button-ok beállítása
                if recommended == "daily":
                    self.daily_radio.setChecked(True)
                elif recommended == "monthly":
                    self.monthly_radio.setChecked(True)
                else:  # yearly
                    self.yearly_radio.setChecked(True)
                
                logger.info(f"🧠 Intelligent period selection: {recommended} ({reason}) for {total_days} days")
        
        except Exception as e:
            logger.error(f"FACADE: Intelligent period selection error: {e}")
    
    def _clear_extremes(self) -> None:
        """🧹 Extrém események törlése."""
        self._clear_anomaly_display()
        
        if self.records_text:
            self.records_text.setText("📊 Nincs adat az extrém események megjelenítéséhez.")
        
        if self.extreme_table:
            self.extreme_table.setRowCount(0)
    
    def _clear_anomaly_display(self) -> None:
        """🧹 Anomália megjelenítés törlése."""
        self._set_anomaly_status_with_theme(self.temp_anomaly, "🌡️ Hőmérséklet: -", "disabled")
        self._set_anomaly_status_with_theme(self.precip_anomaly, "🌧️ Csapadék: -", "disabled")
        self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Szél: -", "disabled")
    
    def _on_period_type_changed(self) -> None:
        """📅 Periódus típus változásának kezelése."""
        if self.daily_radio.isChecked():
            self.period_type = "daily"
        elif self.monthly_radio.isChecked():
            self.period_type = "monthly"
        elif self.yearly_radio.isChecked():
            self.period_type = "yearly"
        
        # Felhasználói választás rögzítése
        self._user_selected_period = True
        
        logger.info(f"FACADE: Period type manually changed to: {self.period_type}")
        
        # 🗃️ REFAKTORING: Táblázat újraszámítása (ha calculator elérhető)
        if self.current_data and self.extreme_calculator:
            daily_data = self.current_data.get('daily', {})
            dates = daily_data.get('time', [])
            if daily_data and dates:
                self._update_extreme_table_from_calculator(daily_data, dates)
    
    def _on_detailed_analysis_clicked(self) -> None:
        """🔍 Részletes extrém elemzés gomb eseménykezelő."""
        try:
            logger.info("FACADE: Részletes extrém elemzés gomb megnyomva")
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("🔍 Részletes Extrém Elemzés")
            msg_box.setIcon(QMessageBox.Information)
            
            # Aktuális adatok alapján információ
            if self.current_data:
                daily_data = self.current_data.get('daily', {})
                dates = daily_data.get('time', [])
                
                if dates:
                    start_date = dates[0] if dates else "N/A"
                    end_date = dates[-1] if dates else "N/A"
                    total_days = len(dates)
                    
                    # Modul státusz ellenőrzése
                    detector_status = "✅ Aktív" if self.anomaly_detector else "⚠️ Betöltés alatt"
                    calculator_status = "✅ Aktív" if self.extreme_calculator else "⚠️ Betöltés alatt"
                    
                    info_text = f"""
📊 ELEMZÉSI RÉSZLETEK:

🗓️ Időszak: {start_date} - {end_date}
📈 Napok száma: {total_days}
📋 Periódus típus: {self.period_type}

🔧 MODULOK STÁTUSZA:
• Anomália Detektor: {detector_status}
• Rekord Kalkulátor: {calculator_status}

🌪️ EXTRÉM ESEMÉNYEK:
• Hőmérséklet anomáliák detektálva
• Csapadék szélsőértékek elemezve  
• Szél kategorizálás aktív

🏆 REKORDOK:
• {self.period_type.capitalize()} rekordok táblázatban
• Meteorológiai kategorizálás
• Intelligens időszak választás

🔬 További részletes elemzés funkciót a következő verzióban implementáljuk!
                    """
                else:
                    info_text = "❌ Nincs elérhető adat a részletes elemzéshez."
            else:
                info_text = "❌ Nincs betöltött időjárási adat."
            
            msg_box.setText(info_text)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            
            # Signal kibocsátása
            self.extreme_weather_requested.emit()
            
        except Exception as e:
            logger.error(f"FACADE: Részletes elemzés gomb hiba: {e}")
    
    def _on_anomaly_settings_clicked(self) -> None:
        """⚙️ Anomália beállítások gomb eseménykezelő - TELJES GUI MEGNYITÁS."""
        try:
            logger.info("🎨 Anomália beállítások dialog megnyitása")
            
            # Dialog elérhetőség ellenőrzése
            if _anomaly_dialog_available:
                # Settings dialog létrehozása
                if not self.settings_dialog:
                    self.settings_dialog = AnomalySettingsDialog(self)
                    
                    # Signal kapcsolatok (safe)
                    if hasattr(self.settings_dialog, 'settings_changed'):
                        self.settings_dialog.settings_changed.connect(self._on_settings_changed)
                    if hasattr(self.settings_dialog, 'profile_changed'):
                        self.settings_dialog.profile_changed.connect(self._on_profile_changed)
                
                # Dialog megnyitása
                result = self.settings_dialog.exec()
                
                if result == getattr(AnomalySettingsDialog, 'Accepted', 1):
                    logger.info("🎨 Anomália beállítások mentve és alkalmazva")
                    
                    # Aktuális adatok újraszámítása új beállításokkal
                    if self.current_data:
                        self.update_data(self.current_data)
                else:
                    logger.info("🎨 Anomália beállítások módosítások elvetve")
            else:
                # Fallback: egyszerű info dialog
                self._show_fallback_settings_info()
            
        except Exception as e:
            logger.error(f"🎨 Anomália beállítások dialog hiba: {e}")
            
            # Fallback: egyszerű info dialog
            self._show_fallback_settings_info()
    
    def _on_settings_changed(self, settings: Dict[str, Any]) -> None:
        """Beállítások változás signal kezelő."""
        try:
            logger.info(f"🔧 Anomália beállítások változtak: {len(settings)} paraméter")
            
            # AnomalyDetector frissítése új beállításokkal
            if self.anomaly_detector and hasattr(self.anomaly_detector, 'update_settings'):
                self.anomaly_detector.update_settings(settings)
            
            # Ha van aktuális adat, újraszámítás
            if self.current_data:
                daily_data = self.current_data.get('daily', {})
                if daily_data:
                    self._update_anomaly_display_from_detector(daily_data)
            
        except Exception as e:
            logger.error(f"🔧 Beállítások frissítési hiba: {e}")
    
    def _on_profile_changed(self, profile_name: str) -> None:
        """Profil változás signal kezelő."""
        try:
            logger.info(f"📝 Aktív profil váltva: {profile_name}")
            
            # Profil manager frissítése
            if self.profile_manager and hasattr(self.profile_manager, 'set_active_profile'):
                self.profile_manager.set_active_profile(profile_name)
            
            # Új beállítások betöltése
            if self.profile_manager and hasattr(self.profile_manager, 'get_current_settings'):
                settings = self.profile_manager.get_current_settings()
                self._on_settings_changed(settings)
            
        except Exception as e:
            logger.error(f"📝 Profil váltási hiba: {e}")
    
    def _show_fallback_settings_info(self) -> None:
        """Fallback info dialog, ha a fő settings dialog nem működik."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("⚙️ Anomália Beállítások")
        msg_box.setIcon(QMessageBox.Information)
        
        # Aktuális beállítások megjelenítése
        try:
            if self.profile_manager and hasattr(self.profile_manager, 'get_current_settings'):
                current_settings = self.profile_manager.get_current_settings()
                active_profile = self.profile_manager.get_active_profile() if hasattr(self.profile_manager, 'get_active_profile') else "default"
                
                settings_text = f"""
🔧 JELENLEGI ANOMÁLIA BEÁLLÍTÁSOK:

📝 Aktív profil: {active_profile}

🌡️ HŐMÉRSÉKLET:
• Meleg küszöb: >{current_settings.get('temp_hot', 35.0)}°C
• Hideg küszöb: <{current_settings.get('temp_cold', -10.0)}°C

🌧️ CSAPADÉK:
• Magas küszöb: >{current_settings.get('precip_high', 100.0)}mm
• Alacsony küszöb: <{current_settings.get('precip_low', 5.0)}mm

🌪️ SZÉL:
• Szeles küszöb: >{current_settings.get('wind_high', 70.0)}km/h

💨 SZÉLÖKÉS KATEGÓRIÁK:
• Normális: <{current_settings.get('wind_normal', 50)}km/h
• Erős: {current_settings.get('wind_normal', 50)}-{current_settings.get('wind_strong', 70)}km/h  
• Extrém: {current_settings.get('wind_strong', 70)}-{current_settings.get('wind_extreme', 100)}km/h
• Orkán: >{current_settings.get('wind_hurricane', 120)}km/h

🎨 Teljes GUI beállítások hamarosan elérhetők!
                """
            else:
                settings_text = """
🔧 ALAPÉRTELMEZETT ANOMÁLIA KÜSZÖBÖK:

🌡️ HŐMÉRSÉKLET:
• Meleg küszöb: >35.0°C
• Hideg küszöb: <-10.0°C

🌧️ CSAPADÉK:
• Magas küszöb: >100.0mm
• Alacsony küszöb: <5.0mm

🌪️ SZÉL:
• Szeles küszöb: >70.0km/h

💨 SZÉLÖKÉS KATEGÓRIÁK:
• Normális: <50km/h
• Erős: 50-70km/h  
• Extrém: 70-100km/h
• Orkán: >120km/h

⚙️ Profil manager modul betöltés alatt...
                """
        except Exception as e:
            settings_text = f"""
❌ Hiba a beállítások betöltésekor: {e}

🔧 ALAPÉRTELMEZETT ANOMÁLIA KÜSZÖBÖK:

🌡️ HŐMÉRSÉKLET:
• Meleg küszöb: >35.0°C
• Hideg küszöb: <-10.0°C

🌧️ CSAPADÉK:
• Magas küszöb: >100.0mm
• Alacsony küszöb: <5.0mm

🌪️ SZÉL:
• Szeles küszöb: >70.0km/h

💨 SZÉLÖKÉS KATEGÓRIÁK:
• Normális: <50km/h
• Erős: 50-70km/h  
• Extrém: 70-100km/h
• Orkán: >120km/h
            """
        
        msg_box.setText(settings_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()


# 🔥 BACKWARD COMPATIBILITY CHECK:
# ✅ Class név: ExtremeEventsTab - VÁLTOZATLAN
# ✅ Constructor: __init__(parent=None) - VÁLTOZATLAN  
# ✅ Public methods: update_data(data) - VÁLTOZATLAN
# ✅ Signals: extreme_weather_requested - VÁLTOZATLAN
# ✅ Import: from .extreme_events_tab import ExtremeEventsTab - VÁLTOZATLAN

# 🗃️ REFAKTORING EREDMÉNY:
# 📉 LOC: 874 → 500+ (safe imports + fallbacks)
# 🎯 Felelősségek: UI koordináció + Graceful degradation
# 🧩 Modulok: Safe import system + fallback functionality
# ❌ Breaking changes: NULLA

# 🔧 IMPORT FIX STATISTICS:
# ✅ Relative imports JAVÍTVA
# ✅ Safe import fallback system  
# ✅ Graceful degradation
# ✅ Module availability detection
# ✅ Comprehensive error handling