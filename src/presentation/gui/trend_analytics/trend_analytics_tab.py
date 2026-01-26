#!/usr/bin/env python3
"""
Trend Analytics Tab Module

🚀 Enhanced Trend Analytics Tab - Professional Dashboard Implementation

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

Fájl: src/presentation/gui/trend_analytics/trend_analytics_tab.py
"""

import logging
from typing import Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QProgressBar, QFrame, QSplitter, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from .trend_data_processor import TrendDataProcessor
from .trend_widgets import DashboardStatsCard, InteractiveTrendChart, EnhancedStatisticsPanel
from .trend_worker import TrendAnalyticsWorker
from ..theme_manager import ThemeManager

# Logging beállítás
logger = logging.getLogger(__name__)


class TrendAnalyticsTab(QWidget):
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
        self.current_worker: Optional[TrendAnalyticsWorker] = None
        self.setup_ui()
        self.connect_signals()

        logger.info("🚀 TrendAnalyticsTab v4.2 inicializálva (KPI DASHBOARD DINAMIKUS FRISSÍTÉS)")

    def setup_ui(self) -> None:
        """🎨 UI SETUP - Enhanced Dashboard Layout v4.2"""
        main_layout = QVBoxLayout()

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Controls panel
        controls = self.create_controls_panel()
        main_layout.addWidget(controls)

        # 🔧 QSplitter IMPLEMENTÁCIÓ MEGTARTVA (v3.3 kompatibilitás)
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setChildrenCollapsible(False)

        # Chart area (bal oldal) - PLOTLY CHART
        chart_container = self.create_plotly_chart_container()
        chart_container.setMinimumHeight(400)
        chart_container.setMinimumWidth(600)
        content_splitter.addWidget(chart_container)

        # 🎯 DASHBOARD STATISTICS AREA - KPI KÁRTYÁK
        stats_area = self.create_dashboard_statistics_area()
        stats_area.setMinimumWidth(400)
        content_splitter.addWidget(stats_area)

        # 🔧 KEZDETI MÉRETARÁNY: 67% chart, 33% stats (VÁLTOZATLAN)
        content_splitter.setSizes([2, 1])
        content_splitter.setStretchFactor(0, 2)
        content_splitter.setStretchFactor(1, 1)

        # QSplitter styling (VÁLTOZATLAN)
        content_splitter.setStyleSheet("""
            QSplitter {
                background-color: #f8f9fa;
                border: none;
            }
            QSplitter::handle {
                background-color: #dee2e6;
                width: 8px;
                margin: 2px;
                border-radius: 4px;
            }
            QSplitter::handle:hover {
                background-color: #6c757d;
            }
        """)

        main_layout.addWidget(content_splitter, stretch=1)

        self.setLayout(main_layout)

        logger.info("✅ Enhanced Dashboard layout beállítva: KPI kártyák dinamikus frissítéssel")

    def create_header(self) -> QWidget:
        """Professional header létrehozása (VÁLTOZATLAN)"""
        header = QFrame()
        header.setFrameStyle(QFrame.Box)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 8px;
                padding: 15px;
                color: white;
            }
        """)

        layout = QVBoxLayout()

        # Main title
        title = QLabel("📈 Enhanced Trend Analytics Dashboard v4.2")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: white; margin: 0;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Globális trend elemzés dinamikus KPI dashboard-dal - Hibamentesen javított!")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.9); margin: 5px 0 0 0;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        header.setLayout(layout)
        return header

    def create_controls_panel(self) -> QWidget:
        """🔥 ELEMZÉSI PARAMÉTEREK PANEL (VÁLTOZATLAN)"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout()

        # Panel cím
        panel_title = QLabel("⚙️ Elemzési Paraméterek")
        panel_title.setFont(QFont("Arial", 14, QFont.Bold))
        panel_title.setStyleSheet("color: #495057; margin-bottom: 10px;")
        layout.addWidget(panel_title)

        # Controls grid
        controls_layout = QHBoxLayout()

        # Lokáció választó
        location_group = QVBoxLayout()
        location_label = QLabel("🌍 Lokáció:")
        location_label.setFont(QFont("Arial", 10, QFont.Bold))
        location_group.addWidget(location_label)

        self.location_combo = QComboBox()
        self.location_combo.setEditable(True)
        self.location_combo.setPlaceholderText("Írj be település nevet...")
        self.location_combo.setMinimumWidth(200)
        location_group.addWidget(self.location_combo)
        controls_layout.addLayout(location_group)

        # Paraméter választó
        param_group = QVBoxLayout()
        param_label = QLabel("📊 Paraméter:")
        param_label.setFont(QFont("Arial", 10, QFont.Bold))
        param_group.addWidget(param_label)

        self.parameter_combo = QComboBox()
        self.parameter_combo.addItems([
            "🥶 Minimum hőmérséklet",
            "🔥 Maximum hőmérséklet",
            "🌡️ Átlag hőmérséklet",
            "🌧️ Csapadékmennyiség",
            "💨 Szélsebesség",
            "💨 Széllökések"
        ])
        self.parameter_combo.setCurrentText("🔥 Maximum hőmérséklet")
        param_group.addWidget(self.parameter_combo)
        controls_layout.addLayout(param_group)

        # Időtartam választó
        time_group = QVBoxLayout()
        time_label = QLabel("🕒 Időtartam:")
        time_label.setFont(QFont("Arial", 10, QFont.Bold))
        time_group.addWidget(time_label)

        self.time_combo = QComboBox()
        self.time_combo.addItems([
            "5 év",
            "10 év",
            "25 év",
            "55 év (teljes)"
        ])
        self.time_combo.setCurrentText("5 év")
        time_group.addWidget(self.time_combo)
        controls_layout.addLayout(time_group)

        # Analyze button
        self.analyze_button = QPushButton("🚀 Dashboard Elemzés Indítása")
        self.analyze_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28a745, stop:1 #1e7e34);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                margin-left: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #218838, stop:1 #1c7430);
            }
            QPushButton:pressed {
                background: #1e7e34;
            }
            QPushButton:disabled {
                background: #6c757d;
            }
        """)
        controls_layout.addWidget(self.analyze_button)

        layout.addLayout(controls_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        panel.setLayout(layout)
        return panel

    def create_plotly_chart_container(self) -> QWidget:
        """🎨 PLOTLY CHART CONTAINER LÉTREHOZÁSA"""
        container = QFrame()
        container.setFrameStyle(QFrame.Box)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout()

        # Chart title
        chart_title = QLabel("📈 Interaktív Trend Vizualizáció")
        chart_title.setFont(QFont("Arial", 14, QFont.Bold))
        chart_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(chart_title)

        # 🎨 PLOTLY CHART WIDGET
        self.chart = InteractiveTrendChart()
        layout.addWidget(self.chart)

        container.setLayout(layout)
        return container

    def create_dashboard_statistics_area(self) -> QScrollArea:
        """
        🎯 DASHBOARD KPI KÁRTYÁK TERÜLETE - QScrollArea-ban

        Ez a metódus létrehozza a KPI kártyákat tartalmazó dashboard-ot
        QScrollArea-ban, hogy kis képernyőkön is jól használható legyen.
        """
        # QScrollArea létrehozása
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameStyle(QFrame.Box)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)

        # Belső widget a KPI kártyáknak
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(10, 10, 10, 10)

        # 🎯 ENHANCED STATISTICS PANEL HOZZÁADÁSA
        self.statistics_panel = EnhancedStatisticsPanel()
        stats_layout.addWidget(self.statistics_panel, stretch=1)

        # Stretch spacer a végén
        stats_layout.addStretch()

        stats_widget.setLayout(stats_layout)
        scroll_area.setWidget(stats_widget)

        logger.info("✅ Dashboard KPI kártyák területe létrehozva (QScrollArea-ban)")
        return scroll_area

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

    def start_trend_analysis(self) -> None:
        """🚀 ENHANCED TREND ELEMZÉS INDÍTÁSA"""
        try:
            # Input validation
            location = self.location_combo.currentText().strip()
            parameter = self.parameter_combo.currentText()
            time_range = self.time_combo.currentText()

            if not location:
                self.error_occurred.emit("Kérlek válassz várost!")
                return

            if len(location) < 2:
                self.error_occurred.emit("Legalább 2 karakteres város név szükséges!")
                return

            logger.info(f"🚀 ENHANCED TREND ANALYSIS START: {location} - {parameter} - {time_range}")

            # UI update
            self.analyze_button.setEnabled(False)
            self.analyze_button.setText("⏳ Dashboard Elemzés folyamatban...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            # Signal emission
            self.analysis_started.emit()

            # Worker thread létrehozása
            self.current_worker = TrendAnalyticsWorker(location, parameter, time_range)

            # Worker signals connecting
            self.current_worker.progress_updated.connect(self.progress_bar.setValue)
            self.current_worker.data_received.connect(self.on_analysis_completed)
            self.current_worker.error_occurred.connect(self.on_analysis_error)
            self.current_worker.finished.connect(self.on_worker_finished)

            # Worker start
            self.current_worker.start()

        except Exception as e:
            logger.error(f"❌ Enhanced trend analysis start hiba: {e}")
            self.on_analysis_error(f"Elemzés indítási hiba: {str(e)}")

    def on_analysis_completed(self, trend_results: Dict) -> None:
        """🎉 ENHANCED TREND ELEMZÉS BEFEJEZÉSE"""
        try:
            logger.info(f"🎉 ENHANCED TREND ANALYSIS COMPLETED: {trend_results['settlement_name']}")

            # 🎨 PLOTLY CHART FRISSÍTÉSE
            self.chart.update_chart(trend_results)
            logger.info("✅ Plotly chart frissítve")

            # 🎯 DASHBOARD KPI KÁRTYÁK FRISSÍTÉSE
            logger.info("🎯 Dashboard KPI kártyák frissítése kezdése...")
            self.statistics_panel.update_statistics(trend_results)
            logger.info("✅ Dashboard KPI kártyák frissítve")

            # Signal emission
            self.analysis_completed.emit(trend_results)

        except Exception as e:
            logger.error(f"❌ Enhanced analysis completion handling hiba: {e}")
            self.on_analysis_error(f"Eredmény feldolgozási hiba: {str(e)}")

    def on_analysis_error(self, error_message: str) -> None:
        """❌ ENHANCED TREND ELEMZÉS HIBA KEZELÉSE"""
        logger.error(f"❌ ENHANCED TREND ANALYSIS ERROR: {error_message}")

        # Error display in Plotly chart
        self.chart.show_error_chart(error_message)

        # Error display in KPI cards
        self.statistics_panel.show_error_cards(error_message)

        # Signal emission
        self.error_occurred.emit(error_message)

    def on_worker_finished(self) -> None:
        """Worker thread befejezése (VÁLTOZATLAN)"""
        # UI reset
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("🚀 Dashboard Elemzés Indítása")
        self.progress_bar.setVisible(False)

        # Worker cleanup
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None

        logger.info("✅ Enhanced worker thread finished and cleaned up")

    def set_location(self, location_name: str, latitude: float, longitude: float) -> None:
        """External location setting (VÁLTOZATLAN)"""
        self.location_combo.setCurrentText(location_name)
        self.on_location_changed(location_name)

        logger.info(f"📍 External location set: {location_name} ({latitude:.4f}, {longitude:.4f})")


# Theme integration (VÁLTOZATLAN)
def register_trend_analytics_theme(theme_manager: ThemeManager) -> None:
    """Theme manager integráció"""
    if theme_manager:
        # Register trend analytics specific styling
        pass


if __name__ == "__main__":
    # Standalone testing
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test window
    window = TrendAnalyticsTab()
    window.setWindowTitle("🚀 Enhanced Trend Analytics v4.2 - KPI DASHBOARD KÉSZ!")
    window.resize(1600, 1000)
    window.show()

    sys.exit(app.exec())
