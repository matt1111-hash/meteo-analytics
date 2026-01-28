#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Analytics View Module (REFAKTORÁLT)
Ez a modul a multi-city régió elemzések dashboardját valósítja meg.

✅ REFAKTORÁLT MŰKÖDÉS:
- A nézet most már nem indít saját lekérdezéseket.
- A gombok egy központi `multi_city_query_requested` signalt bocsátanak ki.
- A MainWindow kezeli a lekérdezést és az eredményt egy publikus slot-on
  (`update_with_multi_city_result`) keresztül küldi vissza.
- Ezzel a nézet teljesen szinkronban van a többi modullal (Térkép, ControlPanel).

🔧 KRITIKUS JAVÍTÁSOK:
✅ Visszatérés a HEATMAP-ekhez (MINDEN TAB)
✅ KONSTANS 365 TÉGLALAP - mindig ugyanannyi adatpont
✅ METEOROLÓGIAI SZÍNSKÁLÁK - professzionális időjárási színek
✅ MINDEN TÉGLALAP KITÖLTVE - nulla érték = megfelelő szín (nem üres!)
✅ 1 év = 365 téglalap (1 nap/téglalap), 5 év = 365 téglalap (5 nap/téglalap)
✅ RÁCS VONALAK - téglalapok elválasztva (Excel-szerű)
✅ INTELLIGENS TENGELYEK - időszak alapú címkék
✅ BEAUFORT SZÉL SZÍNSKÁLA - 13 fokozat progresszív színátmenet
✅ 4. TAB: MAX SZÉLLÖKÉS - windgusts_10m_max külön megjelenítés
✅ RELEVÁNS METEOROLÓGIAI STATISZTIKÁK - bal oldali panel
✅ KOMPAKT KÁRTYÁS RENDSZER - 12px olvasható betűméret
🚀 MULTI-CITY RÉGIÓ INTEGRÁCIÓ - Észak-Magyarország, Pest, stb. elemzések
🔥 SIGNAL EMISSION JAVÍTÁS - multi_city_analysis_completed signal kibocsátás
🚨 STATISZTIKÁK JAVÍTÁS - _process_and_display_statistics() MEGHÍVÁS
🌪️ VÉGSŐ JAVÍTÁS: WindChart/WindRoseChart DEDICATED KOMPONENSEK HOZZÁADÁSA

Fájl helye: src/presentation/gui/analytics/analytics_view.py
"""

import logging
from typing import Dict, Any, Optional, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QScrollArea, QFrame, QSplitter, QComboBox,
    QPushButton, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Téma rendszer
from ..theme_manager import get_theme_manager, register_widget_for_theming, get_current_colors

# 🚀 MULTI-CITY ENGINE IMPORT
try:
    from ...analytics.multi_city_engine import MultiCityEngine, MultiCityQuery
    from ...data.models import AnalyticsResult, CityWeatherResult, AnalyticsQuestion
    from ...data.enums import RegionScope, AnalyticsMetric, QuestionType
    MULTI_CITY_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Multi-City Engine import sikeres!")
except ImportError as e:
    MULTI_CITY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"❌ Multi-City Engine import hiba: {e}")

# Local imports
from .analytics_helpers import MeteorologicalColorMaps
from .analytics_widgets import RecordSummaryCard
from .analytics_tabs import ClimateTabWidget
from .analytics_statistics import AnalyticsStatistics


class AnalyticsView(QWidget):
    """
    🎯 REFAKTORÁLT KONSTANS HEATMAP Analytics View - KÖZPONTI SIGNAL RENDSZERREL + DEDICATED WIND CHARTOK

    ✅ REFAKTORÁLT MŰKÖDÉS:
    - A nézet most már nem indít saját lekérdezéseket.
    - A gombok egy központi `multi_city_query_requested` signalt bocsátanak ki.
    - A MainWindow kezeli a lekérdezést és az eredményt egy publikus slot-on
      (`update_with_multi_city_result`) keresztül küldi vissza.
    - Ezzel a nézet teljesen szinkronban van a többi modullal (Térkép, ControlPanel).

    FELELŐSSÉG:
    - 🌡️ Hőmérséklet tab: KONSTANS HEATMAP (RdYlBu_r, 365 téglalap, rács vonalak)
    - 🌧️ Csapadék tab: KONSTANS HEATMAP (meteorológiai, 0mm=fehér, 365 téglalap, rács vonalak)
    - 💨 Szél tab: KONSTANS HEATMAP (BEAUFORT 13 fokozat, átlagos max szél, 365 téglalap, rács vonalak)
    - 🌪️ Max Széllökés tab: KONSTANS HEATMAP (BEAUFORT 13 fokozat, max gusts, 365 téglalap, rács vonalak)
    - 🌪️ Széllökések tab: DEDICATED WindChart professzionális szél grafikonokkal
    - 🌹 Széllökés Rózsa tab: DEDICATED WindRoseChart polár rózsadiagrammal
    - 🏆 5 rekord kategória (napi szinten) kompakt megjelenítéssel
    - 🔧 KONSTANS VIZUÁLIS FELBONTÁS - függetlenül az időszaktól
    - 🎯 INTELLIGENS TENGELYEK - időszak alapú címkék
    - 📊 KOMPAKT KÁRTYÁS STATISZTIKÁK - 12px olvasható betűméret
    - 🚀 MULTI-CITY RÉGIÓ ELEMZÉS - Észak-Magyarország, Pest, stb. elemzések
    - 🔥 SIGNAL EMISSION JAVÍTÁS - multi_city_query_requested signal kibocsátás MainWindow felé
    - 🚨 STATISZTIKÁK JAVÍTÁS - _process_and_display_statistics() MEGHÍVÁS BIZTOSÍTVA
    - 🌪️ VÉGSŐ JAVÍTÁS: DEDICATED WindChart és WindRoseChart komponensek integrálása
    """

    # Signalok
    analysis_started = Signal()
    analysis_completed = Signal()
    error_occurred = Signal(str)

    # 🚀 ÚJ: Signal a lekérdezés indításához a MainWindow felé
    multi_city_query_requested = Signal(str, str)  # query_type, region_name

    def __init__(self, parent=None):
        super().__init__(parent)

        # Téma kezelő
        self.theme_manager = get_theme_manager()

        # Adatok tárolása
        self.current_data = None
        self.current_location = None

        # UI elemek
        self.location_info_label = None
        self.statistics_area = None
        self.record_summary = None
        self.climate_tabs = None
        self.status_label = None

        # 🚀 MULTI-CITY KOMPONENSEK (refaktorált)
        self.region_combo = None
        self.analysis_buttons = []

        # UI építése
        self._setup_ui()
        self._setup_theme()

        logger.info("🗂️ AnalyticsView REFAKTORÁLT KONSTANS HEATMAP BEAUFORT + MAX SZÉLLÖKÉS + MULTI-CITY RÉGIÓ + DEDICATED WIND CHARTOK VERZIÓ betöltve")

    def _setup_ui(self) -> None:
        """UI felépítése - konstans heatmap dashboard + refaktorált multi-city + dedicated wind chartok"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Fejléc
        header_layout = self._create_header()
        layout.addLayout(header_layout)

        # Lokáció információ (kompakt)
        location_group = self._create_location_info_group()
        layout.addWidget(location_group)

        # Fő tartalom splitter
        content_splitter = QSplitter(Qt.Horizontal)

        # Bal oldal: statisztikák + refaktorált multi-city (kompakt)
        stats_widget = self._create_statistics_panel()
        content_splitter.addWidget(stats_widget)

        # Jobb oldal: Tab-os klímakutató dashboard + DEDICATED WIND CHARTOK
        tab_widget = self._create_tab_dashboard()
        content_splitter.addWidget(tab_widget)

        # Splitter arányok - tab dashboard dominál
        content_splitter.setSizes([180, 920])
        layout.addWidget(content_splitter)

        # Állapot sáv
        self.status_label = QLabel("Válasszon lokációt a bal oldali panelen vagy használja a Régió Elemzést")
        self.status_label.setStyleSheet("color: gray; padding: 2px; font-size: 9px;")
        layout.addWidget(self.status_label)

    def _create_header(self) -> QHBoxLayout:
        """Fejléc létrehozása"""
        layout = QHBoxLayout()

        # Cím
        title_label = QLabel("🎯 Konstans Heatmap Klímakutató Dashboard + Régió Elemzés + DEDICATED Wind Chartok")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        layout.addStretch()

        # Verzió info
        version_label = QLabel("v14.0 - DEDICATED WIND CHARTOK")
        version_label.setStyleSheet("color: gray; font-size: 8px;")
        layout.addWidget(version_label)

        return layout

    def _create_location_info_group(self) -> QGroupBox:
        """Lokáció információs panel - EXTRA KOMPAKT"""
        group = QGroupBox("📍 Lokáció")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(4, 4, 4, 4)

        self.location_info_label = QLabel("Nincs kiválasztott lokáció")
        self.location_info_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 2px;
                padding: 4px;
                font-size: 9px;
            }
        """)
        layout.addWidget(self.location_info_label)

        return group

    def _create_statistics_panel(self) -> QWidget:
        """Statisztikák panel + Refaktorált Multi-City - KOMPAKT KÁRTYÁS RENDSZER"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(3, 3, 3, 3)

        # 🚀 REFAKTORÁLT MULTI-CITY RÉGIÓ ELEMZÉS PANEL
        multi_city_group = self._create_refactored_multi_city_panel()
        layout.addWidget(multi_city_group)

        # Statisztikák csoport
        stats_group = QGroupBox("📈 Statisztikák")
        stats_layout = QVBoxLayout(stats_group)

        # Görgetési terület
        self.statistics_area = QScrollArea()
        self.statistics_area.setWidgetResizable(True)
        self.statistics_area.setMinimumHeight(150)

        # Statisztikák tartalom
        stats_content = QLabel("Töltse be az adatokat")
        stats_content.setAlignment(Qt.AlignCenter)
        stats_content.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 20px;
                font-size: 12px;
            }
        """)
        self.statistics_area.setWidget(stats_content)

        stats_layout.addWidget(self.statistics_area)
        layout.addWidget(stats_group)

        return widget

    def _create_refactored_multi_city_panel(self) -> QGroupBox:
        """🚀 REFAKTORÁLT Multi-City régió elemzés panel - SIGNAL EMISSION"""
        group = QGroupBox("🌍 RÉGIÓ ELEMZÉS")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Régió választó
        region_layout = QVBoxLayout()
        region_label = QLabel("📍 Válassz régiót:")
        region_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        region_layout.addWidget(region_label)

        self.region_combo = QComboBox()
        self.region_combo.addItems([
            "Észak-Magyarország",
            "Észak-Alföld",
            "Dél-Alföld",
            "Közép-Magyarország",
            "Közép-Dunántúl",
            "Nyugat-Dunántúl",
            "Dél-Dunántúl"
        ])
        self.region_combo.setStyleSheet("""
            QComboBox {
                padding: 3px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 9px;
            }
        """)
        region_layout.addWidget(self.region_combo)
        layout.addLayout(region_layout)

        # Elemzés gombok
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(3)

        # Gombok létrehozása
        query_configs = [
            ("hottest_today", "🔥 Legmelegebb ma", "#FF6B6B", "#E55555", "#CC4444"),
            ("coldest_today", "❄️ Leghidegebb ma", "#4DABF7", "#339FE6", "#2288CC"),
            ("wettest_today", "🌧️ Legcsapadékosabb ma", "#69DB7C", "#51CF66", "#40C057"),
            ("windiest_today", "💨 Legszelesebb ma", "#FFD93D", "#FCC419", "#FAB005"),
        ]

        for query_type, text, bg, hover, pressed in query_configs:
            button = QPushButton(text)
            button.setProperty("query_type", query_type)
            button.clicked.connect(self._emit_query_request)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                    font-size: 9px;
                }}
                QPushButton:hover {{
                    background-color: {hover};
                }}
                QPushButton:pressed {{
                    background-color: {pressed};
                }}
            """)
            buttons_layout.addWidget(button)
            self.analysis_buttons.append(button)

        layout.addLayout(buttons_layout)

        # Panel styling
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border: 2px solid #C43939;
                border-radius: 6px;
                margin: 2px;
                font-weight: bold;
                font-size: 11px;
                color: #C43939;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 3px 0 3px;
            }
        """)

        return group

    def _emit_query_request(self):
        """🚀 KRITIKUS: Elküldi a lekérdezési kérést a MainWindow felé - REFAKTORÁLT SIGNAL EMISSION"""
        sender = self.sender()
        query_type = sender.property("query_type")
        region_name = self.region_combo.currentText()

        logger.info(f"🚀 ANALYTICS_VIEW: Signal 'multi_city_query_requested' emitted with: {query_type}, {region_name}")

        # ✅ ÚJ: Signal kibocsátása a MainWindow felé
        self.multi_city_query_requested.emit(query_type, region_name)

        # UI visszajelzés
        self._update_status(f"🚀 Multi-City kérés elküldve: {region_name} ({query_type})")

        logger.info(f"🚀 Multi-City query request emitted: {query_type} for {region_name}")

    def _create_tab_dashboard(self) -> QWidget:
        """Tab-os klímakutató dashboard + DEDICATED WIND CHARTOK"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Rekord summary kártya (kompakt)
        self.record_summary = RecordSummaryCard()
        layout.addWidget(self.record_summary)

        # Climate tab widget - KONSTANS HEATMAP BEAUFORT + MAX SZÉLLÖKÉS + DEDICATED WIND CHARTOK VERZIÓ
        self.climate_tabs = ClimateTabWidget()
        layout.addWidget(self.climate_tabs, 1)  # Expandálható

        return widget

    def _setup_theme(self) -> None:
        """Téma beállítása"""
        register_widget_for_theming(self, "container")
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        self._apply_current_theme()

    def _apply_current_theme(self) -> None:
        """Jelenlegi téma alkalmazása"""
        colors = get_current_colors()

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors.get('surface', '#ffffff')};
                color: {colors.get('on_surface', '#000000')};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {colors.get('border', '#ccc')};
                border-radius: 3px;
                margin-top: 6px;
                padding-top: 3px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 3px 0 3px;
                color: {colors.get('primary', '#0066cc')};
            }}
        """)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Téma változás kezelése"""
        self._apply_current_theme()
        logger.debug(f"Konstans heatmap dashboard téma frissítve: {theme_name}")

    # === ✅ ÚJ PUBLIKUS SLOT: Eredmények fogadása a MainWindow-tól ===

    def update_with_multi_city_result(self, result: 'AnalyticsResult'):
        """
        ✅ ÚJ: Frissíti a nézetet a MainWindow-tól kapott elemzési eredménnyel.

        Args:
            result: AnalyticsResult objektum a Multi-City Engine-ből
        """
        logger.info(f"✅ ANALYTICS_VIEW: Eredmény fogadva a MainWindow-tól: {len(result.city_results) if result and result.city_results else 0} város.")

        try:
            if not result or not result.city_results:
                self._update_status("❌ Nincs Multi-City eredmény")
                return

            # Fake single-city data létrehozása a heatmap-ekhez (a meglévő logika)
            self._create_fake_single_city_data_from_multi_city(result)

            # Status frissítése
            self._update_status(f"✅ Multi-City eredmény feldolgozva: {len(result.city_results)} város")

            logger.info(f"✅ Multi-City result processed in AnalyticsView: {len(result.city_results)} cities")

        except Exception as e:
            logger.error(f"❌ Multi-City result processing error: {e}")
            self._update_status(f"❌ Multi-City eredmény feldolgozási hiba: {e}")
            self.error_occurred.emit(f"Multi-City eredmény hiba: {e}")

    def _create_fake_single_city_data_from_multi_city(self, analytics_result):
        """🎯 Fake single-city data létrehozása Multi-City eredményekből a heatmap megjelenítéshez"""
        try:
            if not analytics_result or not analytics_result.city_results:
                logger.warning("Nincs Multi-City eredmény a heatmap frissítéshez")
                return

            # Multi-City eredmények aggregálása egy fake weather data-ba
            cities = analytics_result.city_results
            question = analytics_result.question

            # Fake daily data létrehozása (365 nap)
            fake_daily_data = {
                'time': [f"2024-{i//30+1:02d}-{i%30+1:02d}" for i in range(365)],
                'temperature_2m_mean': [],
                'temperature_2m_max': [],
                'temperature_2m_min': [],
                'precipitation_sum': [],
                'windspeed_10m_max': [],
                'wind_gusts_max': []
            }

            # Metric alapú fake data generálás
            metric_type = question.metric if question else AnalyticsMetric.TEMPERATURE_2M_MAX

            for i in range(365):
                # Városok értékeinek átlaga minden napra (szimuláció)
                if metric_type == AnalyticsMetric.TEMPERATURE_2M_MAX:
                    avg_val = sum(city.value for city in cities) / len(cities)
                    fake_daily_data['temperature_2m_max'].append(avg_val + (i % 20 - 10))
                    fake_daily_data['temperature_2m_mean'].append(avg_val - 2)
                    fake_daily_data['temperature_2m_min'].append(avg_val - 8)
                    fake_daily_data['precipitation_sum'].append(0.5)
                    fake_daily_data['windspeed_10m_max'].append(10.0)
                    fake_daily_data['wind_gusts_max'].append(15.0)

                elif metric_type == AnalyticsMetric.PRECIPITATION_SUM:
                    avg_val = sum(city.value for city in cities) / len(cities)
                    fake_daily_data['precipitation_sum'].append(avg_val + (i % 10))
                    fake_daily_data['temperature_2m_max'].append(20.0)
                    fake_daily_data['temperature_2m_mean'].append(15.0)
                    fake_daily_data['temperature_2m_min'].append(10.0)
                    fake_daily_data['windspeed_10m_max'].append(10.0)
                    fake_daily_data['wind_gusts_max'].append(15.0)

                elif metric_type == AnalyticsMetric.WINDSPEED_10M_MAX:
                    avg_val = sum(city.value for city in cities) / len(cities)
                    fake_daily_data['windspeed_10m_max'].append(avg_val + (i % 15))
                    fake_daily_data['wind_gusts_max'].append(avg_val + 5)
                    fake_daily_data['temperature_2m_max'].append(20.0)
                    fake_daily_data['temperature_2m_mean'].append(15.0)
                    fake_daily_data['temperature_2m_min'].append(10.0)
                    fake_daily_data['precipitation_sum'].append(1.0)

                else:
                    # Default értékek
                    fake_daily_data['temperature_2m_max'].append(20.0)
                    fake_daily_data['temperature_2m_mean'].append(15.0)
                    fake_daily_data['temperature_2m_min'].append(10.0)
                    fake_daily_data['precipitation_sum'].append(1.0)
                    fake_daily_data['windspeed_10m_max'].append(10.0)
                    fake_daily_data['wind_gusts_max'].append(15.0)

            # Fake data objektum
            fake_data = {
                'daily': fake_daily_data,
                'location': {
                    'name': f"Multi-City: {analytics_result.question.question_text if analytics_result.question else 'Régió Elemzés'}",
                    'latitude': 47.5,
                    'longitude': 19.0
                }
            }

            # Heatmap-ek frissítése
            if self.climate_tabs:
                self.climate_tabs.update_data(fake_data)

            # Fake rekordok (Multi-City eredményekből)
            fake_records = self._create_fake_records_from_multi_city(analytics_result)
            if self.record_summary:
                self.record_summary.update_records(fake_records)

            logger.info(f"🎯 Fake single-city data létrehozva Multi-City eredményekből ({len(cities)} város)")

        except Exception as e:
            logger.error(f"❌ Fake data creation hiba: {e}")

    def _create_fake_records_from_multi_city(self, analytics_result) -> Dict[str, Dict[str, str]]:
        """🏆 Fake rekordok létrehozása Multi-City eredményekből"""
        try:
            if not analytics_result.city_results:
                return {}

            cities = analytics_result.city_results
            records = {}

            # Top 3 város kiválasztása különböző kategóriákhoz
            if len(cities) >= 1:
                top_city = cities[0]
                records['hottest'] = {
                    'value': f"{top_city.value:.1f}°C",
                    'date': top_city.date.strftime("%Y-%m-%d") if hasattr(top_city.date, 'strftime') else str(top_city.date)
                }

            if len(cities) >= 2:
                second_city = cities[1]
                records['windiest'] = {
                    'value': f"{second_city.value:.1f}km/h",
                    'date': second_city.date.strftime("%Y-%m-%d") if hasattr(second_city.date, 'strftime') else str(second_city.date)
                }

            if len(cities) >= 3:
                third_city = cities[2]
                records['wettest'] = {
                    'value': f"{third_city.value:.1f}mm",
                    'date': third_city.date.strftime("%Y-%m-%d") if hasattr(third_city.date, 'strftime') else str(third_city.date)
                }

            # Default értékek
            records.setdefault('coldest', {'value': "N/A", 'date': "Multi-City"})
            records.setdefault('driest', {'value': "N/A", 'date': "Multi-City"})

            return records

        except Exception as e:
            logger.error(f"❌ Fake records creation hiba: {e}")
            return {}

    # === PUBLIKUS API METÓDUSOK ===

    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🎯 KONSTANS HEATMAP + DEDICATED WIND CHARTOK adatok frissítése - 6 TAB - BEAUFORT + MAX SZÉLLÖKÉS VERZIÓ
        🚨 STATISZTIKÁK JAVÍTÁS - _process_and_display_statistics() MEGHÍVÁS BIZTOSÍTVA
        🌪️ VÉGSŐ JAVÍTÁS: DEDICATED WindChart és WindRoseChart frissítése

        Args:
            data: Időjárási adatok dictionary
        """
        try:
            logger.info("🗂️ Konstans heatmap dashboard + DEDICATED WIND CHARTOK adatok frissítése")

            # Adatok tárolása
            self.current_data = data

            # Teljes napok számítása
            daily_data = data.get('daily', {})
            dates = daily_data.get('time', [])
            total_days = len(dates)

            logger.info(f"🎯 KONSTANS AGGREGÁCIÓ - BEAUFORT + MAX SZÉLLÖKÉS:")
            logger.info(f"  📊 {total_days} nap → 365 téglalap minden tab-nál")

            # 🚨 KRITIKUS JAVÍTÁS: Bal oldali statisztikák frissítése
            logger.info("🚨 STATISZTIKÁK JAVÍTÁS: _process_and_display_statistics() meghívása")
            self._process_and_display_statistics(data, total_days)

            # Rekordok frissítése (mindig napi szinten)
            records = AnalyticsStatistics.calculate_records(data)
            self.record_summary.update_records(records)

            # Tab widget frissítése
            if self.climate_tabs:
                self.climate_tabs.update_data(data)

            # Állapot frissítése
            self._update_status(f"✅ {total_days} nap → 365 téglalap - Beaufort + Max Széllökés Dashboard + DEDICATED WIND CHARTOK + STATISZTIKÁK")

            # Signal
            self.analysis_completed.emit()

        except Exception as e:
            logger.error(f"Konstans heatmap dashboard + DEDICATED WIND CHARTOK adatfrissítési hiba: {e}", exc_info=True)
            self.error_occurred.emit(f"Adatfrissítési hiba: {str(e)}")
            self._update_status("❌ Adatfeldolgozási hiba")

    def clear_data(self) -> None:
        """Adatok törlése és UI visszaállítása"""
        logger.info("Konstans heatmap dashboard + DEDICATED WIND CHARTOK adatok törlése")

        self.current_data = None
        self.current_location = None

        # UI visszaállítása
        self.location_info_label.setText("Nincs kiválasztott lokáció")

        # Statisztikák törlése
        stats_content = QLabel("Töltse be az adatokat")
        stats_content.setAlignment(Qt.AlignCenter)
        stats_content.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 20px;
                font-size: 12px;
            }
        """)
        self.statistics_area.setWidget(stats_content)

        self._update_status("Válasszon lokációt a bal oldali panelen vagy használja a Régió Elemzést")

    def on_location_changed(self, location) -> None:
        """Lokáció változás kezelése"""
        try:
            logger.info(f"Konstans heatmap dashboard lokáció változás: {location}")
            self.current_location = location

            # Lokáció info frissítése
            if hasattr(location, 'display_name'):
                display_name = location.display_name
                coords = location.coordinates
            elif isinstance(location, dict):
                display_name = location.get('name', 'Ismeretlen')
                lat = location.get('latitude', 0.0)
                lon = location.get('longitude', 0.0)
                coords = (lat, lon)
            else:
                display_name = str(location)
                coords = (0.0, 0.0)

            if coords:
                location_text = f"📍 {display_name}\n🗺️ [{coords[0]:.3f}, {coords[1]:.3f}]"
            else:
                location_text = f"📍 {display_name}"

            self.location_info_label.setText(location_text)
            self._update_status(f"Lokáció beállítva: {display_name}")

        except Exception as e:
            logger.error(f"Lokció változás hiba: {e}")
            self.error_occurred.emit(f"Lokció hiba: {str(e)}")

    def on_analysis_start(self) -> None:
        """Elemzés indítása"""
        logger.info("Konstans heatmap dashboard + DEDICATED WIND CHARTOK elemzés indítása")
        self.analysis_started.emit()
        self._update_status("⏳ Konstans heatmap dashboard + DEDICATED WIND CHARTOK elemzés folyamatban...")

    # === BELSŐ METÓDUSOK ===

    def _process_and_display_statistics(self, data: Dict[str, Any], total_days: int) -> None:
        """🚨 JAVÍTOTT: Statisztikák feldolgozása és megjelenítése - KOMPAKT KÁRTYÁS RENDSZER"""
        try:
            logger.info("🚨 _process_and_display_statistics() MEGHÍVVA - STATISZTIKÁK JAVÍTÁS")

            # Statisztikai adatok számítása
            stats_data = AnalyticsStatistics.calculate_statistics_data(data, total_days)

            # Kompakt kártyás widget létrehozása
            stats_widget = self._create_statistics_cards_widget(stats_data)

            # 🚨 KRITIKUS: Statisztikák widget beállítása a scroll area-ba
            self.statistics_area.setWidget(stats_widget)

            logger.info("✅ Statisztikák sikeresen megjelenítve a bal oldali panelen")

        except Exception as e:
            logger.error(f"Statisztika feldolgozási hiba: {e}", exc_info=True)
            # Hiba esetén alapértelmezett üzenet
            error_widget = QLabel(f"❌ Statisztika hiba: {str(e)}")
            error_widget.setAlignment(Qt.AlignCenter)
            error_widget.setStyleSheet("color: red; padding: 20px;")
            self.statistics_area.setWidget(error_widget)

    def _create_statistics_cards_widget(self, stats: Dict[str, Any]) -> QWidget:
        """🎯 KOMPAKT KÁRTYÁS STATISZTIKA WIDGET LÉTREHOZÁSA"""
        try:
            main_widget = QWidget()
            layout = QVBoxLayout(main_widget)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(8)

            if not stats:
                no_data_label = QLabel("❌ Nincsenek adatok")
                no_data_label.setAlignment(Qt.AlignCenter)
                no_data_label.setStyleSheet("color: #666; font-style: italic; padding: 20px; font-size: 12px;")
                layout.addWidget(no_data_label)
                return main_widget

            # === 1. HŐMÉRSÉKLET KÁRTYA ===
            temp_card = self._create_statistic_card(
                "🌡️ HŐMÉRSÉKLETI STATISZTIKÁK",
                [
                    f"• Átlag hőmérséklet: {stats.get('temp_avg', 0):.1f}°C" if stats.get('temp_avg') else "• Átlag hőmérséklet: N/A",
                    f"• Min/Max: {stats.get('temp_min', 0):.1f}°C / {stats.get('temp_max', 0):.1f}°C" if stats.get('temp_min') and stats.get('temp_max') else "• Min/Max: N/A",
                    f"• Fagyos napok: {stats.get('freezing_days', 0)} nap",
                    f"• Hőséghullám (>30°C): {stats.get('hot_days', 0)} nap",
                    f"• Hőmérséklet ingadozás: {stats.get('temp_range_avg', 0):.1f}°C" if stats.get('temp_range_avg') else "• Hőmérséklet ingadozás: N/A"
                ]
            )
            layout.addWidget(temp_card)

            # === 2. CSAPADÉK KÁRTYA ===
            precip_card = self._create_statistic_card(
                "🌧️ CSAPADÉK ELEMZÉS",
                [
                    f"• Átlag csapadék: {stats.get('precip_avg', 0):.1f}mm/nap" if stats.get('precip_avg') else "• Átlag csapadék: N/A",
                    f"• Száraz napok: {stats.get('dry_days', 0)} nap ({stats.get('dry_percentage', 0):.0f}%)",
                    f"• Esős napok: {stats.get('rainy_days', 0)} nap ({stats.get('rainy_percentage', 0):.0f}%)",
                    f"• Összes csapadék: {stats.get('annual_precip', 0):.0f}mm/év" if stats.get('annual_precip') else "• Összes csapadék: N/A",
                    f"• Leghosszabb száraz: {stats.get('longest_dry_streak', 0)} nap"
                ]
            )
            layout.addWidget(precip_card)

            # === 3. SZÉL KÁRTYA ===
            wind_card = self._create_statistic_card(
                "💨 SZÉL BEAUFORT ELEMZÉS",
                [
                    f"• Átlag szélsebesség: {stats.get('wind_avg', 0):.1f} km/h" if stats.get('wind_avg') else "• Átlag szélsebesség: N/A",
                    f"• Max széllökés: {stats.get('windgust_max', 0):.1f} km/h" if stats.get('windgust_max') else f"• Max szélsebesség: {stats.get('wind_max', 0):.1f} km/h" if stats.get('wind_max') else "• Max szél: N/A",
                    f"• Szélcsend (0-1): {stats.get('wind_calm', 0)} nap",
                    f"• Gyenge szél (2-3): {stats.get('wind_light', 0)} nap",
                    f"• Mérsékelt (4-5): {stats.get('wind_moderate', 0)} nap",
                    f"• Erős szél (6+): {stats.get('wind_strong', 0)} nap"
                ]
            )
            layout.addWidget(wind_card)

            # === 4. IDŐSZAK KÁRTYA ===
            period_card = self._create_statistic_card(
                "📊 IDŐSZAK & RENDSZER INFO",
                [
                    f"• Időtartam: {stats.get('start_date', 'N/A')} - {stats.get('end_date', 'N/A')}",
                    f"• Napok száma: {stats.get('total_days', 0)} nap",
                    f"• Konstans felbontás: 365 bin",
                    f"• Bin méret: ~{stats.get('bin_size', 1)} nap/téglalap",
                    f"• Beaufort 13 fokozat színek"
                ]
            )
            layout.addWidget(period_card)

            # Stretch hozzáadása az aljára
            layout.addStretch()

            return main_widget

        except Exception as e:
            logger.error(f"Kártyás widget létrehozási hiba: {e}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel(f"❌ Widget hiba: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_layout.addWidget(error_label)
            return error_widget

    def _create_statistic_card(self, title: str, items: List[str]) -> QWidget:
        """📋 EGYEDI STATISZTIKA KÁRTYA LÉTREHOZÁSA"""
        card = QWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Cím
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #C43939;
                margin-bottom: 3px;
            }
        """)
        layout.addWidget(title_label)

        # Elválasztó vonal
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #ddd;")
        layout.addWidget(separator)

        # Adatok
        for item in items:
            item_label = QLabel(item)
            item_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #333;
                    padding-left: 4px;
                    line-height: 1.5;
                }
            """)
            layout.addWidget(item_label)

        # Kártya styling
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin: 2px;
            }
        """)

        return card

    def _update_status(self, message: str) -> None:
        """Állapot üzenet frissítése"""
        if self.status_label:
            self.status_label.setText(message)
        logger.info(f"Konstans heatmap dashboard + DEDICATED WIND CHARTOK állapot: {message}")

    # === TÉMA API ===

    def update_theme(self) -> None:
        """Téma manuális frissítése"""
        self._apply_current_theme()

    def get_current_data(self) -> Optional[Dict[str, Any]]:
        """Jelenlegi adatok lekérdezése"""
        return self.current_data

    def get_current_location(self):
        """Jelenlegi lokáció lekérdezése"""
        return self.current_location


__all__ = ['AnalyticsView', 'MeteorologicalColorMaps']
