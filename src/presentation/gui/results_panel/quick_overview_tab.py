#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Quick Overview Tab Module - DUAL-API CLEAN
📊 "Gyors Áttekintés" TAB - Kompakt statisztikák és mini preview-k
🎨 COLORPALETTE API INTEGRÁCIÓ: scheme.warning → scheme.get_color("warning", "base")
🔧 PRODUCTION READY: ROBUSZTUS STATISZTIKA KEZELÉS
🌪️ WIND GUSTS TÁMOGATÁS: Élethű széllökés értékelés implementálva
🔧 IMPORT HIBÁK JAVÍTVA: get_display_name_for_source → get_source_display_name

✅ DUAL-API CLEAN VÁLTOZTATÁSOK:
- ❌ HungaroMet referenciák eltávolítása
- ✅ Clean dual-API source mapping (Open-Meteo + Meteostat)
- 🔧 utils.py SOURCE_DISPLAY_NAMES integráció - JAVÍTOTT IMPORT
- 📊 Dual-API kompatibilis display logic
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.presentation.gui.theme_manager import get_theme_manager, register_widget_for_theming

# 🔧 KRITIKUS JAVÍTÁS: Import hibák kijavítása
from ..utils import (
    get_source_display_name,  # ← JAVÍTOTT: get_display_name_for_source → get_source_display_name
)
from .utils import DataFrameExtractor, WindGustsAnalyzer

# Logging konfigurálása
logger = logging.getLogger(__name__)


class QuickOverviewTab(QWidget):
    """
    📊 "Gyors Áttekintés" TAB - Kompakt statisztikák és mini preview-k.
    🎨 ✅ COLORPALETTE API INTEGRÁCIÓ: scheme.warning → scheme.get_color("warning", "base")
    🔧 ✅ PRODUCTION READY: ROBUSZTUS STATISZTIKA KEZELÉS
    🌪️ ✅ WIND GUSTS TÁMOGATÁS: Élethű széllökés értékelés implementálva
    ✅ ✅ DUAL-API CLEAN: HungaroMet referenciák eltávolítva, clean dual-API támogatással
    🔧 ✅ IMPORT HIBÁK JAVÍTVA: Helyes függvénynevek használata
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # === THEMEMANAGER INICIALIZÁLÁSA ===
        self.theme_manager = get_theme_manager()

        self.current_data: Optional[Dict[str, Any]] = None
        self._stat_labels: Dict[str, QLabel] = {}

        # UI inicializálása
        self._init_ui()

        # === THEMEMANAGER REGISZTRÁCIÓ ===
        self._register_widgets_for_theming()

        logger.info("QuickOverviewTab ColorPalette API integráció kész (WIND GUSTS + IMPORT FIXES)")

    def _init_ui(self) -> None:
        """UI inicializálása - kompakt áttekintés + COLORPALETTE API."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # === FELSŐ CÍM ===
        self.title_label = QLabel("📊 Gyors Áttekintés")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # === STATISZTIKAI KÁRTYÁK ===
        stats_container = self._create_stats_cards()
        layout.addWidget(stats_container)

        # === MINI ELŐNÉZETI CHARTOK ===
        mini_charts_container = self._create_mini_charts()
        layout.addWidget(mini_charts_container)

        # === GYORS AKCIÓK ===
        quick_actions = self._create_quick_actions()
        layout.addWidget(quick_actions)

        # Stretch hozzáadása
        layout.addStretch()

    def _create_stats_cards(self) -> QWidget:
        """Statisztikai kártyák létrehozása - COLORPALETTE API STYLING."""
        self.stats_container = QWidget()

        layout = QGridLayout(self.stats_container)
        layout.setSpacing(10)

        # Hőmérséklet kártya
        self.temp_card = self._create_stat_card("🌡️ Hőmérséklet", [
            ("Átlag", "avg_temp", "°C"),
            ("Maximum", "max_temp", "°C"),
            ("Minimum", "min_temp", "°C"),
            ("Hőingás", "temp_range", "°C")
        ], "#f59e0b")
        layout.addWidget(self.temp_card, 0, 0)

        # Csapadék kártya
        self.precip_card = self._create_stat_card("🌧️ Csapadék", [
            ("Összesen", "total_precip", "mm"),
            ("Átlag/nap", "avg_precip", "mm"),
            ("Maximum", "max_precip", "mm"),
            ("Esős napok", "rainy_days", "nap")
        ], "#3b82f6")
        layout.addWidget(self.precip_card, 0, 1)

        # 🌪️ KRITIKUS JAVÍTÁS: Szél kártya frissítése
        self.wind_card = self._create_stat_card("🌪️ Széllökések", [
            ("Átlag", "avg_wind", "km/h"),
            ("Maximum", "max_wind", "km/h"),
            ("Szeles napok", "windy_days", "nap"),
            ("Uralkodó irány", "wind_direction", "")
        ], "#10b981")
        layout.addWidget(self.wind_card, 0, 2)

        # Általános információk kártya
        self.info_card = self._create_info_card()
        layout.addWidget(self.info_card, 1, 0, 1, 3)

        return self.stats_container

    def _create_stat_card(self, title: str, stats: List[Tuple[str, str, str]], accent_color: str) -> QGroupBox:
        """Egyetlen statisztikai kártya létrehozása - COLORPALETTE API STYLING."""
        card = QGroupBox(title)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        for label_text, key, unit in stats:
            stat_layout = QHBoxLayout()

            # Stat label - 🎨 DARK THEME FIX: explicit színezés
            label = QLabel(f"{label_text}:")
            label.setMinimumWidth(70)
            self._apply_text_styling(label)  # 🔧 ÚJ: stat label színezés
            stat_layout.addWidget(label)

            # Value label
            value_label = QLabel("-")
            stat_layout.addWidget(value_label)

            # Unit label - 🎨 DARK THEME FIX: explicit színezés
            if unit:
                unit_label = QLabel(unit)
                self._apply_text_styling(unit_label)  # 🔧 ÚJ: unit label színezés
                stat_layout.addWidget(unit_label)

            stat_layout.addStretch()
            layout.addLayout(stat_layout)

            # Label referencia mentése + accent color tárolása
            self._stat_labels[key] = value_label

            # 🎨 KRITIKUS JAVÍTÁS: Accent color alkalmazása ColorPalette API-val
            self._apply_accent_styling(value_label, accent_color)

        return card

    def _apply_text_styling(self, label: QLabel) -> None:
        """
        🎨 ÚJ METÓDUS: Általános text labelek színezése dark/light theme-hez.
        Stat labelek ("Átlag:", "Maximum:") és unit labelek ("°C", "mm") megfelelő színezése.
        
        Args:
            label: Text label (stat vagy unit)
        """
        scheme = self.theme_manager.get_color_scheme()
        if not scheme:
            return

        # Dark/light theme text színek
        text_color = scheme.get_color("primary", "base") or "#000000"

        css = f"""
        QLabel {{
            color: {text_color};
            font-size: 13px;
            font-weight: normal;
        }}
        """
        label.setStyleSheet(css)

        logger.debug(f"Text styling applied: {text_color}")

    def _apply_accent_styling(self, label: QLabel, accent_color: str) -> None:
        """
        🎨 KRITIKUS JAVÍTÁS: Accent színek alkalmazása ColorPalette API-val.
        scheme.warning → scheme.get_color("warning", "base")
        
        Args:
            label: Value label
            accent_color: Accent szín referencia
        """
        # Aktuális színséma lekérdezése
        scheme = self.theme_manager.get_color_scheme()
        if not scheme:
            return

        # 🎨 KRITIKUS JAVÍTÁS: ColorPalette API használata scheme.attribute helyett
        color_mapping = {
            "#f59e0b": scheme.get_color("warning", "base") or "#f59e0b",
            "#3b82f6": scheme.get_color("primary", "base") or "#3b82f6",
            "#10b981": scheme.get_color("success", "base") or "#10b981",
            "#8b5cf6": scheme.get_color("info", "base") or "#8b5cf6"
        }

        theme_color = color_mapping.get(accent_color, scheme.get_color("primary", "base") or "#3b82f6")

        # CSS alkalmazása ColorPalette színekkel
        css = f"""
        QLabel {{
            font-weight: bold;
            color: {theme_color};
            font-size: 14px;
        }}
        """
        label.setStyleSheet(css)

        logger.debug(f"Accent styling applied: {accent_color} → {theme_color}")

    def _create_info_card(self) -> QGroupBox:
        """Általános információs kártya - COLORPALETTE API STYLING."""
        card = QGroupBox("ℹ️ Adatok Információ")

        layout = QVBoxLayout(card)

        # Információ labelek
        self.city_info_label = QLabel("📍 Város: -")
        layout.addWidget(self.city_info_label)

        self.date_range_label = QLabel("📅 Időszak: -")
        layout.addWidget(self.date_range_label)

        self.data_source_label = QLabel("🌍 Adatforrás: -")
        layout.addWidget(self.data_source_label)

        self.record_count_label = QLabel("📊 Rekordok: -")
        layout.addWidget(self.record_count_label)

        return card

    def _create_mini_charts(self) -> QWidget:
        """Mini előnézeti chartok konténere."""
        self.mini_charts_container = QGroupBox("📈 Grafikai Előnézet")
        self.mini_charts_container.setMinimumHeight(200)

        layout = QVBoxLayout(self.mini_charts_container)

        # Placeholder mini chartokhoz
        self.mini_chart_placeholder = QLabel("🔄 Mini grafikon előnézetek")
        self.mini_chart_placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.mini_chart_placeholder)

        return self.mini_charts_container

    def _create_quick_actions(self) -> QWidget:
        """Gyors akció gombok."""
        container = QWidget()
        layout = QHBoxLayout(container)

        # Részletes diagramok gomb
        self.charts_btn = QPushButton("📊 Részletes Diagramok")
        layout.addWidget(self.charts_btn)

        # Adattáblázat gomb
        self.table_btn = QPushButton("📋 Adattáblázat")
        layout.addWidget(self.table_btn)

        # Extrém események gomb
        self.extreme_btn = QPushButton("⚡ Extrém Események")
        layout.addWidget(self.extreme_btn)

        layout.addStretch()

        return container

    def _register_widgets_for_theming(self) -> None:
        """Widget-ek regisztrálása ThemeManager-hez automatikus téma kezeléshez."""
        register_widget_for_theming(self, "container")
        register_widget_for_theming(self.stats_container, "container")

        # 🎨 DARK THEME FIX: Kártya címek explicit regisztrálása
        register_widget_for_theming(self.temp_card, "container")
        register_widget_for_theming(self.precip_card, "container")
        register_widget_for_theming(self.wind_card, "container")
        register_widget_for_theming(self.info_card, "container")
        register_widget_for_theming(self.mini_charts_container, "container")

        register_widget_for_theming(self.title_label, "text")
        register_widget_for_theming(self.city_info_label, "text")
        register_widget_for_theming(self.date_range_label, "text")
        register_widget_for_theming(self.data_source_label, "text")
        register_widget_for_theming(self.record_count_label, "text")
        register_widget_for_theming(self.mini_chart_placeholder, "text")

        register_widget_for_theming(self.charts_btn, "button")
        register_widget_for_theming(self.table_btn, "button")
        register_widget_for_theming(self.extreme_btn, "button")

        logger.debug("QuickOverviewTab - Összes widget regisztrálva ColorPalette API-hez")

        # 🎨 DARK THEME FIX: Explicit styling alkalmazása létrehozás után
        self._apply_card_title_styling()

    def _apply_card_title_styling(self) -> None:
        """
        🎨 ÚJ METÓDUS: Kártya címek (GroupBox title) explicit színezése.
        Dark theme-ben a kártya címek olvashatóságának biztosítása.
        """
        scheme = self.theme_manager.get_color_scheme()
        if not scheme:
            return

        # Címek színe (primary text)
        title_color = scheme.get_color("primary", "base") or "#000000"
        border_color = scheme.get_color("info", "light") or "#d1d5db"

        card_css = f"""
        QGroupBox {{
            font-weight: bold;
            font-size: 14px;
            color: {title_color};
            border: 1px solid {border_color};
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 5px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {title_color};
        }}
        """

        # Kártya címek alkalmazása
        for card in [self.temp_card, self.precip_card, self.wind_card, self.info_card, self.mini_charts_container]:
            if card:
                card.setStyleSheet(card_css)

        logger.debug(f"Card title styling applied: {title_color}")

    def update_data(self, data: Dict[str, Any], city_name: str) -> None:
        """
        Gyors áttekintés adatok frissítése - ✅ PRODUCTION READY IMPLEMENTÁCIÓ.
        🌪️ WIND GUSTS TÁMOGATÁS: Élethű széllökés értékelés.
        ✅ DUAL-API CLEAN: Clean dual-API támogatással.
        🔧 IMPORT HIBÁK JAVÍTVA: Helyes függvénynevek használata.
        
        Args:
            data: OpenMeteo API válasz
            city_name: Város neve
        """
        try:
            logger.info(f"QuickOverviewTab.update_data() - City: {city_name} (DUAL-API CLEAN + IMPORT FIXES)")

            self.current_data = data

            # DataFrame kinyerése - optimalizált módszer
            df = DataFrameExtractor.extract_safely(data)

            if df.empty:
                logger.warning("QuickOverviewTab - DataFrame is empty!")
                self._clear_stats()
                return

            logger.info(f"QuickOverviewTab DataFrame shape: {df.shape}")

            # === HATÉKONY STATISZTIKA SZÁMÍTÁS ===
            self._calculate_temperature_stats(df)
            self._calculate_precipitation_stats(df)
            self._calculate_wind_stats(df)  # 🌪️ WIND GUSTS support

            # === INFORMÁCIÓK FRISSÍTÉSE ===
            self._update_info_labels(data, city_name, df)

            # 🎨 DARK THEME FIX: Styling frissítése adatfrissítés után
            self._apply_card_title_styling()

            logger.info("QuickOverviewTab update_data SIKERES! (DUAL-API CLEAN + IMPORT FIXES)")

        except Exception as e:
            logger.error(f"QuickOverviewTab adatfrissítési hiba: {e}")
            self._clear_stats()

    def _calculate_temperature_stats(self, df: pd.DataFrame) -> None:
        """Hőmérséklet statisztikák számítása."""
        try:
            if 'temp_max' in df.columns:
                max_series = df['temp_max'].dropna()
                if not max_series.empty:
                    max_temp = max_series.max()
                    if pd.notna(max_temp) and max_temp != float('-inf'):
                        self._stat_labels['max_temp'].setText(f"{max_temp:.1f}")
                    else:
                        self._stat_labels['max_temp'].setText("N/A")
                else:
                    self._stat_labels['max_temp'].setText("N/A")
            else:
                self._stat_labels['max_temp'].setText("N/A")

            if 'temp_min' in df.columns:
                min_series = df['temp_min'].dropna()
                if not min_series.empty:
                    min_temp = min_series.min()
                    if pd.notna(min_temp) and min_temp != float('inf'):
                        self._stat_labels['min_temp'].setText(f"{min_temp:.1f}")
                    else:
                        self._stat_labels['min_temp'].setText("N/A")
                else:
                    self._stat_labels['min_temp'].setText("N/A")
            else:
                self._stat_labels['min_temp'].setText("N/A")

            # Átlagos hőmérséklet számítása
            avg_temp = None

            if 'temp_mean' in df.columns:
                mean_series = df['temp_mean'].dropna()
                if not mean_series.empty:
                    avg_temp = mean_series.mean()

            if avg_temp is None or not pd.notna(avg_temp):
                if ('temp_max' in df.columns and 'temp_min' in df.columns):
                    max_series = df['temp_max'].dropna()
                    min_series = df['temp_min'].dropna()
                    if not max_series.empty and not min_series.empty:
                        avg_temp = (max_series.mean() + min_series.mean()) / 2

            if avg_temp is not None and pd.notna(avg_temp):
                self._stat_labels['avg_temp'].setText(f"{avg_temp:.1f}")
            else:
                self._stat_labels['avg_temp'].setText("N/A")

            # Hőingás számítása
            if ('temp_max' in df.columns and 'temp_min' in df.columns):
                max_series = df['temp_max'].dropna()
                min_series = df['temp_min'].dropna()

                if not max_series.empty and not min_series.empty:
                    max_val = max_series.max()
                    min_val = min_series.min()

                    if (pd.notna(max_val) and pd.notna(min_val) and
                        max_val != float('-inf') and min_val != float('inf')):
                        temp_range = max_val - min_val
                        self._stat_labels['temp_range'].setText(f"{temp_range:.1f}")
                    else:
                        self._stat_labels['temp_range'].setText("N/A")
                else:
                    self._stat_labels['temp_range'].setText("N/A")
            else:
                self._stat_labels['temp_range'].setText("N/A")

        except Exception as e:
            logger.error(f"Hőmérséklet statisztika hiba: {e}")
            for key in ['avg_temp', 'max_temp', 'min_temp', 'temp_range']:
                if key in self._stat_labels:
                    self._stat_labels[key].setText("N/A")

    def _calculate_precipitation_stats(self, df: pd.DataFrame) -> None:
        """Csapadék statisztikák számítása."""
        try:
            if 'precipitation' in df.columns:
                precip_series = df['precipitation'].dropna()

                if not precip_series.empty:
                    total_precip = precip_series.sum()
                    if pd.notna(total_precip):
                        self._stat_labels['total_precip'].setText(f"{total_precip:.1f}")
                    else:
                        self._stat_labels['total_precip'].setText("N/A")

                    avg_precip = precip_series.mean()
                    if pd.notna(avg_precip):
                        self._stat_labels['avg_precip'].setText(f"{avg_precip:.1f}")
                    else:
                        self._stat_labels['avg_precip'].setText("N/A")

                    max_precip = precip_series.max()
                    if pd.notna(max_precip):
                        self._stat_labels['max_precip'].setText(f"{max_precip:.1f}")
                    else:
                        self._stat_labels['max_precip'].setText("N/A")

                    rainy_days = len(precip_series[precip_series > 0.1])
                    self._stat_labels['rainy_days'].setText(f"{rainy_days}")

                else:
                    for key in ['total_precip', 'avg_precip', 'max_precip']:
                        self._stat_labels[key].setText("N/A")
                    self._stat_labels['rainy_days'].setText("0")
            else:
                for key in ['total_precip', 'avg_precip', 'max_precip', 'rainy_days']:
                    if key in self._stat_labels:
                        self._stat_labels[key].setText("N/A")

        except Exception as e:
            logger.error(f"Csapadék statisztika hiba: {e}")
            for key in ['total_precip', 'avg_precip', 'max_precip', 'rainy_days']:
                if key in self._stat_labels:
                    self._stat_labels[key].setText("N/A")

    def _calculate_wind_stats(self, df: pd.DataFrame) -> None:
        """
        🌪️ KRITIKUS JAVÍTÁS: Szél statisztikák számítása WIND GUSTS támogatással.
        Élethű széllökés értékelés és intelligens kategorizálás.
        """
        try:
            if 'windspeed' in df.columns:
                wind_series = df['windspeed'].dropna()

                if not wind_series.empty:
                    # Adatforrás meghatározása
                    wind_data_source = df.get('wind_data_source', ['unknown']).iloc[0] if 'wind_data_source' in df.columns else 'unknown'

                    # Átlagos szél
                    avg_wind = wind_series.mean()
                    if pd.notna(avg_wind):
                        self._stat_labels['avg_wind'].setText(f"{avg_wind:.1f}")
                    else:
                        self._stat_labels['avg_wind'].setText("N/A")

                    # Maximum szél
                    max_wind = wind_series.max()
                    if pd.notna(max_wind):
                        self._stat_labels['max_wind'].setText(f"{max_wind:.1f}")

                        # 🌪️ KRITIKUS JAVÍTÁS: Élethű széllökés értékelés
                        category = WindGustsAnalyzer.categorize_wind_gust(max_wind, wind_data_source)

                        if category == 'hurricane':
                            logger.critical(f"KRITIKUS: Hurrikán erősségű széllökés: {max_wind:.1f} km/h")
                        elif category == 'extreme':
                            logger.warning(f"Extrém széllökés: {max_wind:.1f} km/h")
                        elif category == 'strong':
                            logger.warning(f"Erős széllökés: {max_wind:.1f} km/h")

                    else:
                        self._stat_labels['max_wind'].setText("N/A")

                    # 🌪️ KRITIKUS JAVÍTÁS: Szeles napok intelligens küszöbbel
                    windy_threshold = WindGustsAnalyzer.get_windy_days_threshold(wind_data_source)
                    windy_days = len(wind_series[wind_series > windy_threshold])
                    self._stat_labels['windy_days'].setText(f"{windy_days}")

                    logger.info(f"Wind stats - Source: {wind_data_source}, Threshold: {windy_threshold} km/h, Windy days: {windy_days}")

                else:
                    for key in ['avg_wind', 'max_wind']:
                        self._stat_labels[key].setText("N/A")
                    self._stat_labels['windy_days'].setText("0")
            else:
                for key in ['avg_wind', 'max_wind', 'windy_days']:
                    if key in self._stat_labels:
                        self._stat_labels[key].setText("N/A")

            # Wind direction (nem elérhető jelenleg)
            if 'wind_direction' in self._stat_labels:
                self._stat_labels['wind_direction'].setText("N/A")

        except Exception as e:
            logger.error(f"Szél statisztika hiba: {e}")
            for key in ['avg_wind', 'max_wind', 'windy_days', 'wind_direction']:
                if key in self._stat_labels:
                    self._stat_labels[key].setText("N/A")

    def _update_info_labels(self, data: Dict[str, Any], city_name: str, df: pd.DataFrame) -> None:
        """
        ✅ DUAL-API CLEAN: Információs labelek frissítése - HungaroMet referenciák eltávolítva.
        🔧 IMPORT HIBÁK JAVÍTVA: Helyes függvénynév használata.
        """
        try:
            self.city_info_label.setText(f"📍 Város: {city_name}")

            daily_data = data.get("daily", {})
            dates = daily_data.get("time", [])
            if dates:
                start_date = dates[0]
                end_date = dates[-1]
                days_count = len(dates)
                self.date_range_label.setText(f"📅 Időszak: {start_date} - {end_date} ({days_count} nap)")
            else:
                self.date_range_label.setText("📅 Időszak: -")

            # ✅ DUAL-API CLEAN: Source detection és display mapping
            data_source = data.get("source_type", data.get("data_source", "unknown"))

            # 🔧 KRITIKUS JAVÍTÁS: Helyes függvénynév használata
            display_source = get_source_display_name(data_source)

            self.data_source_label.setText(f"🌍 Adatforrás: {display_source}")

            record_count = len(df) if not df.empty else 0
            self.record_count_label.setText(f"📊 Rekordok: {record_count} sor")

            logger.debug(f"Info labels updated (DUAL-API CLEAN + IMPORT FIXES) - Source: {data_source} → {display_source}")

        except Exception as e:
            logger.error(f"Info labelek frissítési hiba: {e}")
            self.city_info_label.setText("📍 Város: -")
            self.date_range_label.setText("📅 Időszak: -")
            self.data_source_label.setText("🌍 Adatforrás: -")
            self.record_count_label.setText("📊 Rekordok: -")

    def _clear_stats(self) -> None:
        """Statisztikák törlése."""
        try:
            for label in self._stat_labels.values():
                label.setText("N/A")

            self.city_info_label.setText("📍 Város: -")
            self.date_range_label.setText("📅 Időszak: -")
            self.data_source_label.setText("🌍 Adatforrás: -")
            self.record_count_label.setText("📊 Rekordok: -")

        except Exception as e:
            logger.error(f"Statisztikák törlési hiba: {e}")
