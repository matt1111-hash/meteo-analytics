#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Extreme Events Tab Module
🌪️ KRITIKUS JAVÍTÁS: "Extrém Események" TAB - Dict[List] adatformátum támogatás
🎨 KRITIKUS JAVÍTÁS: ColorPalette API integráció - scheme.success → scheme.get_color("success", "base")
🚨 ESEMÉNYKEZELŐ JAVÍTÁS: Hiányzó _on_detailed_analysis_clicked() és _on_anomaly_settings_clicked() hozzáadva
Anomáliák és rekordok kezelése élethű széllökés értékekkel.

🚀 PROFESSZIONÁLIS KÓDOLÁSI ELVEK:
✅ DRY: WindGustsAnalyzer utility osztály használata
✅ KISS: Egyszerű, érthető anomália detektálás
✅ SOLID: Single Responsibility - csak UI logika
✅ Type hints: Minden metódus explicit típusokkal
✅ Error handling: Robusztus kivételkezelés
✅ Logging: Strukturált hibakövetés
✅ Dict[List] adatformátum natív támogatása
✅ Eseménykezelők: Minden gomb bekötve
"""

import logging
from typing import Optional, Dict, Any, List, Union, Tuple
import pandas as pd
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSplitter,
    QGroupBox, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QProgressBar, QFrame, QScrollArea, QGridLayout, QTextEdit,
    QButtonGroup, QRadioButton, QHeaderView, QMessageBox  # ÚJ: QMessageBox az eseménykezelőkhez
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from ...config import GUIConfig
from ..utils import GUIConstants, AnomalyConstants  # AnomalyConstants a fő utils.py-ból
from ..theme_manager import get_theme_manager, register_widget_for_theming
from .utils import WindGustsConstants, DataFrameExtractor, WindGustsAnalyzer

# Logging konfigurálása
logger = logging.getLogger(__name__)


class ExtremeEventsTab(QWidget):
    """
    🌪️ KRITIKUS JAVÍTÁS: "Extrém Események" TAB - Dict[List] adatformátum támogatás
    🎨 KRITIKUS JAVÍTÁS: ColorPalette API integráció - scheme.success → scheme.get_color("success", "base")
    🚨 ESEMÉNYKEZELŐ JAVÍTÁS: Hiányzó _on_detailed_analysis_clicked() és _on_anomaly_settings_clicked() hozzáadva
    Anomáliák és rekordok kezelése élethű széllökés értékekkel.
    
    🚀 PROFESSZIONÁLIS KÓDOLÁSI ELVEK:
    ✅ DRY: WindGustsAnalyzer utility osztály használata
    ✅ KISS: Egyszerű, érthető anomália detektálás
    ✅ SOLID: Single Responsibility - csak UI logika
    ✅ Type hints: Minden metódus explicit típusokkal
    ✅ Error handling: Robusztus kivételkezelés
    ✅ Logging: Strukturált hibakövetés
    ✅ Dict[List] adatformátum natív támogatása
    ✅ Eseménykezelők: Minden gomb bekötve
    """
    
    extreme_weather_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.theme_manager = get_theme_manager()
        
        self.current_data: Optional[Dict[str, Any]] = None
        self.temp_anomaly: Optional[QLabel] = None
        self.precip_anomaly: Optional[QLabel] = None
        self.wind_anomaly: Optional[QLabel] = None
        self.records_text: Optional[QTextEdit] = None
        self.extreme_table: Optional[QTableWidget] = None
        self.period_type: str = "daily"  # Alapértelmezett: napi rekordok
        
        self._init_ui()
        self._register_widgets_for_theming()
        
        logger.info("ExtremeEventsTab Dict[List] adatformátum támogatással inicializálva")
    
    def _init_ui(self) -> None:
        """UI inicializálása."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        self.title_label = QLabel("⚡ Extrém Időjárási Események")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        self.anomaly_section = self._create_anomaly_section()
        layout.addWidget(self.anomaly_section)
        
        self.records_section = self._create_records_section()
        layout.addWidget(self.records_section)
        
        actions_section = self._create_actions_section()
        layout.addWidget(actions_section)
        
        layout.addStretch()
    
    def _create_anomaly_section(self) -> QGroupBox:
        """Anomália detektálás szekció."""
        section = QGroupBox("🔍 Anomália Detektálás")
        
        layout = QVBoxLayout(section)
        
        indicators_layout = QGridLayout()
        
        self.temp_anomaly = QLabel("🌡️ Hőmérséklet: Normális")
        indicators_layout.addWidget(self.temp_anomaly, 0, 0)
        
        self.precip_anomaly = QLabel("🌧️ Csapadék: Normális")
        indicators_layout.addWidget(self.precip_anomaly, 0, 1)
        
        # 🌪️ KRITIKUS JAVÍTÁS: Széllökés anomália cím frissítése
        self.wind_anomaly = QLabel("🌪️ Széllökések: Normális")
        indicators_layout.addWidget(self.wind_anomaly, 0, 2)
        
        layout.addLayout(indicators_layout)
        
        # 🎨 KRITIKUS JAVÍTÁS: Inicializálás ColorPalette API-val
        self._set_anomaly_status_with_theme(self.temp_anomaly, "🌡️ Hőmérséklet: Normális", "success")
        self._set_anomaly_status_with_theme(self.precip_anomaly, "🌧️ Csapadék: Normális", "success")
        self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Széllökések: Normális", "success")
        
        return section
    
    def _create_records_section(self) -> QGroupBox:
        """Rekordok kimutatása szekció - HAVI/NAPI TÁBLÁZATTAL."""
        section = QGroupBox("🏆 Rekordok és Szélsőértékek")
        
        layout = QVBoxLayout(section)
        
        # === PERIÓDUS KIVÁLASZTÓ ===
        period_group = self._create_period_selection_group()
        layout.addWidget(period_group)
        
        # === EXTRÉM ÉRTÉKEK TÁBLÁZATA ===
        self.extreme_table = self._create_extreme_table()
        layout.addWidget(self.extreme_table)
        
        # === SZÖVEGES ÖSSZEFOGLALÓ (megtartva) ===
        self.records_text = QTextEdit()
        self.records_text.setMaximumHeight(80)
        self.records_text.setReadOnly(True)
        layout.addWidget(self.records_text)
        
        return section
    
    def _create_period_selection_group(self) -> QGroupBox:
        """Periódus kiválasztó widget létrehozása - INTELLIGENS IDŐSZAK VÁLASZTÁS."""
        period_group = QGroupBox("📅 Időszak típusa")
        period_layout = QHBoxLayout(period_group)
        
        # Gomb csoport a kölcsönös kizáráshoz
        from PySide6.QtWidgets import QButtonGroup, QRadioButton
        self.period_type_group = QButtonGroup()
        
        # Radio gombok - INTELLIGENS VÁLASZTÁS
        self.daily_radio = QRadioButton("📊 Napi rekordok")
        self.monthly_radio = QRadioButton("📅 Havi rekordok") 
        self.yearly_radio = QRadioButton("🗓️ Éves rekordok")  # ÚJ!
        
        # Intelligens alapértelmezett kiválasztás (később beállítjuk)
        self.daily_radio.setChecked(True)
        self.period_type = "daily"
        
        # Gombok hozzáadása a csoporthoz
        self.period_type_group.addButton(self.daily_radio)
        self.period_type_group.addButton(self.monthly_radio)
        self.period_type_group.addButton(self.yearly_radio)
        
        # Layout-hoz adás
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
        """Extrém értékek táblázatának létrehozása."""
        from PySide6.QtWidgets import QTableWidget, QHeaderView
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["📊 Kategória", "🏆 Rekord típus", "📈 Érték", "📅 Dátum"])
        
        # Táblázat beállítások
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.verticalHeader().setVisible(False)
        
        # Oszlop szélességek
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Kategória
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Rekord típus
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Érték
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Dátum
        
        table.setMinimumHeight(200)
        
        return table
    
    def _create_actions_section(self) -> QWidget:
        """Akciók szekció - BEKÖTÖTT ESEMÉNYKEZELŐKKEL."""
        container = QWidget()
        layout = QHBoxLayout(container)
        
        self.detailed_btn = QPushButton("🔍 Részletes Extrém Elemzés")
        self.detailed_btn.clicked.connect(self._on_detailed_analysis_clicked)  # BEKÖTVE
        layout.addWidget(self.detailed_btn)
        
        self.settings_btn = QPushButton("⚙️ Anomália Beállítások")
        self.settings_btn.clicked.connect(self._on_anomaly_settings_clicked)  # BEKÖTVE
        layout.addWidget(self.settings_btn)
        
        layout.addStretch()
        
        return container
    
    def _set_anomaly_status_with_theme(self, label: QLabel, text: str, status_type: str) -> None:
        """
        🎨 KRITIKUS JAVÍTÁS: Anomália státusz beállítása ColorPalette API-val.
        scheme.success → scheme.get_color("success", "base")
        
        Args:
            label: Anomália label
            text: Megjelenítendő szöveg
            status_type: Státusz típus (success, warning, error, disabled)
        """
        scheme = self.theme_manager.get_color_scheme()
        if not scheme:
            return
        
        # 🎨 KRITIKUS JAVÍTÁS: ColorPalette API használata scheme.attribute helyett
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
        
        logger.debug(f"Anomaly status applied: {status_type} → {bg_color}")
    
    def _register_widgets_for_theming(self) -> None:
        """Widget-ek regisztrálása ThemeManager-hez."""
        register_widget_for_theming(self, "container")
        register_widget_for_theming(self.anomaly_section, "container")
        register_widget_for_theming(self.records_section, "container")
        register_widget_for_theming(self.title_label, "text")
        register_widget_for_theming(self.records_text, "input")
        register_widget_for_theming(self.detailed_btn, "button")
        register_widget_for_theming(self.settings_btn, "button")
        
        # ÚJ: Táblázat és radio button-ok regisztrálása
        if hasattr(self, 'extreme_table') and self.extreme_table:
            register_widget_for_theming(self.extreme_table, "table")
        if hasattr(self, 'daily_radio') and self.daily_radio:
            register_widget_for_theming(self.daily_radio, "chart")
        if hasattr(self, 'monthly_radio') and self.monthly_radio:
            register_widget_for_theming(self.monthly_radio, "chart")
        if hasattr(self, 'yearly_radio') and self.yearly_radio:
            register_widget_for_theming(self.yearly_radio, "chart")
        
        logger.debug("ExtremeEventsTab - Összes widget regisztrálva ColorPalette API-hez")
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🌪️ KRITIKUS JAVÍTÁS: Extrém események adatok frissítése Dict[List] formátummal
        
        Args:
            data: OpenMeteo API válasz Dict[List] formátumban
        """
        try:
            logger.info("🌪️ KRITIKUS JAVÍTÁS: ExtremeEventsTab.update_data() - Dict[List] formátum")
            self.current_data = data
            
            # 🎯 KRITIKUS JAVÍTÁS: Közvetlen Dict[List] adatfeldolgozás
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
            
            logger.info(f"ExtremeEventsTab - Feldolgozás: {len(dates)} nap Dict[List] formátumban")
            
            # 🎯 INTELLIGENS PERIÓDUS VÁLASZTÁS az időszak hossza alapján
            self._set_intelligent_period_selection(len(dates))
            
            # 🌪️ KRITIKUS JAVÍTÁS: Anomália és rekord detektálás Dict[List] adatokkal
            self._detect_anomalies_from_dict(daily_data)
            self._find_records_from_dict(daily_data, dates)
            self._calculate_extremes()  # ÚJ: Táblázatos rekordok számítása
            
            logger.info("✅ ExtremeEventsTab update_data SIKERES! (Dict[List] formátum)")
            
        except Exception as e:
            logger.error(f"ExtremeEventsTab adatfrissítési hiba: {e}")
            self._clear_extremes()
    
    def _detect_anomalies_from_dict(self, daily_data: Dict[str, List]) -> None:
        """
        🌪️ KRITIKUS JAVÍTÁS: Anomália detektálás Dict[List] adatokból
        """
        try:
            # Hőmérséklet anomália
            self._detect_temperature_anomaly_from_dict(daily_data)
            
            # Csapadék anomália
            self._detect_precipitation_anomaly_from_dict(daily_data)
            
            # 🌪️ KRITIKUS JAVÍTÁS: Széllökés anomália Dict[List] formátumból
            self._detect_wind_anomaly_from_dict(daily_data)
            
        except Exception as e:
            logger.error(f"Anomália detektálási hiba (Dict[List]): {e}")
            self._clear_extremes()
    
    def _detect_temperature_anomaly_from_dict(self, daily_data: Dict[str, List]) -> None:
        """Hőmérséklet anomália detektálás Dict[List] adatokból."""
        try:
            temp_max_list = daily_data.get('temperature_2m_max', [])
            temp_min_list = daily_data.get('temperature_2m_min', [])
            
            if temp_max_list and temp_min_list:
                # None értékek kiszűrése
                clean_max = [t for t in temp_max_list if t is not None]
                clean_min = [t for t in temp_min_list if t is not None]
                
                if clean_max and clean_min:
                    avg_temp = (sum(clean_max) / len(clean_max) + sum(clean_min) / len(clean_min)) / 2
                    
                    if avg_temp > AnomalyConstants.TEMP_HOT_THRESHOLD:
                        self._set_anomaly_status_with_theme(self.temp_anomaly, "🔥 Hőmérséklet: Szokatlanul meleg", "error")
                    elif avg_temp < AnomalyConstants.TEMP_COLD_THRESHOLD:
                        self._set_anomaly_status_with_theme(self.temp_anomaly, "🧊 Hőmérséklet: Szokatlanul hideg", "warning")
                    else:
                        self._set_anomaly_status_with_theme(self.temp_anomaly, "🌡️ Hőmérséklet: Normális", "success")
                else:
                    self._set_anomaly_status_with_theme(self.temp_anomaly, "🌡️ Hőmérséklet: Nincs adat", "disabled")
            else:
                self._set_anomaly_status_with_theme(self.temp_anomaly, "🌡️ Hőmérséklet: Nincs adat", "disabled")
        except Exception as e:
            logger.error(f"Hőmérséklet anomália detektálási hiba: {e}")
            self._set_anomaly_status_with_theme(self.temp_anomaly, "🌡️ Hőmérséklet: Hiba", "disabled")
    
    def _detect_precipitation_anomaly_from_dict(self, daily_data: Dict[str, List]) -> None:
        """Csapadék anomália detektálás Dict[List] adatokból."""
        try:
            precip_list = daily_data.get('precipitation_sum', [])
            
            if precip_list:
                # None értékek kiszűrése
                clean_precip = [p for p in precip_list if p is not None]
                
                if clean_precip:
                    total_precip = sum(clean_precip)
                    
                    if total_precip > AnomalyConstants.PRECIP_HIGH_THRESHOLD:
                        self._set_anomaly_status_with_theme(self.precip_anomaly, "🌊 Csapadék: Szokatlanul csapadékos", "warning")
                    elif total_precip < AnomalyConstants.PRECIP_LOW_THRESHOLD:
                        self._set_anomaly_status_with_theme(self.precip_anomaly, "🏜️ Csapadék: Szokatlanul száraz", "error")
                    else:
                        self._set_anomaly_status_with_theme(self.precip_anomaly, "🌧️ Csapadék: Normális", "success")
                else:
                    self._set_anomaly_status_with_theme(self.precip_anomaly, "🌧️ Csapadék: Nincs adat", "disabled")
            else:
                self._set_anomaly_status_with_theme(self.precip_anomaly, "🌧️ Csapadék: Nincs adat", "disabled")
        except Exception as e:
            logger.error(f"Csapadék anomália detektálási hiba: {e}")
            self._set_anomaly_status_with_theme(self.precip_anomaly, "🌧️ Csapadék: Hiba", "disabled")
    
    def _detect_wind_anomaly_from_dict(self, daily_data: Dict[str, List]) -> None:
        """
        🌪️ KRITIKUS JAVÍTÁS: Széllökés anomália detektálás Dict[List] adatokból
        """
        try:
            # 🌪️ PRIORITÁS: wind_gusts_max → windspeed_10m_max → windspeed (kompatibilitás)
            wind_gusts_max = daily_data.get('wind_gusts_max', [])
            windspeed_10m_max = daily_data.get('windspeed_10m_max', [])
            windspeed = daily_data.get('windspeed', [])  # kompatibilitási kulcs
            
            wind_data = None
            wind_source = "no_data"
            
            if wind_gusts_max:
                wind_data = wind_gusts_max
                wind_source = "wind_gusts_max"
                logger.debug("Wind data source: wind_gusts_max")
            elif windspeed_10m_max:
                wind_data = windspeed_10m_max
                wind_source = "windspeed_10m_max"
                logger.debug("Wind data source: windspeed_10m_max")
            elif windspeed:
                wind_data = windspeed
                wind_source = "windspeed"
                logger.debug("Wind data source: windspeed (kompatibilitás)")
            
            if wind_data:
                # None értékek kiszűrése
                clean_wind = [w for w in wind_data if w is not None]
                
                if clean_wind:
                    avg_wind = sum(clean_wind) / len(clean_wind)
                    max_wind = max(clean_wind)
                    
                    logger.info(f"Wind anomaly detection - Source: {wind_source}, Avg: {avg_wind:.1f}, Max: {max_wind:.1f}")
                    
                    # 🌪️ KRITIKUS JAVÍTÁS: Élethű széllökés küszöbök
                    if wind_source == 'wind_gusts_max':
                        category = WindGustsAnalyzer.categorize_wind_gust(max_wind, wind_source)
                        description = WindGustsAnalyzer.generate_wind_description(max_wind, category, wind_source)
                        
                        if category == 'hurricane':
                            self._set_anomaly_status_with_theme(self.wind_anomaly, f"🚨 Széllökések: {description}", "error")
                        elif category == 'extreme':
                            self._set_anomaly_status_with_theme(self.wind_anomaly, f"⚠️ Széllökések: {description}", "error")
                        elif category == 'strong':
                            self._set_anomaly_status_with_theme(self.wind_anomaly, f"🌪️ Széllökések: {description}", "warning")
                        else:
                            self._set_anomaly_status_with_theme(self.wind_anomaly, f"🌪️ Széllökések: {description}", "success")
                    else:
                        # windspeed_10m_max vagy windspeed esetén eredeti küszöbök
                        if avg_wind > AnomalyConstants.WIND_HIGH_THRESHOLD:
                            self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Szél: Szokatlanul szeles", "error")
                        else:
                            self._set_anomaly_status_with_theme(self.wind_anomaly, "💨 Szél: Normális", "success")
                else:
                    self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Széllökések: Nincs adat", "disabled")
            else:
                self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Széllökések: Nincs adat", "disabled")
        except Exception as e:
            logger.error(f"Széllökés anomália detektálási hiba: {e}")
            self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Széllökések: Hiba", "disabled")
    
    def _find_records_from_dict(self, daily_data: Dict[str, List], dates: List[str]) -> None:
        """
        🌪️ KRITIKUS JAVÍTÁS: Rekordok meghatározása Dict[List] adatokból
        """
        try:
            if not self.records_text:
                return
            
            records_text = "📊 IDŐJÁRÁSI REKORDOK ÉS SZÉLSŐÉRTÉKEK\n"
            records_text += "=" * 50 + "\n\n"
            
            # Hőmérséklet rekordok
            records_text += self._generate_temperature_records_from_dict(daily_data, dates)
            
            # Csapadék rekordok
            records_text += self._generate_precipitation_records_from_dict(daily_data, dates)
            
            # 🌪️ KRITIKUS JAVÍTÁS: Széllökés rekordok Dict[List] adatokból
            records_text += self._generate_wind_records_from_dict(daily_data, dates)
            
            self.records_text.setText(records_text)
            
        except Exception as e:
            logger.error(f"Rekordok meghatározási hiba (Dict[List]): {e}")
            if self.records_text:
                self.records_text.setText("❌ Hiba a rekordok számítása során - nincs megfelelő adat")
    
    def _generate_temperature_records_from_dict(self, daily_data: Dict[str, List], dates: List[str]) -> str:
        """Hőmérséklet rekordok generálása Dict[List] adatokból."""
        try:
            temp_max_list = daily_data.get('temperature_2m_max', [])
            temp_min_list = daily_data.get('temperature_2m_min', [])
            
            if temp_max_list and temp_min_list and len(temp_max_list) == len(dates) and len(temp_min_list) == len(dates):
                # None értékek kezelése
                clean_max = [(i, t) for i, t in enumerate(temp_max_list) if t is not None]
                clean_min = [(i, t) for i, t in enumerate(temp_min_list) if t is not None]
                
                if clean_max and clean_min:
                    max_temp_idx, max_temp = max(clean_max, key=lambda x: x[1])
                    min_temp_idx, min_temp = min(clean_min, key=lambda x: x[1])
                    
                    records_text = f"🌡️ HŐMÉRSÉKLET REKORDOK:\n"
                    records_text += f"   🔥 Legmelegebb nap: {max_temp:.1f}°C ({dates[max_temp_idx]})\n"
                    records_text += f"   🧊 Leghidegebb nap: {min_temp:.1f}°C ({dates[min_temp_idx]})\n"
                    records_text += f"   📈 Hőingás: {max_temp - min_temp:.1f}°C\n\n"
                    return records_text
                else:
                    return f"🌡️ HŐMÉRSÉKLET REKORDOK: Nincs megfelelő adat\n\n"
            else:
                return f"🌡️ HŐMÉRSÉKLET REKORDOK: Nincs hőmérséklet adat\n\n"
        except Exception as e:
            logger.error(f"Hőmérséklet rekordok hiba: {e}")
            return f"🌡️ HŐMÉRSÉKLET REKORDOK: Hiba a számítás során\n\n"
    
    def _generate_precipitation_records_from_dict(self, daily_data: Dict[str, List], dates: List[str]) -> str:
        """Csapadék rekordok generálása Dict[List] adatokból."""
        try:
            precip_list = daily_data.get('precipitation_sum', [])
            
            if precip_list and len(precip_list) == len(dates):
                # None értékek kezelése
                clean_precip = [(i, p) for i, p in enumerate(precip_list) if p is not None]
                
                if clean_precip:
                    max_precip_idx, max_precip = max(clean_precip, key=lambda x: x[1])
                    dry_days = len([p for p in precip_list if p is not None and p <= 0.1])
                    total_precip = sum([p for p in precip_list if p is not None])
                    
                    records_text = f"🌧️ CSAPADÉK REKORDOK:\n"
                    records_text += f"   💧 Legtöbb csapadék: {max_precip:.1f}mm ({dates[max_precip_idx]})\n"
                    records_text += f"   🏜️ Száraz napok: {dry_days} nap\n"
                    records_text += f"   📊 Összes csapadék: {total_precip:.1f}mm\n\n"
                    return records_text
                else:
                    return f"🌧️ CSAPADÉK REKORDOK: Nincs csapadék adat\n\n"
            else:
                return f"🌧️ CSAPADÉK REKORDOK: Nincs csapadék adat\n\n"
        except Exception as e:
            logger.error(f"Csapadék rekordok hiba: {e}")
            return f"🌧️ CSAPADÉK REKORDOK: Hiba a számítás során\n\n"
    
    def _generate_wind_records_from_dict(self, daily_data: Dict[str, List], dates: List[str]) -> str:
        """
        🌪️ KRITIKUS JAVÍTÁS: Széllökés rekordok Dict[List] adatokból
        """
        try:
            # 🌪️ PRIORITÁS: wind_gusts_max → windspeed_10m_max → windspeed
            wind_gusts_max = daily_data.get('wind_gusts_max', [])
            windspeed_10m_max = daily_data.get('windspeed_10m_max', [])
            windspeed = daily_data.get('windspeed', [])
            
            wind_data = None
            wind_source = "no_data"
            
            if wind_gusts_max and len(wind_gusts_max) == len(dates):
                wind_data = wind_gusts_max
                wind_source = "wind_gusts_max"
            elif windspeed_10m_max and len(windspeed_10m_max) == len(dates):
                wind_data = windspeed_10m_max
                wind_source = "windspeed_10m_max"
            elif windspeed and len(windspeed) == len(dates):
                wind_data = windspeed
                wind_source = "windspeed"
            
            if wind_data:
                # None értékek kezelése
                clean_wind = [(i, w) for i, w in enumerate(wind_data) if w is not None]
                
                if clean_wind:
                    max_wind_idx, max_wind_value = max(clean_wind, key=lambda x: x[1])
                    avg_wind = sum([w for w in wind_data if w is not None]) / len([w for w in wind_data if w is not None])
                    
                    # 🌪️ KRITIKUS JAVÍTÁS: Széllökés cím és kategorizálás
                    if wind_source == 'wind_gusts_max':
                        category = WindGustsAnalyzer.categorize_wind_gust(max_wind_value, wind_source)
                        
                        records_text = f"🌪️ SZÉLLÖKÉS REKORDOK:\n"
                        records_text += f"   🚨 Legerősebb széllökés: {max_wind_value:.1f}km/h ({dates[max_wind_idx]})\n"
                        
                        if category == 'hurricane':
                            records_text += f"   ⚠️ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]} (>{WindGustsConstants.HURRICANE_THRESHOLD:.0f} km/h)\n"
                        elif category == 'extreme':
                            records_text += f"   ⚠️ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]} (>{WindGustsConstants.EXTREME_THRESHOLD:.0f} km/h)\n"
                        elif category == 'strong':
                            records_text += f"   ⚠️ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]} (>{WindGustsConstants.STRONG_THRESHOLD:.0f} km/h)\n"
                        else:
                            records_text += f"   ✅ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]}\n"
                    else:
                        records_text = f"💨 SZÉL REKORDOK:\n"
                        records_text += f"   🌪️ Legerősebb szél: {max_wind_value:.1f}km/h ({dates[max_wind_idx]})\n"
                    
                    records_text += f"   📊 Átlagos szélsebesség: {avg_wind:.1f}km/h\n"
                    records_text += f"   📈 Adatforrás: {wind_source}\n\n"
                    
                    logger.info(f"Wind records - Source: {wind_source}, Max: {max_wind_value:.1f} km/h")
                    
                    return records_text
                else:
                    return f"🌪️ SZÉLLÖKÉS REKORDOK: Nincs szél adat\n\n"
            else:
                return f"🌪️ SZÉLLÖKÉS REKORDOK: Nincs szél adat\n\n"
        except Exception as e:
            logger.error(f"Széllökés rekordok hiba: {e}")
            return f"🌪️ SZÉLLÖKÉS REKORDOK: Hiba a számítás során\n\n"
    
    def _clear_extremes(self) -> None:
        """Extrém események törlése."""
        self._set_anomaly_status_with_theme(self.temp_anomaly, "🌡️ Hőmérséklet: -", "disabled")
        self._set_anomaly_status_with_theme(self.precip_anomaly, "🌧️ Csapadék: -", "disabled")
        self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Széllökések: -", "disabled")
        
        if self.records_text:
            self.records_text.setText("📊 Nincs adat az extrém események megjelenítéséhez.")
        
        if self.extreme_table:
            self.extreme_table.setRowCount(0)
    
    def _on_period_type_changed(self) -> None:
        """Periódus típus változásának kezelése - FELHASZNÁLÓI VÁLASZTÁS KÖVETÉSE."""
        if self.daily_radio.isChecked():
            self.period_type = "daily"
        elif self.monthly_radio.isChecked():
            self.period_type = "monthly"
        elif self.yearly_radio.isChecked():
            self.period_type = "yearly"
        
        # Felhasználói választás rögzítése
        self._user_selected_period = True
        
        logger.info(f"Period type manually changed to: {self.period_type}")
        self._calculate_extremes()
    
    def _set_intelligent_period_selection(self, total_days: int) -> None:
        """
        🧠 INTELLIGENS periódus választás az időszak hossza alapján.
        
        Args:
            total_days: Összes napok száma
        """
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
                
                # Információs tooltip a felhasználónak
                period_names = {"daily": "napi", "monthly": "havi", "yearly": "éves"}
                self.period_type_group.buttons()[0].setToolTip(f"Automatikusan {period_names[recommended]} választva ({total_days} nap)")
        
        except Exception as e:
            logger.error(f"Intelligent period selection error: {e}")
    
    def _calculate_extremes(self) -> None:
        """
        🏆 Extrém időjárási értékek kiszámítása és táblázat frissítése.
        Havi és napi rekordok számítása az aktuális adatokból.
        """
        if not self.current_data or not self.extreme_table:
            return
        
        try:
            daily_data = self.current_data.get('daily', {})
            if not daily_data:
                return
            
            dates = daily_data.get('time', [])
            if not dates:
                return
            
            logger.info(f"Calculating {self.period_type} extremes for {len(dates)} days")
            
            # Táblázat törlése
            self.extreme_table.setRowCount(0)
            
            if self.period_type == "daily":
                self._calculate_daily_extremes(daily_data, dates)
            elif self.period_type == "monthly":
                self._calculate_monthly_extremes(daily_data, dates)
            else:  # yearly
                self._calculate_yearly_extremes(daily_data, dates)
                
        except Exception as e:
            logger.error(f"Extremes calculation error: {e}")
    
    def _calculate_daily_extremes(self, daily_data: Dict[str, List], dates: List[str]) -> None:
        """
        📊 Napi extrém értékek számítása és táblázat feltöltése.
        """
        extremes = []
        
        try:
            # === HŐMÉRSÉKLET REKORDOK ===
            temp_max_list = daily_data.get('temperature_2m_max', [])
            temp_min_list = daily_data.get('temperature_2m_min', [])
            
            if temp_max_list and len(temp_max_list) == len(dates):
                clean_max = [(i, t) for i, t in enumerate(temp_max_list) if t is not None]
                if clean_max:
                    max_idx, max_temp = max(clean_max, key=lambda x: x[1])
                    extremes.append(("🌡️ Hőmérséklet", "🔥 Legmelegebb nap", f"{max_temp:.1f}°C", dates[max_idx]))
            
            if temp_min_list and len(temp_min_list) == len(dates):
                clean_min = [(i, t) for i, t in enumerate(temp_min_list) if t is not None]
                if clean_min:
                    min_idx, min_temp = min(clean_min, key=lambda x: x[1])
                    extremes.append(("🌡️ Hőmérséklet", "🧊 Leghidegebb nap", f"{min_temp:.1f}°C", dates[min_idx]))
            
            # Legnagyobb napi hőingás
            if temp_max_list and temp_min_list:
                daily_ranges = []
                for i in range(min(len(temp_max_list), len(temp_min_list))):
                    if temp_max_list[i] is not None and temp_min_list[i] is not None:
                        daily_range = temp_max_list[i] - temp_min_list[i]
                        daily_ranges.append((i, daily_range))
                
                if daily_ranges:
                    max_range_idx, max_range = max(daily_ranges, key=lambda x: x[1])
                    extremes.append(("🌡️ Hőmérséklet", "📊 Legnagyobb napi hőingás", f"{max_range:.1f}°C", dates[max_range_idx]))
            
            # === CSAPADÉK REKORDOK ===
            precip_list = daily_data.get('precipitation_sum', [])
            if precip_list and len(precip_list) == len(dates):
                clean_precip = [(i, p) for i, p in enumerate(precip_list) if p is not None]
                if clean_precip:
                    max_precip_idx, max_precip = max(clean_precip, key=lambda x: x[1])
                    extremes.append(("🌧️ Csapadék", "💧 Legcsapadékosabb nap", f"{max_precip:.1f}mm", dates[max_precip_idx]))
            
            # === SZÉLLÖKÉS REKORDOK ===
            wind_data = daily_data.get('wind_gusts_max', []) or daily_data.get('windspeed_10m_max', [])
            wind_source = "wind_gusts_max" if daily_data.get('wind_gusts_max') else "windspeed_10m_max"
            
            if wind_data and len(wind_data) == len(dates):
                clean_wind = [(i, w) for i, w in enumerate(wind_data) if w is not None]
                if clean_wind:
                    max_wind_idx, max_wind = max(clean_wind, key=lambda x: x[1])
                    
                    # Kategória meghatározása
                    if wind_source == 'wind_gusts_max':
                        category = WindGustsAnalyzer.categorize_wind_gust(max_wind, wind_source)
                        category_info = WindGustsConstants.CATEGORIES.get(category, 'ISMERETLEN')
                        extremes.append(("🌪️ Széllökés", f"🚨 Legerősebb ({category_info})", f"{max_wind:.1f}km/h", dates[max_wind_idx]))
                    else:
                        extremes.append(("💨 Szél", "🌪️ Legszelesebb nap", f"{max_wind:.1f}km/h", dates[max_wind_idx]))
            
            # Táblázat feltöltése
            self._populate_extreme_table(extremes)
            
        except Exception as e:
            logger.error(f"Daily extremes calculation error: {e}")
    
    def _calculate_monthly_extremes(self, daily_data: Dict[str, List], dates: List[str]) -> None:
        """
        📅 Havi extrém értékek számítása és táblázat feltöltése.
        """
        try:
            import pandas as pd
            from datetime import datetime
            
            # DataFrame létrehozása a havi aggregációhoz
            df_data = {'date': dates}
            
            # Adatok hozzáadása
            for key, values in daily_data.items():
                if key != 'time' and values:
                    df_data[key] = values[:len(dates)]  # Megfelelő hosszúság biztosítása
            
            df = pd.DataFrame(df_data)
            df['date'] = pd.to_datetime(df['date'])
            df['year_month'] = df['date'].dt.to_period('M')
            
            extremes = []
            
            # === HAVI HŐMÉRSÉKLET AGGREGÁCIÓK ===
            if 'temperature_2m_max' in df.columns:
                monthly_temp_max = df.groupby('year_month')['temperature_2m_max'].max()
                if not monthly_temp_max.empty:
                    hottest_month = monthly_temp_max.idxmax()
                    hottest_temp = monthly_temp_max.max()
                    extremes.append(("🌡️ Hőmérséklet", "🔥 Legmelegebb hónap", f"{hottest_temp:.1f}°C", str(hottest_month)))
            
            if 'temperature_2m_min' in df.columns:
                monthly_temp_min = df.groupby('year_month')['temperature_2m_min'].min()
                if not monthly_temp_min.empty:
                    coldest_month = monthly_temp_min.idxmin()
                    coldest_temp = monthly_temp_min.min()
                    extremes.append(("🌡️ Hőmérséklet", "🧊 Leghidegebb hónap", f"{coldest_temp:.1f}°C", str(coldest_month)))
            
            # === HAVI CSAPADÉK AGGREGÁCIÓK ===
            if 'precipitation_sum' in df.columns:
                monthly_precip = df.groupby('year_month')['precipitation_sum'].sum()
                if not monthly_precip.empty:
                    wettest_month = monthly_precip.idxmax()
                    wettest_precip = monthly_precip.max()
                    extremes.append(("🌧️ Csapadék", "💧 Legcsapadékosabb hónap", f"{wettest_precip:.1f}mm", str(wettest_month)))
                    
                    driest_month = monthly_precip.idxmin()
                    driest_precip = monthly_precip.min()
                    extremes.append(("🌧️ Csapadék", "🏜️ Legszárazabb hónap", f"{driest_precip:.1f}mm", str(driest_month)))
            
            # === HAVI SZÉL AGGREGÁCIÓK ===
            wind_col = None
            if 'wind_gusts_max' in df.columns:
                wind_col = 'wind_gusts_max'
                wind_source = 'wind_gusts_max'
            elif 'windspeed_10m_max' in df.columns:
                wind_col = 'windspeed_10m_max'
                wind_source = 'windspeed_10m_max'
            
            if wind_col:
                monthly_wind = df.groupby('year_month')[wind_col].max()
                if not monthly_wind.empty:
                    windiest_month = monthly_wind.idxmax()
                    windiest_speed = monthly_wind.max()
                    
                    if wind_source == 'wind_gusts_max':
                        category = WindGustsAnalyzer.categorize_wind_gust(windiest_speed, wind_source)
                        category_info = WindGustsConstants.CATEGORIES.get(category, 'ISMERETLEN')
                        extremes.append(("🌪️ Széllökés", f"🚨 Legszelesebb hónap ({category_info})", f"{windiest_speed:.1f}km/h", str(windiest_month)))
                    else:
                        extremes.append(("💨 Szél", "🌪️ Legszelesebb hónap", f"{windiest_speed:.1f}km/h", str(windiest_month)))
            
            # Táblázat feltöltése
            self._populate_extreme_table(extremes)
            
        except Exception as e:
            logger.error(f"Monthly extremes calculation error: {e}")
            # Fallback: napi számítás
            self._calculate_daily_extremes(daily_data, dates)
    
    def _calculate_yearly_extremes(self, daily_data: Dict[str, List], dates: List[str]) -> None:
        """
        🗓️ Éves extrém értékek számítása és táblázat feltöltése.
        HOSSZÚ IDŐSZAKOK (10+ év) kezelésére optimalizálva.
        """
        try:
            import pandas as pd
            from datetime import datetime
            
            # DataFrame létrehozása az éves aggregációhoz
            df_data = {'date': dates}
            
            # Adatok hozzáadása
            for key, values in daily_data.items():
                if key != 'time' and values:
                    df_data[key] = values[:len(dates)]  # Megfelelő hosszúság biztosítása
            
            df = pd.DataFrame(df_data)
            df['date'] = pd.to_datetime(df['date'])
            df['year'] = df['date'].dt.year
            
            extremes = []
            years = sorted(df['year'].unique())
            
            logger.info(f"Calculating yearly extremes for {len(years)} years: {years[0]}-{years[-1]}")
            
            # === ÉVES HŐMÉRSÉKLET AGGREGÁCIÓK ===
            if 'temperature_2m_max' in df.columns:
                yearly_temp_max = df.groupby('year')['temperature_2m_max'].max()
                if not yearly_temp_max.empty:
                    hottest_year = yearly_temp_max.idxmax()
                    hottest_temp = yearly_temp_max.max()
                    extremes.append(("🌡️ Hőmérséklet", "🔥 Legmelegebb év", f"{hottest_temp:.1f}°C", str(hottest_year)))
                    
                    # Átlag hőmérséklet trend
                    yearly_temp_avg = df.groupby('year')['temperature_2m_max'].mean()
                    warmest_avg_year = yearly_temp_avg.idxmax()
                    warmest_avg_temp = yearly_temp_avg.max()
                    extremes.append(("🌡️ Hőmérséklet", "📈 Legmelegebb átlag év", f"{warmest_avg_temp:.1f}°C", str(warmest_avg_year)))
            
            if 'temperature_2m_min' in df.columns:
                yearly_temp_min = df.groupby('year')['temperature_2m_min'].min()
                if not yearly_temp_min.empty:
                    coldest_year = yearly_temp_min.idxmin()
                    coldest_temp = yearly_temp_min.min()
                    extremes.append(("🌡️ Hőmérséklet", "🧊 Leghidegebb év", f"{coldest_temp:.1f}°C", str(coldest_year)))
                    
                    # Átlag hőmérséklet trend
                    yearly_temp_avg = df.groupby('year')['temperature_2m_min'].mean()
                    coldest_avg_year = yearly_temp_avg.idxmin()
                    coldest_avg_temp = yearly_temp_avg.min()
                    extremes.append(("🌡️ Hőmérséklet", "📉 Leghidegebb átlag év", f"{coldest_avg_temp:.1f}°C", str(coldest_avg_year)))
            
            # === ÉVES CSAPADÉK AGGREGÁCIÓK ===
            if 'precipitation_sum' in df.columns:
                yearly_precip = df.groupby('year')['precipitation_sum'].sum()
                if not yearly_precip.empty:
                    wettest_year = yearly_precip.idxmax()
                    wettest_precip = yearly_precip.max()
                    extremes.append(("🌧️ Csapadék", "💧 Legcsapadékosabb év", f"{wettest_precip:.0f}mm", str(wettest_year)))
                    
                    driest_year = yearly_precip.idxmin()
                    driest_precip = yearly_precip.min()
                    extremes.append(("🌧️ Csapadék", "🏜️ Legszárazabb év", f"{driest_precip:.0f}mm", str(driest_year)))
                    
                    # Évenkénti száraz napok száma
                    yearly_dry_days = df.groupby('year').apply(lambda x: (x['precipitation_sum'] <= 0.1).sum())
                    driest_by_days_year = yearly_dry_days.idxmax()
                    driest_by_days_count = yearly_dry_days.max()
                    extremes.append(("🌧️ Csapadék", "🏜️ Legtöbb száraz nap", f"{driest_by_days_count} nap", str(driest_by_days_year)))
            
            # === ÉVES SZÉL AGGREGÁCIÓK ===
            wind_col = None
            if 'wind_gusts_max' in df.columns:
                wind_col = 'wind_gusts_max'
                wind_source = 'wind_gusts_max'
            elif 'windspeed_10m_max' in df.columns:
                wind_col = 'windspeed_10m_max'
                wind_source = 'windspeed_10m_max'
            
            if wind_col:
                yearly_wind_max = df.groupby('year')[wind_col].max()
                if not yearly_wind_max.empty:
                    windiest_year = yearly_wind_max.idxmax()
                    windiest_speed = yearly_wind_max.max()
                    
                    if wind_source == 'wind_gusts_max':
                        category = WindGustsAnalyzer.categorize_wind_gust(windiest_speed, wind_source)
                        category_info = WindGustsConstants.CATEGORIES.get(category, 'ISMERETLEN')
                        extremes.append(("🌪️ Széllökés", f"🚨 Legszelesebb év ({category_info})", f"{windiest_speed:.1f}km/h", str(windiest_year)))
                    else:
                        extremes.append(("💨 Szél", "🌪️ Legszelesebb év", f"{windiest_speed:.1f}km/h", str(windiest_year)))
                
                # Átlagos szélsebesség trend
                yearly_wind_avg = df.groupby('year')[wind_col].mean()
                if not yearly_wind_avg.empty:
                    windiest_avg_year = yearly_wind_avg.idxmax()
                    windiest_avg_speed = yearly_wind_avg.max()
                    
                    if wind_source == 'wind_gusts_max':
                        extremes.append(("🌪️ Széllökés", "📈 Legszélesebb átlag év", f"{windiest_avg_speed:.1f}km/h", str(windiest_avg_year)))
                    else:
                        extremes.append(("💨 Szél", "📈 Legszélesebb átlag év", f"{windiest_avg_speed:.1f}km/h", str(windiest_avg_year)))
            
            # === KLÍMAVÁLTOZÁSI TRENDEK (ha 10+ év) ===
            if len(years) >= 10:
                # Hőmérséklet trend
                if 'temperature_2m_mean' in df.columns or ('temperature_2m_max' in df.columns and 'temperature_2m_min' in df.columns):
                    # Egyszerű trend számítás (első 5 év vs utolsó 5 év)
                    early_years = years[:5]
                    late_years = years[-5:]
                    
                    if 'temperature_2m_mean' in df.columns:
                        temp_col = 'temperature_2m_mean'
                    else:
                        # Átlag számítása max és min-ből
                        df['temp_calculated_mean'] = (df['temperature_2m_max'] + df['temperature_2m_min']) / 2
                        temp_col = 'temp_calculated_mean'
                    
                    early_avg = df[df['year'].isin(early_years)][temp_col].mean()
                    late_avg = df[df['year'].isin(late_years)][temp_col].mean()
                    temp_trend = late_avg - early_avg
                    
                    if temp_trend > 0.5:
                        extremes.append(("🌡️ Trend", "🔥 Felmelegedés trend", f"+{temp_trend:.1f}°C", f"{years[0]}-{years[-1]}"))
                    elif temp_trend < -0.5:
                        extremes.append(("🌡️ Trend", "🧊 Lehűlés trend", f"{temp_trend:.1f}°C", f"{years[0]}-{years[-1]}"))
                    else:
                        extremes.append(("🌡️ Trend", "📊 Stabil hőmérséklet", f"{temp_trend:+.1f}°C", f"{years[0]}-{years[-1]}"))
            
            # Táblázat feltöltése
            self._populate_extreme_table(extremes)
            
            logger.info(f"Yearly extremes calculated: {len(extremes)} records for {len(years)} years")
            
        except Exception as e:
            logger.error(f"Yearly extremes calculation error: {e}")
            # Fallback: havi számítás
            self._calculate_monthly_extremes(daily_data, dates)
    
    def _populate_extreme_table(self, extremes: List[Tuple[str, str, str, str]]) -> None:
        """
        🏆 Extrém értékek táblázat feltöltése.
        
        Args:
            extremes: Lista tuple-ekkel (kategória, típus, érték, dátum)
        """
        if not self.extreme_table:
            return
        
        try:
            self.extreme_table.setRowCount(len(extremes))
            
            for row, (category, record_type, value, date) in enumerate(extremes):
                # Táblázat celláinak feltöltése
                self.extreme_table.setItem(row, 0, QTableWidgetItem(category))
                self.extreme_table.setItem(row, 1, QTableWidgetItem(record_type))
                self.extreme_table.setItem(row, 2, QTableWidgetItem(value))
                self.extreme_table.setItem(row, 3, QTableWidgetItem(date))
            
            logger.info(f"Extreme table populated with {len(extremes)} records ({self.period_type})")
            
        except Exception as e:
            logger.error(f"Table population error: {e}")
    
    # 🚨 KRITIKUS JAVÍTÁS: HIÁNYZÓ ESEMÉNYKEZELŐ METÓDUSOK HOZZÁADÁSA
    
    def _on_detailed_analysis_clicked(self) -> None:
        """
        🔍 Részletes extrém elemzés gomb eseménykezelő.
        """
        try:
            logger.info("Részletes extrém elemzés gomb megnyomva")
            
            # Egyszerű információs üzenet
            from PySide6.QtWidgets import QMessageBox
            
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
                    
                    info_text = f"""
📊 ELEMZÉSI RÉSZLETEK:

🗓️ Időszak: {start_date} - {end_date}
📈 Napok száma: {total_days}
📋 Periódus típus: {self.period_type}

🌪️ EXTRÉM ESEMÉNYEK:
• Hőmérséklet anomáliák detektálva
• Csapadék szélsőértékek elemezve  
• Széllökés kategorizálás aktív

🏆 REKORDOK:
• {self.period_type.capitalize()} rekordok táblázatban
• Meteorológiai kategorizálás
• Intelligens időszak választás

🔬 További részletes elemzés funkciókat a következő verzióban implementáljuk!
                    """
                else:
                    info_text = "❌ Nincs elérhető adat a részletes elemzéshez."
            else:
                info_text = "❌ Nincs betöltött időjárási adat."
            
            msg_box.setText(info_text)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            
            # Signal kibocsátása (ha szükséges)
            self.extreme_weather_requested.emit()
            
        except Exception as e:
            logger.error(f"Részletes elemzés gomb hiba: {e}")
    
    def _on_anomaly_settings_clicked(self) -> None:
        """
        ⚙️ Anomália beállítások gomb eseménykezelő.
        """
        try:
            logger.info("Anomália beállítások gomb megnyomva")
            
            # Beállítások dialog
            from PySide6.QtWidgets import QMessageBox
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("⚙️ Anomália Beállítások")
            msg_box.setIcon(QMessageBox.Information)
            
            # Aktuális küszöbértékek megjelenítése
            settings_text = f"""
🔧 JELENLEGI ANOMÁLIA KÜSZÖBÖK:

🌡️ HŐMÉRSÉKLET:
• Meleg küszöb: >{AnomalyConstants.TEMP_HOT_THRESHOLD}°C
• Hideg küszöb: <{AnomalyConstants.TEMP_COLD_THRESHOLD}°C

🌧️ CSAPADÉK:
• Magas küszöb: >{AnomalyConstants.PRECIP_HIGH_THRESHOLD}mm
• Alacsony küszöb: <{AnomalyConstants.PRECIP_LOW_THRESHOLD}mm

🌪️ SZÉL:
• Szeles küszöb: >{AnomalyConstants.WIND_HIGH_THRESHOLD}km/h

💨 SZÉLLÖKÉS KATEGÓRIÁK:
• Normális: <{WindGustsConstants.MODERATE_THRESHOLD}km/h
• Mérsékelt: {WindGustsConstants.MODERATE_THRESHOLD}-{WindGustsConstants.STRONG_THRESHOLD}km/h  
• Erős: {WindGustsConstants.STRONG_THRESHOLD}-{WindGustsConstants.EXTREME_THRESHOLD}km/h
• Extrém: {WindGustsConstants.EXTREME_THRESHOLD}-{WindGustsConstants.HURRICANE_THRESHOLD}km/h
• Orkán: >{WindGustsConstants.HURRICANE_THRESHOLD}km/h

🔧 A küszöbértékek testreszabása a következő verzióban lesz elérhető!
            """
            
            msg_box.setText(settings_text)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            
        except Exception as e:
            logger.error(f"Anomália beállítások gomb hiba: {e}")