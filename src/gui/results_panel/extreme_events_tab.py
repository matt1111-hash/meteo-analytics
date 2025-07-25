#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Extreme Events Tab Module
🌪️ KRITIKUS JAVÍTÁS: "Extrém Események" TAB - WIND GUSTS támogatással
🎨 KRITIKUS JAVÍTÁS: ColorPalette API integráció - scheme.success → scheme.get_color("success", "base")
Anomáliák és rekordok kezelése élethű széllökés értékekkel.

🚀 PROFESSZIONÁLIS KÓDOLÁSI ELVEK:
✅ DRY: WindGustsAnalyzer utility osztály használata
✅ KISS: Egyszerű, érthető anomália detektálás
✅ SOLID: Single Responsibility - csak UI logika
✅ Type hints: Minden metódus explicit típusokkal
✅ Error handling: Robusztus kivételkezelés
✅ Logging: Strukturált hibakövetés
"""

import logging
from typing import Optional, Dict, Any, List, Union, Tuple
import pandas as pd
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSplitter,
    QGroupBox, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QProgressBar, QFrame, QScrollArea, QGridLayout, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from ...config import GUIConfig
from ..utils import GUIConstants, AnomalyConstants
from ..theme_manager import get_theme_manager, register_widget_for_theming
from .utils import WindGustsConstants, DataFrameExtractor, WindGustsAnalyzer

# Logging konfigurálása
logger = logging.getLogger(__name__)


class ExtremeEventsTab(QWidget):
    """
    🌪️ KRITIKUS JAVÍTÁS: "Extrém Események" TAB - WIND GUSTS támogatással.
    🎨 KRITIKUS JAVÍTÁS: ColorPalette API integráció - scheme.success → scheme.get_color("success", "base")
    Anomáliák és rekordok kezelése élethű széllökés értékekkel.
    
    🚀 PROFESSZIONÁLIS KÓDOLÁSI ELVEK:
    ✅ DRY: WindGustsAnalyzer utility osztály használata
    ✅ KISS: Egyszerű, érthető anomália detektálás
    ✅ SOLID: Single Responsibility - csak UI logika
    ✅ Type hints: Minden metódus explicit típusokkal
    ✅ Error handling: Robusztus kivételkezelés
    ✅ Logging: Strukturált hibakövetés
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
        
        self._init_ui()
        self._register_widgets_for_theming()
        
        logger.info("ExtremeEventsTab ColorPalette API integráció kész (WIND GUSTS support)")
    
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
        """Rekordok kimutatása szekció."""
        section = QGroupBox("🏆 Rekordok és Szélsőértékek")
        
        layout = QVBoxLayout(section)
        
        self.records_text = QTextEdit()
        self.records_text.setMaximumHeight(120)
        self.records_text.setReadOnly(True)
        layout.addWidget(self.records_text)
        
        return section
    
    def _create_actions_section(self) -> QWidget:
        """Akciók szekció."""
        container = QWidget()
        layout = QHBoxLayout(container)
        
        self.detailed_btn = QPushButton("🔍 Részletes Extrém Elemzés")
        self.detailed_btn.clicked.connect(self.extreme_weather_requested.emit)
        layout.addWidget(self.detailed_btn)
        
        self.settings_btn = QPushButton("⚙️ Anomália Beállítások")
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
        
        logger.debug("ExtremeEventsTab - Összes widget regisztrálva ColorPalette API-hez")
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🌪️ KRITIKUS JAVÍTÁS: Extrém események adatok frissítése WIND GUSTS támogatással.
        
        Args:
            data: OpenMeteo API válasz
        """
        try:
            logger.info("ExtremeEventsTab.update_data() CALLED! (WIND GUSTS support)")
            self.current_data = data
            
            df = DataFrameExtractor.extract_safely(data)
            
            if df.empty:
                logger.warning("ExtremeEventsTab - DataFrame is empty!")
                self._clear_extremes()
                return
            
            logger.info(f"ExtremeEventsTab DataFrame shape: {df.shape}")
            
            # 🌪️ KRITIKUS JAVÍTÁS: WIND GUSTS anomália és rekord detektálás
            self._detect_anomalies(df)
            self._find_records(df)
            
            logger.info("ExtremeEventsTab update_data SIKERES! (WIND GUSTS support)")
            
        except Exception as e:
            logger.error(f"ExtremeEventsTab adatfrissítési hiba: {e}")
            self._clear_extremes()
    
    def _detect_anomalies(self, df: pd.DataFrame) -> None:
        """
        🌪️ KRITIKUS JAVÍTÁS: Anomália detektálás WIND GUSTS támogatással.
        Élethű széllökés küszöbök alkalmazása.
        """
        try:
            # Hőmérséklet anomália
            self._detect_temperature_anomaly(df)
            
            # Csapadék anomália
            self._detect_precipitation_anomaly(df)
            
            # 🌪️ KRITIKUS JAVÍTÁS: Széllökés anomália WIND GUSTS támogatással
            self._detect_wind_anomaly(df)
            
        except Exception as e:
            logger.error(f"Anomália detektálási hiba: {e}")
            self._clear_extremes()
    
    def _detect_temperature_anomaly(self, df: pd.DataFrame) -> None:
        """Hőmérséklet anomália detektálás."""
        try:
            if ('temp_max' in df.columns and 'temp_min' in df.columns):
                max_series = df['temp_max'].dropna()
                min_series = df['temp_min'].dropna()
                
                if not max_series.empty and not min_series.empty:
                    avg_temp = (max_series.mean() + min_series.mean()) / 2
                    
                    if pd.notna(avg_temp):
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
            else:
                self._set_anomaly_status_with_theme(self.temp_anomaly, "🌡️ Hőmérséklet: Nincs adat", "disabled")
        except Exception as e:
            logger.error(f"Hőmérséklet anomália detektálási hiba: {e}")
            self._set_anomaly_status_with_theme(self.temp_anomaly, "🌡️ Hőmérséklet: Hiba", "disabled")
    
    def _detect_precipitation_anomaly(self, df: pd.DataFrame) -> None:
        """Csapadék anomália detektálás."""
        try:
            if 'precipitation' in df.columns:
                precip_series = df['precipitation'].dropna()
                
                if not precip_series.empty:
                    total_precip = precip_series.sum()
                    
                    if pd.notna(total_precip):
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
            else:
                self._set_anomaly_status_with_theme(self.precip_anomaly, "🌧️ Csapadék: Nincs adat", "disabled")
        except Exception as e:
            logger.error(f"Csapadék anomália detektálási hiba: {e}")
            self._set_anomaly_status_with_theme(self.precip_anomaly, "🌧️ Csapadék: Hiba", "disabled")
    
    def _detect_wind_anomaly(self, df: pd.DataFrame) -> None:
        """
        🌪️ KRITIKUS JAVÍTÁS: Széllökés anomália WIND GUSTS támogatással.
        Élethű széllökés küszöbök alkalmazása.
        """
        try:
            if 'windspeed' in df.columns:
                wind_series = df['windspeed'].dropna()
                
                if not wind_series.empty:
                    avg_wind = wind_series.mean()
                    max_wind = wind_series.max()
                    wind_data_source = df.get('wind_data_source', ['unknown']).iloc[0] if 'wind_data_source' in df.columns else 'unknown'
                    
                    logger.info(f"Wind anomaly detection - Source: {wind_data_source}, Avg: {avg_wind:.1f}, Max: {max_wind:.1f}")
                    
                    if pd.notna(avg_wind) and pd.notna(max_wind):
                        # 🌪️ KRITIKUS JAVÍTÁS: Élethű széllökés küszöbök
                        if wind_data_source == 'wind_gusts_max':
                            category = WindGustsAnalyzer.categorize_wind_gust(max_wind, wind_data_source)
                            description = WindGustsAnalyzer.generate_wind_description(max_wind, category, wind_data_source)
                            
                            if category == 'hurricane':
                                self._set_anomaly_status_with_theme(self.wind_anomaly, f"🚨 Széllökések: {description}", "error")
                            elif category == 'extreme':
                                self._set_anomaly_status_with_theme(self.wind_anomaly, f"⚠️ Széllökések: {description}", "error")
                            elif category == 'strong':
                                self._set_anomaly_status_with_theme(self.wind_anomaly, f"🌪️ Széllökések: {description}", "warning")
                            elif avg_wind > 50:
                                self._set_anomaly_status_with_theme(self.wind_anomaly, "💨 Széllökések: Szokatlanul szeles", "warning")
                            else:
                                self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Széllökések: Normális", "success")
                        else:
                            # windspeed_10m_max esetén eredeti küszöbök
                            if avg_wind > AnomalyConstants.WIND_HIGH_THRESHOLD:
                                self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Szél: Szokatlanul szeles", "error")
                            else:
                                self._set_anomaly_status_with_theme(self.wind_anomaly, "💨 Szél: Normális", "success")
                    else:
                        self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Széllökések: Nincs adat", "disabled")
                else:
                    self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Széllökések: Nincs adat", "disabled")
            else:
                self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Széllökések: Nincs adat", "disabled")
        except Exception as e:
            logger.error(f"Széllökés anomália detektálási hiba: {e}")
            self._set_anomaly_status_with_theme(self.wind_anomaly, "🌪️ Széllökések: Hiba", "disabled")
    
    def _find_records(self, df: pd.DataFrame) -> None:
        """
        🌪️ KRITIKUS JAVÍTÁS: Rekordok meghatározása WIND GUSTS támogatással.
        Élethű széllökés kategorizálás és részletes rekord információk.
        """
        try:
            if not self.records_text:
                return
            
            records_text = "📊 IDŐJÁRÁSI REKORDOK ÉS SZÉLSŐÉRTÉKEK\n"
            records_text += "=" * 50 + "\n\n"
            
            # Hőmérséklet rekordok
            records_text += self._generate_temperature_records(df)
            
            # Csapadék rekordok
            records_text += self._generate_precipitation_records(df)
            
            # 🌪️ KRITIKUS JAVÍTÁS: Széllökés rekordok WIND GUSTS támogatással
            records_text += self._generate_wind_records(df)
            
            self.records_text.setText(records_text)
            
        except Exception as e:
            logger.error(f"Rekordok meghatározási hiba: {e}")
            if self.records_text:
                self.records_text.setText("❌ Hiba a rekordok számítása során - nincs megfelelő adat")
    
    def _generate_temperature_records(self, df: pd.DataFrame) -> str:
        """Hőmérséklet rekordok generálása."""
        try:
            if ('temp_max' in df.columns and 'temp_min' in df.columns):
                max_series = df['temp_max'].dropna()
                min_series = df['temp_min'].dropna()
                
                if not max_series.empty and not min_series.empty:
                    max_temp_idx = max_series.idxmax()
                    min_temp_idx = min_series.idxmin()
                    
                    max_temp_day = df.loc[max_temp_idx]
                    min_temp_day = df.loc[min_temp_idx]
                    
                    records_text = f"🌡️ HŐMÉRSÉKLET REKORDOK:\n"
                    records_text += f"   🔥 Legmelegebb nap: {max_temp_day['temp_max']:.1f}°C ({max_temp_day['date']})\n"
                    records_text += f"   🧊 Leghidegebb nap: {min_temp_day['temp_min']:.1f}°C ({min_temp_day['date']})\n"
                    records_text += f"   📈 Hőingás: {max_temp_day['temp_max'] - min_temp_day['temp_min']:.1f}°C\n\n"
                    return records_text
                else:
                    return f"🌡️ HŐMÉRSÉKLET REKORDOK: Nincs megfelelő adat\n\n"
            else:
                return f"🌡️ HŐMÉRSÉKLET REKORDOK: Nincs hőmérséklet adat\n\n"
        except Exception as e:
            logger.error(f"Hőmérséklet rekordok hiba: {e}")
            return f"🌡️ HŐMÉRSÉKLET REKORDOK: Hiba a számítás során\n\n"
    
    def _generate_precipitation_records(self, df: pd.DataFrame) -> str:
        """Csapadék rekordok generálása."""
        try:
            if 'precipitation' in df.columns:
                precip_series = df['precipitation'].dropna()
                
                if not precip_series.empty:
                    max_precip_idx = precip_series.idxmax()
                    max_precip_day = df.loc[max_precip_idx]
                    dry_days = len(precip_series[precip_series <= 0.1])
                    
                    records_text = f"🌧️ CSAPADÉK REKORDOK:\n"
                    records_text += f"   💧 Legtöbb csapadék: {max_precip_day['precipitation']:.1f}mm ({max_precip_day['date']})\n"
                    records_text += f"   🏜️ Száraz napok: {dry_days} nap\n"
                    records_text += f"   📊 Összes csapadék: {precip_series.sum():.1f}mm\n\n"
                    return records_text
                else:
                    return f"🌧️ CSAPADÉK REKORDOK: Nincs csapadék adat\n\n"
            else:
                return f"🌧️ CSAPADÉK REKORDOK: Nincs csapadék adat\n\n"
        except Exception as e:
            logger.error(f"Csapadék rekordok hiba: {e}")
            return f"🌧️ CSAPADÉK REKORDOK: Hiba a számítás során\n\n"
    
    def _generate_wind_records(self, df: pd.DataFrame) -> str:
        """
        🌪️ KRITIKUS JAVÍTÁS: Széllökés rekordok WIND GUSTS támogatással.
        Élethű kategorizálás és részletes információk.
        """
        try:
            if 'windspeed' in df.columns:
                wind_series = df['windspeed'].dropna()
                
                if not wind_series.empty:
                    max_wind_idx = wind_series.idxmax()
                    max_wind_day = df.loc[max_wind_idx]
                    wind_data_source = df.get('wind_data_source', ['unknown']).iloc[0] if 'wind_data_source' in df.columns else 'unknown'
                    
                    max_wind_value = max_wind_day['windspeed']
                    
                    # 🌪️ KRITIKUS JAVÍTÁS: Széllökés cím és kategorizálás
                    if wind_data_source == 'wind_gusts_max':
                        category = WindGustsAnalyzer.categorize_wind_gust(max_wind_value, wind_data_source)
                        
                        records_text = f"🌪️ SZÉLLÖKÉS REKORDOK:\n"
                        records_text += f"   🚨 Legerősebb széllökés: {max_wind_value:.1f}km/h ({max_wind_day['date']})\n"
                        
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
                        records_text += f"   🌪️ Legerősebb szél: {max_wind_value:.1f}km/h ({max_wind_day['date']})\n"
                    
                    records_text += f"   📊 Átlagos szélsebesség: {wind_series.mean():.1f}km/h\n"
                    records_text += f"   📈 Adatforrás: {wind_data_source}\n\n"
                    
                    logger.info(f"Wind records - Source: {wind_data_source}, Max: {max_wind_value:.1f} km/h")
                    
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
