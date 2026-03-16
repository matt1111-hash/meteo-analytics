#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Analytics View - UI Builder Module
UI komponensek létrehozása az AnalyticsViewhoz.
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.presentation.gui.analytics.analytics_view.core import AnalyticsView


logger = logging.getLogger(__name__)


class AnalyticsViewUIBuilder:
    """UI építő osztály az AnalyticsViewhoz."""

    def __init__(self, view: "AnalyticsView"):
        """Inicializálás."""
        self.view = view

    def create_header(self) -> QHBoxLayout:
        """Fejléc létrehozása."""
        layout = QHBoxLayout()

        # Cím
        title_label = QLabel(
            "🎯 Konstans Heatmap Klímakutató Dashboard + Régió Elemzés + DEDICATED Wind Chartok"
        )
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

    def create_location_info_group(self) -> QGroupBox:
        """Lokáció információs panel - EXTRA KOMPAKT."""
        group = QGroupBox("📍 Lokáció")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(4, 4, 4, 4)

        self.view.location_info_label = QLabel("Nincs kiválasztott lokáció")
        self.view.location_info_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 2px;
                padding: 4px;
                font-size: 9px;
            }
        """)
        layout.addWidget(self.view.location_info_label)

        return group

    def create_refactored_multi_city_panel(self) -> QGroupBox:
        """🚀 REFAKTORÁLT Multi-City régió elemzés panel - SIGNAL EMISSION."""
        group = QGroupBox("🌍 RÉGIÓ ELEMZÉS")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Régió választó
        region_layout = QVBoxLayout()
        region_label = QLabel("📍 Válassz régiót:")
        region_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        region_layout.addWidget(region_label)

        self.view.region_combo = QComboBox()
        self.view.region_combo.addItems(
            [
                "Észak-Magyarország",
                "Észak-Alföld",
                "Dél-Alföld",
                "Közép-Magyarország",
                "Közép-Dunántúl",
                "Nyugat-Dunántúl",
                "Dél-Dunántúl",
            ]
        )
        self.view.region_combo.setStyleSheet("""
            QComboBox {
                padding: 3px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 9px;
            }
        """)
        region_layout.addWidget(self.view.region_combo)
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

        self.view.analysis_buttons = []

        for query_type, text, bg, hover, pressed in query_configs:
            button = QPushButton(text)
            button.setProperty("query_type", query_type)
            button.clicked.connect(self.view._emit_query_request)
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
            self.view.analysis_buttons.append(button)

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

    def create_statistics_panel(self) -> QWidget:
        """Statisztikák panel + Refaktorált Multi-City - KOMPAKT KÁRTYÁS RENDSZER."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(3, 3, 3, 3)

        # 🚀 REFAKTORÁLT MULTI-CITY RÉGIÓ ELEMZÉS PANEL
        multi_city_group = self.create_refactored_multi_city_panel()
        layout.addWidget(multi_city_group)

        # Statisztikák csoport
        stats_group = QGroupBox("📈 Statisztikák")
        stats_layout = QVBoxLayout(stats_group)

        # Görgetési terület
        self.view.statistics_area = QScrollArea()
        self.view.statistics_area.setWidgetResizable(True)
        self.view.statistics_area.setMinimumHeight(150)

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
        self.view.statistics_area.setWidget(stats_content)

        stats_layout.addWidget(self.view.statistics_area)
        layout.addWidget(stats_group)

        return widget

    def create_tab_dashboard(self) -> QWidget:
        """Tab-os klímakutató dashboard + DEDICATED WIND CHARTOK."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Import a widgetekhez
        from ..analytics_tabs import ClimateTabWidget
        from ..analytics_widgets import RecordSummaryCard

        # Rekord summary kártya (kompakt)
        self.view.record_summary = RecordSummaryCard()
        layout.addWidget(self.view.record_summary)

        # Climate tab widget - KONSTANS HEATMAP BEAUFORT + MAX SZÉLLÖKÉS + DEDICATED WIND CHARTOK VERZIÓ
        self.view.climate_tabs = ClimateTabWidget()
        layout.addWidget(self.view.climate_tabs, 1)  # Expandálható

        return widget
