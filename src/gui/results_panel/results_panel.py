#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Results Panel Main Module
MVC kompatibilis eredmények megjelenítő fő panel.
🎨 KRITIKUS JAVÍTÁS: ColorPalette API integráció - scheme.border → scheme.get_color("info", "light")
🌪️ WIND GUSTS TÁMOGATÁS: Minden tab frissítve élethű széllökés kezelésre.
🔧 MODULÁRIS BONTÁS: chart_widgets.py → chart_container.py import frissítés

🚀 PROFESSZIONÁLIS KÓDOLÁSI ELVEK:
✅ DRY: Közös utility osztályok használata
✅ KISS: Egyszerű, érthető panel kezelés
✅ YAGNI: Csak szükséges funkcionalitás
✅ SOLID: MVC kompatibilitás, egyszeres felelősség
✅ Type hints: Minden metódus explicit típusokkal
✅ Error handling: Robusztus kivételkezelés
✅ Logging: Strukturált működés követés
"""

import logging
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ...config import GUIConfig
from ..theme_manager import get_theme_manager, register_widget_for_theming
from .quick_overview_tab import QuickOverviewTab
from .detailed_charts_tab import DetailedChartsTab
from .data_table_tab import DataTableTab
from .extreme_events_tab import ExtremeEventsTab

# Logging konfigurálása
logger = logging.getLogger(__name__)


class ResultsPanel(QWidget):
    """
    MVC kompatibilis eredmények megjelenítő fő panel.
    🎨 KRITIKUS JAVÍTÁS: ColorPalette API integráció - scheme.border → scheme.get_color("info", "light")
    🌪️ WIND GUSTS TÁMOGATÁS: Minden tab frissítve élethű széllökés kezelésre.
    
    🚀 PROFESSZIONÁLIS KÓDOLÁSI ELVEK:
    ✅ DRY: Közös utility osztályok használata
    ✅ KISS: Egyszerű, érthető panel kezelés
    ✅ YAGNI: Csak szükséges funkcionalitás
    ✅ SOLID: MVC kompatibilitás, egyszeres felelősség
    ✅ Type hints: Minden metódus explicit típusokkal
    ✅ Error handling: Robusztus kivételkezelés
    ✅ Logging: Strukturált működés követés
    """
    
    # === KIMENŐ SIGNALOK ===
    extreme_weather_requested = Signal()
    export_requested = Signal(str)
    chart_type_changed = Signal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Eredmény panel inicializálása."""
        super().__init__(parent)
        
        logger.info("ResultsPanel inicializálás START (ColorPalette API + WIND GUSTS support)")
        
        # === THEMEMANAGER INICIALIZÁLÁSA ===
        self.theme_manager = get_theme_manager()
        
        # === ÁLLAPOT VÁLTOZÓK ===
        self.current_data: Optional[Dict[str, Any]] = None
        self.current_city: Optional[str] = None
        
        # === TAB WIDGET REFERENCIÁK ===
        self.tab_widget: Optional[QTabWidget] = None
        self.overview_tab: Optional[QuickOverviewTab] = None
        self.charts_tab: Optional[DetailedChartsTab] = None
        self.table_tab: Optional[DataTableTab] = None
        self.extreme_tab: Optional[ExtremeEventsTab] = None
        
        # === UI INICIALIZÁLÁSA ===
        self._init_ui()
        self._connect_internal_signals()
        
        # === THEMEMANAGER REGISZTRÁCIÓ ===
        self._register_widgets_for_theming()
        
        logger.info("ResultsPanel inicializálás BEFEJEZVE (ColorPalette API + WIND GUSTS support)")
    
    def _init_ui(self) -> None:
        """UI elemek inicializálása."""
        logger.debug("ResultsPanel._init_ui() START")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # === FŐCÍM ===
        title_layout = QHBoxLayout()
        
        self.title_label = QLabel("📊 Időjárási Adatok Elemzése")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        self.global_export_btn = QPushButton("📁 Export")
        self.global_export_btn.clicked.connect(lambda: self.export_requested.emit("csv"))
        title_layout.addWidget(self.global_export_btn)
        
        layout.addLayout(title_layout)
        
        # === TAB WIDGET LÉTREHOZÁSA ===
        self.tab_widget = QTabWidget()
        
        # === TAB-OK LÉTREHOZÁSA ===
        self.overview_tab = QuickOverviewTab()
        self.tab_widget.addTab(self.overview_tab, "📊 Gyors Áttekintés")
        
        self.charts_tab = DetailedChartsTab()
        self.tab_widget.addTab(self.charts_tab, "📈 Részletes Diagramok")
        
        self.table_tab = DataTableTab()
        self.tab_widget.addTab(self.table_tab, "📋 Adattáblázat")
        
        # 🌪️ KRITIKUS JAVÍTÁS: Extrém események tab WIND GUSTS támogatással
        self.extreme_tab = ExtremeEventsTab()
        self.tab_widget.addTab(self.extreme_tab, "⚡ Extrém Események")
        
        layout.addWidget(self.tab_widget)
        
        logger.debug("ResultsPanel._init_ui() BEFEJEZVE")
    
    def _register_widgets_for_theming(self) -> None:
        """Widget-ek regisztrálása ThemeManager-hez."""
        register_widget_for_theming(self, "container")
        register_widget_for_theming(self.tab_widget, "container")
        register_widget_for_theming(self.title_label, "text")
        register_widget_for_theming(self.global_export_btn, "button")
        
        logger.debug("ResultsPanel - Főkomponensek regisztrálva ColorPalette API-hez")
    
    def _connect_internal_signals(self) -> None:
        """Belső signal-slot kapcsolatok."""
        if self.extreme_tab:
            self.extreme_tab.extreme_weather_requested.connect(self.extreme_weather_requested.emit)
        
        if self.table_tab:
            if self.table_tab.csv_btn:
                self.table_tab.csv_btn.clicked.connect(lambda: self.export_requested.emit("csv"))
            
            if self.table_tab.excel_btn:
                self.table_tab.excel_btn.clicked.connect(lambda: self.export_requested.emit("excel"))
        
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _on_theme_changed(self, theme_name: str) -> None:
        """Téma változás kezelése."""
        logger.debug(f"ResultsPanel téma változás: {theme_name}")
        self._apply_tab_widget_theming()
    
    def _apply_tab_widget_theming(self) -> None:
        """
        🎨 KRITIKUS JAVÍTÁS: Tab widget CSS alkalmazása ColorPalette API-val.
        scheme.border → scheme.get_color("info", "light")
        """
        if not self.tab_widget:
            return
        
        scheme = self.theme_manager.get_color_scheme()
        if not scheme:
            return
        
        # 🎨 KRITIKUS JAVÍTÁS: ColorPalette API használata scheme.attribute helyett
        border_color = scheme.get_color("info", "light") or "#d1d5db"
        surface_color = scheme.get_color("surface", "base") or "#ffffff"
        surface_variant_color = scheme.get_color("surface", "light") or "#f5f5f5"
        on_surface_variant_color = scheme.get_color("info", "base") or "#6b7280"
        hover_overlay_color = scheme.get_color("primary", "light") or "#dbeafe"
        primary_color = scheme.get_color("primary", "base") or "#2563eb"
        
        css = f"""
        QTabWidget::pane {{
            border: 1px solid {border_color};
            border-radius: 8px;
            background: {surface_color};
        }}
        QTabWidget::tab-bar {{
            alignment: left;
        }}
        QTabBar::tab {{
            background: {surface_variant_color};
            border: 1px solid {border_color};
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 12px 20px;
            margin-right: 2px;
            font-weight: 500;
            font-size: 13px;
            color: {on_surface_variant_color};
        }}
        QTabBar::tab:hover {{
            background: {hover_overlay_color};
            color: {primary_color};
        }}
        QTabBar::tab:selected {{
            background: {surface_color};
            border-bottom: 1px solid {surface_color};
            color: {primary_color};
            font-weight: 600;
        }}
        """
        
        self.tab_widget.setStyleSheet(css)
        
        logger.debug("Tab widget ColorPalette API styling applied")
    
    # === PUBLIKUS API (CONTROLLER FELŐLI KOMMUNIKÁCIÓ) ===
    
    def update_data(self, data: Dict[str, Any], city_name: str) -> None:
        """
        Adatok frissítése új időjárási adatokkal.
        🌪️ WIND GUSTS TÁMOGATÁS: Minden tab frissítve élethű széllökés kezelésre.
        
        Args:
            data: OpenMeteo API válasz
            city_name: Város neve
        """
        logger.info(f"ResultsPanel.update_data() - City: {city_name} (ColorPalette API + WIND GUSTS support)")
        
        try:
            self.current_data = data
            self.current_city = city_name
            
            # === TAB FRISSÍTÉSEK ===
            if self.overview_tab:
                logger.debug("QuickOverviewTab frissítése (ColorPalette API + WIND GUSTS)...")
                self.overview_tab.update_data(data, city_name)
            
            if self.charts_tab:
                logger.debug("DetailedChartsTab frissítése...")
                self.charts_tab.update_data(data)
            
            if self.table_tab:
                logger.debug("DataTableTab frissítése...")
                self.table_tab.update_data(data)
            
            # 🌪️ KRITIKUS JAVÍTÁS: EXTRÉM ESEMÉNYEK TAB WIND GUSTS TÁMOGATÁSSAL
            if self.extreme_tab:
                logger.debug("ExtremeEventsTab frissítése (ColorPalette API + WIND GUSTS)...")
                self.extreme_tab.update_data(data)
            
            logger.info("ResultsPanel.update_data() ÖSSZES TAB FRISSÍTÉSE SIKERES! (ColorPalette API + WIND GUSTS)")
            
        except Exception as e:
            logger.error(f"ResultsPanel adatfrissítési hiba: {e}")
            self.clear_data()
    
    def clear_data(self) -> None:
        """Adatok törlése."""
        logger.debug("ResultsPanel.clear_data() MEGHÍVVA")
        
        self.current_data = None
        self.current_city = None
        
        if self.overview_tab:
            self.overview_tab._clear_stats()
        
        if self.charts_tab:
            self.charts_tab.clear_data()
        
        if self.table_tab:
            self.table_tab.clear_data()
        
        if self.extreme_tab:
            self.extreme_tab._clear_extremes()
        
        logger.debug("ResultsPanel.clear_data() BEFEJEZVE")
    
    def apply_theme(self, dark_theme: bool) -> None:
        """Téma alkalmazása."""
        logger.debug(f"ResultsPanel.apply_theme({dark_theme}) MEGHÍVVA")
        
        if self.charts_tab:
            self.charts_tab.apply_theme(dark_theme)
        
        if self.table_tab:
            self.table_tab.apply_theme(dark_theme)
        
        self._apply_tab_widget_theming()
        
        logger.debug("ResultsPanel.apply_theme() BEFEJEZVE")
    
    # === TAB SPECIFIKUS API ===
    
    def switch_to_tab(self, tab_name: str) -> None:
        """Specifikus tab-ra váltás."""
        if not self.tab_widget:
            return
        
        tab_indices = {
            "overview": 0,
            "charts": 1,
            "table": 2,
            "extreme": 3
        }
        
        if tab_name in tab_indices:
            self.tab_widget.setCurrentIndex(tab_indices[tab_name])
    
    def get_current_tab(self) -> str:
        """Jelenlegi aktív tab nevének lekérdezése."""
        if not self.tab_widget:
            return "overview"
        
        current_index = self.tab_widget.currentIndex()
        tab_names = ["overview", "charts", "table", "extreme"]
        
        if 0 <= current_index < len(tab_names):
            return tab_names[current_index]
        return "overview"
    
    # === PUBLIKUS GETTEREK ===
    
    def get_charts_container(self) -> Optional[object]:
        """Charts container referenciájának lekérdezése."""
        if self.charts_tab:
            return self.charts_tab.charts_container
        return None
    
    def get_data_table(self) -> Optional[object]:
        """Data table referenciájának lekérdezése."""
        if self.table_tab:
            return self.table_tab.data_table
        return None
    
    # === THEMEMANAGER PUBLIKUS API ===
    
    def apply_theme_by_name(self, theme_name: str) -> None:
        """Téma alkalmazása név alapján."""
        success = self.theme_manager.set_theme(theme_name)
        if success:
            logger.info(f"ResultsPanel téma alkalmazva: {theme_name}")
        else:
            logger.error(f"ResultsPanel téma alkalmazás sikertelen: {theme_name}")
    
    def get_current_theme_name(self) -> str:
        """Jelenlegi téma nevének lekérdezése."""
        return self.theme_manager.get_current_theme()
