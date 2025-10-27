#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Main Window Module
🚨 KRITIKUS FIX: THREAD CLEANUP IMPLEMENTÁLVA!
🧹 WORKER LIFECYCLE MANAGEMENT BEFEJEZVE!
🌐 WEBENGINE SHUTDOWN SEQUENCE HOZZÁADVA!

✅ BEFEJEZETT FUNKCIÓK:
🎯 Analytics View signal chain helyreállítva
🗺️ Magyar megyék automatikus integrációja  
🌍 Provider status tracking és multi-city engine
🧹 Thread cleanup és worker lifecycle management - ÚJ!
"""

from typing import Optional, Dict, Any
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QSplitter,
    QStatusBar, QMessageBox, QToolBar, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QSettings, Signal, QSize, QThread, QTimer
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWebEngineWidgets import QWebEngineView

from ..config import AppInfo
from .utils import (
    GUIConstants, ThemeType, get_source_display_name, format_provider_usage,
    get_provider_warning_level, format_provider_status, get_provider_icon,
    format_cost_summary
)
from .theme_manager import get_theme_manager, register_widget_for_theming
from .color_palette import ColorPalette
from .app_controller import AppController
from .control_panel import ControlPanel
from .results_panel import ResultsPanel
from .data_widgets import WeatherDataTable
from .dialogs import ExtremeWeatherDialog
from .analytics_view import AnalyticsView
from .map_view import MapView
from .trend_analytics_tab import TrendAnalyticsTab
from .hungarian_map_tab import HungarianMapTab

# 🗺️ MAGYAR MEGYÉK AUTOMATIKUS INTEGRÁCIÓJA
try:
    from ..analytics.hungarian_counties_integration import HungarianCountiesLoader
    HUNGARIAN_COUNTIES_AVAILABLE = True
except ImportError as e:
    HUNGARIAN_COUNTIES_AVAILABLE = False


class MainWindow(QMainWindow):
    """
    🚨 TELJES FUNKCIONALITÁS + THREAD CLEANUP FIX!
    
    ✅ 1. HULLÁM - Analytics signal chain helyreállítva
    ✅ 2. HULLÁM - Magyar megyék automatikus integrációja  
    ✅ 3. HULLÁM - Provider status és multi-city engine bővítése
    ✅ 4. HULLÁM - Thread cleanup és worker lifecycle management
    
    🧹 THREAD CLEANUP FUNKCIÓK:
    - Worker thread graceful shutdown
    - WebEngine cleanup sequence
    - Analysis worker termination
    - QTimer cleanup
    - Memory leak prevention
    """
    
    # 📧 QUERY TYPE → TÉRKÉP PARAMÉTER MAPPING
    QUERY_TYPE_TO_PARAMETER = {
        "hottest_today": "Hőmérséklet",
        "coldest_today": "Hőmérséklet", 
        "windiest_today": "Szél",
        "wettest_today": "Csapadék",
        "rainiest_today": "Csapadék",
        "sunniest_today": "Hőmérséklet",
        "temperature_range": "Hőmérséklet"
    }
    
    def __init__(self):
        """Főablak inicializálása - TELJES FUNKCIONALITÁS + THREAD TRACKING."""
        super().__init__()
        
        # 🧹 THREAD TRACKING LISTA HOZZÁADVA
        self.active_threads = []
        self.active_workers = []
        self.web_engine_views = []
        self.cleanup_timers = []
        
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
        
        # 🗺️ MAGYAR MEGYÉK ÁLLAPOT TRACKING
        self.hungarian_counties_loaded = False
        self.counties_geodataframe = None
        
        # === MVC KOMPONENSEK LÉTREHOZÁSA ===
        
        # Controller (Model + business logic)
        self.controller = AppController()
        
        # Worker Manager (a Controller használja, de referencia kell a UI-hoz)
        self.worker_manager = self.controller.worker_manager
        
        # === VIEW KOMPONENSEK ===
        
        # Navigációs toolbar
        self.toolbar: Optional[QToolBar] = None
        
        # Stacked Widget a nézetek váltásához
        self.stacked_widget: Optional[QStackedWidget] = None
        
        # VIEW REFERENCIÁK
        self.current_view_name = "single_city"
        self.current_theme = ThemeType.LIGHT
        
        # SingleCity view komponensei (KÖZPONTI FUNKCIONALITÁS)
        self.control_panel: Optional[ControlPanel] = None
        self.results_panel: Optional[ResultsPanel] = None
        self.data_table: Optional[WeatherDataTable] = None
        
        # 📊 ANALYTICS VIEW KOMPONENS - REFAKTORÁLT!
        self.analytics_panel: Optional[AnalyticsView] = None
        
        # 🗺️ MAP VIEW KOMPONENS
        self.map_view: Optional[MapView] = None
        
        # 🌤️ HUNGARIAN MAP TAB KOMPONENS
        self.hungarian_map_tab: Optional[HungarianMapTab] = None
        
        # 📈 TREND ANALYTICS KOMPONENS
        self.trend_analytics_tab: Optional[TrendAnalyticsTab] = None
        
        # 🌍 STATUS BAR PROVIDER WIDGETS
        self.provider_status_label: Optional[QLabel] = None
        self.usage_status_label: Optional[QLabel] = None
        self.cost_status_label: Optional[QLabel] = None
        
        # === UI INICIALIZÁLÁSA ===
        
        self._setup_window()
        self._init_navigation_toolbar()
        self._init_stacked_views()
        self._init_menu_bar()
        self._init_status_bar_with_provider_display()
        
        # === SIGNAL CHAIN ÖSSZEKÖTÉSE ===
        
        self._connect_mvc_signals_clean_with_city_analysis_fix()
        
        # === THEMEMANAGER SETUP ===
        
        self._setup_theme_integration()
        
        # === MAGYAR MEGYÉK AUTOMATIKUS BETÖLTÉSE ===
        
        self._load_hungarian_counties()
        
        # === BEÁLLÍTÁSOK BETÖLTÉSE ===
        
        self._load_settings()
    
    def _load_hungarian_counties(self) -> None:
        """
        🗺️ Magyar megyék automatikus betöltése és integráció a HungarianMapTab-be.
        """
        try:
            # 1. MODUL ELÉRHETŐSÉG ELLENŐRZÉSE
            if not HUNGARIAN_COUNTIES_AVAILABLE:
                self.hungarian_counties_loaded = False
                return
            
            # 2. HUNGARIAN COUNTIES LOADER LÉTREHOZÁSA
            counties_loader = HungarianCountiesLoader()
            
            # 3. MEGYÉK BETÖLTÉSE (KSH ADATBÁZIS VAGY DEMO)
            self.counties_geodataframe = counties_loader.load_counties_geodataframe()
            
            if self.counties_geodataframe is None:
                self.hungarian_counties_loaded = False
                return
            
            # 4. HUNGARIAN MAP TAB KERESÉSE ÉS KONFIGURÁLÁSA
            self._configure_hungarian_map_with_counties()
            
            # 5. SIKERESEN BETÖLTVE
            self.hungarian_counties_loaded = True
            
        except Exception as e:
            self.hungarian_counties_loaded = False
            self.counties_geodataframe = None
    
    def _configure_hungarian_map_with_counties(self) -> None:
        """
        🗺️ HungarianMapTab automatikus konfigurálása magyar megyékkel.
        """
        try:
            # HUNGARIAN MAP TAB KERESÉSE
            if self.hungarian_map_tab is None:
                return
            
            # MAP VISUALIZER KOMPONENS KERESÉSE A HUNGARIAN MAP TAB-BEN
            if hasattr(self.hungarian_map_tab, 'map_visualizer'):
                map_visualizer = self.hungarian_map_tab.map_visualizer
            else:
                return
            
            # COUNTIES GEODATAFRAME BEÁLLÍTÁSA A MAP VISUALIZER-EN
            if hasattr(map_visualizer, 'set_counties_geodataframe'):
                map_visualizer.set_counties_geodataframe(self.counties_geodataframe)
                
                # MEGYEHATÁROK AUTOMATIKUS BEKAPCSOLÁSA
                if hasattr(map_visualizer, 'show_county_borders'):
                    map_visualizer.show_county_borders = True
            
        except Exception as e:
            pass
    
    def _setup_window(self) -> None:
        """Ablak alapbeállításai."""
        self.setWindowTitle(f"{AppInfo.NAME} - THREAD CLEANUP FIX")
        
        # Ablak méretek
        self.setGeometry(
            GUIConstants.MAIN_WINDOW_X,
            GUIConstants.MAIN_WINDOW_Y,
            1400,
            900
        )
        self.setMinimumSize(1200, 700)
        
        # Widget regisztráció THEMEMANAGER-hez
        register_widget_for_theming(self, "navigation")
        
        # Téma rendszer integráció - alapértelmezett light theme
        self._apply_theme_internal(ThemeType.LIGHT)
    
    def _setup_theme_integration(self) -> None:
        """ThemeManager integráció beállítása."""
        # ThemeManager signalok feliratkozása
        self.theme_manager.theme_changed.connect(self._on_theme_manager_changed)
        
        # Widget regisztrációk fő komponensekhez
        register_widget_for_theming(self, "navigation")
    
    def _on_theme_manager_changed(self, theme_name: str) -> None:
        """ThemeManager téma változás kezelése."""
        # Téma tracking frissítése
        try:
            self.current_theme = ThemeType(theme_name)
        except ValueError:
            self.current_theme = ThemeType.LIGHT
    
    def _init_navigation_toolbar(self) -> None:
        """Navigációs eszköztár létrehozása - 5 TAB VERZIÓ."""
        # Eszköztár létrehozása
        self.toolbar = QToolBar("Navigáció")
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.setIconSize(QSize(24, 24))
        
        # Widget regisztráció THEMEMANAGER-hez
        register_widget_for_theming(self.toolbar, "navigation")
        
        # === NAVIGÁCIÓS AKCIÓK - 5 TAB VERZIÓ ===
        
        # 🏙️ Pontszerű Elemzés (KÖZPONTI NÉZET)
        self.single_city_action = QAction("Város Elemzés", self)
        self.single_city_action.setToolTip("Egyetlen város részletes időjárási elemzése")
        self.single_city_action.triggered.connect(lambda: self._switch_view("single_city"))
        self.single_city_action.setCheckable(True)
        self.single_city_action.setChecked(True)
        self.toolbar.addAction(self.single_city_action)
        
        # 📊 Analytics (REFAKTORÁLT FUNKCIÓ)
        self.analytics_action = QAction("Analitika", self)
        self.analytics_action.setToolTip("Időjárási elemzések és statisztikák")
        self.analytics_action.triggered.connect(lambda: self._switch_view("analytics"))
        self.analytics_action.setCheckable(True)
        self.toolbar.addAction(self.analytics_action)
        
        # 📈 Trend Elemző
        self.trend_action = QAction("Trend Elemzés", self)
        self.trend_action.setToolTip("Hosszú távú klimatikus trendek elemzése")
        self.trend_action.triggered.connect(lambda: self._switch_view("trend_analysis"))
        self.trend_action.setCheckable(True)
        self.toolbar.addAction(self.trend_action)
        
        # 🗺️ Interaktív Térkép
        self.map_action = QAction("Térkép", self)
        self.map_action.setToolTip("Interaktív időjárási térkép magyar megyékkel")
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
        
        # === AKCIÓK CSOPORTOSÍTÁSA ===
        
        self.view_action_group = QActionGroup(self)
        self.view_action_group.addAction(self.single_city_action)
        self.view_action_group.addAction(self.analytics_action)
        self.view_action_group.addAction(self.trend_action)
        self.view_action_group.addAction(self.map_action)
        self.view_action_group.addAction(self.settings_action)
        
        # Eszköztár hozzáadása az ablakhoz
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
    
    def _init_stacked_views(self) -> None:
        """QStackedWidget inicializálása különböző nézetekkel - 5 NÉZET."""
        # Központi widget és layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Widget regisztráció
        register_widget_for_theming(central_widget, "container")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)
        
        # === STACKED WIDGET LÉTREHOZÁSA ===
        
        self.stacked_widget = QStackedWidget()
        register_widget_for_theming(self.stacked_widget, "container")
        main_layout.addWidget(self.stacked_widget)
        
        # === VIEW-K LÉTREHOZÁSA - 5 NÉZET VERZIÓ ===
        
        # 1. Single City View (KÖZPONTI FUNKCIONALITÁS)
        single_city_view = self._create_single_city_view()
        self.stacked_widget.addWidget(single_city_view)  # INDEX 0
        
        # 2. Analytics View (REFAKTORÁLT VERZIÓ)
        analytics_view = self._create_analytics_view()
        self.stacked_widget.addWidget(analytics_view)  # INDEX 1
        
        # 3. Trend Analysis View
        trend_view = self._create_trend_analysis_view()
        self.stacked_widget.addWidget(trend_view)  # INDEX 2
        
        # 4. Map View
        map_view = self._create_hungarian_map_view()
        self.stacked_widget.addWidget(map_view)  # INDEX 3
        
        # 5. Settings View
        settings_view = self._create_settings_placeholder()
        self.stacked_widget.addWidget(settings_view)  # INDEX 4
        
        # === ALAPÉRTELMEZETT NÉZET BEÁLLÍTÁSA ===
        
        self.stacked_widget.setCurrentIndex(0)  # Single City View alapértelmezett
    
    def _create_single_city_view(self) -> QWidget:
        """Single City View létrehozása."""
        print("🔧 DEBUG: Creating Single City View...")
        
        view = QWidget()
        register_widget_for_theming(view, "container")
        
        layout = QVBoxLayout(view)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        # === SPLITTER ===
        
        main_splitter = QSplitter(Qt.Horizontal)
        
        print("🔧 DEBUG: Configuring splitter...")
        
        # Splitter beállítások
        main_splitter.setHandleWidth(18)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setOpaqueResize(True)
        
        # Splitter widget regisztráció THEMEMANAGER-hez
        register_widget_for_theming(main_splitter, "splitter")
        
        # === BAL OLDAL: CONTROL PANEL ===
        
        print("🎛️ DEBUG: Creating ControlPanel...")
        self.control_panel = ControlPanel(self.worker_manager)
        
        # Control panel widget regisztráció
        register_widget_for_theming(self.control_panel, "container")
        
        # Size constraints
        self.control_panel.setMinimumWidth(320)
        self.control_panel.setMaximumWidth(520)
        self.control_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        main_splitter.addWidget(self.control_panel)
        print(f"✅ DEBUG: ControlPanel added")
        
        # === JOBB OLDAL: RESULTS PANEL ===
        
        print("📊 DEBUG: Creating ResultsPanel...")
        self.results_panel = ResultsPanel()
        
        # Results panel widget regisztráció
        register_widget_for_theming(self.results_panel, "container")
        
        # Results panel constraints
        self.results_panel.setMinimumWidth(450)
        self.results_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        main_splitter.addWidget(self.results_panel)
        print("✅ DEBUG: ResultsPanel added")
        
        # === STRETCH FACTOR KONFIGURÁCIÓK ===
        
        print("🔧 DEBUG: Setting stretch factors...")
        
        # Stretch factor beállítás:
        # 0 = Control Panel (fix szélesség 320-520px között)
        # 1 = Results Panel (kitölti a teljes maradék helyet)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        
        print("✅ DEBUG: Stretch factors set")
        
        # === INITIAL SIZES ===
        
        # Kezdeti méretek
        total_width = 1400
        control_width = 420
        results_width = total_width - control_width - 20
        
        main_splitter.setSizes([control_width, results_width])
        
        print(f"✅ DEBUG: Initial sizes set - Control: {control_width}px, Results: {results_width}px")
        
        # === LAYOUT FINALIZÁLÁS ===
        
        layout.addWidget(main_splitter)
        
        print("🔧 DEBUG: Single City View created")
        
        return view
    
    def _create_analytics_view(self) -> QWidget:
        """Analytics View létrehozása - REFAKTORÁLT IMPLEMENTÁCIÓ + THEMEMANAGER + SIGNAL INTEGRATION."""
        print("📊 DEBUG: Creating REFAKTORÁLT AnalyticsView with ThemeManager + Signal Integration...")
        
        # Refaktorált AnalyticsView létrehozása
        self.analytics_panel = AnalyticsView()  # 🔧 REFAKTORÁLT VERZIÓ
        
        # 🎨 WIDGET REGISZTRÁCIÓ
        register_widget_for_theming(self.analytics_panel, "container")
        
        print("✅ DEBUG: REFAKTORÁLT AnalyticsView created with ThemeManager + Signal Integration")
        return self.analytics_panel
    
    def _create_trend_analysis_view(self) -> QWidget:
        """📈 Trend Analysis view létrehozása - VALÓDI TRENDANALYTICSTAB KOMPONENS + THEMEMANAGER."""
        print("📈 DEBUG: Creating real TrendAnalyticsTab component with ThemeManager...")
        
        # Valódi TrendAnalyticsTab komponens létrehozása
        self.trend_analytics_tab = TrendAnalyticsTab()
        
        # 🎨 WIDGET REGISZTRÁCIÓ THEMEMANAGER-HEZ
        register_widget_for_theming(self.trend_analytics_tab, "container")
        
        print("✅ DEBUG: Real TrendAnalyticsTab component created with ThemeManager")
        return self.trend_analytics_tab
    
    def _create_hungarian_map_view(self) -> QWidget:
        """🌤️ Hungarian Map view létrehozása - VALÓDI HUNGARIAN MAP TAB KOMPONENS + THEMEMANAGER + WEATHER INTEGRATION + MAGYAR MEGYÉK AUTOMATIKUS INTEGRÁCIÓJA."""
        print("🌤️ DEBUG: Creating real HungarianMapTab component with ThemeManager + Weather Integration + Magyar Megyék...")
        
        # Valódi HungarianMapTab komponens létrehozása
        self.hungarian_map_tab = HungarianMapTab()
        
        # 🎨 WIDGET REGISZTRÁCIÓ THEMEMANAGER-HEZ
        register_widget_for_theming(self.hungarian_map_tab, "container")
        
        # 🗺️ KRITIKUS: MAGYAR MEGYÉK AUTOMATIKUS KONFIGURÁLÁSA MOST HOGY A KOMPONENS LÉTEZIK
        if self.counties_geodataframe is not None:
            print("🗺️ DEBUG: HungarianMapTab létezik - megyék automatikus konfigurálása...")
            self._configure_hungarian_map_with_counties()
        else:
            print("⚠️ DEBUG: Counties még nincsenek betöltve a HungarianMapTab létrehozásakor")
        
        print("✅ DEBUG: Real HungarianMapTab component created with ThemeManager + Weather Integration + Magyar Megyék")
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
        """Nézet váltás kezelése - 🗺️ 5 NÉZET VERZIÓ."""
        print(f"🔄 DEBUG: Switching to view: {view_name}")
        
        # View index mapping - 5 NÉZET
        view_indices = {
            "single_city": 0,    # SINGLE CITY KÖZPONTI NÉZET
            "analytics": 1,      # REFAKTORÁLT ANALYTICS VIEW
            "trend_analysis": 2, # 📈 VALÓDI TREND ANALYTICS TAB
            "map_view": 3,       # 🌤️ VALÓDI HUNGARIAN MAP TAB + MAGYAR MEGYÉK
            "settings": 4
        }
        
        if view_name not in view_indices:
            print(f"⚠️ DEBUG: Unknown view name: {view_name}")
            return
        
        # Nézet váltás
        self.current_view_name = view_name
        view_index = view_indices[view_name]
        self.stacked_widget.setCurrentIndex(view_index)
        
        print(f"✅ DEBUG: View switched to: {view_name} (index: {view_index})")
    
    def _init_menu_bar(self) -> None:
        """Menüsáv inicializálása - 🗺️ MAGYAR MEGYÉK VERZIÓ."""
        menubar = self.menuBar()
        register_widget_for_theming(menubar, "navigation")
        
        # === FÁJL MENÜ ===
        file_menu = menubar.addMenu("📄 Fájl")
        
        # Export akció
        export_action = QAction("📊 Adatok exportálása...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_data)
        export_action.setEnabled(False)  # Kezdetben letiltva
        file_menu.addAction(export_action)
        self.export_action = export_action
        
        file_menu.addSeparator()
        
        # Kilépés akció
        exit_action = QAction("🚪 Kilépés", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # === NÉZET MENÜ ===
        view_menu = menubar.addMenu("👁️ Nézet")
        
        # Navigáció - 5 TAB
        view_menu.addAction(self.single_city_action)
        view_menu.addAction(self.analytics_action)
        view_menu.addAction(self.trend_action)  # 📈 VALÓDI TREND ANALYTICS
        view_menu.addAction(self.map_action)  # 🎉 MULTI-CITY RÉGIÓ/MEGYE HUNGARIAN MAP TAB + MAGYAR MEGYÉK
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
        """Status bar inicializálása Provider Display-jel."""
        print("🌍 DEBUG: Creating status bar...")
        
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
        
        self.status_bar.showMessage("✅ THREAD CLEANUP FIX + WORKER LIFECYCLE MANAGEMENT IMPLEMENTÁLVA!")
        
        # Provider info inicializálása
        self._initialize_provider_status()
        
        print("✅ DEBUG: Status bar created")
    
    # === 🧹 CLEAN SIGNAL CHAIN + ANALYTICS SIGNAL FIX + 🌍 PROVIDER STATUS SIGNALS ===
    
    def _connect_mvc_signals_clean_with_city_analysis_fix(self) -> None:
        """
        🚨 KRITIKUS: CLEAN MVC komponensek signal-slot összekötése + ANALYTICS SIGNAL FIX + 🌍 PROVIDER STATUS SIGNALS!
        """
        
        print("🔗 DEBUG: Starting CLEAN signals + ANALYTICS SIGNAL FIX + PROVIDER STATUS...")
        
        # === 🎯 KÖZPONTI KAPCSOLAT: CONTROLPANEL → APPCONTROLLER ===
        
        print("🎯 DEBUG: Setting up CENTRAL connection: ControlPanel → AppController...")
        
        if self.control_panel:
            # 🚀 KRITIKUS: Egyetlen központi kapcsolat - minden elemzési kérést az AppController kezel
            if hasattr(self.control_panel, 'analysis_requested'):
                self.control_panel.analysis_requested.connect(
                    self.controller.handle_analysis_request
                )
                print("✅ CLEAN: ControlPanel.analysis_requested → AppController.handle_analysis_request CONNECTED")
            else:
                print("⚠️ DEBUG: ControlPanel.analysis_requested signal NOT FOUND!")
            
            # 🛠 MEGSZAKÍTÁS GOMB BEKÖTÉSE
            if hasattr(self.control_panel, 'cancel_requested'):
                self.control_panel.cancel_requested.connect(
                    self.controller.stop_current_analysis
                )
                print("✅ CLEAN: ControlPanel.cancel_requested → AppController.stop_current_analysis CONNECTED")
            else:
                print("⚠️ DEBUG: ControlPanel.cancel_requested signal NOT FOUND!")
        else:
            print("⚠️ DEBUG: ControlPanel is None!")
        
        # === 📡 APPCONTROLLER ÉLETCIKLUS JELEK FIGYELÉSE + 🎯 VÁROS ELEMZÉS ADATFOLYAM FIX ===
        
        print("📡 DEBUG: Connecting AppController lifecycle signals + VÁROS ELEMZÉS ADATFOLYAM FIX...")
        
        # Elemzés indulása
        if hasattr(self.controller, 'analysis_started'):
            self.controller.analysis_started.connect(self._on_analysis_started)
            print("✅ CLEAN: AppController.analysis_started → MainWindow._on_analysis_started CONNECTED")
        
        # 🎯 KRITIKUS: Elemzés befejezése (SIKER) - VÁROS ELEMZÉS FIX!
        if hasattr(self.controller, 'analysis_completed'):
            self.controller.analysis_completed.connect(self._on_analysis_completed_with_city_fix)
            print("🎯 ✅ KRITIKUS: AppController.analysis_completed → MainWindow._on_analysis_completed_with_city_fix CONNECTED (VÁROS ELEMZÉS FIX)!")
        
        # Elemzés hiba
        if hasattr(self.controller, 'analysis_failed'):
            self.controller.analysis_failed.connect(self._on_analysis_failed)
            print("✅ CLEAN: AppController.analysis_failed → MainWindow._on_analysis_failed CONNECTED")
        
        # Elemzés megszakítva
        if hasattr(self.controller, 'analysis_cancelled'):
            self.controller.analysis_cancelled.connect(self._on_analysis_cancelled)
            print("✅ CLEAN: AppController.analysis_cancelled → MainWindow._on_analysis_cancelled CONNECTED")
        
        # Progress frissítések
        if hasattr(self.controller, 'analysis_progress'):
            self.controller.analysis_progress.connect(self._update_progress_clean)
            print("✅ CLEAN: AppController.analysis_progress → MainWindow._update_progress_clean CONNECTED")
        
        # === 🚨 KRITIKUS: ANALYTICS VIEW SIGNAL HANDLING VISSZAÁLLÍTÁSA ===
        
        if self.analytics_panel:
            print("🚨 DEBUG: ANALYTICS SIGNAL HANDLING VISSZAÁLLÍTÁSA...")
            
            # 🚨 KRITIKUS: Analytics View multi_city_query_requested signal
            if hasattr(self.analytics_panel, 'multi_city_query_requested'):
                def debug_analytics_multi_city_query_requested(query_type: str, region_name: str):
                    print(f"🚨 DEBUG [ANALYTICS→MAIN_WINDOW]: multi_city_query_requested: {query_type}, {region_name}")
                
                self.analytics_panel.multi_city_query_requested.connect(debug_analytics_multi_city_query_requested)
                self.analytics_panel.multi_city_query_requested.connect(
                    self._handle_analytics_view_query
                )
                print("🚨 ✅ KRITIKUS: AnalyticsView.multi_city_query_requested → MainWindow._handle_analytics_view_query CONNECTED!")
            else:
                print("❌ DEBUG: AnalyticsView.multi_city_query_requested signal NOT FOUND!")
            
            # Analytics további signalok
            if hasattr(self.analytics_panel, 'analysis_started'):
                self.analytics_panel.analysis_started.connect(
                    lambda: self.status_bar.showMessage("📊 Analytics elemzés folyamatban...")
                )
                print("✅ DEBUG: AnalyticsView.analysis_started signal connected")
            
            if hasattr(self.analytics_panel, 'error_occurred'):
                self.analytics_panel.error_occurred.connect(
                    lambda msg: self.status_bar.showMessage(f"❌ Analytics hiba: {msg}")
                )
                print("✅ DEBUG: AnalyticsView.error_occurred signal connected")
        else:
            print("❌ DEBUG: Analytics panel is None - signalok nem kapcsolódnak!")
        
        # === 🌍 PROVIDER STATUS SIGNALOK ===
        
        print("🌍 DEBUG: Connecting Provider Status signals...")
        
        # Provider váltás
        self.controller.provider_selected.connect(self._on_provider_selected)
        print("✅ DEBUG: Controller.provider_selected → MainWindow._on_provider_selected CONNECTED")
        
        # Usage statistics frissítése
        self.controller.provider_usage_updated.connect(self._on_provider_usage_updated)
        print("✅ DEBUG: Controller.provider_usage_updated → MainWindow._on_provider_usage_updated CONNECTED")
        
        # Warning events
        self.controller.provider_warning.connect(self._on_provider_warning)
        print("✅ DEBUG: Controller.provider_warning → MainWindow._on_provider_warning CONNECTED")
        
        # Fallback notifications
        self.controller.provider_fallback.connect(self._on_provider_fallback)
        print("✅ DEBUG: Controller.provider_fallback → MainWindow._on_provider_fallback CONNECTED")
        
        # === 📊 RESULTS PANEL SIGNALOK (EGYSZERŰSÍTVE) ===
        
        if self.results_panel:
            # Export kérések
            if hasattr(self.results_panel, 'export_requested'):
                self.results_panel.export_requested.connect(self._handle_export_request)
                print("✅ DEBUG: ResultsPanel.export_requested → MainWindow._handle_export_request CONNECTED")
            else:
                print("⚠️ DEBUG: ResultsPanel.export_requested signal NOT FOUND!")
            
            # Extrém időjárás kérések (DEFENSIVE CHECK)
            if hasattr(self.results_panel, 'extreme_weather_requested'):
                self.results_panel.extreme_weather_requested.connect(self._show_extreme_weather)
                print("✅ DEBUG: ResultsPanel.extreme_weather_requested → MainWindow._show_extreme_weather CONNECTED")
            else:
                print("⚠️ DEBUG: ResultsPanel.extreme_weather_requested signal NOT FOUND - SKIPPING")
        else:
            print("⚠️ DEBUG: ResultsPanel is None!")
        
        # === 🎨 TÉMA SIGNALOK - THEMEMANAGER INTEGRÁCIÓ ===
        
        self.theme_changed.connect(self._propagate_theme_change)
        print("✅ DEBUG: MainWindow.theme_changed → MainWindow._propagate_theme_change CONNECTED")
        
        print("🚨 ✅ DEBUG: ALL CLEAN signals connected successfully + ANALYTICS SIGNAL FIX + PROVIDER STATUS!")
    
    # === 🚨 ANALYTICS VIEW QUERY HANDLER - VISSZAÁLLÍTOTT METÓDUS! ===
    
    def _handle_analytics_view_query(self, query_type: str, region_name: str):
        """
        🚨 VISSZAÁLLÍTVA: Kezeli az AnalyticsView-ből érkező multi-city lekérdezési kéréseket.
        
        Args:
            query_type: Lekérdezés típusa (pl. "hottest_today", "coldest_today")
            region_name: Régió neve (pl. "Észak-Magyarország")
        """
        print(f"🚨 DEBUG: _handle_analytics_view_query called (VISSZAÁLLÍTVA): {query_type}, {region_name}")
        
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
        🔧 ÚJ: Query type leképezése térképi paraméterre.
        
        Args:
            query_type: Analytics query type (pl. "windiest_today")
            
        Returns:
            Térkép paraméter neve (pl. "Szél")
        """
        mapped_param = self.QUERY_TYPE_TO_PARAMETER.get(query_type, "Hőmérséklet")
        print(f"🔧 DEBUG: Query type mapping: {query_type} → {mapped_param}")
        return mapped_param
    
    # === 📡 ÚJ: APPCONTROLLER ÉLETCIKLUS SLOT METÓDUSOK + VÁROS ELEMZÉS ADATFOLYAM FIX ===
    
    def _on_analysis_started(self, analysis_type: str) -> None:
        """
        🚀 Elemzés indulásának kezelése - ÚJ SLOT METÓDUS.
        
        Args:
            analysis_type: Elemzés típusa (pl. "single_city", "multi_city", "trend_analysis")
        """
        print(f"🚀 DEBUG: _on_analysis_started called: {analysis_type}")
        
        # Státusz frissítése
        type_names = {
            "single_city": "Város elemzés",
            "multi_city": "Multi-city elemzés", 
            "trend_analysis": "Trend elemzés",
            "analytics": "Analitika elemzés"
        }
        
        type_name = type_names.get(analysis_type, analysis_type)
        self.status_bar.showMessage(f"🚀 {type_name} folyamatban...")
        
        # UI elemek letiltása (opcionális)
        # Például: export menü letiltása elemzés közben
        if hasattr(self, 'export_action'):
            self.export_action.setEnabled(False)
        
        print(f"✅ DEBUG: Analysis start handled: {analysis_type}")
    
    def _on_analysis_completed_with_city_fix(self, result_data: Dict[str, Any]) -> None:
        """
        🎯 KRITIKUS JAVÍTÁS: Elemzés sikeres befejezésének kezelése - DUPLA KONVERZIÓ JAVÍTVA!
        
        Az AnalysisWorker már tökéletesen konvertálta List[Dict] → Dict[List] formátumra!
        A MainWindow NEM konvertál újra, hanem KÖZVETLENÜL használja az eredményt!
        
        Args:
            result_data: Elemzés eredménye (kontextustól függő struktúra)
        """
        print(f"🎯 KRITIKUS DEBUG: _on_analysis_completed_with_city_fix called - DUPLA KONVERZIÓ JAVÍTVA!")
        print(f"🎯 DEBUG: Result keys: {list(result_data.keys()) if result_data else 'NO RESULT'}")
        
        try:
            # Elemzés típusának meghatározása
            analysis_type = result_data.get('analysis_type', 'unknown')
            print(f"🎯 DEBUG: Analysis type detected: {analysis_type}")
            
            # Státusz frissítése
            self.status_bar.showMessage(f"✅ {analysis_type.title()} elemzés befejezve")
            
            # UI elemek engedélyezése
            if hasattr(self, 'export_action'):
                self.export_action.setEnabled(True)
            
            # === 🎯 KRITIKUS: EREDMÉNY TOVÁBBÍTÁSA A MEGFELELŐ NÉZETEKNEK - DUPLA KONVERZIÓ JAVÍTVA! ===
            
            if analysis_type in ["single_city", "single_location"]:
                print("🎯 KRITIKUS: Single city/location analysis detected - DUPLA KONVERZIÓ JAVÍTVA!")
                
                # 🎯 KRITIKUS FIX: Az AnalysisWorker már Dict[List] formátumban adja vissza az eredményt!
                weather_data = result_data.get('result_data', {})
                print(f"🎯 DEBUG: Weather data type: {type(weather_data)}")
                print(f"🎯 DEBUG: Weather data keys: {list(weather_data.keys()) if isinstance(weather_data, dict) else 'NOT DICT'}")
                
                # ELLENŐRZÉS: Az AnalysisWorker eredménye már Dict[List] formátumban van
                if isinstance(weather_data, dict) and 'daily' in weather_data:
                    print("🎯 ✅ KRITIKUS: AnalysisWorker eredménye HELYES Dict[List] formátumban!")
                    print(f"🎯 DEBUG: Daily keys: {list(weather_data['daily'].keys())}")
                    
                    # Location adatok kinyerése
                    city_name = result_data.get('request_data', {}).get('location_name', 'Moscow')
                    location_data = {
                        'name': city_name,
                        'latitude': result_data.get('request_data', {}).get('latitude', 55.7558),
                        'longitude': result_data.get('request_data', {}).get('longitude', 37.6178)
                    }
                    
                    print(f"🎯 DEBUG: City: {city_name}")
                    print(f"🎯 DEBUG: Location data: {location_data}")
                    
                    # 🎯 KRITIKUS FIX: RESULTS PANEL FRISSÍTÉSE (KÖZVETLEN Dict[List] formátum)
                    if self.results_panel:
                        print("🎯 KRITIKUS: Updating ResultsPanel with DIRECT weather data...")
                        try:
                            self.results_panel.update_data(weather_data, city_name)
                            print("✅ KRITIKUS: ResultsPanel updated successfully!")
                        except Exception as e:
                            print(f"❌ KRITIKUS: ResultsPanel update error: {e}")
                            import traceback
                            traceback.print_exc()
                    
                    # 🎯 KRITIKUS FIX: ANALYTICS PANEL AUTOMATIKUS FRISSÍTÉSE (KÖZVETLEN Dict[List] formátum)
                    if self.analytics_panel:
                        print("🎯 KRITIKUS: Updating AnalyticsView with DIRECT weather data - DUPLA KONVERZIÓ JAVÍTVA!")
                        try:
                            # Location információ hozzáadása ha elérhető
                            if location_data:
                                self.analytics_panel.on_location_changed(location_data)
                            
                            # Weather data frissítése - KÖZVETLEN használat, NINCS konverzió!
                            self.analytics_panel.update_data(weather_data)
                            print("✅ KRITIKUS: AnalyticsView updated successfully - DUPLA KONVERZIÓ JAVÍTVA!")
                        except Exception as e:
                            print(f"❌ KRITIKUS: AnalyticsView update error: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"❌ KRITIKUS: AnalyticsView update skipped - analytics_panel: {self.analytics_panel is not None}")
                        
                else:
                    print("❌ KRITIKUS: Invalid weather data format - expected Dict[List] from AnalysisWorker")
                    print(f"❌ DEBUG: Received type: {type(weather_data)}")
                    if isinstance(weather_data, dict):
                        print(f"❌ DEBUG: Dict keys: {list(weather_data.keys())}")
            
            print(f"✅ DEBUG: Analysis completion handled: {analysis_type}")
            
        except Exception as e:
            print(f"⚠️ DEBUG: Analysis completion handling error: {e}")
            import traceback
            traceback.print_exc()
            self._show_error(f"Eredmény feldolgozási hiba: {e}")
    
    def _on_analysis_failed(self, error_message: str) -> None:
        """
        🔧 HOTFIX: Elemzés sikertelen befejezésének kezelése - HIÁNYZÓ METÓDUS HOZZÁADVA!
        
        Args:
            error_message: Hiba üzenet az elemzés sikertelenségéről
        """
        print(f"❌ DEBUG: _on_analysis_failed called: {error_message}")
        
        # Státusz frissítése
        self.status_bar.showMessage(f"❌ Elemzés sikertelen: {error_message}")
        
        # UI elemek visszaállítása alaphelyzetbe
        if hasattr(self, 'export_action'):
            self.export_action.setEnabled(False)
        
        # Hiba üzenet megjelenítése felhasználónak
        self._show_error(f"Elemzési hiba: {error_message}")
        
        print("✅ DEBUG: Analysis failure handled")
    
    def _on_analysis_cancelled(self) -> None:
        """🛠 Elemzés megszakítás kezelése - ÚJ SLOT METÓDUS."""
        print("🛠 DEBUG: _on_analysis_cancelled called")
        
        # Státusz frissítése
        self.status_bar.showMessage("🛠 Elemzés megszakítva")
        
        # UI elemek visszaállítása alaphelyzetbe
        if hasattr(self, 'export_action'):
            self.export_action.setEnabled(False)
        
        print("✅ DEBUG: Analysis cancellation handled")
    
    def _update_progress_clean(self, progress: int, message: str = "") -> None:
        """📊 Progress frissítése - CLEAN verzió."""
        if message:
            self.status_bar.showMessage(f"⏳ {message} ({progress}%)")
        else:
            self.status_bar.showMessage(f"⏳ Folyamatban: {progress}%")
        
        print(f"📊 DEBUG: Progress updated: {progress}% - {message}")
    
    # === 🌍 PROVIDER STATUS SLOT METÓDUSOK ===
    
    def _on_provider_selected(self, provider_name: str) -> None:
        """🌍 Provider kiválasztás kezelése Controller-től."""
        print(f"🌍 DEBUG: _on_provider_selected called: {provider_name}")
        
        # Provider tracking frissítése
        self.current_provider = provider_name
        
        # Status display frissítése
        self._update_provider_status_display()
        
        print(f"✅ DEBUG: Provider selection handled: {provider_name}")
    
    def _on_provider_usage_updated(self, usage_stats: Dict[str, Dict[str, Any]]) -> None:
        """🌍 Provider usage statistics frissítése Controller-től."""
        print(f"🌍 DEBUG: _on_provider_usage_updated called: {len(usage_stats)} providers")
        
        # Usage stats frissítése
        self.provider_usage_stats = usage_stats
        
        # Status display frissítése
        self._update_provider_status_display()
        
        print(f"✅ DEBUG: Provider usage updated")
    
    def _on_provider_warning(self, provider_name: str, usage_percent: int) -> None:
        """🌍 Provider warning kezelése Controller-től."""
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
        
        print(f"✅ DEBUG: Provider warning handled: {provider_name} {usage_percent}%")
    
    def _on_provider_fallback(self, from_provider: str, to_provider: str) -> None:
        """🌍 Provider fallback notification kezelése Controller-től."""
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
        
        print(f"✅ DEBUG: Provider fallback handled: {from_provider} → {to_provider}")
    
    def _initialize_provider_status(self) -> None:
        """🌍 Provider status inicializálása - Controller-től származó információkkal."""
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
            print(f"⚠️ DEBUG: Provider status initialization error: {e}")
            # Fallback to default values
            self.current_provider = "auto"
            self.provider_usage_stats = {}
            self._update_provider_status_display()
    
    def _update_provider_status_display(self) -> None:
        """🌍 Provider status display frissítése a status bar-ban."""
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
            print(f"⚠️ DEBUG: Provider status display update error: {e}")
    
    def _apply_warning_styling(self, warning_level: Optional[str]) -> None:
        """🌍 Warning level alapján styling alkalmazása status bar widget-ekre."""
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
    
    # === EGYSZERŰSÍTETT SLOT METÓDUSOK - BŐVÍTVE ===
    
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
    
    # === 🎨 TÉMA KEZELÉS BŐVÍTÉSEK ===
    
    # Signal definition for theme changes
    theme_changed = Signal(str)
    
    def _propagate_theme_change(self, theme_name: str) -> None:
        """🎨 Téma változás továbbítása - THEMEMANAGER AUTOMATIKUSAN KEZELI."""
        print("⚠️ DEBUG: _propagate_theme_change() DEPRECATED - ThemeManager handles automatically")
        
        # ThemeManager automatikusan kezeli az összes regisztrált widget-et
        # De a splitter-t külön kell frissíteni, mert az speciális
        dark_theme = (theme_name == "dark")
        self._update_splitter_theme(dark_theme)
        
        print(f"✅ DEBUG: Theme propagation complete via ThemeManager: {theme_name}")
    
    def _update_splitter_theme(self, dark_theme: bool) -> None:
        """🔧 SPLITTER téma frissítése theme váltáskor + THEMEMANAGER SZÍNEK."""
        print(f"🔧 DEBUG: Updating splitter theme with ThemeManager colors (dark: {dark_theme})")
        
        # Single City View splitter keresése és frissítése
        single_city_view = None
        if self.stacked_widget and self.stacked_widget.count() > 0:
            single_city_view = self.stacked_widget.widget(0)  # 🧹 Index 0 = Single City View
        
        if single_city_view:
            # Splitter megkeresése a view-ban
            splitters = single_city_view.findChildren(QSplitter)
            for splitter in splitters:
                # 🎨 THEMEMANAGER SPLITTER CSS ALKALMAZÁSA
                splitter_css = self.theme_manager.generate_css_for_class("splitter")
                splitter.setStyleSheet(splitter_css)
                
                print(f"✅ DEBUG: Splitter theme updated with ThemeManager CSS: {'dark' if dark_theme else 'light'}")
    
    # === BEÁLLÍTÁSOK KEZELÉS BŐVÍTVE ===
    
    def _save_settings(self) -> None:
        """Beállítások mentése + THEMEMANAGER + PROVIDER STATUS."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("current_view", self.current_view_name)
        self.settings.setValue("theme", self.current_theme.value)
        
        # 🎨 THEMEMANAGER BEÁLLÍTÁSOK MENTÉSE
        self.theme_manager.save_theme_preferences(self.settings)
        
        # 🌍 PROVIDER STATUS MENTÉSE
        self.settings.setValue("current_provider", self.current_provider)
    
    def _load_settings(self) -> None:
        """Beállítások betöltése - THEMEMANAGER INTEGRÁCIÓVAL + PROVIDER STATUS INICIALIZÁLÁS."""
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
        
        # 🌍 PROVIDER STATUS INICIALIZÁLÁSA
        self._initialize_provider_status()
        
        # Single City alapértelmezett nézet
        self._switch_view("single_city")
        print("🧹 DEBUG: Single City set as default view")
    
    # === MENÜ AKCIÓK ===
    
    def _export_data(self) -> None:
        """Adatok exportálása menüből."""
        weather_data = self.controller.get_current_weather_data()
        if not weather_data:
            self._show_error("Nincsenek exportálható adatok. Először kérdezzen le adatokat.")
            return
        
        print("📊 DEBUG: Export data requested")
    
    def _show_about(self) -> None:
        """Névjegy ablak megjelenítése."""
        about_text = f"""
        <h2>{AppInfo.NAME}</h2>
        <p><b>Verzió:</b> {AppInfo.VERSION} (THREAD CLEANUP FIX IMPLEMENTÁLVA)</p>
        <p><b>Leírás:</b> {AppInfo.DESCRIPTION}</p>
        <p><b>Architektúra:</b> Clean MVC + THREAD CLEANUP + WORKER LIFECYCLE MANAGEMENT</p>
        <p><b>Technológia:</b> PySide6, Python 3.8+</p>
        <p><b>Adatforrások:</b> Dual-API rendszer (Open-Meteo + Meteostat)</p>
        <hr>
        <p><i>🧹 <b>THREAD CLEANUP FIX IMPLEMENTÁLVA!</b></i></p>
        <p><i>🧹 ✅ Worker thread graceful shutdown sequence</i></p>
        <p><i>🧹 ✅ WebEngine cleanup és memory leak prevention</i></p>
        <p><i>🧹 ✅ Analysis worker proper termination</i></p>
        <p><i>🧹 ✅ QTimer cleanup és resource management</i></p>
        <p><i>🧹 ✅ Thread tracking és active worker monitoring</i></p>
        <p><i>🧹 ✅ Proper closeEvent() implementation</i></p>
        <p><i>🧹 ✅ No more "QThread: Destroyed while thread is still running"</i></p>
        <p><i>🧹 ✅ No more JavaScript bridge errors</i></p>
        <p><i>🧹 ✅ Clean application exit without crashes</i></p>
        """
        
        QMessageBox.about(self, "Névjegy", about_text)
    
    # === 🎨 TÉMA KEZELÉS - THEMEMANAGER INTEGRÁCIÓ ===
    
    def _apply_theme(self, theme_type: ThemeType) -> None:
        """THEMEMANAGER INTEGRÁLT téma alkalmazása."""
        print(f"🎨 DEBUG: Applying theme through ThemeManager: {theme_type.value}")
        
        # THEMEMANAGER TÉMA BEÁLLÍTÁSA
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
        """Belső téma alkalmazás - THEMEMANAGER-RE DELEGÁLVA."""
        print("⚠️ DEBUG: _apply_theme_internal() DEPRECATED - using ThemeManager instead")
        
        # ThemeManager-re delegálás
        self._apply_theme(theme_type)
    
    # === ERROR HANDLING ===
    
    def _show_error(self, message: str) -> None:
        """Hibaüzenet megjelenítése."""
        QMessageBox.critical(self, "Hiba", message)
    
    # === 🧹 KRITIKUS: THREAD CLEANUP IMPLEMENTATION ===
    
    def _register_thread(self, thread: QThread) -> None:
        """🧹 Thread regisztrálása tracking céljából."""
        if thread not in self.active_threads:
            self.active_threads.append(thread)
            print(f"🧹 DEBUG: Thread registered for tracking: {thread}")
    
    def _register_worker(self, worker) -> None:
        """🧹 Worker regisztrálása tracking céljából."""
        if worker not in self.active_workers:
            self.active_workers.append(worker)
            print(f"🧹 DEBUG: Worker registered for tracking: {worker}")
    
    def _register_web_view(self, web_view: QWebEngineView) -> None:
        """🧹 WebEngine view regisztrálása tracking céljából."""
        if web_view not in self.web_engine_views:
            self.web_engine_views.append(web_view)
            print(f"🧹 DEBUG: WebEngine view registered for tracking: {web_view}")
    
    def _register_timer(self, timer: QTimer) -> None:
        """🧹 QTimer regisztrálása tracking céljából."""
        if timer not in self.cleanup_timers:
            self.cleanup_timers.append(timer)
            print(f"🧹 DEBUG: Timer registered for tracking: {timer}")
    
    def _cleanup_all_threads(self) -> None:
        """🧹 KRITIKUS: Összes aktív thread graceful cleanup-ja."""
        print(f"🧹 DEBUG: Starting thread cleanup - {len(self.active_threads)} threads")
        
        for thread in self.active_threads[:]:  # Copy to avoid modification during iteration
            try:
                if thread.isRunning():
                    print(f"🧹 DEBUG: Stopping thread: {thread}")
                    
                    # Graceful shutdown request
                    thread.quit()
                    
                    # Wait for thread to finish (max 5 seconds)
                    if not thread.wait(5000):
                        print(f"⚠️ DEBUG: Thread did not finish gracefully, terminating: {thread}")
                        thread.terminate()
                        thread.wait(2000)  # Wait for termination
                    
                    # Clean up
                    thread.deleteLater()
                    print(f"✅ DEBUG: Thread cleaned up: {thread}")
                
                self.active_threads.remove(thread)
                
            except Exception as e:
                print(f"⚠️ DEBUG: Thread cleanup error: {e}")
                # Remove anyway to avoid infinite loops
                if thread in self.active_threads:
                    self.active_threads.remove(thread)
        
        print("✅ DEBUG: All threads cleaned up")
    
    def _cleanup_all_workers(self) -> None:
        """🧹 KRITIKUS: Összes aktív worker graceful cleanup-ja."""
        print(f"🧹 DEBUG: Starting worker cleanup - {len(self.active_workers)} workers")
        
        for worker in self.active_workers[:]:  # Copy to avoid modification during iteration
            try:
                print(f"🧹 DEBUG: Stopping worker: {worker}")
                
                # Stop worker if it has a stop method
                if hasattr(worker, 'stop'):
                    worker.stop()
                elif hasattr(worker, 'cancel'):
                    worker.cancel()
                elif hasattr(worker, 'quit'):
                    worker.quit()
                
                # If worker has a thread, clean it up
                if hasattr(worker, 'thread'):
                    thread = worker.thread()
                    if thread and thread.isRunning():
                        thread.quit()
                        thread.wait(3000)
                
                # Clean up worker
                worker.deleteLater()
                print(f"✅ DEBUG: Worker cleaned up: {worker}")
                
                self.active_workers.remove(worker)
                
            except Exception as e:
                print(f"⚠️ DEBUG: Worker cleanup error: {e}")
                # Remove anyway to avoid infinite loops
                if worker in self.active_workers:
                    self.active_workers.remove(worker)
        
        print("✅ DEBUG: All workers cleaned up")
    
    def _cleanup_all_web_engines(self) -> None:
        """🧹 KRITIKUS: Összes WebEngine view graceful cleanup-ja."""
        print(f"🧹 DEBUG: Starting WebEngine cleanup - {len(self.web_engine_views)} views")
        
        for web_view in self.web_engine_views[:]:  # Copy to avoid modification during iteration
            try:
                print(f"🧹 DEBUG: Stopping WebEngine view: {web_view}")
                
                # Stop loading and clear content
                web_view.stop()
                web_view.setUrl("")
                
                # Clean up
                web_view.deleteLater()
                print(f"✅ DEBUG: WebEngine view cleaned up: {web_view}")
                
                self.web_engine_views.remove(web_view)
                
            except Exception as e:
                print(f"⚠️ DEBUG: WebEngine cleanup error: {e}")
                # Remove anyway to avoid infinite loops
                if web_view in self.web_engine_views:
                    self.web_engine_views.remove(web_view)
        
        print("✅ DEBUG: All WebEngine views cleaned up")
    
    def _cleanup_all_timers(self) -> None:
        """🧹 KRITIKUS: Összes QTimer graceful cleanup-ja."""
        print(f"🧹 DEBUG: Starting timer cleanup - {len(self.cleanup_timers)} timers")
        
        for timer in self.cleanup_timers[:]:  # Copy to avoid modification during iteration
            try:
                print(f"🧹 DEBUG: Stopping timer: {timer}")
                
                # Stop timer
                if timer.isActive():
                    timer.stop()
                
                # Clean up
                timer.deleteLater()
                print(f"✅ DEBUG: Timer cleaned up: {timer}")
                
                self.cleanup_timers.remove(timer)
                
            except Exception as e:
                print(f"⚠️ DEBUG: Timer cleanup error: {e}")
                # Remove anyway to avoid infinite loops
                if timer in self.cleanup_timers:
                    self.cleanup_timers.remove(timer)
        
        print("✅ DEBUG: All timers cleaned up")
    
    # === 🧹 KRITIKUS: ENHANCED CLOSEEVENT WITH PROPER THREAD CLEANUP ===
    
    def closeEvent(self, event) -> None:
        """
        🧹 KRITIKUS FIX: Alkalmazás bezárásának kezelése - TELJES THREAD CLEANUP IMPLEMENTÁLVA!
        
        Ez a metódus megoldja a QThread cleanup problémát és megakadályozza az alkalmazás összeomlását.
        """
        try:
            print("🧹 KRITIKUS DEBUG: Enhanced MainWindow closeEvent called - THREAD CLEANUP FIX!")
            
            # === 1. FELHASZNÁLÓI MEGERŐSÍTÉS (OPCIONÁLIS) ===
            
            reply = QMessageBox.question(
                self, 
                "Kilépés megerősítése", 
                "Biztosan ki szeretne lépni az alkalmazásból?\n\nFutó elemzések megszakadnak.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                event.ignore()
                return
            
            # === 2. STÁTUSZ FRISSÍTÉS ===
            
            self.status_bar.showMessage("🧹 Alkalmazás leállítása - Thread cleanup...")
            
            # === 3. ANALYSIS WORKER LEÁLLÍTÁSA ===
            
            print("🧹 DEBUG: Stopping current analysis...")
            if hasattr(self.controller, 'stop_current_analysis'):
                self.controller.stop_current_analysis()
            
            # === 4. UI KOMPONENSEK LEÁLLÍTÁSA ===
            
            print("🧹 DEBUG: Stopping UI components...")
            
            # Analytics panel leállítása
            if self.analytics_panel:
                print("🧹 DEBUG: Stopping analytics panel...")
                if hasattr(self.analytics_panel, 'clear_data'):
                    self.analytics_panel.clear_data()
                if hasattr(self.analytics_panel, 'stop_all_operations'):
                    self.analytics_panel.stop_all_operations()
            
            # Trend analytics tab leállítása
            if self.trend_analytics_tab:
                print("🧹 DEBUG: Stopping trend analytics tab...")
                if hasattr(self.trend_analytics_tab, 'clear_data'):
                    self.trend_analytics_tab.clear_data()
                if hasattr(self.trend_analytics_tab, 'stop_all_operations'):
                    self.trend_analytics_tab.stop_all_operations()
            
            # Hungarian Map tab leállítása
            if self.hungarian_map_tab:
                print("🧹 DEBUG: Stopping hungarian map tab...")
                if hasattr(self.hungarian_map_tab, 'cleanup'):
                    self.hungarian_map_tab.cleanup()
            
            # Results panel leállítása
            if self.results_panel:
                print("🧹 DEBUG: Stopping results panel...")
                if hasattr(self.results_panel, 'cleanup'):
                    self.results_panel.cleanup()
            
            # Control panel leállítása
            if self.control_panel:
                print("🧹 DEBUG: Stopping control panel...")
                if hasattr(self.control_panel, 'cleanup'):
                    self.control_panel.cleanup()
            
            # === 5. 🧹 KRITIKUS: THREAD CLEANUP SEQUENCE ===
            
            print("🧹 KRITIKUS: Starting comprehensive thread cleanup sequence...")
            
            # WebEngine views cleanup (első helyen - JavaScript bridge problémák elkerülése)
            self._cleanup_all_web_engines()
            
            # Workers cleanup (második helyen - aktív műveletek leállítása)
            self._cleanup_all_workers()
            
            # Threads cleanup (harmadik helyen - thread resources felszabadítása)
            self._cleanup_all_threads()
            
            # Timers cleanup (negyedik helyen - timer resources felszabadítása)
            self._cleanup_all_timers()
            
            # === 6. CONTROLLER LEÁLLÍTÁSA ===
            
            print("🧹 DEBUG: Shutting down controller...")
            if hasattr(self.controller, 'shutdown'):
                self.controller.shutdown()
            
            # === 7. BEÁLLÍTÁSOK MENTÉSE ===
            
            print("🧹 DEBUG: Saving settings...")
            self._save_settings()
            
            # === 8. THEMEMANAGER CLEANUP ===
            
            print("🧹 DEBUG: ThemeManager cleanup...")
            if hasattr(self.theme_manager, 'cleanup'):
                self.theme_manager.cleanup()
            
            # === 9. FINAL CLEANUP ===
            
            print("🧹 DEBUG: Final cleanup...")
            
            # Clear all references
            self.active_threads.clear()
            self.active_workers.clear()
            self.web_engine_views.clear()
            self.cleanup_timers.clear()
            
            # === 10. EVENT ELFOGADÁSA ===
            
            print("✅ KRITIKUS: Thread cleanup sequence completed successfully!")
            print("✅ KRITIKUS: Application closing cleanly - NO THREAD LEAKS!")
            
            event.accept()
            
        except Exception as e:
            print(f"⚠️ KRITIKUS DEBUG: CloseEvent error: {e}")
            import traceback
            traceback.print_exc()
            
            # Emergency cleanup
            try:
                if hasattr(self.controller, 'shutdown'):
                    self.controller.shutdown()
            except:
                pass
            
            # Force accept to avoid infinite loops
            event.accept()
    
    # === PUBLIKUS API ===
    
    def get_current_view(self) -> str:
        """Jelenlegi nézet nevének lekérdezése."""
        return self.current_view_name
    
    def switch_to_view(self, view_name: str) -> None:
        """Programmatic nézet váltás."""
        self._switch_view(view_name)
    
    def get_analytics_panel(self) -> Optional[AnalyticsView]:
        """Analytics panel referencia lekérdezése."""
        return self.analytics_panel
    
    def focus_analytics_panel(self) -> None:
        """Analytics panel fókuszba helyezése."""
        self._switch_view("analytics")
    
    def get_available_views(self) -> list:
        """Elérhető nézetek listájának lekérdezése - 🗺️ 5 NÉZET VERZIÓ."""
        return ["single_city", "analytics", "trend_analysis", "map_view", "settings"]
    
    def get_map_view(self) -> Optional[MapView]:
        """🗺️ Map view referencia lekérdezése - ÚJ FUNKCIÓ."""
        return self.map_view
    
    def focus_map_view(self) -> None:
        """🗺️ Map view fókuszba helyezése - ÚJ FUNKCIÓ."""
        self._switch_view("map_view")
    
    def get_hungarian_map_tab(self) -> Optional[HungarianMapTab]:
        """🌤️ Hungarian Map Tab referencia lekérdezése - ÚJ FUNKCIÓ + MAGYAR MEGYÉK INTEGRÁCIÓJA."""
        return self.hungarian_map_tab
    
    def focus_hungarian_map_tab(self) -> None:
        """🌤️ Hungarian Map Tab fókuszba helyezése - ÚJ FUNKCIÓ + MAGYAR MEGYÉK INTEGRÁCIÓJA."""
        self._switch_view("map_view")
    
    def get_trend_analytics_tab(self) -> Optional[TrendAnalyticsTab]:
        """📈 Trend Analytics tab referencia lekérdezése - ÚJ FUNKCIÓ."""
        return self.trend_analytics_tab
    
    def focus_trend_analytics_tab(self) -> None:
        """📈 Trend Analytics tab fókuszba helyezése - ÚJ FUNKCIÓ."""
        self._switch_view("trend_analysis")
    
    def get_hungarian_counties_status(self) -> Dict[str, Any]:
        """
        🗺️ ÚJ: Magyar megyék betöltési státuszának lekérdezése.
        
        Returns:
            Státusz információk a magyar megyékről
        """
        return {
            'loaded': self.hungarian_counties_loaded,
            'counties_count': len(self.counties_geodataframe) if self.counties_geodataframe is not None else 0,
            'geodataframe_available': self.counties_geodataframe is not None,
            'integration_module_available': HUNGARIAN_COUNTIES_AVAILABLE
        }
    
    # === 🧹 ÚJ: THREAD TRACKING PUBLIKUS API ===
    
    def get_active_threads_count(self) -> int:
        """🧹 Aktív thread-ek számának lekérdezése."""
        return len(self.active_threads)
    
    def get_active_workers_count(self) -> int:
        """🧹 Aktív worker-ek számának lekérdezése."""
        return len(self.active_workers)
    
    def get_web_engine_views_count(self) -> int:
        """🧹 Aktív WebEngine view-k számának lekérdezése."""
        return len(self.web_engine_views)
    
    def get_cleanup_status(self) -> Dict[str, Any]:
        """🧹 Thread cleanup státusz információk lekérdezése."""
        return {
            'active_threads': len(self.active_threads),
            'active_workers': len(self.active_workers), 
            'web_engine_views': len(self.web_engine_views),
            'cleanup_timers': len(self.cleanup_timers),
            'cleanup_ready': (
                len(self.active_threads) == 0 and 
                len(self.active_workers) == 0 and 
                len(self.web_engine_views) == 0
            )
        }


# Export
__all__ = ['MainWindow']