#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trend Analytics Tab - UI Builder

🎨 UI elemek létrehozása trend analytics tabhoz

Képességek:
- Header létrehozása
- Controls panel létrehozása
- Chart container létrehozása
- Dashboard statistics area létrehozása

Fájl: src/presentation/gui/trend_analytics/trend_analytics_tab/ui_builder.py
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from ..trend_widgets import EnhancedStatisticsPanel, InteractiveTrendChart


def create_header(parent_widget: QWidget) -> QWidget:
    """
    Professional header létrehozása (VÁLTOZATLAN).

    Args:
        parent_widget: Szülő widget

    Returns:
        QWidget: Header widget
    """
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
    parent_widget.layout().addWidget(header)
    return header


def create_controls_panel(parent_widget: QWidget) -> dict:
    """
    🔥 ELEMZÉSI PARAMÉTEREK PANEL (VÁLTOZATLAN).

    Args:
        parent_widget: Szülő widget

    Returns:
        Dict with UI elements
    """
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

    location_combo = QComboBox()
    location_combo.setEditable(True)
    location_combo.setPlaceholderText("Írj be település nevet...")
    location_combo.setMinimumWidth(200)
    location_group.addWidget(location_combo)
    controls_layout.addLayout(location_group)

    # Paraméter választó
    param_group = QVBoxLayout()
    param_label = QLabel("📊 Paraméter:")
    param_label.setFont(QFont("Arial", 10, QFont.Bold))
    param_group.addWidget(param_label)

    parameter_combo = QComboBox()
    parameter_combo.addItems([
        "🥶 Minimum hőmérséklet",
        "🔥 Maximum hőmérséklet",
        "🌡️ Átlag hőmérséklet",
        "🌧️ Csapadékmennyiség",
        "💨 Szélsebesség",
        "💨 Széllökések"
    ])
    parameter_combo.setCurrentText("🔥 Maximum hőmérséklet")
    param_group.addWidget(parameter_combo)
    controls_layout.addLayout(param_group)

    # Időtartam választó
    time_group = QVBoxLayout()
    time_label = QLabel("🕒 Időtartam:")
    time_label.setFont(QFont("Arial", 10, QFont.Bold))
    time_group.addWidget(time_label)

    time_combo = QComboBox()
    time_combo.addItems([
        "5 év",
        "10 év",
        "25 év",
        "55 év (teljes)"
    ])
    time_combo.setCurrentText("5 év")
    time_group.addWidget(time_combo)
    controls_layout.addLayout(time_group)

    # Analyze button
    analyze_button = QPushButton("🚀 Dashboard Elemzés Indítása")
    analyze_button.setFont(QFont("Arial", 11, QFont.Bold))
    analyze_button.setStyleSheet("""
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
    controls_layout.addWidget(analyze_button)

    layout.addLayout(controls_layout)

    # Progress bar
    progress_bar = QProgressBar()
    progress_bar.setVisible(False)
    progress_bar.setStyleSheet("""
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
    layout.addWidget(progress_bar)

    panel.setLayout(layout)
    parent_widget.layout().addWidget(panel)

    return {
        "location_combo": location_combo,
        "parameter_combo": parameter_combo,
        "time_combo": time_combo,
        "analyze_button": analyze_button,
        "progress_bar": progress_bar
    }


def create_plotly_chart_container(parent_widget: QWidget) -> "InteractiveTrendChart":
    """
    🎨 PLOTLY CHART CONTAINER LÉTREHOZÁSA.

    Args:
        parent_widget: Szülő widget

    Returns:
        InteractiveTrendChart: Plotly chart widget
    """
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
    from ..trend_widgets import InteractiveTrendChart
    chart = InteractiveTrendChart()
    layout.addWidget(chart)

    container.setLayout(layout)
    parent_widget.layout().addWidget(container)

    return chart


def create_dashboard_statistics_area(parent_widget: QWidget) -> "EnhancedStatisticsPanel":
    """
    🎯 DASHBOARD KPI KÁRTYÁK TERÜLETE - QScrollArea-ban.

    Ez a metódus létrehozza a KPI kártyákat tartalmazó dashboard-ot
    QScrollArea-ban, hogy kis képernyőkön is jól használható legyen.

    Args:
        parent_widget: Szülő widget

    Returns:
        EnhancedStatisticsPanel: Statistics panel widget
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

    # 🎯 ENHANCED STATISTICS PANEL
    from ..trend_widgets import EnhancedStatisticsPanel
    statistics_panel = EnhancedStatisticsPanel()
    stats_layout.addWidget(statistics_panel, stretch=1)

    # Stretch spacer a végén
    stats_layout.addStretch()

    stats_widget.setLayout(stats_layout)
    scroll_area.setWidget(stats_widget)

    parent_widget.layout().addWidget(scroll_area)

    return statistics_panel


def setup_content_splitter(parent_widget: QWidget, chart_container: QWidget, stats_area: QWidget) -> None:
    """
    🔧 QSplitter IMPLEMENTÁCIÓ MEGTARTVA (v3.3 kompatibilitás).

    Args:
        parent_widget: Szülő widget
        chart_container: Chart container widget
        stats_area: Stats area widget
    """
    # 🔧 QSplitter IMPLEMENTÁCIÓ MEGTARTVA (v3.3 kompatibilitás)
    content_splitter = QSplitter(Qt.Horizontal)
    content_splitter.setChildrenCollapsible(False)

    # Chart area (bal oldal) - PLOTLY CHART
    chart_container.setMinimumHeight(400)
    chart_container.setMinimumWidth(600)
    content_splitter.addWidget(chart_container)

    # 🎯 DASHBOARD STATISTICS AREA - KPI KÁRTYÁK
    stats_area.setMinimumWidth(400)
    content_splitter.addWidget(stats_area)

    # 🔧 KEZDEI MÉRETARÁNY: 67% chart, 33% stats (VÁLTOZATLAN)
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

    parent_widget.layout().addWidget(content_splitter, stretch=1)
