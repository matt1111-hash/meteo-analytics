#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trend Analytics Tab - Core

🚀 TrendAnalyticsTab fő osztály és UI setup

Képességek:
- Main TrendAnalyticsTab class
- UI setup és signal connection
- Location handling

Fájl: src/presentation/gui/trend_analytics/trend_analytics_tab/core.py
"""

import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.presentation.gui.theme_manager import ThemeManager
from ..trend_data_processor import TrendDataProcessor
from .analysis_handlers import TrendAnalysisHandlerMixin
from .public_api import TrendAnalyticsPublicAPIMixin
from .ui_builder import (
    create_controls_panel,
    create_dashboard_statistics_area,
    create_header,
    create_plotly_chart_container,
    setup_content_splitter,
)

logger = logging.getLogger(__name__)


class TrendAnalyticsTab(
    TrendAnalyticsPublicAPIMixin,
    TrendAnalysisHandlerMixin,
    QWidget
):
    """
    🚀 ENHANCED TREND ANALYTICS TAB v4.2 - PROFESSIONAL DASHBOARD IMPLEMENTATION

    🎨 FEJLESZTÉSEK v4.2:
    - ✅ KRITIKUS JAVÍTÁS: weather_client.get_weather_data() EGYSÉGES API
    - ✅ Tuple unpacking hiba véglegesen megoldva
    - ✅ PLOTLY INTERAKTÍV CHARTOK: Zoom, pan, hover tooltips
    - ✅ DASHBOARD-SZERŰ KPI KÁRTYÁK: Vizuális trend mutatók
    - ✅ ENHANCED STATISTICS PANEL: Grid layout stat cards
    - ✅ QSPLITTER MEGTARTÁSA: Felhasználó által állítható layout
    - ✅ PROFESSIONAL ERROR HANDLING: Structured logging
    - ✅ TYPE HINTS: Teljes típus annotáció
    - ✅ MODULÁRIS ARCHITEKTÚRA: DRY, KISS, YAGNI, SOLID elvek

    LAYOUT STRUKTÚRA v4.2:
    ┌───────────────────────────────────────────────────────────┐
    │                    HEADER + CONTROLS                      │
    ├─────────────────────┬─────────────────────────────────────┤
    │  📈 PLOTLY CHART    │ 🎯 KPI DASHBOARD CARDS              │
    │  (QSplitter bal)    │ (QSplitter jobb)                   │
    │  - Interaktív       │ ┌─────────────────────────────────┐ │
    │  - Zoom/Pan         │ │ [🎯 Trend] [🎯 Megbízhatóság] │ │
    │  - Hover tooltips   │ │ [⚡ Szign.] [📊 Tartomány]    │ │
    │  - Export           │ └─────────────────────────────────┘ │
    └─────────────────────┴─────────────────────────────────────┘

    KORÁBBI v3.0-4.1 FUNKCIÓK MEGMARADTAK + GLOBALIZÁCIÓ:
    - CityManager globális koordináta lekérdezés (3200+ magyar + 44k nemzetközi)
    - Weather_client.py multi-year API hívások (✅ EGYSÉGES API)
    - 5-10-25-55 éves trend opciók
    - Professional trend számítás
    - Signal-based communication
    """

    # Signals for main window communication
    analysis_started = Signal()
    analysis_completed = Signal(dict)
    error_occurred = Signal(str)
    location_selected = Signal(str, float, float)  # name, lat, lon

    def __init__(self):
        super().__init__()
        self.current_worker: any = None
        self.setup_ui()
        self.connect_signals()

        logger.info("🚀 TrendAnalyticsTab v4.2 inicializálva (KPI DASHBOARD DINAMIKUS FRISSÍTÉS)")

    def setup_ui(self) -> None:
        """🎨 UI SETUP - Enhanced Dashboard Layout v4.2"""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Header
        create_header(self)

        # Controls panel
        controls = create_controls_panel(self)
        self.location_combo = controls["location_combo"]
        self.parameter_combo = controls["parameter_combo"]
        self.time_combo = controls["time_combo"]
        self.analyze_button = controls["analyze_button"]
        self.progress_bar = controls["progress_bar"]

        # Chart area (bal oldal) - PLOTLY CHART
        chart_container = create_plotly_chart_container(self)
        self.chart = chart_container

        # 🎯 DASHBOARD STATISTICS AREA - KPI KÁRTYÁK
        stats_area = create_dashboard_statistics_area(self)
        self.statistics_panel = stats_area

        # 🔧 QSplitter implementáció
        setup_content_splitter(self, chart_container, stats_area)

        logger.info("✅ Enhanced Dashboard layout beállítva: KPI kártyák dinamikus frissítéssel")

    def connect_signals(self) -> None:
        """Signal connections beállítása (VÁLTOZATLAN)"""
        # Analyze button
        self.analyze_button.clicked.connect(self.start_trend_analysis)

        # Location selection
        self.location_combo.currentTextChanged.connect(self.on_location_changed)

    def on_location_changed(self, location_name: str) -> None:
        """Location selection kezelése (VÁLTOZATLAN)"""
        if location_name and len(location_name.strip()) > 2:
            # Get coordinates for location
            processor = TrendDataProcessor()
            coordinates = processor.get_settlement_coordinates(location_name.strip())

            if coordinates:
                lat, lon = coordinates
                logger.info(f"📍 Location selected: {location_name} ({lat:.4f}, {lon:.4f})")
                self.location_selected.emit(location_name, lat, lon)


# Theme integration
def register_trend_analytics_theme(theme_manager: ThemeManager) -> None:
    """Theme manager integráció"""
    if theme_manager:
        # Register trend analytics specific styling
        pass
