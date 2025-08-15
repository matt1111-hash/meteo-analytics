#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Main Window Module - ANALYTICS → MAP SYNC FIX BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA!
Refaktorált fő alkalmazás ablak modulja - CLEAN ARCHITECTURE SINGLE CITY FÓKUSSZAL + TREND ANALYTICS TAB + ANALYTICS → TÉRKÉP AUTOMATIKUS INTEGRÁCIÓ + MULTI-CITY RÉGIÓ/MEGYE SUPPORT + SIGNAL CONNECTIONS IMPLEMENTÁLVA + HIBÁS JELZÉSEK ELTÁVOLÍTVA.

🚨 ANALYTICS → MAP SYNC FIX BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA:
✅ _setup_control_panel_connections() metódus implementálva
✅ Debug wrappers minden signal típushoz
✅ Signal connections: analysis_parameters_changed, weather_parameters_changed, date_range_changed, parameters_bundle_changed
✅ ControlPanel → HungarianMapTab direkt signal connections
✅ Comprehensive parameter bundle alapú sync
✅ Debug logging minden signal emit-nél
🔧 HIBÁS JELZÉSEK ELTÁVOLÍTVA: analytics_panel.analysis_completed hibás bekötések törölve!

🔥 ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA:
✅ _handle_analytics_view_query() handler metódus kész
✅ _on_multi_city_result_ready_for_views() szétosztó metódus implementálva
✅ AnalyticsView.multi_city_query_requested signal connection
✅ AnalyticsView.update_with_multi_city_result() publikus slot bekötése
✅ Analytics gombok → központi lekérdező rendszer integráció
✅ Signal chain: AnalyticsView → MainWindow → MultiCityEngine → HungarianMapTab
✅ Duplikált lekérdező logika eltávolítása AnalyticsView-ból
🔧 HIBÁS JELZÉSEK ELTÁVOLÍTVA: analytics_completed → térkép hibás frissítés törölve!

🎉 MULTI-CITY RÉGIÓ/MEGYE TÉRKÉP INTEGRÁCIÓ 100% BEFEJEZVE:
✅ multi_city_weather_requested signal kezelés implementálva
✅ _handle_multi_city_weather_request() handler metódus kész  
✅ Multi-City Engine teljes integráció
✅ Régió/megye lekérdezés → térkép overlay automatikus generálás
✅ AnalyticsResult objektum közvetlen átadás HungarianMapTab-nek (NO DICT CONVERSION!)
✅ Analytics View bypass - közvetlen térkép frissítés
✅ Error handling multi-city requestekhez
✅ Debug üzenetek teljes workflow követéséhez

🌤️ TISZTA ANALYTICS → TÉRKÉP INTEGRATION:
✅ Csak a központi, paraméterezett adatkezelés marad
✅ Hibás, felülíró jelzések eltávolítva
✅ Query type alapú térképi paraméter beállítás
✅ Egyértelmű adatfolyam: AnalyticsView → MainWindow → HungarianMapTab

🔧 KRITIKUS JAVÍTÁS - WINDSPEED METRIC BEFEJEZÉSE:
✅ QUERY_TYPE_TO_PARAMETER mapping implementálva
✅ "windiest_today" → "Szél" paraméter mapping
✅ handle_multi_city_weather_request TELJES implementáció
✅ 2-lépéses koordináció: paraméter beállítás + adat átadás
✅ Enhanced debug logging minden lépéshez

FÁJL HELYE: src/gui/main_window.py
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QSplitter, QStatusBar, QMenuBar, QMessageBox, QToolBar, QLabel,
    QSizePolicy
)
from PySide6.QtCore import Qt, QSettings, Signal, QSize
from PySide6.QtGui import QAction, QIcon, QActionGroup

from ..config import AppInfo, GUIConfig
from .utils import (
    GUIConstants, ThemeType, get_source_display_name, get_optimal_data_source,
    format_provider_usage, calculate_provider_costs, get_provider_warning_level,
    format_provider_status, get_provider_icon, format_cost_summary
)
from .theme_manager import get_theme_manager, register_widget_for_theming, ThemeManager
from .color_palette import ColorPalette
from .app_controller import AppController
from .control_panel import ControlPanel
from .results_panel import ResultsPanel
from .data_widgets import WeatherDataTable
from .workers.data_fetch_worker import WorkerManager
from .dialogs import ExtremeWeatherDialog
from .analytics_view import AnalyticsView
from .map_view import MapView
from .trend_analytics_tab import TrendAnalyticsTab
from .hungarian_map_tab import HungarianMapTab


class MainWindow(QMainWindow):
    """
    🚨 ANALYTICS → MAP SYNC FIX BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA + 🔥 ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + 🎉 MULTI-CITY RÉGIÓ/MEGYE TÉRKÉP INTEGRÁCIÓ 100% BEFEJEZVE + 🌤️ TISZTA ANALYTICS → TÉRKÉP INTEGRATION + 🚀 TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE - CLEAN ARCHITECTURE SINGLE CITY FÓKUSSZAL + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ANALYTICS EGYSZERŰSÍTETT INTEGRÁCIÓ + PROVIDER STATUS BAR + THEMEMANAGER + DUAL-API + MAP VIEW INTEGRÁCIÓ + TREND ANALYTICS TAB + 🔧 WINDSPEED METRIC TELJES JAVÍTÁS.
    """
    
    # 🔧 KRITIKUS: QUERY TYPE → TÉRKÉP PARAMÉTER MAPPING - WINDSPEED JAVÍTÁS!
    QUERY_TYPE_TO_PARAMETER = {
        "hottest_today": "Hőmérséklet",
        "coldest_today": "Hőmérséklet", 
        "windiest_today": "Szél",        # ← EZ A KRITIKUS JAVÍTÁS!
        "wettest_today": "Csapadék",
        "rainiest_today": "Csapadék",
        "sunniest_today": "Hőmérséklet",
        "temperature_range": "Hőmérséklet"
    }
    
    # Signalok a téma kezeléshez
    theme_changed = Signal(str)  # theme name
    view_changed = Signal(str)   # view name
    
    # 🌍 Provider signalok
    provider_status_updated = Signal(str)  # provider status message
    
    def __init__(self):
        """Főablak inicializálása - ANALYTICS → MAP SYNC FIX BEFEJEZVE + ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA."""
        super().__init__()
        
        print("🚨 DEBUG: ANALYTICS → MAP SYNC FIX BEFEJEZVE + ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA MainWindow __init__ started")
        
        # QSettings a beállítások perzisztálásához
        self.settings = QSettings("Weather Analytics", AppInfo.NAME)
        
        # 🎨 THEMEMANAGER INTEGRÁCIÓ
        self.theme_manager = get_theme_manager()
        self.color_palette = ColorPalette()
        
        # 🌍 PROVIDER STATUS TRACKING
        self.current_provider = "auto"
        self.provider_usage_stats = {}
        self.provider_cost_summary = ""
        self.provider_warning_level = None
        
        # === MVC KOMPONENSEK LÉTREHOZÁSA ===
        
        print("🎯 DEBUG: Creating CLEAN AppController with DUAL-API...")
        # Controller (Model + business logic)
        self.controller = AppController()
        print("✅ DEBUG: CLEAN AppController created with DUAL-API support")
        
        # Worker Manager (a Controller használja, de referencia kell a UI-hoz)
        self.worker_manager = self.controller.worker_manager
        
        # === VIEW KOMPONENSEK ===
        
        # Navigációs toolbar
        self.toolbar: Optional[QToolBar] = None
        
        # Stacked Widget a nézetek váltásához
        self.stacked_widget: Optional[QStackedWidget] = None
        
        # VIEW REFERENCIÁK
        self.current_view_name = "single_city"  # 🧹 Single City az alapértelmezett
        self.current_theme = ThemeType.LIGHT  # 🎨 ÚJ: Téma tracking
        
        # SingleCity view komponensei (KÖZPONTI FUNKCIONALITÁS)
        self.control_panel: Optional[ControlPanel] = None
        self.results_panel: Optional[ResultsPanel] = None
        self.data_table: Optional[WeatherDataTable] = None
        
        # 📊 ANALYTICS VIEW KOMPONENS - REFAKTORÁLT!
        self.analytics_panel: Optional[AnalyticsView] = None
        
        # 🗺️ MAP VIEW KOMPONENS
        self.map_view: Optional[MapView] = None
        
        # 🌤️ HUNGARIAN MAP TAB KOMPONENS - ÚJ!
        self.hungarian_map_tab: Optional[HungarianMapTab] = None
        
        # 📈 TREND ANALYTICS KOMPONENS - ÚJ!
        self.trend_analytics_tab: Optional[TrendAnalyticsTab] = None
        
        # 🌍 STATUS BAR PROVIDER WIDGETS
        self.provider_status_label: Optional[QLabel] = None
        self.usage_status_label: Optional[QLabel] = None
        self.cost_status_label: Optional[QLabel] = None
        
        # === UI INICIALIZÁLÁSA ===
        
        print("🖼️ DEBUG: Setting up UI...")
        self._setup_window()
        self._init_navigation_toolbar()
        self._init_stacked_views()
        self._init_menu_bar()
        self._init_status_bar_with_provider_display()
        print("✅ DEBUG: UI setup complete")
        
        # === 🧹 CLEAN SIGNAL CHAIN ===
        
        print("🔗 DEBUG: Connecting CLEAN signals...")
        self._connect_mvc_signals()
        print("✅ DEBUG: CLEAN SIGNAL CHAIN CONNECTED")
        
        # === 🚨 ANALYTICS → MAP SYNC SIGNAL CONNECTIONS ===
        
        print("🚨 DEBUG: Setting up ANALYTICS → MAP SYNC signal connections...")
        self._setup_control_panel_connections()
        print("✅ DEBUG: ANALYTICS → MAP SYNC SIGNAL CONNECTIONS CONNECTED")
        
        # === 🎨 THEMEMANAGER SETUP ===
        
        print("🎨 DEBUG: Setting up ThemeManager integration...")
        self._setup_theme_integration()
        print("✅ DEBUG: ThemeManager integration complete")
        
        # === BEÁLLÍTÁSOK BETÖLTÉSE ===
        
        self._load_settings()
        
        print("✅ DEBUG: ANALYTICS → MAP SYNC FIX BEFEJEZVE + ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA MainWindow initialized")
    
    def _setup_window(self) -> None:
        """🔧 LAYOUT CONSTRAINTS OPTIMALIZÁLT ablak alapbeállításai - THEMEMANAGER INTEGRÁCIÓVAL + DUAL-API."""
        self.setWindowTitle(f"{AppInfo.NAME} - {AppInfo.VERSION} (Analytics → Map Sync Fix + Analytics View Refaktorálás + Hibás Jelzések Eltávolítva)")
        
        # 🔧 OPTIMALIZÁLT ABLAK MÉRETEK
        self.setGeometry(
            GUIConstants.MAIN_WINDOW_X,
            GUIConstants.MAIN_WINDOW_Y,
            1400,  # 🔧 SZÉLESEBB ABLAK
            900    # 🔧 MAGASABB ABLAK
        )
        self.setMinimumSize(
            1200,  # 🔧 NAGYOBB MIN WIDTH
            700    # 🔧 NAGYOBB MIN HEIGHT
        )
        
        # 🎨 WIDGET REGISZTRÁCIÓ THEMEMANAGER-HEZ
        register_widget_for_theming(self, "navigation")
        
        # 🎨 Téma rendszer integráció - alapértelmezett light theme
        self._apply_theme_internal(ThemeType.LIGHT)
        
        print("🔧 DEBUG: Window setup complete")
    
    def _setup_theme_integration(self) -> None:
        """
        🎨 ThemeManager integráció beállítása.
        """
        print("🎨 DEBUG: Setting up ThemeManager integration...")
        
        # ThemeManager signalok feliratkozása
        self.theme_manager.theme_changed.connect(self._on_theme_manager_changed)
        
        # Widget regisztrációk fő komponensekhez
        register_widget_for_theming(self, "navigation")
        
        print("✅ DEBUG: ThemeManager integration setup complete")
    
    def _on_theme_manager_changed(self, theme_name: str) -> None:
        """
        🎨 ThemeManager téma változás kezelése.
        
        Args:
            theme_name: Új téma neve ("light" vagy "dark")
        """
        print(f"🎨 DEBUG: MainWindow received ThemeManager theme change: {theme_name}")
        
        # Téma tracking frissítése
        try:
            self.current_theme = ThemeType(theme_name)
        except ValueError:
            self.current_theme = ThemeType.LIGHT
        
        # Splitter téma frissítése
        self._update_splitter_theme(theme_name == "dark")
        
        # Saját signal kibocsátása backward compatibility-hez
        self.theme_changed.emit(theme_name)
        
        print(f"✅ DEBUG: MainWindow theme change handled: {theme_name}")
    
    def _init_navigation_toolbar(self) -> None:
        """
        Navigációs eszköztár létrehozása CLEAN architektúrához + THEMEMANAGER + ANALYTICS - DASHBOARD CLEANUP BEFEJEZVE + TREND ANALYTICS.
        """
        print("🧭 DEBUG: Creating navigation toolbar...")
        
        # Eszköztár létrehozása
        self.toolbar = QToolBar("Navigáció")
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.setIconSize(QSize(24, 24))
        
        # 🎨 WIDGET REGISZTRÁCIÓ THEMEMANAGER-HEZ
        register_widget_for_theming(self.toolbar, "navigation")
        
        # === NAVIGÁCIÓS AKCIÓK ===
        
        # 🏙️ Pontszerű Elemzés (KÖZPONTI NÉZET)
        self.single_city_action = QAction("Város Elemzés", self)
        self.single_city_action.setToolTip("Egyetlen város részletes időjárási elemzése - KÖZPONTI FUNKCIÓ")
        self.single_city_action.triggered.connect(lambda: self._switch_view("single_city"))
        self.single_city_action.setCheckable(True)
        self.single_city_action.setChecked(True)  # 🧹 Single City az alapértelmezett
        self.toolbar.addAction(self.single_city_action)
        
        # 📊 Analytics (REFAKTORÁLT FUNKCIÓ)
        self.analytics_action = QAction("Analitika", self)
        self.analytics_action.setToolTip("Időjárási elemzések és statisztikák (refaktorált)")
        self.analytics_action.triggered.connect(lambda: self._switch_view("analytics"))
        self.analytics_action.setCheckable(True)
        self.toolbar.addAction(self.analytics_action)
        
        # 📈 Trend Elemző (MŰKÖDIK!)
        self.trend_action = QAction("Trend Elemzés", self)
        self.trend_action.setToolTip("Hosszú távú klimatikus trendek elemzése professional vizualizációkkal")
        self.trend_action.triggered.connect(lambda: self._switch_view("trend_analysis"))
        self.trend_action.setCheckable(True)
        self.toolbar.addAction(self.trend_action)
        
        # 🗺️ Interaktív Térkép (MŰKÖDIK!)
        self.map_action = QAction("Térkép", self)
        self.map_action.setToolTip("Interaktív időjárási térkép")
        self.map_action.triggered.connect(lambda: self._switch_view("map_view"))
        self.map_action.setCheckable(True)
        self.toolbar.addAction(self.map_action)
        
        self.toolbar.addSeparator()
        
        # ⚙️ Beállítások
        self.settings_action = QAction("Beállítások", self)
        self.settings_action.setToolTip("Alkalmazás beállítások")
        self.settings_action.triggered.connect(lambda: self._switch_view("settings"))
        self.settings_action.setCheckable(True)
        self.toolbar.addAction(self.settings_action)
        
        # === AKCIÓK CSOPORTOSÍTÁSA (kölcsönös kizárás) ===
        
        self.view_action_group = QActionGroup(self)
        self.view_action_group.addAction(self.single_city_action)
        self.view_action_group.addAction(self.analytics_action)
        self.view_action_group.addAction(self.trend_action)
        self.view_action_group.addAction(self.map_action)
        self.view_action_group.addAction(self.settings_action)
        
        # Eszköztár hozzáadása az ablakhoz
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        print("✅ DEBUG: Navigation toolbar created")
    
    def _init_stacked_views(self) -> None:
        """
        🚨 ANALYTICS → MAP SYNC FIX BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA + 🔥 ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + 🎉 MULTI-CITY RÉGIÓ/MEGYE TÉRKÉP INTEGRÁCIÓ 100% BEFEJEZVE + 🌤️ TISZTA ANALYTICS → TÉRKÉP INTEGRATION + 🚀 TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE QStackedWidget inicializálása különböző nézetekkel.
        """
        print("📚 DEBUG: Creating stacked views...")
        
        # Központi widget és layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 🎨 WIDGET REGISZTRÁCIÓ
        register_widget_for_theming(central_widget, "container")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)
        
        # === STACKED WIDGET LÉTREHOZÁSA ===
        
        self.stacked_widget = QStackedWidget()
        register_widget_for_theming(self.stacked_widget, "container")
        main_layout.addWidget(self.stacked_widget)
        
        # === VIEW-K LÉTREHOZÁSA ===
        
        # 1. Single City View (KÖZPONTI FUNKCIONALITÁS)
        single_city_view = self._create_single_city_view_constraints_optimized()
        self.stacked_widget.addWidget(single_city_view)  # INDEX 0
        
        # 2. Analytics View (REFAKTORÁLT VERZIÓ)
        analytics_view = self._create_analytics_view_refactored()
        self.stacked_widget.addWidget(analytics_view)  # INDEX 1
        
        # 3. Trend Analysis View (VALÓDI TREND ANALYTICS TAB!)
        trend_view = self._create_trend_analysis_view()
        self.stacked_widget.addWidget(trend_view)  # INDEX 2
        
        # 4. Map View (VALÓDI HUNGARIAN MAP TAB!)
        map_view = self._create_hungarian_map_view()
        self.stacked_widget.addWidget(map_view)  # INDEX 3
        
        # 5. Settings View (PLACEHOLDER)
        settings_view = self._create_settings_placeholder()
        self.stacked_widget.addWidget(settings_view)  # INDEX 4
        
        # === ALAPÉRTELMEZETT NÉZET BEÁLLÍTÁSA ===
        
        self.stacked_widget.setCurrentIndex(0)  # Single City View alapértelmezett
        
        print("✅ DEBUG: Stacked views created")
    
    def _create_single_city_view_constraints_optimized(self) -> QWidget:
        """
        🔧 KRITIKUS SPLITTER CONSTRAINTS OPTIMALIZÁLT - Single City View létrehozása - FINAL FIX RESPONSIVE LAYOUT.
        """
        print("🔧 DEBUG: Creating SPLITTER CONSTRAINTS OPTIMALIZÁLT Single City View...")
        
        view = QWidget()
        register_widget_for_theming(view, "container")
        
        layout = QVBoxLayout(view)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        # === 🔧 KRITIKUS JAVÍTÁS: SPLITTER CONSTRAINTS OPTIMALIZÁLT ===
        
        main_splitter = QSplitter(Qt.Horizontal)
        
        print("🔧 DEBUG: Configuring OPTIMALIZÁLT splitter...")
        
        # 🔧 KRITIKUS SPLITTER BEÁLLÍTÁSOK - OPTIMALIZÁLT
        main_splitter.setHandleWidth(18)  # 🔧 SZÉLESEBB HANDLE
        main_splitter.setChildrenCollapsible(False)  # 🔧 Panel-ek nem csukhatók össze
        main_splitter.setOpaqueResize(True)  # 🔧 Valós idejű átméretezés
        
        # 🎨 SPLITTER WIDGET REGISZTRÁCIÓ THEMEMANAGER-HEZ
        register_widget_for_theming(main_splitter, "splitter")
        
        # === BAL OLDAL: CONTROL PANEL - OPTIMALIZÁLT CONSTRAINTS ===
        
        print("🎛️ DEBUG: Creating ControlPanel with FINAL OPTIMALIZÁLT size constraints...")
        self.control_panel = ControlPanel(self.worker_manager)
        
        # 🎨 CONTROL PANEL WIDGET REGISZTRÁCIÓ
        register_widget_for_theming(self.control_panel, "container")
        
        # 🔧 KRITIKUS: OPTIMALIZÁLT PANEL SIZE CONSTRAINTS - FINAL FIX
        self.control_panel.setMinimumWidth(320)  # 🔧 OPTIMALIZÁLT MIN
        self.control_panel.setMaximumWidth(520)  # 🔧 SZÉLESEBB MAX
        
        # 🔧 EXPLICIT SIZE POLICY BEÁLLÍTÁS
        self.control_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        main_splitter.addWidget(self.control_panel)
        print(f"✅ DEBUG: ControlPanel added with FINAL OPTIMALIZÁLT constraints: {320}-{520}px")
        
        # === JOBB OLDAL: RESULTS PANEL - EXPANDABLE OPTIMALIZÁLVA ===
        
        print("📊 DEBUG: Creating ResultsPanel with OPTIMALIZÁLT expand capability...")
        self.results_panel = ResultsPanel()
        
        # 🎨 RESULTS PANEL WIDGET REGISZTRÁCIÓ
        register_widget_for_theming(self.results_panel, "container")
        
        # 🔧 RESULTS PANEL OPTIMALIZÁLT CONSTRAINTS
        self.results_panel.setMinimumWidth(450)  # 🔧 NAGYOBB MINIMUM
        # Nincs maximum width - expandálhat
        
        # 🔧 EXPLICIT SIZE POLICY BEÁLLÍTÁS
        self.results_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        main_splitter.addWidget(self.results_panel)
        print("✅ DEBUG: ResultsPanel added with OPTIMALIZÁLT expand capability")
        
        # === 🔧 KRITIKUS: STRETCH FACTOR KONFIGURÁCIÓK OPTIMALIZÁLVA ===
        
        print("🔧 DEBUG: Setting OPTIMALIZÁLT stretch factors...")
        
        # 🔧 OPTIMALIZÁLT Stretch factor beállítás:
        # 0 = Control Panel (fix szélesség 320-520px között)
        # 1 = Results Panel (kitölti a teljes maradék helyet)
        main_splitter.setStretchFactor(0, 0)  # 🔧 Control panel fix
        main_splitter.setStretchFactor(1, 1)  # 🔧 Results panel teljes stretch
        
        print("✅ DEBUG: OPTIMALIZÁLT stretch factors set")
        
        # === 🔧 KRITIKUS: INITIAL SIZES OPTIMALIZÁLT - FINAL FIX ===
        
        # 🔧 OPTIMALIZÁLT kezdeti méretek
        total_width = 1400  # 🔧 Új ablak szélesség
        control_width = 420  # 🔧 OPTIMALIZÁLT control panel width
        results_width = total_width - control_width - 20  # 🔧 Maradék a results panel-nek
        
        main_splitter.setSizes([control_width, results_width])
        
        print(f"✅ DEBUG: OPTIMALIZÁLT initial sizes set - Control: {control_width}px, Results: {results_width}px")
        
        # === LAYOUT FINALIZÁLÁS ===
        
        layout.addWidget(main_splitter)
        
        print("🔧 DEBUG: SPLITTER CONSTRAINTS OPTIMALIZÁLT Single City View created")
        
        return view
    
    def _create_analytics_view_refactored(self) -> QWidget:
        """
        📊 Analytics View létrehozása - REFAKTORÁLT IMPLEMENTÁCIÓ + THEMEMANAGER + SIGNAL INTEGRATION.
        """
        print("📊 DEBUG: Creating REFAKTORÁLT AnalyticsView with ThemeManager + Signal Integration...")
        
        # Refaktorált AnalyticsView létrehozása
        self.analytics_panel = AnalyticsView()  # 🔧 REFAKTORÁLT VERZIÓ
        
        # 🎨 WIDGET REGISZTRÁCIÓ
        register_widget_for_theming(self.analytics_panel, "container")
        
        print("✅ DEBUG: REFAKTORÁLT AnalyticsView created with ThemeManager + Signal Integration")
        return self.analytics_panel
    
    def _create_trend_analysis_view(self) -> QWidget:
        """
        📈 Trend Analysis view létrehozása - VALÓDI TRENDANALYTICSTAB KOMPONENS + THEMEMANAGER.
        """
        print("📈 DEBUG: Creating real TrendAnalyticsTab component with ThemeManager...")
        
        # Valódi TrendAnalyticsTab komponens létrehozása
        self.trend_analytics_tab = TrendAnalyticsTab()
        
        # 🎨 WIDGET REGISZTRÁCIÓ THEMEMANAGER-HEZ
        register_widget_for_theming(self.trend_analytics_tab, "container")
        
        print("✅ DEBUG: Real TrendAnalyticsTab component created with ThemeManager")
        return self.trend_analytics_tab
    
    def _create_hungarian_map_view(self) -> QWidget:
        """
        🌤️ Hungarian Map view létrehozása - VALÓDI HUNGARIAN MAP TAB KOMPONENS + THEMEMANAGER + WEATHER INTEGRATION.
        """
        print("🌤️ DEBUG: Creating real HungarianMapTab component with ThemeManager + Weather Integration...")
        
        # Valódi HungarianMapTab komponens létrehozása
        self.hungarian_map_tab = HungarianMapTab()
        
        # 🎨 WIDGET REGISZTRÁCIÓ THEMEMANAGER-HEZ
        register_widget_for_theming(self.hungarian_map_tab, "container")
        
        print("✅ DEBUG: Real HungarianMapTab component created with ThemeManager + Weather Integration")
        return self.hungarian_map_tab
    
    def _create_settings_placeholder(self) -> QWidget:
        """Settings view placeholder létrehozása + THEMEMANAGER."""
        view = QWidget()
        register_widget_for_theming(view, "container")
        layout = QVBoxLayout(view)
        
        placeholder = self._create_placeholder_content(
            "Beállítások",
            "Fejlesztés alatt - FÁZIS 8",
            [
                "• Alkalmazás beállítások központosítása",
                "• API konfigurációk",
                "• Téma és megjelenés beállítások",
                "• Nyelvi beállítások",
                "• Export preferenciák"
            ]
        )
        layout.addWidget(placeholder)
        
        return view
    
    def _create_placeholder_content(self, title: str, subtitle: str, features: list) -> QWidget:
        """Egységes placeholder tartalom létrehozása + THEMEMANAGER."""
        placeholder = QWidget()
        register_widget_for_theming(placeholder, "container")
        
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # Főcím
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        register_widget_for_theming(title_label, "text")
        layout.addWidget(title_label)
        
        # Alcím
        subtitle_label = QLabel(subtitle)
        subtitle_label.setAlignment(Qt.AlignCenter)
        register_widget_for_theming(subtitle_label, "text")
        layout.addWidget(subtitle_label)
        
        # Funkciók listája
        features_widget = QWidget()
        register_widget_for_theming(features_widget, "text")
        features_layout = QVBoxLayout(features_widget)
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setAlignment(Qt.AlignLeft)
            register_widget_for_theming(feature_label, "text")
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_widget)
        
        return placeholder
    
    def _switch_view(self, view_name: str) -> None:
        """
        Nézet váltás kezelése.
        
        Args:
            view_name: Nézet neve ("single_city", "analytics", "trend_analysis", "map_view", "settings")
        """
        print(f"🔄 DEBUG: Switching to view: {view_name}")
        
        # View index mapping
        view_indices = {
            "single_city": 0,    # SINGLE CITY KÖZPONTI NÉZET
            "analytics": 1,      # REFAKTORÁLT ANALYTICS VIEW
            "trend_analysis": 2, # 📈 VALÓDI TREND ANALYTICS TAB
            "map_view": 3,       # 🌤️ VALÓDI HUNGARIAN MAP TAB
            "settings": 4
        }
        
        if view_name not in view_indices:
            print(f"⚠️ DEBUG: Unknown view name: {view_name}")
            return
        
        # Nézet váltás
        self.current_view_name = view_name
        view_index = view_indices[view_name]
        self.stacked_widget.setCurrentIndex(view_index)
        
        # Signal kibocsátása
        self.view_changed.emit(view_name)
        
        # Státusz frissítése
        view_titles = {
            "single_city": "Város Elemzés (Központi)",
            "analytics": "Analitika (Refaktorált)",
            "trend_analysis": "Trend Elemzés (Professional)",
            "map_view": "Térkép (Multi-City Régió/Megye + Weather)",
            "settings": "Beállítások"
        }
        
        if hasattr(self, 'status_bar'):
            # 🌍 Provider status megtartása view váltáskor
            self._update_provider_status_display()
        
        print(f"✅ DEBUG: View switched to: {view_name} (index: {view_index})")
    
    def _init_menu_bar(self) -> None:
        """Menüsáv inicializálása."""
        menubar = self.menuBar()
        register_widget_for_theming(menubar, "navigation")
        
        # === FÁJL MENÜ ===
        file_menu = menubar.addMenu("📁 Fájl")
        
        # Export akció
        export_action = QAction("📊 Adatok exportálása...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_data)
        export_action.setEnabled(False)  # Kezdetben letiltva
        file_menu.addAction(export_action)
        self.export_action = export_action  # Referencia a későbbi engedélyezéshez
        
        file_menu.addSeparator()
        
        # Kilépés akció
        exit_action = QAction("🚪 Kilépés", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # === NÉZET MENÜ ===
        view_menu = menubar.addMenu("👁️ Nézet")
        
        # Navigáció
        view_menu.addAction(self.single_city_action)
        view_menu.addAction(self.analytics_action)  # REFAKTORÁLT ANALYTICS
        view_menu.addAction(self.trend_action)  # 📈 VALÓDI TREND ANALYTICS
        view_menu.addAction(self.map_action)  # 🎉 MULTI-CITY RÉGIÓ/MEGYE HUNGARIAN MAP TAB
        view_menu.addAction(self.settings_action)
        
        view_menu.addSeparator()
        
        # 🎨 TÉMA VÁLTÁS - THEMEMANAGER INTEGRÁCIÓ
        light_theme_action = QAction("☀️ Világos téma", self)
        light_theme_action.triggered.connect(lambda: self._apply_theme(ThemeType.LIGHT))
        view_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("🌙 Sötét téma", self)
        dark_theme_action.triggered.connect(lambda: self._apply_theme(ThemeType.DARK))
        view_menu.addAction(dark_theme_action)
        
        view_menu.addSeparator()
        
        # Extrém időjárás ablak
        extreme_action = QAction("⚡ Extrém időjárás...", self)
        extreme_action.setShortcut("Ctrl+X")
        extreme_action.triggered.connect(self._show_extreme_weather)
        extreme_action.setEnabled(False)  # Kezdetben letiltva
        view_menu.addAction(extreme_action)
        self.extreme_action = extreme_action
        
        # === SÚGÓ MENÜ ===
        help_menu = menubar.addMenu("❓ Súgó")
        
        about_action = QAction("ℹ️ Névjegy...", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _init_status_bar_with_provider_display(self) -> None:
        """
        🌍 ENHANCED STATUS BAR inicializálása Provider Display-jel + THEMEMANAGER + DUAL-API.
        """
        print("🌍 DEBUG: Creating enhanced status bar with provider display...")
        
        self.status_bar = QStatusBar()
        register_widget_for_theming(self.status_bar, "navigation")
        self.setStatusBar(self.status_bar)
        
        # === 🌍 PROVIDER STATUS WIDGETS LÉTREHOZÁSA ===
        
        # 1. Provider Status Label
        self.provider_status_label = QLabel("🤖 Automatikus routing")
        self.provider_status_label.setToolTip("Aktív adatforrás provider")
        register_widget_for_theming(self.provider_status_label, "text")
        self.status_bar.addPermanentWidget(self.provider_status_label)
        
        # 2. Usage Status Label  
        self.usage_status_label = QLabel("💎 0/10000 (0%)")
        self.usage_status_label.setToolTip("API használat statisztika")
        register_widget_for_theming(self.usage_status_label, "text")
        self.status_bar.addPermanentWidget(self.usage_status_label)
        
        # 3. Cost Status Label
        self.cost_status_label = QLabel("💰 $0.00/hó")
        self.cost_status_label.setToolTip("Becsült havi költség")
        register_widget_for_theming(self.cost_status_label, "text")
        self.status_bar.addPermanentWidget(self.cost_status_label)
        
        # === KEZDETI PROVIDER STATUS ===
        
        self.status_bar.showMessage("✅ Single City központi nézet aktív - 🚨 Analytics → Map sync BEFEJEZVE - 🔥 Analytics View REFAKTORÁLÁS BEFEJEZVE - 🔧 Hibás Jelzések ELTÁVOLÍTVA - 🗺️ Hungarian Map Tab integrálva - 📈 Trend Analytics működik. [Tiszta térképi paraméter sync + WINDSPEED JAVÍTÁS!]")
        
        # Provider info inicializálása
        self._initialize_provider_status()
        
        print("✅ DEBUG: Enhanced status bar created with provider display")
    
    def _initialize_provider_status(self) -> None:
        """
        🌍 Provider status inicializálása - Controller-től származó információkkal.
        """
        try:
            print("🌍 DEBUG: Initializing provider status...")
            
            # Provider info lekérdezése a Controller-től
            provider_info = self.controller.get_provider_info()
            
            self.current_provider = provider_info.get('current_provider', 'auto')
            self.provider_usage_stats = provider_info.get('usage_stats', {})
            
            # Provider status frissítése
            self._update_provider_status_display()
            
            print("✅ DEBUG: Provider status initialized")
            
        except Exception as e:
            print(f"❌ DEBUG: Provider status initialization error: {e}")
            # Fallback to default values
            self.current_provider = "auto"
            self.provider_usage_stats = {}
            self._update_provider_status_display()
    
    def _update_provider_status_display(self) -> None:
        """
        🌍 Provider status display frissítése a status bar-ban.
        """
        try:
            # 1. Provider Status frissítése
            provider_status = format_provider_status(
                self.current_provider, 
                True,  # is_current
                self.provider_usage_stats
            )
            
            provider_icon = get_provider_icon(self.current_provider)
            self.provider_status_label.setText(f"{provider_icon} {provider_status}")
            
            # 2. Usage Status frissítése
            if self.current_provider == 'open-meteo':
                usage_text = "🌍 Ingyenes (korlátlan)"
            elif self.current_provider == 'auto':
                usage_text = "🤖 Smart routing"
            else:
                # Premium provider usage
                formatted_usage = format_provider_usage(self.provider_usage_stats)
                usage_text = formatted_usage.get(self.current_provider, "💎 0/10000 (0%)")
            
            self.usage_status_label.setText(usage_text)
            
            # 3. Cost Status frissítése
            cost_summary = format_cost_summary(self.provider_usage_stats)
            self.cost_status_label.setText(cost_summary)
            
            # 4. Warning level ellenőrzése
            warning_level = None
            if self.current_provider != 'open-meteo' and self.current_provider != 'auto':
                warning_level = get_provider_warning_level(self.current_provider, self.provider_usage_stats)
            
            # Warning styling alkalmazása
            self._apply_warning_styling(warning_level)
            
            print(f"✅ DEBUG: Provider status display updated: {self.current_provider}")
            
        except Exception as e:
            print(f"❌ DEBUG: Provider status display update error: {e}")
    
    def _apply_warning_styling(self, warning_level: Optional[str]) -> None:
        """
        🌍 Warning level alapján styling alkalmazása status bar widget-ekre.
        
        Args:
            warning_level: "info", "warning", "critical" vagy None
        """
        if warning_level == "critical":
            # Kritikus - piros színezés
            self.usage_status_label.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.cost_status_label.setStyleSheet("color: #dc2626; font-weight: bold;")
        elif warning_level == "warning":
            # Figyelmeztetés - sárga színezés
            self.usage_status_label.setStyleSheet("color: #f59e0b; font-weight: bold;")
            self.cost_status_label.setStyleSheet("color: #f59e0b;")
        elif warning_level == "info":
            # Info - kék színezés
            self.usage_status_label.setStyleSheet("color: #3b82f6;")
            self.cost_status_label.setStyleSheet("color: #3b82f6;")
        else:
            # Normális - alapértelmezett színek
            self.usage_status_label.setStyleSheet("")
            self.cost_status_label.setStyleSheet("")
    
    def _setup_control_panel_connections(self) -> None:
        """
        🚨 KRITIKUS: ANALYTICS → MAP SYNC SIGNAL CONNECTIONS IMPLEMENTÁLÁSA!
        
        Ez a metódus kapcsolja össze a ControlPanel signalokat a HungarianMapTab-bel,
        hogy automatikus legyen a térkép sync minden paraméter változáskor.
        """
        print("🚨 DEBUG: Setting up ANALYTICS → MAP SYNC signal connections...")
        
        if not self.control_panel:
            print("❌ DEBUG: ControlPanel is None - cannot setup signal connections!")
            return
        
        if not self.hungarian_map_tab:
            print("❌ DEBUG: HungarianMapTab is None - cannot setup signal connections!")
            return
        
        # === DEBUG WRAPPER METÓDUSOK ===
        
        def debug_analytics_params_changed(params: Dict[str, Any]):
            print(f"🚨 DEBUG [CONTROL→MAP]: analysis_parameters_changed signal received")
            print(f"🚨 DEBUG: Analytics params: {params}")
        
        def debug_weather_params_changed(params: Dict[str, Any]):
            print(f"🚨 DEBUG [CONTROL→MAP]: weather_parameters_changed signal received") 
            print(f"🚨 DEBUG: Weather params: {params}")
        
        def debug_date_range_changed(start_date: str, end_date: str):
            print(f"🚨 DEBUG [CONTROL→MAP]: date_range_changed signal received")
            print(f"🚨 DEBUG: Date range: {start_date} → {end_date}")
        
        def debug_bundle_changed(bundle: Dict[str, Any]):
            print(f"🚨 DEBUG [CONTROL→MAP]: parameters_bundle_changed signal received")
            print(f"🚨 DEBUG: Bundle keys: {list(bundle.keys()) if bundle else 'NO BUNDLE'}")
        
        # === SIGNAL CONNECTIONS IMPLEMENTÁLÁSA ===
        
        # 1. Analysis Parameters Changed
        if hasattr(self.control_panel, 'analysis_parameters_changed'):
            self.control_panel.analysis_parameters_changed.connect(debug_analytics_params_changed)
            
            # Ellenőrizzük hogy létezik-e az update_analysis_parameters metódus
            if hasattr(self.hungarian_map_tab, 'update_analysis_parameters'):
                self.control_panel.analysis_parameters_changed.connect(
                    self.hungarian_map_tab.update_analysis_parameters
                )
                print("✅ DEBUG: ControlPanel.analysis_parameters_changed → HungarianMapTab.update_analysis_parameters CONNECTED")
            else:
                print("⚠️ DEBUG: HungarianMapTab.update_analysis_parameters method NOT FOUND!")
        else:
            print("⚠️ DEBUG: ControlPanel.analysis_parameters_changed signal NOT FOUND!")
        
        # 2. Weather Parameters Changed  
        if hasattr(self.control_panel, 'weather_parameters_changed'):
            self.control_panel.weather_parameters_changed.connect(debug_weather_params_changed)
            
            # Ellenőrizzük hogy létezik-e az update_weather_parameters metódus
            if hasattr(self.hungarian_map_tab, 'update_weather_parameters'):
                self.control_panel.weather_parameters_changed.connect(
                    self.hungarian_map_tab.update_weather_parameters
                )
                print("✅ DEBUG: ControlPanel.weather_parameters_changed → HungarianMapTab.update_weather_parameters CONNECTED")
            else:
                print("⚠️ DEBUG: HungarianMapTab.update_weather_parameters method NOT FOUND!")
        else:
            print("⚠️ DEBUG: ControlPanel.weather_parameters_changed signal NOT FOUND!")
        
        # 3. Date Range Changed
        if hasattr(self.control_panel, 'date_range_changed'):
            self.control_panel.date_range_changed.connect(debug_date_range_changed)
            
            # Ellenőrizzük hogy létezik-e az update_date_range metódus
            if hasattr(self.hungarian_map_tab, 'update_date_range'):
                self.control_panel.date_range_changed.connect(
                    self.hungarian_map_tab.update_date_range
                )
                print("✅ DEBUG: ControlPanel.date_range_changed → HungarianMapTab.update_date_range CONNECTED")
            else:
                print("⚠️ DEBUG: HungarianMapTab.update_date_range method NOT FOUND!")
        else:
            print("⚠️ DEBUG: ControlPanel.date_range_changed signal NOT FOUND!")
        
        # 4. Parameters Bundle Changed (COMPREHENSIVE)
        if hasattr(self.control_panel, 'parameters_bundle_changed'):
            self.control_panel.parameters_bundle_changed.connect(debug_bundle_changed)
            
            # Ellenőrizzük hogy létezik-e a refresh_with_new_parameters metódus
            if hasattr(self.hungarian_map_tab, 'refresh_with_new_parameters'):
                self.control_panel.parameters_bundle_changed.connect(
                    self.hungarian_map_tab.refresh_with_new_parameters
                )
                print("✅ DEBUG: ControlPanel.parameters_bundle_changed → HungarianMapTab.refresh_with_new_parameters CONNECTED")
            else:
                print("⚠️ DEBUG: HungarianMapTab.refresh_with_new_parameters method NOT FOUND!")
        else:
            print("⚠️ DEBUG: ControlPanel.parameters_bundle_changed signal NOT FOUND!")
        
        # === KIEGÉSZÍTŐ SIGNAL CONNECTIONS ===
        
        # Force sync API (ha van)
        if hasattr(self.control_panel, 'force_map_sync') and hasattr(self.hungarian_map_tab, 'force_refresh'):
            def debug_force_sync():
                print("🚨 DEBUG [CONTROL→MAP]: force_map_sync triggered")
            
            # Manual trigger opció
            def trigger_force_sync():
                debug_force_sync()
                if hasattr(self.hungarian_map_tab, 'force_refresh'):
                    self.hungarian_map_tab.force_refresh()
            
            # Ezt nem kötjük automatikusan signalhoz, hanem API-ként használható
            self.control_panel._manual_map_sync = trigger_force_sync
            print("✅ DEBUG: Manual force_map_sync API setup complete")
        
        print("🚨 ✅ DEBUG: ANALYTICS → MAP SYNC signal connections COMPLETED!")
        
        # === TESZTELÉSI TRIGGER (OPCIONÁLIS) ===
        
        # Trigger egy initial sync-et hogy lássuk működik-e
        if hasattr(self.control_panel, 'emit_parameter_change_signals'):
            print("🚨 DEBUG: Triggering initial parameter sync for testing...")
            try:
                self.control_panel.emit_parameter_change_signals()
                print("✅ DEBUG: Initial parameter sync triggered successfully")
            except Exception as e:
                print(f"⚠️ DEBUG: Initial parameter sync error: {e}")
    
    def _connect_mvc_signals(self) -> None:
        """
        🎉 KRITIKUS: MULTI-CITY RÉGIÓ/MEGYE TÉRKÉP INTEGRÁCIÓ 100% BEFEJEZÉSE + 🔥 ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZÉSE + 🌤️ TISZTA ANALYTICS → TÉRKÉP INTEGRATION + 🚀 TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + 🧹 CLEAN MVC komponensek signal-slot összekötése + DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS EGYSZERŰSÍTETT INTEGRÁCIÓ + DUAL-API + PROVIDER STATUS + HIBÁS JELZÉSEK ELTÁVOLÍTVA.
        """
        
        print("🔗 DEBUG: Starting CLEAN signals with MULTI-CITY RÉGIÓ/MEGYE TÉRKÉP INTEGRÁCIÓ 100% BEFEJEZÉSE + ANALYTICS VIEW REFAKTORÁLÁS + HIBÁS JELZÉSEK ELTÁVOLÍTVA...")
        
        # === 🌍 PROVIDER STATUS SIGNALOK ===
        
        print("🌍 DEBUG: Connecting Provider Status signals...")
        
        # Provider váltás
        def debug_provider_selected(provider_name: str):
            print(f"🌍 DEBUG [CONTROLLER→MAIN_WINDOW]: provider_selected: {provider_name}")
        
        self.controller.provider_selected.connect(debug_provider_selected)
        self.controller.provider_selected.connect(self._on_provider_selected)
        print("✅ DEBUG: Controller.provider_selected → MainWindow._on_provider_selected CONNECTED")
        
        # Usage statistics frissítése
        def debug_provider_usage_updated(usage_stats: dict):
            print(f"🌍 DEBUG [CONTROLLER→MAIN_WINDOW]: provider_usage_updated: {len(usage_stats)} providers")
        
        self.controller.provider_usage_updated.connect(debug_provider_usage_updated)
        self.controller.provider_usage_updated.connect(self._on_provider_usage_updated)
        print("✅ DEBUG: Controller.provider_usage_updated → MainWindow._on_provider_usage_updated CONNECTED")
        
        # Warning events
        def debug_provider_warning(provider_name: str, usage_percent: int):
            print(f"🌍 DEBUG [CONTROLLER→MAIN_WINDOW]: provider_warning: {provider_name} {usage_percent}%")
        
        self.controller.provider_warning.connect(debug_provider_warning)
        self.controller.provider_warning.connect(self._on_provider_warning)
        print("✅ DEBUG: Controller.provider_warning → MainWindow._on_provider_warning CONNECTED")
        
        # Fallback notifications
        def debug_provider_fallback(from_provider: str, to_provider: str):
            print(f"🌍 DEBUG [CONTROLLER→MAIN_WINDOW]: provider_fallback: {from_provider} → {to_provider}")
        
        self.controller.provider_fallback.connect(debug_provider_fallback)
        self.controller.provider_fallback.connect(self._on_provider_fallback)
        print("✅ DEBUG: Controller.provider_fallback → MainWindow._on_provider_fallback CONNECTED")
        
        # === CONTROLPANEL → CONTROLLER SIGNALOK ===
        
        print("🎛️ DEBUG: Connecting ControlPanel → Controller signals...")
        
        if self.control_panel:
            # 🌍 Provider változás signal
            if hasattr(self.control_panel, 'provider_changed'):
                def debug_control_panel_provider_changed(provider_name: str):
                    print(f"🌍 DEBUG [CONTROL_PANEL→CONTROLLER]: provider_changed: {provider_name}")
                
                self.control_panel.provider_changed.connect(debug_control_panel_provider_changed)
                self.control_panel.provider_changed.connect(
                    self.controller.handle_provider_change
                )
                print("✅ DEBUG: ControlPanel provider_changed → Controller.handle_provider_change CONNECTED")
            
            # Keresés signal
            def debug_control_panel_search_requested(query: str):
                print(f"🔍 DEBUG [CONTROL_PANEL→CONTROLLER]: search_requested: '{query}' (DUAL-API)")
            
            self.control_panel.search_requested.connect(debug_control_panel_search_requested)
            self.control_panel.search_requested.connect(
                self.controller.handle_search_request
            )
            print("✅ DEBUG: ControlPanel search_requested → Controller.handle_search_request CONNECTED (DUAL-API)")
            
            # Város kiválasztás signal
            def debug_control_panel_city_selected(name: str, lat: float, lon: float, data: dict):
                source = data.get('preferred_source', 'unknown')
                print(f"📍 DEBUG [CONTROL_PANEL→CONTROLLER]: city_selected: {name} ({lat:.4f}, {lon:.4f}) source: {source}")
            
            self.control_panel.city_selected.connect(debug_control_panel_city_selected)
            self.control_panel.city_selected.connect(
                self.controller.handle_city_selection
            )
            print("✅ DEBUG: ControlPanel city_selected → Controller.handle_city_selection CONNECTED (DUAL-API)")
            
            # Weather data kérések
            def debug_control_panel_weather_requested(lat: float, lon: float, start: str, end: str, params: dict):
                use_case = params.get('use_case', 'single_city')
                optimal_source = get_optimal_data_source(use_case)
                print(f"🌤️ DEBUG [CONTROL_PANEL→CONTROLLER]: weather_data_requested ({lat:.4f}, {lon:.4f}) → {optimal_source}")
            
            self.control_panel.weather_data_requested.connect(debug_control_panel_weather_requested)
            self.control_panel.weather_data_requested.connect(
                self.controller.handle_weather_data_request
            )
            print("✅ DEBUG: ControlPanel weather_data_requested → Controller.handle_weather_data_request CONNECTED (DUAL-API)")
            
            # 🎉 KRITIKUS: MULTI-CITY WEATHER REQUESTED SIGNAL - ÚJ!
            def debug_control_panel_multi_city_requested(analysis_type: str, region_id: str, start_date: str, end_date: str, params: dict):
                print(f"🎉 DEBUG [CONTROL_PANEL→MAIN_WINDOW]: multi_city_weather_requested: {analysis_type} '{region_id}' ({start_date} → {end_date})")
                print(f"🎉 DEBUG: Multi-city params: {params}")
            
            if hasattr(self.control_panel, 'multi_city_weather_requested'):
                self.control_panel.multi_city_weather_requested.connect(debug_control_panel_multi_city_requested)
                self.control_panel.multi_city_weather_requested.connect(
                    self._handle_multi_city_weather_request
                )
                print("🎉 ✅ KRITIKUS: ControlPanel.multi_city_weather_requested → MainWindow._handle_multi_city_weather_request CONNECTED!")
            else:
                print("❌ DEBUG: ControlPanel.multi_city_weather_requested signal NOT FOUND!")
            
        else:
            print("❌ DEBUG: ControlPanel is None!")
        
        # === 🔥 ANALYTICS VIEW REFAKTORÁLÁS SIGNAL INTEGRÁCIÓ + HIBÁS JELZÉSEK ELTÁVOLÍTVA ===
        
        if self.analytics_panel and self.control_panel:
            print("🔥 DEBUG: Connecting REFAKTORÁLT Analytics Panel signals + HIBÁS JELZÉSEK ELTÁVOLÍTVA...")
            
            # 🔗 KRITIKUS: ControlPanel → AnalyticsView direct connection
            def debug_control_panel_location_changed(location):
                print(f"🔗 DEBUG [CONTROL_PANEL→ANALYTICS]: location_changed: {location}")
            
            if hasattr(self.control_panel, 'location_changed'):
                self.control_panel.location_changed.connect(debug_control_panel_location_changed)
                self.control_panel.location_changed.connect(
                    self.analytics_panel.on_location_changed
                )
                print("✅ DEBUG: ControlPanel.location_changed → AnalyticsView.on_location_changed CONNECTED")
            
            # 🔗 KRITIKUS: ControlPanel city_selected → AnalyticsView kompatibilitás
            def debug_control_panel_city_to_analytics(name: str, lat: float, lon: float, data: dict):
                print(f"🔗 DEBUG [CONTROL_PANEL→ANALYTICS]: city_selected→location_changed: {name}")
                # Dictionary objektum létrehozása az AnalyticsView számára
                location_dict = {
                    'name': name,
                    'latitude': lat,
                    'longitude': lon,
                    **data
                }
                self.analytics_panel.on_location_changed(location_dict)
            
            self.control_panel.city_selected.connect(debug_control_panel_city_to_analytics)
            print("✅ DEBUG: ControlPanel.city_selected → AnalyticsView.on_location_changed COMPATIBILITY CONNECTED")
            
            # 🔥 ÚJ: ANALYTICS VIEW REFAKTORÁLT SIGNAL CONNECTIONS - EZ VOLT A HIÁNYZÓ RÉSZ!
            
            # AnalyticsView.multi_city_query_requested → MainWindow handler
            def debug_analytics_multi_city_query_requested(query_type: str, region_name: str):
                print(f"🔥 DEBUG [ANALYTICS→MAIN_WINDOW]: multi_city_query_requested: {query_type}, {region_name}")
            
            if hasattr(self.analytics_panel, 'multi_city_query_requested'):
                self.analytics_panel.multi_city_query_requested.connect(debug_analytics_multi_city_query_requested)
                self.analytics_panel.multi_city_query_requested.connect(
                    self._handle_analytics_view_query
                )
                print("🔥 ✅ KRITIKUS: AnalyticsView.multi_city_query_requested → MainWindow._handle_analytics_view_query CONNECTED!")
            else:
                print("❌ DEBUG: AnalyticsView.multi_city_query_requested signal NOT FOUND!")
            
            # 🔗 Analytics refaktorált signalok visszafelé (CSAK A TISZTÁK!)
            def debug_analytics_analysis_started():
                print("🔥 DEBUG [ANALYTICS→MAIN_WINDOW]: analysis_started (refaktorált)")
            
            self.analytics_panel.analysis_started.connect(debug_analytics_analysis_started)
            self.analytics_panel.analysis_started.connect(
                lambda: self.status_bar.showMessage("🔥 Analytics elemzés folyamatban... (refaktorált)")
            )
            print("✅ DEBUG: AnalyticsView.analysis_started → MainWindow status update CONNECTED")
            
            # 🔧 HIBÁS JELZÉS ELTÁVOLÍTVA: analytics_completed signal connection TÖRÖLVE!
            # Az alábbi blokk KOMMENTEZVE - ez volt a hibás jelzés:
            # -----------------------------------------------------------------
            # # Analytics befejezés
            # def debug_analytics_analysis_completed():
            #     print("🔥 DEBUG [ANALYTICS→MAIN_WINDOW]: analysis_completed (refaktorált)")
            # 
            # self.analytics_panel.analysis_completed.connect(
            #     lambda: self.status_bar.showMessage("✅ Analytics elemzés kész (refaktorált)")
            # )
            # print("✅ DEBUG: AnalyticsView.analysis_completed → MainWindow status update CONNECTED")
            # -----------------------------------------------------------------
            print("🔧 DEBUG: analytics_completed signal connection ELTÁVOLÍTVA (hibás jelzés)")
            
            # Analytics hibák
            def debug_analytics_error_occurred(error_msg: str):
                print(f"❌ DEBUG [ANALYTICS→MAIN_WINDOW]: error_occurred: {error_msg}")
            
            self.analytics_panel.error_occurred.connect(debug_analytics_error_occurred)
            self.analytics_panel.error_occurred.connect(
                lambda msg: self.status_bar.showMessage(f"❌ Analytics hiba: {msg}")
            )
            print("✅ DEBUG: AnalyticsView.error_occurred → MainWindow status update CONNECTED")
            
        else:
            print("⚠️ DEBUG: Analytics panel or Control panel is None - signalok nem kapcsolódnak")
        
        # === 🌤️ KRITIKUS: TISZTA ANALYTICS → TÉRKÉP INTEGRATION (HIBÁS JELZÉSEK ELTÁVOLÍTVA) ===
        
        # 🔧 HIBÁS JELZÉS ELTÁVOLÍTVA: analytics_completed → térképi frissítés blokk TÖRÖLVE!
        # Az alábbi teljes blokk KOMMENTEZVE - ez volt a hibás, felülíró jelzés:
        # -----------------------------------------------------------------
        # if self.analytics_panel and self.hungarian_map_tab:
        #     print("🌤️ DEBUG: Connecting ANALYTICS → HUNGARIAN MAP TAB WEATHER INTEGRATION signals...")
        #     
        #     # 🌤️ KRITIKUS: Analytics View analytics_completed → Hungarian Map Tab set_analytics_result
        #     def debug_analytics_to_map_integration():
        #         print(f"🌤️ DEBUG [ANALYTICS→MAP]: analytics_completed signal received - starting weather integration")
        #         
        #         # Analytics eredmény lekérdezése
        #         analytics_data = self.analytics_panel.get_current_data() if self.analytics_panel else None
        #         print(f"🌤️ DEBUG: Analytics data keys: {list(analytics_data.keys()) if analytics_data else 'NO DATA'}")
        #         
        #         # Analytics eredmény átadása a térképnek (weather overlay automatikus generálás)
        #         if self.hungarian_map_tab and hasattr(self.hungarian_map_tab, 'set_analytics_result') and analytics_data:
        #             try:
        #                 # Analytics eredmény konvertálása AnalyticsResult objektummá (ha szükséges)
        #                 self.hungarian_map_tab.set_analytics_result(analytics_data)
        #                 print("✅ DEBUG: Analytics result successfully passed to Hungarian Map Tab")
        #                 
        #                 # Status update
        #                 self.status_bar.showMessage("🌤️ Analytics eredmény átadva térképnek - Weather overlay generálás...")
        #                 
        #             except Exception as e:
        #                 print(f"❌ DEBUG: Analytics → Map integration error: {e}")
        #                 self.status_bar.showMessage(f"❌ Analytics → Térkép integráció hiba: {e}")
        #         else:
        #             print("❌ DEBUG: Hungarian Map Tab or set_analytics_result method or analytics data not available")
        #     
        #     # Analytics eredmény → Map automatikus kapcsolat
        #     if hasattr(self.analytics_panel, 'analysis_completed'):
        #         self.analytics_panel.analysis_completed.connect(debug_analytics_to_map_integration)
        #         print("🌤️ ✅ KRITIKUS: AnalyticsView.analysis_completed → HungarianMapTab.set_analytics_result CONNECTED!")
        #     else:
        #         print("❌ DEBUG: AnalyticsView.analysis_completed signal not found")
        # -----------------------------------------------------------------
        print("🔧 DEBUG: HIBÁS ANALYTICS → MAP INTEGRATION signals ELTÁVOLÍTVA (analytics_completed hibás bekötés)")
        print("✅ DEBUG: Most már csak a TISZTA, központi adatkezelés marad (_on_multi_city_result_ready_for_views)")
        
        # === 📈 TREND ANALYTICS SIGNALOK ===
        
        if self.trend_analytics_tab and self.control_panel:
            print("📈 DEBUG: Connecting TREND ANALYTICS TAB signals...")
            
            # 🔗 KRITIKUS: ControlPanel city_selected → TrendAnalyticsTab set_location
            def debug_control_panel_city_to_trend(name: str, lat: float, lon: float, data: dict):
                print(f"🔗 DEBUG [CONTROL_PANEL→TREND_ANALYTICS]: city_selected→set_location: {name} ({lat:.4f}, {lon:.4f})")
                self.trend_analytics_tab.set_location(name, lat, lon)
            
            self.control_panel.city_selected.connect(debug_control_panel_city_to_trend)
            print("✅ DEBUG: ControlPanel.city_selected → TrendAnalyticsTab.set_location CONNECTED")
            
            # 🔗 TrendAnalyticsTab signalok visszafelé
            def debug_trend_analysis_started():
                print("📈 DEBUG [TREND_ANALYTICS→MAIN_WINDOW]: analysis_started")
            
            self.trend_analytics_tab.analysis_started.connect(debug_trend_analysis_started)
            self.trend_analytics_tab.analysis_started.connect(
                lambda: self.status_bar.showMessage("📈 Trend elemzés folyamatban...")
            )
            print("✅ DEBUG: TrendAnalyticsTab.analysis_started → MainWindow status update CONNECTED")
            
            # Trend analysis befejezés
            def debug_trend_analysis_completed(results: dict):
                city_name = results.get('city_name', 'Unknown')
                print(f"📈 DEBUG [TREND_ANALYTICS→MAIN_WINDOW]: analysis_completed: {city_name}")
            
            self.trend_analytics_tab.analysis_completed.connect(debug_trend_analysis_completed)
            self.trend_analytics_tab.analysis_completed.connect(self._on_trend_analysis_completed)
            print("✅ DEBUG: TrendAnalyticsTab.analysis_completed → MainWindow._on_trend_analysis_completed CONNECTED")
            
            # Trend analysis hibák
            def debug_trend_error_occurred(error_msg: str):
                print(f"❌ DEBUG [TREND_ANALYTICS→MAIN_WINDOW]: error_occurred: {error_msg}")
            
            self.trend_analytics_tab.error_occurred.connect(debug_trend_error_occurred)
            self.trend_analytics_tab.error_occurred.connect(self._on_trend_analysis_error)
            print("✅ DEBUG: TrendAnalyticsTab.error_occurred → MainWindow._on_trend_analysis_error CONNECTED")
            
            # Trend location selection
            def debug_trend_location_selected(name: str, lat: float, lon: float):
                print(f"📍 DEBUG [TREND_ANALYTICS→MAIN_WINDOW]: location_selected: {name} ({lat:.4f}, {lon:.4f})")
            
            self.trend_analytics_tab.location_selected.connect(debug_trend_location_selected)
            print("✅ DEBUG: TrendAnalyticsTab.location_selected signal CONNECTED")
            
        else:
            print("⚠️ DEBUG: Trend Analytics tab or Control panel is None - signalok nem kapcsolódnak")
        
        # === CONTROLLER → GUI VISSZACSATOLÁS ===
        
        print("📡 DEBUG: Connecting Controller → GUI response signals...")
        
        # Geocoding results
        def debug_controller_geocoding_results(results: list):
            print(f"📍 DEBUG [CONTROLLER→GUI]: geocoding_results_ready: {len(results)} results (DUAL-API)")
        
        self.controller.geocoding_results_ready.connect(debug_controller_geocoding_results)
        
        if self.control_panel:
            self.controller.geocoding_results_ready.connect(
                self.control_panel._on_geocoding_completed
            )
            print("✅ DEBUG: Controller.geocoding_results_ready → ControlPanel._on_geocoding_completed CONNECTED")
        
        # === WEATHER DATA SIGNALS ===
        
        # Időjárási adatok készek
        def debug_controller_weather_data_ready(data: dict):
            daily_data = data.get("daily", {})
            record_count = len(daily_data.get("time", []))
            data_source = data.get("data_source", "Unknown")
            source_type = data.get("source_type", "unknown")
            print(f"📊 DEBUG [CONTROLLER→MAIN_WINDOW]: weather_data_ready: {record_count} records from {data_source} (type: {source_type})")
        
        self.controller.weather_data_ready.connect(debug_controller_weather_data_ready)
        self.controller.weather_data_ready.connect(
            self._on_weather_data_received
        )
        print("✅ DEBUG: Controller.weather_data_ready → MainWindow._on_weather_data_received CONNECTED (DUAL-API)")
        
        # 🔗 KRITIKUS: Controller → AnalyticsView data pipeline
        if self.analytics_panel:
            def debug_controller_weather_data_to_analytics(data: dict):
                print("🔗 DEBUG [CONTROLLER→ANALYTICS]: weather_data_ready → update_data")
            
            self.controller.weather_data_ready.connect(debug_controller_weather_data_to_analytics)
            self.controller.weather_data_ready.connect(
                self.analytics_panel.update_data
            )
            print("✅ DEBUG: Controller.weather_data_ready → AnalyticsView.update_data CONNECTED")
        
        # === CONTROLLER → MAIN WINDOW ÁLTALÁNOS SIGNALOK ===
        
        # Hibakezelés
        def debug_controller_error_occurred(message: str):
            print(f"❌ DEBUG [CONTROLLER→MAIN_WINDOW]: error_occurred: '{message}'")
        
        self.controller.error_occurred.connect(debug_controller_error_occurred)
        self.controller.error_occurred.connect(self._show_error)
        print("✅ DEBUG: Controller.error_occurred → MainWindow._show_error CONNECTED")
        
        # Státusz frissítések
        def debug_controller_status_updated(message: str):
            print(f"📝 DEBUG [CONTROLLER→MAIN_WINDOW]: status_updated: '{message}'")
        
        self.controller.status_updated.connect(debug_controller_status_updated)
        self.controller.status_updated.connect(self._update_status)
        print("✅ DEBUG: Controller.status_updated → MainWindow._update_status CONNECTED")
        
        # Progress frissítések
        def debug_controller_progress_updated(worker_type: str, progress: int):
            print(f"⏳ DEBUG [CONTROLLER→MAIN_WINDOW]: progress_updated: {worker_type} {progress}%")
        
        self.controller.progress_updated.connect(debug_controller_progress_updated)
        self.controller.progress_updated.connect(self._update_progress)
        print("✅ DEBUG: Controller.progress_updated → MainWindow._update_progress CONNECTED")
        
        # === CONTROLPANEL KIEGÉSZÍTŐ SIGNALOK ===
        
        if self.control_panel:
            # Weather data befejezés jelzése
            self.controller.weather_data_ready.connect(
                self.control_panel.on_weather_data_completed
            )
            
            # Progress és status updates ControlPanel-hez
            self.controller.progress_updated.connect(
                self.control_panel.update_progress
            )
            self.controller.status_updated.connect(
                self.control_panel.update_status_from_controller
            )
            self.controller.error_occurred.connect(
                self.control_panel.on_controller_error
            )
            print("✅ DEBUG: Controller → ControlPanel additional signals CONNECTED")
        
        # === RESULTS PANEL SIGNALOK ===
        
        if self.results_panel:
            # Export kérések
            def debug_results_panel_export_requested(format: str):
                print(f"📊 DEBUG [RESULTS_PANEL→MAIN_WINDOW]: export_requested: {format}")
            
            self.results_panel.export_requested.connect(debug_results_panel_export_requested)
            self.results_panel.export_requested.connect(self._handle_export_request)
            print("✅ DEBUG: ResultsPanel.export_requested → MainWindow._handle_export_request CONNECTED")
            
            # Extrém időjárás kérések
            def debug_results_panel_extreme_weather_requested():
                print("⚡ DEBUG [RESULTS_PANEL→MAIN_WINDOW]: extreme_weather_requested")
            
            self.results_panel.extreme_weather_requested.connect(debug_results_panel_extreme_weather_requested)
            self.results_panel.extreme_weather_requested.connect(self._show_extreme_weather)
            print("✅ DEBUG: ResultsPanel.extreme_weather_requested → MainWindow._show_extreme_weather CONNECTED")
        
        # === CHARTS & TABLE SIGNALOK - RESULTS PANEL KERESZTÜL ===
        
        # Chart widget referencia lekérdezése a results panel-től
        charts_container = None
        if self.results_panel:
            charts_container = self.results_panel.get_charts_container()
        
        if charts_container:
            # Chart export
            def debug_charts_exported(filepath: str, success: bool):
                print(f"📈 DEBUG [CHARTS→MAIN_WINDOW]: chart_exported: {filepath} - {'success' if success else 'failed'}")
            
            charts_container.chart_exported.connect(debug_charts_exported)
            charts_container.chart_exported.connect(self._on_chart_exported)
            print("✅ DEBUG: ChartsContainer.chart_exported → MainWindow._on_chart_exported CONNECTED")
        
        # Data table referencia lekérdezése a results panel-től
        data_table = None
        if self.results_panel:
            data_table = self.results_panel.get_data_table()
        
        if data_table:
            # Table export
            def debug_table_export_completed(filepath: str, success: bool):
                print(f"📋 DEBUG [DATA_TABLE→MAIN_WINDOW]: export_completed: {filepath} - {'success' if success else 'failed'}")
            
            data_table.export_completed.connect(debug_table_export_completed)
            data_table.export_completed.connect(self._on_table_exported)
            print("✅ DEBUG: DataTable.export_completed → MainWindow._on_table_exported CONNECTED")
            
            # Sor kiválasztás
            def debug_table_row_selected(row_index: int):
                print(f"📋 DEBUG [DATA_TABLE→MAIN_WINDOW]: row_selected: row {row_index}")
            
            data_table.row_selected.connect(debug_table_row_selected)
            data_table.row_selected.connect(self._on_table_row_selected)
            print("✅ DEBUG: DataTable.row_selected → MainWindow._on_table_row_selected CONNECTED")
        
        # === TÉMA SIGNALOK - THEMEMANAGER INTEGRÁCIÓ ===
        
        def debug_theme_changed(theme_name: str):
            print(f"🎨 DEBUG [MAIN_WINDOW]: theme_changed: {theme_name}")
        
        self.theme_changed.connect(debug_theme_changed)
        self.theme_changed.connect(self._propagate_theme_change)
        print("✅ DEBUG: MainWindow.theme_changed → MainWindow._propagate_theme_change CONNECTED")
        
        def debug_view_changed(view_name: str):
            print(f"🔄 DEBUG [MAIN_WINDOW]: view_changed: {view_name}")
        
        self.view_changed.connect(debug_view_changed)
        print("✅ DEBUG: MainWindow.view_changed signal CONNECTED")
        
        print("🎉 ✅ DEBUG: ALL CLEAN signals connected successfully with MULTI-CITY RÉGIÓ/MEGYE TÉRKÉP INTEGRÁCIÓ 100% BEFEJEZVE + ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + TISZTA ANALYTICS → TÉRKÉP INTEGRATION + TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + Analytics Refaktorált + DUAL-API + PROVIDER STATUS + HIBÁS JELZÉSEK ELTÁVOLÍTVA!")
    
    # === 🔥 ÚJ: ANALYTICS VIEW QUERY HANDLER - REFAKTORÁLT METÓDUS! ===
    
    def _handle_analytics_view_query(self, query_type: str, region_name: str):
        """
        🔥 ÚJ: Kezeli az AnalyticsView-ból érkező multi-city lekérdezési kéréseket.
        
        Args:
            query_type: Lekérdezés típusa (pl. "hottest_today", "coldest_today")
            region_name: Régió neve (pl. "Észak-Magyarország")
        """
        print(f"🔥 DEBUG: _handle_analytics_view_query called: {query_type}, {region_name}")
        
        # A meglévő, központi lekérdező metódus hívása
        # Készítünk egy 'params' dictionary-t, ami kompatibilis a meglévő rendszerrel
        params = {
            "query_type": query_type,
            "auto_switch_to_map": False  # Nem váltunk automatikusan fület
        }
        
        # Mai dátum használata
        today_str = datetime.now().strftime("%Y-%m-%d")

        # A már meglévő, központi handler hívása
        self._handle_multi_city_weather_request(
            analysis_type="region", 
            region_id=region_name, 
            start_date=today_str, 
            end_date=today_str, 
            params=params
        )

    def _on_multi_city_result_ready_for_views(self, result: 'AnalyticsResult', query_type: str = "hottest_today"):
        """
        🔥 ÚJ: Szétosztja a multi-city elemzés eredményét a releváns nézeteknek + QUERY TYPE INFORMÁCIÓ.
        Ezt a _handle_multi_city_weather_request hívja meg a végén.
        
        Args:
            result: AnalyticsResult objektum a Multi-City Engine-ből
            query_type: Lekérdezés típusa (pl. "windiest_today", "hottest_today")
        """
        print(f"🔥 DEBUG: _on_multi_city_result_ready_for_views called - szétosztás a nézeteknek (query_type: {query_type})...")
        
        try:
            # Eredmény küldése a Térképnek + QUERY TYPE INFO
            if self.hungarian_map_tab and hasattr(self.hungarian_map_tab, 'set_analytics_result'):
                # 🔧 KRITIKUS: Query type alapú paraméter meghatározása
                analytics_parameter = self._map_query_type_to_parameter(query_type)
                print(f"🔧 DEBUG: Mapped query_type '{query_type}' to parameter '{analytics_parameter}'")
                
                # 🚨 ÚJ: Paraméter beállítása a térképen MIELŐTT az eredményt átadjuk
                if hasattr(self.hungarian_map_tab, 'set_analytics_parameter'):
                    self.hungarian_map_tab.set_analytics_parameter(analytics_parameter)
                    print(f"✅ DEBUG: Analytics parameter set on HungarianMapTab: {analytics_parameter}")
                
                # Eredmény átadása
                self.hungarian_map_tab.set_analytics_result(result)
                print("  -> Eredmény elküldve a HungarianMapTab-nek (with query type info).")

            # Eredmény küldése az Analitika nézetnek
            if self.analytics_panel and hasattr(self.analytics_panel, 'update_with_multi_city_result'):
                self.analytics_panel.update_with_multi_city_result(result)
                print("  -> Eredmény elküldve az AnalyticsView-nak.")
                
            print("✅ DEBUG: Multi-city result distribution completed (with query type)")
            
        except Exception as e:
            print(f"❌ DEBUG: Multi-city result distribution error: {e}")
            self._show_error(f"Multi-city eredmény szétosztási hiba: {e}")
    
    def _map_query_type_to_parameter(self, query_type: str) -> str:
        """
        🔧 ÚJ: Query type leképezése térképi paraméterré.
        
        Args:
            query_type: Analytics query type (pl. "windiest_today")
            
        Returns:
            Térkép paraméter neve (pl. "Szél")
        """
        mapped_param = self.QUERY_TYPE_TO_PARAMETER.get(query_type, "Hőmérséklet")
        print(f"🔧 DEBUG: Query type mapping: {query_type} → {mapped_param}")
        return mapped_param
    
    # === 🎉 MULTI-CITY WEATHER REQUEST HANDLER - KRITIKUS JAVÍTOTT METÓDUS! ===
    
    def _handle_multi_city_weather_request(self, analysis_type: str, region_id: str, start_date: str, end_date: str, params: dict) -> None:
        """
        🎉 KRITIKUS JAVÍTÁS: Multi-City weather request kezelése - RÉGIÓ/MEGYE → MULTI-CITY ENGINE → TÉRKÉP OVERLAY AUTOMATIKUS WORKFLOW + ANALYTICS RESULT KÖZVETLEN ÁTADÁS + 🔧 WINDSPEED METRIC TELJES JAVÍTÁS.
        
        Ez a hiányzó 0.1% ami befejezi a teljes multi-city régió/megye térkép integrációt!
        A kritikus javítás: AnalyticsResult objektum közvetlen átadása (NO DICT CONVERSION!)
        
        🔧 WINDSPEED METRIC JAVÍTÁS:
        - QUERY_TYPE_TO_PARAMETER mapping használata
        - 2-lépéses koordináció: paraméter beállítás + adat átadás
        - Enhanced debug logging minden lépéshez
        
        Args:
            analysis_type: Elemzés típusa ("region" vagy "county")
            region_id: Régió/megye azonosító (pl. "Közép-Magyarország", "Budapest")
            start_date: Kezdő dátum ISO formátumban
            end_date: Vég dátum ISO formátumban
            params: További paraméterek dictionary
        """
        print(f"🎉 DEBUG: _handle_multi_city_weather_request called - COMPLETING MULTI-CITY INTEGRATION + WINDSPEED FIX!")
        print(f"🎉 DEBUG: Analysis type: {analysis_type}, Region: '{region_id}', Date range: {start_date} → {end_date}")
        print(f"🎉 DEBUG: Params: {params}")
        
        try:
            # Status update - Multi-city lekérdezés kezdése
            self.status_bar.showMessage(f"🎉 Multi-city lekérdezés indítása: {region_id} ({analysis_type})")
            
            # 🔧 KRITIKUS: Query type meghatározása és paraméter mapping
            query_type = params.get("query_type", "hottest_today")
            limit = params.get("limit", 20)  # Alapértelmezett: 20 város
            
            print(f"🔧 DEBUG: Query type: {query_type}, Limit: {limit}")
            
            # 🔧 KRITIKUS: 1. LÉPÉS - PARAMÉTER BEÁLLÍTÁS A TÉRKÉPEN
            if self.hungarian_map_tab:
                display_parameter = self._map_query_type_to_parameter(query_type)
                print(f"🔧 DEBUG: 1. LÉPÉS - Setting analytics parameter on map: {display_parameter}")
                
                if hasattr(self.hungarian_map_tab, 'set_analytics_parameter'):
                    self.hungarian_map_tab.set_analytics_parameter(display_parameter)
                    print(f"✅ DEBUG: Analytics parameter set successfully: {display_parameter}")
                else:
                    print("⚠️ DEBUG: HungarianMapTab.set_analytics_parameter method not found!")
            
            # 1. Multi-City Engine példányosítás/használat
            print("🎉 DEBUG: Importing Multi-City Engine...")
            from src.analytics.multi_city_engine import MultiCityEngine
            
            engine = MultiCityEngine()
            print("✅ DEBUG: Multi-City Engine instance created")
            
            print(f"🎉 DEBUG: Running multi-city analysis - Query: {query_type}, Limit: {limit}")
            
            # 2. Multi-city elemzés futtatása
            result = engine.analyze_multi_city(
                query_type,
                region_id,
                start_date,
                limit=limit
            )
            
            # 🔧 KRITIKUS JAVÍTÁS: RESULT TYPE ELLENŐRZÉS ÉS HIBAKEZELÉS
            if not hasattr(result, 'city_results'):
                print(f"❌ DEBUG: Multi-city engine returned invalid result type: {type(result)}")
                error_msg = f"Multi-city engine hibás eredmény típus: {type(result)}"
                self.status_bar.showMessage(f"❌ {error_msg}")
                self._show_error(error_msg)
                return
            
            print(f"✅ DEBUG: Multi-city analysis completed - {len(result.city_results)} results")
            print(f"🔧 DEBUG: Result type: {type(result)}, has city_results: {hasattr(result, 'city_results')}")
            
            # 3. OPCIONÁLIS: city_results logging célokra (de NEM konverzió!)
            print("🎉 DEBUG: Multi-city results summary:")
            for i, city_result in enumerate(result.city_results[:5]):  # Első 5 a loghoz
                print(f"  {i+1}. {city_result.city_name}: {city_result.value} {getattr(city_result.metric, 'value', '')} (rank: {city_result.rank})")
            
            # 🔧 KRITIKUS: 2. LÉPÉS - ADAT ÁTADÁS A TÉRKÉPNEK
            if self.hungarian_map_tab and hasattr(self.hungarian_map_tab, 'set_analytics_result'):
                print(f"🔧 DEBUG: 2. LÉPÉS - Setting analytics result on map...")
                self.hungarian_map_tab.set_analytics_result(result)
                print("✅ DEBUG: Analytics result set successfully on HungarianMapTab")
            else:
                print("⚠️ DEBUG: HungarianMapTab.set_analytics_result method not found!")
            
            # 4. 🔥 KRITIKUS JAVÍTÁS: EREDMÉNY SZÉTOSZTÁSA MINDEN RELEVÁNS NÉZETRE + QUERY TYPE INFORMÁCIÓ
            print("🔥 DEBUG: Distributing AnalyticsResult to all relevant views...")
            self._on_multi_city_result_ready_for_views(result, query_type)
            
            # 5. Status update - sikeres
            success_message = f"🎉 Multi-city eredmény szétosztva: {len(result.city_results)} város ({region_id}) [Query: {query_type}]"
            self.status_bar.showMessage(success_message)
            
            # Provider status frissítése (multi-city lekérdezések API használatot jeleznek)
            self._update_provider_status_display()
            
            # Automatikus térkép tab váltás (opcionális)
            if params.get("auto_switch_to_map", True):
                print("🎉 DEBUG: Auto-switching to map view...")
                self._switch_view("map_view")
            
            print(f"🔧 ✅ DEBUG: WINDSPEED METRIC JAVÍTÁS BEFEJEZVE - {query_type} → {self._map_query_type_to_parameter(query_type)}")
            
        except ImportError as e:
            print(f"❌ DEBUG: Multi-City Engine import error: {e}")
            error_msg = f"Multi-City Engine nem elérhető: {e}"
            self.status_bar.showMessage(f"❌ {error_msg}")
            self._show_error(error_msg)
            
        except Exception as e:
            print(f"❌ DEBUG: Multi-city request error: {e}")
            import traceback
            traceback.print_exc()
            
            error_msg = f"Multi-city lekérdezés hiba: {e}"
            self.status_bar.showMessage(f"❌ {error_msg}")
            self._show_error(error_msg)
        
        print("🎉 DEBUG: _handle_multi_city_weather_request completed - MULTI-CITY INTEGRATION + WINDSPEED FIX FINISHED!")
    
    # === 🌍 PROVIDER STATUS SLOT METÓDUSOK ===
    
    def _on_provider_selected(self, provider_name: str) -> None:
        """
        🌍 Provider kiválasztás kezelése Controller-től.
        
        Args:
            provider_name: Kiválasztott provider neve
        """
        print(f"🌍 DEBUG: _on_provider_selected called: {provider_name}")
        
        # Provider tracking frissítése
        self.current_provider = provider_name
        
        # Status display frissítése
        self._update_provider_status_display()
        
        # Provider status signal
        self.provider_status_updated.emit(f"Provider váltva: {provider_name}")
        
        print(f"✅ DEBUG: Provider selection handled: {provider_name}")
    
    def _on_provider_usage_updated(self, usage_stats: Dict[str, Dict[str, Any]]) -> None:
        """
        🌍 Provider usage statistics frissítése Controller-től.
        
        Args:
            usage_stats: Usage statistics dictionary
        """
        print(f"🌍 DEBUG: _on_provider_usage_updated called: {len(usage_stats)} providers")
        
        # Usage stats frissítése
        self.provider_usage_stats = usage_stats
        
        # Status display frissítése
        self._update_provider_status_display()
        
        # Provider status signal
        formatted_usage = format_provider_usage(usage_stats)
        usage_summary = ', '.join([f"{name}: {usage}" for name, usage in formatted_usage.items()])
        self.provider_status_updated.emit(f"Usage frissítve: {usage_summary}")
        
        print(f"✅ DEBUG: Provider usage updated")
    
    def _on_provider_warning(self, provider_name: str, usage_percent: int) -> None:
        """
        🌍 Provider warning kezelése Controller-től.
        
        Args:
            provider_name: Provider neve
            usage_percent: Usage százalék
        """
        print(f"🌍 DEBUG: _on_provider_warning called: {provider_name} {usage_percent}%")
        
        # Warning styling frissítése
        if usage_percent >= 95:
            warning_level = "critical"
            warning_message = f"⚠️ {provider_name} limit közel: {usage_percent}%"
        elif usage_percent >= 80:
            warning_level = "warning"  
            warning_message = f"⚠️ {provider_name} használat magas: {usage_percent}%"
        else:
            warning_level = "info"
            warning_message = f"📊 {provider_name} használat: {usage_percent}%"
        
        # Warning styling alkalmazása
        self._apply_warning_styling(warning_level)
        
        # Status bar message
        self.status_bar.showMessage(warning_message)
        
        # Provider status signal
        self.provider_status_updated.emit(warning_message)
        
        print(f"✅ DEBUG: Provider warning handled: {provider_name} {usage_percent}%")
    
    def _on_provider_fallback(self, from_provider: str, to_provider: str) -> None:
        """
        🌍 Provider fallback notification kezelése Controller-től.
        
        Args:
            from_provider: Eredeti provider
            to_provider: Fallback provider
        """
        print(f"🌍 DEBUG: _on_provider_fallback called: {from_provider} → {to_provider}")
        
        # Provider tracking frissítése
        self.current_provider = to_provider
        
        # Status display frissítése
        self._update_provider_status_display()
        
        # Fallback notification message
        from_display = get_source_display_name(from_provider)
        to_display = get_source_display_name(to_provider)
        fallback_message = f"🔄 Provider fallback: {from_display} → {to_display}"
        
        # Status bar message
        self.status_bar.showMessage(fallback_message)
        
        # Provider status signal
        self.provider_status_updated.emit(fallback_message)
        
        print(f"✅ DEBUG: Provider fallback handled: {from_provider} → {to_provider}")
    
    # === 📈 TREND ANALYTICS SLOT METÓDUSOK - ÚJ! ===
    
    def _on_trend_analysis_completed(self, results: Dict[str, Any]) -> None:
        """
        📈 Trend analysis completion handler - ÚJ SLOT METÓDUS.
        
        Args:
            results: Trend elemzés eredményei
        """
        try:
            city_name = results.get('city_name', 'Unknown')
            parameter = results.get('parameter', 'Unknown')
            time_range = results.get('time_range', 'Unknown')
            
            # Status message
            success_message = f"📈 Trend elemzés kész: {city_name} ({parameter}, {time_range})"
            self.status_bar.showMessage(success_message)
            
            # További feldolgozás (ha szükséges)
            if 'statistics' in results and 'trend_stats' in results['statistics']:
                trend_stats = results['statistics']['trend_stats']
                r_squared = trend_stats.get('r_squared', 0)
                trend_direction = trend_stats.get('trend_direction', 'ismeretlen')
                
                print(f"📈 DEBUG: Trend analysis completed - R²: {r_squared:.3f}, Direction: {trend_direction}")
            
            print(f"✅ DEBUG: Trend analysis completion handled: {city_name}")
            
        except Exception as e:
            print(f"❌ DEBUG: Trend analysis completion handling error: {e}")
            self._show_error(f"Trend elemzés eredmény feldolgozási hiba: {e}")
    
    def _on_trend_analysis_error(self, error_msg: str) -> None:
        """
        📈 Trend analysis error handler - ÚJ SLOT METÓDUS.
        
        Args:
            error_msg: Hibaüzenet
        """
        print(f"❌ DEBUG: _on_trend_analysis_error called: {error_msg}")
        
        # Status message
        error_message = f"❌ Trend elemzés hiba: {error_msg}"
        self.status_bar.showMessage(error_message)
        
        # Error dialog (opcionális - lehet túl zavaró)
        # self._show_error(f"Trend elemzés hiba: {error_msg}")
        
        print(f"✅ DEBUG: Trend analysis error handled: {error_msg}")
    
    # === SLOT METÓDUSOK - CLEAN VERZIÓ + THEMEMANAGER + ANALYTICS REFAKTORÁLT + DUAL-API ===
    
    def _on_weather_data_received(self, data: dict) -> None:
        """
        🔧 CLEAN időjárási adatok fogadása a Controller-től - DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS REFAKTORÁLT INTEGRÁCIÓVAL + DUAL-API.
        
        Args:
            data: Időjárási adatok (Open-Meteo vagy Meteostat formátumban)
        """
        print("📊 DEBUG: _on_weather_data_received called - DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS REFAKTORÁLT INTEGRATION + DUAL-API")
        
        try:
            # 🌍 DUAL-API adatforrás azonosítása
            data_source = data.get('data_source', 'Unknown')
            source_type = data.get('source_type', 'unknown')
            
            print(f"📊 DEBUG: Processing weather data from {data_source} (type: {source_type})")
            
            # City info lekérdezése a Controller-től
            city_data = self.controller.get_current_city()
            city_name = city_data.get('name', 'Ismeretlen') if city_data else 'Ismeretlen'
            
            # 🌍 DUAL-API display name meghatározása
            display_name = get_source_display_name(source_type)
            city_name_with_source = f"{city_name} ({display_name})"
            
            print(f"📊 DEBUG: Processing weather data for {city_name_with_source}")
            
            # Results panel frissítése (Single City view - KÖZPONTI FUNKCIÓ)
            if self.results_panel:
                print("📊 DEBUG: Updating results panel...")
                self.results_panel.update_data(data, city_name_with_source)
            
            # 📊 ANALYTICS REFAKTORÁLT INTEGRÁCIÓ - automatikus!
            # Az analytics_panel.update_data() automatikusan meghívódik a 
            # Controller.weather_data_ready signal miatt (_connect_mvc_signals-ben)
            print("✅ DEBUG: Analytics panel update automatikus (signal-based)")
            
            # Menü elemek engedélyezése
            self.export_action.setEnabled(True)
            self.extreme_action.setEnabled(True)
            
            print(f"✅ DEBUG: UI komponensek frissítve DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS REFAKTORÁLT INTEGRÁCIÓVAL + DUAL-API: {city_name_with_source}")
            
        except Exception as e:
            print(f"❌ DEBUG: UI frissítési hiba: {e}")
            import traceback
            traceback.print_exc()
            self._show_error(f"UI frissítési hiba: {e}")
    
    def _update_status(self, message: str) -> None:
        """Státuszsor frissítése - Provider status megtartásával."""
        # General status message update, provider widgets megmaradnak
        self.status_bar.showMessage(message)
    
    def _update_progress(self, worker_type: str, progress: int) -> None:
        """Progress frissítése - DUAL-API kompatibilis + Provider status megtartásával."""
        if progress == 100:
            # Worker típus alapján specifikus befejező üzenet
            completion_messages = {
                "geocoding": "✅ Keresés befejezve",
                "weather_data": "✅ Időjárási adatok lekérdezve (Dual-API)",
                "sql_query": "✅ Adatbázis lekérdezés befejezve"
            }
            
            message = completion_messages.get(worker_type, f"✅ {worker_type} befejezve")
            self.status_bar.showMessage(message)
        else:
            # Progress üzenetek
            progress_messages = {
                "geocoding": f"🔍 Keresés: {progress}%",
                "weather_data": f"🌍 Adatok lekérdezése (Dual-API): {progress}%",
                "sql_query": f"🗂️ Adatbázis: {progress}%"
            }
            
            message = progress_messages.get(worker_type, f"⏳ {worker_type}: {progress}%")
            self.status_bar.showMessage(message)
    
    def _show_error(self, message: str) -> None:
        """Hibaüzenet megjelenítése."""
        QMessageBox.critical(self, "Hiba", message)
        self.status_bar.showMessage(f"❌ {message}")
    
    def _handle_export_request(self, format: str) -> None:
        """Export kérés kezelése a results panel-től."""
        data_table = None
        if self.results_panel:
            data_table = self.results_panel.get_data_table()
        
        if format == "csv" and data_table:
            data_table._export_data("csv")
        elif format == "excel" and data_table:
            data_table._export_data("excel")
        else:
            self._show_error(f"Nem támogatott export formátum: {format}")
    
    def _on_chart_exported(self, filepath: str, success: bool) -> None:
        """Chart export eredmény kezelése."""
        if success:
            self.status_bar.showMessage(f"✅ Grafikon exportálva: {filepath}")
        else:
            self._show_error(f"Grafikon export hiba: {filepath}")
    
    def _on_table_exported(self, filepath: str, success: bool) -> None:
        """Table export eredmény kezelése."""
        if success:
            self.status_bar.showMessage(f"✅ Adatok exportálva: {filepath}")
        else:
            self._show_error(f"Adatok export hiba: {filepath}")
    
    def _on_table_row_selected(self, row_index: int) -> None:
        """Táblázat sor kiválasztás kezelése."""
        print(f"📋 Táblázat sor kiválasztva: {row_index}")
    
    # === MENÜ AKCIÓK ===
    
    def _export_data(self) -> None:
        """Adatok exportálása menüből."""
        weather_data = self.controller.get_current_weather_data()
        if not weather_data:
            self._show_error("Nincsenek exportálható adatok. Először kérdezzen le adatokat.")
            return
        
        data_table = None
        if self.results_panel:
            data_table = self.results_panel.get_data_table()
        
        if data_table:
            data_table._export_data("csv")
        else:
            self._show_error("Adattáblázat nem elérhető az exporthoz.")
    
    def _show_extreme_weather(self) -> None:
        """Extrém időjárási események megjelenítése."""
        weather_data = self.controller.get_current_weather_data()
        city_data = self.controller.get_current_city()
        
        if not weather_data or not city_data:
            self._show_error("Nincsenek megjeleníthető adatok. Először kérdezzen le időjárási adatokat.")
            return
        
        city_name = city_data.get('name', 'Ismeretlen')
        
        try:
            dialog = ExtremeWeatherDialog(self, weather_data, city_name)
            dialog.exec()
        except Exception as e:
            self._show_error(f"Extrém időjárás ablak hiba: {e}")
    
    def _show_about(self) -> None:
        """Névjegy ablak megjelenítése - ANALYTICS → MAP SYNC FIX BEFEJEZVE + ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA + WINDSPEED METRIC TELJES JAVÍTÁS VERSION."""
        about_text = f"""
        <h2>{AppInfo.NAME}</h2>
        <p><b>Verzió:</b> {AppInfo.VERSION} (Analytics → Map Sync Fix + Analytics View Refaktorálás Befejezve + Hibás Jelzések Eltávolítva + Multi-City Régió/Megye Térkép Integráció 100% Befejezve + Tiszta Analytics → Térkép Integration + Trend Analytics Integráció Befejezve + Dashboard Cleanup Befejezve + Splitter Constraints Optimalizálva + Analytics Refaktorált + Provider Status + ThemeManager + Dual-API + Map View Integráció + 🔧 WINDSPEED METRIC TELJES JAVÍTÁS)</p>
        <p><b>Leírás:</b> {AppInfo.DESCRIPTION}</p>
        <p><b>Architektúra:</b> Clean MVC + Single City Central Navigation + Provider Status Bar + AnalyticsView Refaktorált + ThemeManager + Dual-API + Splitter Constraints Optimalizálva + Map View Integráció + TrendAnalyticsTab Professional + Tiszta Analytics → Térkép Integration + Multi-City Régió/Megye Support + Analytics → Map Sync Fix + Analytics View Refaktorálás + Hibás Jelzések Eltávolítva + 🔧 WINDSPEED METRIC TELJES JAVÍTÁS</p>
        <p><b>Technológia:</b> PySide6, Python 3.8+</p>
        <p><b>Adatforrások:</b> Dual-API rendszer (Open-Meteo + Meteostat)</p>
        <hr>
        <p><i>🚨 Analytics → Map Sync Fix BEFEJEZVE!</i></p>
        <p><i>🔗 ControlPanel signal connections HungarianMapTab-hez</i></p>
        <p><i>🚨 analysis_parameters_changed → update_analysis_parameters automatikus</i></p>
        <p><i>🚨 weather_parameters_changed → update_weather_parameters automatikus</i></p>
        <p><i>🚨 date_range_changed → update_date_range automatikus</i></p>
        <p><i>🚨 parameters_bundle_changed → refresh_with_new_parameters automatikus</i></p>
        <p><i>🔧 Debug logging minden signal emit-nél</i></p>
        <p><i>🔥 Analytics View Refaktorálás BEFEJEZVE!</i></p>
        <p><i>🚀 AnalyticsView.multi_city_query_requested → MainWindow központi rendszer</i></p>
        <p><i>🔗 MainWindow._handle_analytics_view_query() → MultiCityEngine workflow</i></p>
        <p><i>📊 MainWindow._on_multi_city_result_ready_for_views() eredmény szétosztás</i></p>
        <p><i>🎯 AnalyticsView.update_with_multi_city_result() publikus slot</i></p>
        <p><i>🧹 Duplikált lekérdező logika eltávolítása AnalyticsView-ból</i></p>
        <p><i>🔥 Signal chain: AnalyticsView → MainWindow → MultiCityEngine → HungarianMapTab</i></p>
        <p><i>🔧 HIBÁS JELZÉSEK ELTÁVOLÍTVA!</i></p>
        <p><i>❌ analytics_completed hibás signal bekötések törölve</i></p>
        <p><i>❌ Felülíró térképi frissítések eltávolítva</i></p>
        <p><i>✅ Csak a tiszta, központi, paraméterezett adatkezelés marad</i></p>
        <p><i>✅ Query type alapú térképi paraméter beállítás</i></p>
        <p><i>✅ Egyértelmű adatfolyam: AnalyticsView → MainWindow → HungarianMapTab</i></p>
        <p><i>🔧 WINDSPEED METRIC TELJES JAVÍTÁS!</i></p>
        <p><i>🗺️ QUERY_TYPE_TO_PARAMETER mapping implementálva</i></p>
        <p><i>🌬️ "windiest_today" → "Szél" paraméter mapping</i></p>
        <p><i>🔧 2-lépéses koordináció: paraméter beállítás + adat átadás</i></p>
        <p><i>🔧 Enhanced debug logging minden lépéshez</i></p>
        <p><i>✅ _handle_multi_city_weather_request TELJES implementáció</i></p>
        <p><i>🎉 Multi-City Régió/Megye Térkép Integráció 100% BEFEJEZVE!</i></p>
        <p><i>🏞️ Régió/megye választás → Multi-City Engine → térkép overlay automatikus</i></p>
        <p><i>🗺️ AnalyticsResult objektum közvetlen átadás HungarianMapTab-nek</i></p>
        <p><i>📊 Analytics View bypass multi-city esetén - optimalizált workflow</i></p>
        <p><i>🔧 Error handling + debug üzenetek teljes multi-city workflow-hoz</i></p>
        <p><i>🌤️ Tiszta Analytics → Térkép Integration - Automatikus weather overlay!</i></p>
        <p><i>📊 Analytics View 365 napos weather data → Folium térkép automatikus átadás</i></p>
        <p><i>🗺️ Weather overlay automatikus generálás analytics eredményből</i></p>
        <p><i>🌍 WeatherDataBridge + Multi-City Engine teljes integráció</i></p>
        <p><i>🔗 Tiszta signal chain az összes analytics eredményhez</i></p>
        <p><i>🎯 Valós idejű weather overlay frissítés térképen</i></p>
        <p><i>🚀 Trend Analytics Integráció Befejezve - Professional vizualizációk!</i></p>
        <p><i>📈 Hőtérkép style trend chart + lineáris regresszió</i></p>
        <p><i>📊 R² értékek + trend/évtized + szignifikancia tesztek</i></p>
        <p><i>🎨 Modern glassmorphism UI design</i></p>
        <p><i>🏛️ Magyar település prioritás (3178 magyar + 44k globális)</i></p>
        <p><i>📅 5 év/10 év/minden adat elemzési opciók</i></p>
        <p><i>🎨 Professional színpaletta + ThemeManager integráció</i></p>
        <p><i>🔗 Clean signal chain: ControlPanel → TrendAnalyticsTab sync</i></p>
        <p><i>🧹 Dashboard Cleanup Befejezve - Clean Architecture!</i></p>
        <p><i>🏙️ Single City központi és alapértelmezett nézet</i></p>
        <p><i>📊 Egyszerűsített workflow: Keresés → Kiválasztás → Adatlekérdezés → Eredmények</i></p>
        <p><i>🎯 Azonnali feedback és hibakezelés</i></p>
        <p><i>🎯 Clean interface, világos funkciók (Dashboard komplexitás eltávolítva)</i></p>
        <p><i>🔧 Splitter handle width: 18px (még könnyebb mozgatás)</i></p>
        <p><i>🔧 Panel constraints: ControlPanel 320-520px, ResultsPanel min 450px</i></p>
        <p><i>🔧 Stretch factors: ControlPanel(0) fix, ResultsPanel(1) expand</i></p>
        <p><i>🔧 Layout margins optimalizálva (2px/0px spacing)</i></p>
        <p><i>🔧 Window size optimalizálva: 1400x900px (min 1200x700px)</i></p>
        <p><i>🔧 Initial sizes: ControlPanel 420px (UniversalLocationSelector komfort)</i></p>
        <p><i>🔧 Responsive layout behavior javítva</i></p>
        <p><i>🌍 Smart API routing: ingyenes és prémium szolgáltatások</i></p>
        <p><i>💎 Cost-aware selection: use-case alapú optimalizáció</i></p>
        <p><i>📊 Real-time provider status display status bar-ban</i></p>
        <p><i>⚠️ Usage tracking és warning notifications</i></p>
        <p><i>🔄 Provider fallback notifications</i></p>
        <p><i>💰 Cost monitoring és usage statistics</i></p>
        <p><i>📊 AnalyticsView REFAKTORÁLT integráció (duplikált logika eltávolítva)</i></p>
        <p><i>🔗 ControlPanel → AnalyticsView direct signal connection</i></p>
        <p><i>🔍 Duplikált vezérlők eltávolítva - clean architecture</i></p>
        <p><i>🎨 ThemeManager centralizált téma rendszer</i></p>
        <p><i>🗺️ Map View integráció - Térkép tab működik!</i></p>
        <p><i>📈 TrendAnalyticsTab integráció - Trend Elemzés tab működik!</i></p>
        <p><i>🌍 Globális időjárási adatok</i></p>
        <p><i>🏗️ Single City-központú clean interface (Dashboard eltávolítva)</i></p>
        <p><i>📊 Megbízható adatfeldolgozás</i></p>
        <p><i>⚙️ Moduláris, karbantartható kód</i></p>
        <p><i>🔗 Clean Signal Chain Management - refaktorált</i></p>
        <p><i>🎨 ColorPalette professzionális színrendszer</i></p>
        <p><i>📈 Analytics backend REFAKTORÁLT integráció</i></p>
        <p><i>📈 Trend Analytics backend PROFESSIONAL integráció</i></p>
        <p><i>🌤️ Tiszta Analytics → Térkép AUTOMATIKUS weather integration</i></p>
        <p><i>🎉 Multi-City Engine TELJES régió/megye support</i></p>
        <p><i>🔄 Fallback mechanizmus API hibák esetén</i></p>
        <p><i>❌ Dashboard komplexitás teljes eltávolítás</i></p>
        <p><i>🔧 Hibás jelzések teljes tisztítása</i></p>
        """
        
        QMessageBox.about(self, "Névjegy", about_text)
    
    # === 🎨 TÉMA KEZELÉS - THEMEMANAGER INTEGRÁCIÓ ===
    
    def _apply_theme(self, theme_type: ThemeType) -> None:
        """
        🎨 THEMEMANAGER INTEGRÁLT téma alkalmazása - ThemeManager singleton használatával.
        
        Args:
            theme_type: Téma típusa (ThemeType enum)
        """
        print(f"🎨 DEBUG: Applying theme through ThemeManager: {theme_type.value}")
        
        # 🎨 THEMEMANAGER TÉMA BEÁLLÍTÁSA (ez mindent automatikusan kezel)
        success = self.theme_manager.set_theme(theme_type.value)
        
        if success:
            # Téma tracking frissítése
            self.current_theme = theme_type
            
            # Beállítások mentése
            self.settings.setValue("theme", theme_type.value)
            
            print(f"✅ DEBUG: Theme applied and saved through ThemeManager: {theme_type.value}")
        else:
            print(f"❌ DEBUG: Theme application failed: {theme_type.value}")
    
    def _apply_theme_internal(self, theme_type: ThemeType) -> None:
        """
        🎨 DEPRECATED: Belső téma alkalmazás - THEMEMANAGER-RE DELEGÁLVA.
        
        Args:
            theme_type: Téma típusa (DEPRECATED, használd a ThemeManager-t)
        """
        print("⚠️ DEBUG: _apply_theme_internal() DEPRECATED - using ThemeManager instead")
        
        # ThemeManager-re delegálás
        self._apply_theme(theme_type)
    
    def _propagate_theme_change(self, theme_name: str) -> None:
        """
        🎨 DEPRECATED: Téma változás továbbítása - THEMEMANAGER AUTOMATIKUSAN KEZELI.
        
        Args:
            theme_name: Téma neve ("light" vagy "dark") (DEPRECATED, ThemeManager kezeli)
        """
        print("⚠️ DEBUG: _propagate_theme_change() DEPRECATED - ThemeManager handles automatically")
        
        # ThemeManager automatikusan kezeli az összes regisztrált widget-et
        # De a splitter-t külön kell frissíteni, mert az speciális
        dark_theme = (theme_name == "dark")
        self._update_splitter_theme(dark_theme)
        
        print(f"✅ DEBUG: Theme propagation complete via ThemeManager: {theme_name}")
    
    def _update_splitter_theme(self, dark_theme: bool) -> None:
        """
        🔧 SPLITTER téma frissítése theme váltáskor + THEMEMANAGER SZÍNEK.
        
        Args:
            dark_theme: Sötét téma-e
        """
        print(f"🔧 DEBUG: Updating splitter theme with ThemeManager colors (dark: {dark_theme})")
        
        # Single City View splitter keresése és frissítése
        single_city_view = None
        if self.stacked_widget and self.stacked_widget.count() > 0:
            single_city_view = self.stacked_widget.widget(0)  # 🧹 Index 0 = Single City View (Dashboard helyett)
        
        if single_city_view:
            # Splitter megkeresése a view-ban
            splitters = single_city_view.findChildren(QSplitter)
            for splitter in splitters:
                # 🎨 THEMEMANAGER SPLITTER CSS ALKALMAZÁSA
                splitter_css = self.theme_manager.generate_css_for_class("splitter")
                splitter.setStyleSheet(splitter_css)
                
                print(f"✅ DEBUG: Splitter theme updated with ThemeManager CSS: {'dark' if dark_theme else 'light'}")
    
    # === BEÁLLÍTÁSOK KEZELÉS ===
    
    def _load_settings(self) -> None:
        """Beállítások betöltése - THEMEMANAGER INTEGRÁCIÓVAL."""
        # Ablak pozíció és méret
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # 🎨 TÉMA BEÁLLÍTÁS - THEMEMANAGER INTEGRÁCIÓ
        theme_name = self.settings.value("theme", "light")
        try:
            theme_type = ThemeType(theme_name)
            self._apply_theme(theme_type)
        except ValueError:
            # Ha invalid téma érték, alapértelmezett light
            self._apply_theme(ThemeType.LIGHT)
        
        # 🧹 Single City alapértelmezett nézet (Dashboard helyett)
        self._switch_view("single_city")
        print("🧹 DEBUG: Single City set as default view (Dashboard cleanup befejezve)")
    
    def _save_settings(self) -> None:
        """Beállítások mentése + THEMEMANAGER."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("current_view", self.current_view_name)
        self.settings.setValue("theme", self.current_theme.value)
        
        # 🎨 THEMEMANAGER BEÁLLÍTÁSOK MENTÉSE
        self.theme_manager.save_theme_preferences(self.settings)
    
    # === LIFECYCLE ===
    
    def closeEvent(self, event) -> None:
        """Alkalmazás bezárásának kezelése + ANALYTICS → MAP SYNC FIX BEFEJEZVE + ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA + WINDSPEED METRIC TELJES JAVÍTÁS."""
        try:
            print("🛑 DEBUG: ANALYTICS → MAP SYNC FIX BEFEJEZVE + ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA + WINDSPEED METRIC TELJES JAVÍTÁS MainWindow closeEvent called")
            
            # Analytics panel leállítása (REFAKTORÁLT)
            if self.analytics_panel:
            print("🛑 DEBUG: Stopping refactored analytics panel...")
            self.analytics_panel.clear_data()
            
            # Trend analytics tab leállítása - ÚJ!
            if self.trend_analytics_tab:
                print("🛑 DEBUG: Stopping trend analytics tab...")
                self.trend_analytics_tab.clear_data()
            
            # Hungarian Map tab leállítása - ÚJ!
            if self.hungarian_map_tab:
                print("🛑 DEBUG: Stopping hungarian map tab...")
                # Ha a HungarianMapTab-nak lenne cleanup metódusa, itt hívnánk meg
            
            # Map view leállítása
            if self.map_view:
                print("🛑 DEBUG: Stopping map view component...")
                # Ha a MapView-nak lenne cleanup metódusa, itt hívnánk meg
            
            # Beállítások mentése
            self._save_settings()
            
            # Controller leállítása
            print("🛑 DEBUG: Shutting down controller...")
            self.controller.shutdown()
            
            # Esemény elfogadása
            event.accept()
            
            print("✅ DEBUG: ANALYTICS → MAP SYNC FIX BEFEJEZVE + ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA + WINDSPEED METRIC TELJES JAVÍTÁS MainWindow bezárva")
            
        except Exception as e:
            print(f"⚠️ DEBUG: Bezárási hiba: {e}")
            import traceback
            traceback.print_exc()
            event.accept()
    
    # === PUBLIKUS API ===
    
    def get_current_view(self) -> str:
        """Jelenlegi nézet nevének lekérdezése."""
        return self.current_view_name
    
    def switch_to_view(self, view_name: str) -> None:
        """Programmatic nézet váltás (külső használatra)."""
        self._switch_view(view_name)
    
    def get_available_views(self) -> list:
        """Elérhető nézetek listájának lekérdezése - ANALYTICS → MAP SYNC FIX BEFEJEZVE + ANALYTICS VIEW REFAKTORÁLÁS BEFEJEZVE + HIBÁS JELZÉSEK ELTÁVOLÍTVA + WINDSPEED METRIC TELJES JAVÍTÁS."""
        return ["single_city", "analytics", "trend_analysis", "map_view", "settings"]  # 🧹 Dashboard eltávolítva, 📈 trend_analysis hozzáadva, 🌤️ map_view frissítve, 🔥 analytics refaktorálva, 🔧 windspeed javítva
    
    def get_analytics_panel(self) -> Optional[AnalyticsView]:
        """
        📊 Analytics panel referencia lekérdezése - REFAKTORÁLT FUNKCIÓ.
        
        Returns:
            AnalyticsView refaktorált példány vagy None
        """
        return self.analytics_panel
    
    def focus_analytics_panel(self) -> None:
        """
        📊 Analytics panel fókuszba helyezése - REFAKTORÁLT FUNKCIÓ.
        """
        self._switch_view("analytics")
    
    def get_map_view(self) -> Optional[MapView]:
        """
        🗺️ Map view referencia lekérdezése - ÚJ FUNKCIÓ.
        
        Returns:
            MapView példány vagy None
        """
        return self.map_view
    
    def focus_map_view(self) -> None:
        """
        🗺️ Map view fókuszba helyezése - ÚJ FUNKCIÓ.
        """
        self._switch_view("map_view")
    
    def get_hungarian_map_tab(self) -> Optional[HungarianMapTab]:
        """
        🌤️ Hungarian Map Tab referencia lekérdezése - ÚJ FUNKCIÓ.
        
        Returns:
            HungarianMapTab példány vagy None
        """
        return self.hungarian_map_tab
    
    def focus_hungarian_map_tab(self) -> None:
        """
        🌤️ Hungarian Map Tab fókuszba helyezése - ÚJ FUNKCIÓ.
        """
        self._switch_view("map_view")
    
    def get_trend_analytics_tab(self) -> Optional[TrendAnalyticsTab]:
        """
        📈 Trend Analytics tab referencia lekérdezése - ÚJ FUNKCIÓ.
        
        Returns:
            TrendAnalyticsTab professional példány vagy None
        """
        return self.trend_analytics_tab
    
    def focus_trend_analytics_tab(self) -> None:
        """
        📈 Trend Analytics tab fókuszba helyezése - ÚJ FUNKCIÓ.
        """
        self._switch_view("trend_analysis")


# Export
__all__ = ['MainWindow']analysis_completed.connect(debug_analytics_analysis_completed)
            # self.analytics_panel.