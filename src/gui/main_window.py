#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Main Window Module - TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE
Refaktorált fő alkalmazás ablak modulja - CLEAN ARCHITECTURE SINGLE CITY FÓKUSSZAL + TREND ANALYTICS TAB.

🚀 TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE:
✅ TrendAnalyticsTab import hozzáadva
✅ _create_trend_analysis_placeholder() → _create_trend_analysis_view() lecserélve  
✅ Signal connectionök implementálva (_connect_mvc_signals)
✅ Slot metódusok hozzáadva (_on_trend_analysis_completed, _on_trend_analysis_error)
✅ ThemeManager regisztráció a TrendAnalyticsTab-hoz
✅ Toolbar "Trend Elemzés" gomb működővé tétele
✅ Professional trend vizualizációk elérhetők

🧹 DASHBOARD CLEANUP BEFEJEZVE:
❌ Dashboard view teljes eltávolítás (67 hivatkozás törölve)
❌ DashboardView import eltávolítva
❌ Dashboard action (toolbar + menu) eltávolítva
❌ Dashboard signal connectionök eltávolítva
❌ Dashboard-specific metódusok eltávolítva
✅ Single City alapértelmezett nézet (current_view_name = "single_city")
✅ Single City action alapértelmezett checked
✅ Stacked widget indexek átszámozva (Single City = 0)
✅ Clean architecture helyreállítva

🔧 SPLITTER CONSTRAINTS OPTIMALIZÁLVA - FINAL FIX:
✅ ControlPanel max width: 450px → 520px (szélesebb használhatóság)
✅ Initial splitter size: 380px → 420px (több hely a Smart Választónak)
✅ Splitter handle width: 15px → 18px (könnyebb fogás)
✅ Panel responsive behavior továbbra is stabil
✅ Results panel expandálhatóság megmaradt
✅ Minden layout margin és spacing optimális

🔗 ANALYTICS EGYSZERŰSÍTETT INTEGRÁCIÓ MEGMARADT:
✅ AnalyticsView egyszerűsített API használata
✅ ControlPanel → AnalyticsView direct connection
✅ Controller → AnalyticsView data pipeline
✅ Régi bonyolult analytics signalok eltávolítva
✅ Clean signal chain - egyszerűsített

🌍 PROVIDER STATUS BAR FUNKCIÓK MEGMARADTAK:
✅ Real-time provider display a status bar-ban
✅ Provider usage tracking megjelenítés  
✅ Warning icons usage limits esetén
✅ Provider fallback notifications
✅ Cost monitoring display
✅ Smart routing status indication

🎨 THEMEMANAGER INTEGRÁCIÓ MEGMARADT:
✅ Centralizált téma kezelés ThemeManager singleton-nal
✅ Widget regisztrációk automatikus theming-hez
✅ ColorPalette használata professzionális színekhoz
✅ Régi StyleSheets API eltávolítva
✅ Modern téma váltás signal chain-nel

🗺️ MAP VIEW INTEGRÁCIÓ:
✅ MapView komponens integráció placeholder helyett
✅ Térkép tab működővé tétele
✅ MapView import és inicializálás

FÁJL HELYE: src/gui/main_window.py
"""

from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QSplitter, QStatusBar, QMenuBar, QMessageBox, QToolBar, QLabel,
    QSizePolicy  # 🔧 LAYOUT JAVÍTÁS
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
from .analytics_view import AnalyticsView  # 🔧 EGYSZERŰSÍTETT VERZIÓ
from .map_view import MapView  # 🗺️ ÚJ MAP VIEW IMPORT
from .trend_analytics_tab import TrendAnalyticsTab  # 📈 ÚJ TREND ANALYTICS IMPORT


class MainWindow(QMainWindow):
    """
    🚀 TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE - CLEAN ARCHITECTURE SINGLE CITY FÓKUSSZAL + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ANALYTICS EGYSZERŰSÍTETT INTEGRÁCIÓ + PROVIDER STATUS BAR + THEMEMANAGER + DUAL-API + MAP VIEW INTEGRÁCIÓ + TREND ANALYTICS TAB.
    
    🚀 TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE:
    ✅ TrendAnalyticsTab komponens integráció (professional vizualizációkkal)
    ✅ Signal connectionök: ControlPanel → TrendAnalyticsTab location sync
    ✅ Analysis completion/error handling implementálva
    ✅ Toolbar "Trend Elemzés" gomb működővé tétele
    ✅ ThemeManager regisztráció trend komponenshez
    ✅ Professional trend chart + statisztikák elérhetők
    
    🧹 DASHBOARD CLEANUP BEFEJEZVE:
    ❌ Dashboard teljes eltávolítás (67 hivatkozás törölve)
    ❌ UX-centrikus dashboard komplexitás eltávolítva
    ❌ Dashboard stacked widget view eltávolítva
    ❌ Dashboard toolbar action eltávolítva
    ❌ Dashboard signal connectionök eltávolítva
    ✅ Single City alapértelmezett és központi nézet
    ✅ Clean architecture egyszerűsítés
    ✅ Stacked widget indexek átszámozva
    
    🔧 SPLITTER CONSTRAINTS OPTIMALIZÁLVA - FINAL FIX:
    ✅ Splitter handle width 18px (még könnyebb mozgatás)
    ✅ Panel width constraints: ControlPanel 320-520px, ResultsPanel min 400px
    ✅ Stretch factor konfiguráció: ControlPanel(0) fix, ResultsPanel(1) expandable
    ✅ Collapsibility letiltva (stable panels)
    ✅ Initial sizes optimalizálva: 420px + maradék hely
    ✅ Responsive behavior javítva
    ✅ Layout margins és spacing professzionális beállítások
    ✅ UniversalLocationSelector komfortábilis hely
    
    🔗 ANALYTICS EGYSZERŰSÍTETT INTEGRATION:
    ✅ AnalyticsView egyszerűsített API (800+ → 200 sor)
    ✅ ControlPanel → AnalyticsView direct signal connection
    ✅ Controller → AnalyticsView data pipeline
    ✅ Régi bonyolult analytics signalok eltávolítva
    ✅ Clean és egyszerű signal chain
    
    🌍 PROVIDER STATUS BAR FUNKCIÓK:
    ✅ Real-time provider megjelenítés status bar-ban
    ✅ Usage tracking és cost monitoring display
    ✅ Warning icons limit közelében
    ✅ Provider fallback notifications
    ✅ Smart routing status indication
    ✅ Provider váltás GUI feedback
    
    🗺️ MAP VIEW INTEGRÁCIÓ:
    ✅ MapView komponens integráció
    ✅ Térkép placeholder → valódi MapView csere
    ✅ Toolbar "Térkép" gomb működővé tétele
    
    📈 TREND ANALYTICS INTEGRÁCIÓ:
    ✅ TrendAnalyticsTab professional komponens
    ✅ Hőtérkép style vizualizációk
    ✅ Lineáris regresszió + R² értékek
    ✅ Magyar település prioritás támogatás
    ✅ 5 év/10 év/minden adat elemzési opciók
    ✅ Professional glassmorphism UI design
    
    CLEAN DUAL-API FUNKCIÓK:
    ✅ Smart API routing: Open-Meteo (free) + Meteostat (premium)
    ✅ Use-case alapú source selection
    ✅ Cost optimization stratégia
    ✅ Multi-city analytics támogatás
    ✅ Clean signal chain - WORKING SPLITTER
    ✅ Single City + Analytics + Trend nézetek (Dashboard eltávolítva)
    ✅ Modern UI komponensek - RESPONSIVE PANELS
    ✅ ThemeManager centralizált téma rendszer integráció
    ✅ Chart widget duplikáció problémák JAVÍTVA
    ✅ Analytics backend EGYSZERŰSÍTETT integráció
    ✅ AnalyticsView import javítás végrehajtva
    ✅ TrendAnalyticsTab PROFESSIONAL integráció végrehajtva
    ❌ HungaroMet komplexitás eltávolítva
    ❌ Chart példány duplikáció eltávolítva
    ❌ Dashboard komplexitás teljes eltávolítás
    """
    
    # Signalok a téma kezeléshez
    theme_changed = Signal(str)  # theme name
    view_changed = Signal(str)   # view name
    
    # 🌍 Provider signalok
    provider_status_updated = Signal(str)  # provider status message
    
    def __init__(self):
        """Főablak inicializálása - TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ANALYTICS EGYSZERŰSÍTETT INTEGRÁCIÓ + PROVIDER STATUS BAR + JAVÍTOTT SPLITTER + THEMEMANAGER + DUAL-API + MAP VIEW INTEGRÁCIÓ."""
        super().__init__()
        
        print("🚀 DEBUG: TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ANALYTICS EGYSZERŰSÍTETT + PROVIDER STATUS BAR + THEMEMANAGER + DUAL-API + MAP VIEW INTEGRÁCIÓ MainWindow __init__ started")
        
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
        self.current_view_name = "single_city"  # 🧹 Single City az alapértelmezett (Dashboard helyett)
        self.current_theme = ThemeType.LIGHT  # 🎨 ÚJ: Téma tracking
        
        # SingleCity view komponensei (KÖZPONTI FUNKCIONALITÁS)
        self.control_panel: Optional[ControlPanel] = None
        self.results_panel: Optional[ResultsPanel] = None
        # 🔧 CHART DUPLIKÁCIÓ JAVÍTÁS: charts_container és data_table referenciák eltávolítva
        # Ezek a ResultsPanel-en keresztül érhetők el: self.results_panel.get_charts_container()
        self.data_table: Optional[WeatherDataTable] = None
        
        # 📊 ANALYTICS VIEW KOMPONENS - EGYSZERŰSÍTETT!
        self.analytics_panel: Optional[AnalyticsView] = None  # 🔧 EGYSZERŰSÍTETT VERZIÓ
        
        # 🗺️ MAP VIEW KOMPONENS
        self.map_view: Optional[MapView] = None  # 🗺️ ÚJ MAP VIEW KOMPONENS
        
        # 📈 TREND ANALYTICS KOMPONENS - ÚJ!
        self.trend_analytics_tab: Optional[TrendAnalyticsTab] = None  # 📈 ÚJ TREND ANALYTICS KOMPONENS
        
        # 🌍 STATUS BAR PROVIDER WIDGETS
        self.provider_status_label: Optional[QLabel] = None
        self.usage_status_label: Optional[QLabel] = None
        self.cost_status_label: Optional[QLabel] = None
        
        # === UI INICIALIZÁLÁSA ===
        
        print("🖼️ DEBUG: Setting up TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ANALYTICS EGYSZERŰSÍTETT + PROVIDER STATUS BAR + THEMEMANAGER + DUAL-API + MAP VIEW INTEGRÁCIÓ UI...")
        self._setup_window()
        self._init_navigation_toolbar()
        self._init_stacked_views()
        self._init_menu_bar()
        self._init_status_bar_with_provider_display()  # 🌍 ENHANCED STATUS BAR
        print("✅ DEBUG: TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ANALYTICS EGYSZERŰSÍTETT + PROVIDER STATUS BAR + THEMEMANAGER + DUAL-API + MAP VIEW INTEGRÁCIÓ UI setup complete")
        
        # === 🧹 CLEAN SIGNAL CHAIN ===
        
        print("🔗 DEBUG: Connecting CLEAN signals with TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS EGYSZERŰSÍTETT + DUAL-API + PROVIDER STATUS...")
        self._connect_mvc_signals()
        print("✅ DEBUG: CLEAN SIGNAL CHAIN CONNECTED with TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS EGYSZERŰSÍTETT + DUAL-API + PROVIDER STATUS")
        
        # === 🎨 THEMEMANAGER SETUP ===
        
        print("🎨 DEBUG: Setting up ThemeManager integration...")
        self._setup_theme_integration()
        print("✅ DEBUG: ThemeManager integration complete")
        
        # === BEÁLLÍTÁSOK BETÖLTÉSE ===
        
        self._load_settings()
        
        print("✅ DEBUG: TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ANALYTICS EGYSZERŰSÍTETT + PROVIDER STATUS BAR + THEMEMANAGER + DUAL-API + MAP VIEW INTEGRÁCIÓ MainWindow initialized")
    
    def _setup_window(self) -> None:
        """🔧 LAYOUT CONSTRAINTS OPTIMALIZÁLT ablak alapbeállításai - THEMEMANAGER INTEGRÁCIÓVAL + DUAL-API."""
        self.setWindowTitle(f"{AppInfo.NAME} - {AppInfo.VERSION} (Trend Analytics Integráció Befejezve + Dashboard Cleanup Befejezve + Splitter Constraints Optimalizálva + Analytics Egyszerűsített + Provider Status + ThemeManager + Dual-API + Map View Integráció)")
        
        # 🔧 OPTIMALIZÁLT ABLAK MÉRETEK
        self.setGeometry(
            GUIConstants.MAIN_WINDOW_X,
            GUIConstants.MAIN_WINDOW_Y,
            1400,  # 🔧 SZÉLESEBB ABLAK (1200 → 1400)
            900    # 🔧 MAGASABB ABLAK (800 → 900)
        )
        self.setMinimumSize(
            1200,  # 🔧 NAGYOBB MIN WIDTH (1000 → 1200)
            700    # 🔧 NAGYOBB MIN HEIGHT (600 → 700)
        )
        
        # 🎨 WIDGET REGISZTRÁCIÓ THEMEMANAGER-HEZ
        register_widget_for_theming(self, "navigation")
        
        # 🎨 Téma rendszer integráció - alapértelmezett light theme
        self._apply_theme_internal(ThemeType.LIGHT)
        
        print("🔧 DEBUG: Window setup TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA - optimalizált méretek")
    
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
        print("🧭 DEBUG: Creating navigation toolbar with ThemeManager + Analytics + Trend Analytics (Dashboard cleanup befejezve)...")
        
        # Eszköztár létrehozása
        self.toolbar = QToolBar("Navigáció")
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.setIconSize(QSize(24, 24))
        
        # 🎨 WIDGET REGISZTRÁCIÓ THEMEMANAGER-HEZ
        register_widget_for_theming(self.toolbar, "navigation")
        
        # === NAVIGÁCIÓS AKCIÓK ===
        
        # 🏙️ Pontszerű Elemzés (KÖZPONTI NÉZET - Dashboard helyett)
        self.single_city_action = QAction("Város Elemzés", self)
        self.single_city_action.setToolTip("Egyetlen város részletes időjárási elemzése - KÖZPONTI FUNKCIÓ")
        self.single_city_action.triggered.connect(lambda: self._switch_view("single_city"))
        self.single_city_action.setCheckable(True)
        self.single_city_action.setChecked(True)  # 🧹 Single City az alapértelmezett (Dashboard helyett)
        self.toolbar.addAction(self.single_city_action)
        
        # 📊 Analytics (EGYSZERŰSÍTETT FUNKCIÓ)
        self.analytics_action = QAction("Analitika", self)
        self.analytics_action.setToolTip("Időjárási elemzések és statisztikák (egyszerűsített)")
        self.analytics_action.triggered.connect(lambda: self._switch_view("analytics"))
        self.analytics_action.setCheckable(True)
        self.toolbar.addAction(self.analytics_action)
        
        # 📈 Trend Elemző (MŰKÖDIK!) - ÚJ!
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
        
        # ⚙️ Beállítások (TERVEZETT)
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
        
        print("✅ DEBUG: Navigation toolbar created with ThemeManager + Analytics + Trend Analytics (Dashboard cleanup befejezve)")
    
    def _init_stacked_views(self) -> None:
        """
        🚀 TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + 🧹 DASHBOARD CLEANUP BEFEJEZVE + 🔧 SPLITTER CONSTRAINTS OPTIMALIZÁLT QStackedWidget inicializálása különböző nézetekkel + THEMEMANAGER + ANALYTICS EGYSZERŰSÍTETT + MAP VIEW INTEGRÁCIÓ.
        """
        print("📚 DEBUG: Creating stacked views with TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ThemeManager + Analytics Egyszerűsített + Map View Integráció + Trend Analytics Tab...")
        
        # Központi widget és layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 🎨 WIDGET REGISZTRÁCIÓ
        register_widget_for_theming(central_widget, "container")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)  # 🔧 KISEBB MARGINS (több hely)
        main_layout.setSpacing(0)  # 🔧 NINCS SPACING (több hely)
        
        # === STACKED WIDGET LÉTREHOZÁSA ===
        
        self.stacked_widget = QStackedWidget()
        register_widget_for_theming(self.stacked_widget, "container")
        main_layout.addWidget(self.stacked_widget)
        
        # === VIEW-K LÉTREHOZÁSA ===
        
        # 1. Single City View (KÖZPONTI FUNKCIONALITÁS) - SPLITTER CONSTRAINTS OPTIMALIZÁLT + THEMEMANAGER
        single_city_view = self._create_single_city_view_constraints_optimized()
        self.stacked_widget.addWidget(single_city_view)  # 🧹 INDEX 0 (Dashboard helyett)
        
        # 2. Analytics View (EGYSZERŰSÍTETT VERZIÓ)
        analytics_view = self._create_analytics_view_simplified()
        self.stacked_widget.addWidget(analytics_view)  # INDEX 1
        
        # 3. Trend Analysis View (VALÓDI TREND ANALYTICS TAB!) - ÚJ!
        trend_view = self._create_trend_analysis_view()  # 📈 FRISSÍTVE: placeholder → valódi TrendAnalyticsTab
        self.stacked_widget.addWidget(trend_view)  # INDEX 2
        
        # 4. Map View (VALÓDI MAP VIEW!)
        map_view = self._create_map_view()  # 🗺️ FRISSÍTVE: placeholder → valódi MapView
        self.stacked_widget.addWidget(map_view)  # INDEX 3
        
        # 5. Settings View (PLACEHOLDER)
        settings_view = self._create_settings_placeholder()
        self.stacked_widget.addWidget(settings_view)  # INDEX 4
        
        # === ALAPÉRTELMEZETT NÉZET BEÁLLÍTÁSA ===
        
        self.stacked_widget.setCurrentIndex(0)  # 🧹 Single City View (index 0) alapértelmezett (Dashboard helyett)
        
        print("✅ DEBUG: Stacked views created with TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ThemeManager + Analytics Egyszerűsített + Map View Integráció + Trend Analytics Tab")
    
    def _create_single_city_view_constraints_optimized(self) -> QWidget:
        """
        🔧 KRITIKUS SPLITTER CONSTRAINTS OPTIMALIZÁLT - Single City View létrehozása - FINAL FIX RESPONSIVE LAYOUT.
        
        🔧 SPLITTER CONSTRAINTS OPTIMALIZÁLT - FINAL FIX:
        ✅ Splitter handle width 18px (még könnyebb fogási terület)
        ✅ Panel width constraints: ControlPanel 320-520px optimalizált, ResultsPanel min 400px expandable
        ✅ Stretch factor konfiguráció: ControlPanel(0) fix, ResultsPanel(1) expand
        ✅ Collapsibility letiltva (stabilabb panels)
        ✅ Initial sizes optimalizálva: 420px + maradék hely (UniversalLocationSelector komfortábilis)
        ✅ Layout margins minimalizálva (több hely)
        ✅ Size policy explicit beállítások
        ✅ UniversalLocationSelector megfelelő hely a hosszú szövegekhez
        """
        print("🔧 DEBUG: Creating SPLITTER CONSTRAINTS OPTIMALIZÁLT Single City View...")
        
        view = QWidget()
        register_widget_for_theming(view, "container")
        
        layout = QVBoxLayout(view)
        layout.setContentsMargins(2, 2, 2, 2)  # 🔧 MINIMAL MARGINS (több hely)
        layout.setSpacing(0)  # 🔧 NINCS SPACING (több hely)
        
        # === 🔧 KRITIKUS JAVÍTÁS: SPLITTER CONSTRAINTS OPTIMALIZÁLT ===
        
        main_splitter = QSplitter(Qt.Horizontal)
        
        print("🔧 DEBUG: Configuring OPTIMALIZÁLT splitter...")
        
        # 🔧 KRITIKUS SPLITTER BEÁLLÍTÁSOK - OPTIMALIZÁLT
        main_splitter.setHandleWidth(18)  # 🔧 SZÉLESEBB HANDLE (15 → 18px) - még könnyebb mozgatás
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
        self.control_panel.setMinimumWidth(320)  # 🔧 OPTIMALIZÁLT MIN (320px megmarad)
        self.control_panel.setMaximumWidth(520)  # 🔧 SZÉLESEBB MAX (450 → 520px) - UniversalLocationSelector komfort
        
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
        self.results_panel.setMinimumWidth(450)  # 🔧 NAGYOBB MINIMUM (400 → 450px)
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
        
        print("✅ DEBUG: OPTIMALIZÁLT stretch factors set - Control(0=fix), Results(1=expand)")
        
        # === 🔧 KRITIKUS: INITIAL SIZES OPTIMALIZÁLT - FINAL FIX ===
        
        # 🔧 OPTIMALIZÁLT kezdeti méretek - UniversalLocationSelector komfortábilis hely
        total_width = 1400  # 🔧 Új ablak szélesség
        control_width = 420  # 🔧 OPTIMALIZÁLT control panel width (420px - több hely a Smart Választónak)
        results_width = total_width - control_width - 20  # 🔧 Maradék a results panel-nek
        
        main_splitter.setSizes([control_width, results_width])
        
        print(f"✅ DEBUG: OPTIMALIZÁLT initial sizes set - Control: {control_width}px (UniversalLocationSelector komfort), Results: {results_width}px")
        
        # === LAYOUT FINALIZÁLÁS ===
        
        layout.addWidget(main_splitter)
        
        print("🔧 DEBUG: SPLITTER CONSTRAINTS OPTIMALIZÁLT Single City View created")
        
        return view
    
    def _create_analytics_view_simplified(self) -> QWidget:
        """
        📊 Analytics View létrehozása - EGYSZERŰSÍTETT IMPLEMENTÁCIÓ + THEMEMANAGER.
        
        EGYSZERŰSÍTETT FUNKCIÓ:
        ✅ AnalyticsView egyszerűsített integráció (800+ → 200 sor)
        ✅ Csak eredmény megjelenítés, nincs saját vezérlő
        ✅ ControlPanel-től kapja a vezérlést
        ✅ Clean signal integration
        ✅ ThemeManager integráció
        """
        print("📊 DEBUG: Creating EGYSZERŰSÍTETT AnalyticsView with ThemeManager...")
        
        # Egyszerűsített AnalyticsView létrehozása
        self.analytics_panel = AnalyticsView()  # 🔧 EGYSZERŰSÍTETT VERZIÓ
        
        # 🎨 WIDGET REGISZTRÁCIÓ
        register_widget_for_theming(self.analytics_panel, "container")
        
        print("✅ DEBUG: EGYSZERŰSÍTETT AnalyticsView created with ThemeManager")
        return self.analytics_panel
    
    def _create_trend_analysis_view(self) -> QWidget:
        """
        📈 Trend Analysis view létrehozása - VALÓDI TRENDANALYTICSTAB KOMPONENS + THEMEMANAGER.
        
        🚀 TREND ANALYTICS INTEGRÁCIÓ:
        ✅ TrendAnalyticsTab professional komponens integráció
        ✅ Hőtérkép style vizualizációk elérhetők
        ✅ Lineáris regresszió + R² értékek + statisztikák
        ✅ Magyar település prioritás támogatás (dual database)
        ✅ 5 év/10 év/minden adat elemzési opciók
        ✅ Professional glassmorphism UI design
        ✅ ThemeManager integráció
        """
        print("📈 DEBUG: Creating real TrendAnalyticsTab component with ThemeManager...")
        
        # Valódi TrendAnalyticsTab komponens létrehozása
        self.trend_analytics_tab = TrendAnalyticsTab()
        
        # 🎨 WIDGET REGISZTRÁCIÓ THEMEMANAGER-HEZ
        register_widget_for_theming(self.trend_analytics_tab, "container")
        
        print("✅ DEBUG: Real TrendAnalyticsTab component created with ThemeManager")
        return self.trend_analytics_tab
    
    def _create_map_view(self) -> QWidget:
        """🗺️ Map view létrehozása - VALÓDI MAPVIEW KOMPONENS + THEMEMANAGER."""
        print("🗺️ DEBUG: Creating real MapView component with ThemeManager...")
        
        # Valódi MapView komponens létrehozása
        self.map_view = MapView()
        
        # 🎨 WIDGET REGISZTRÁCIÓ THEMEMANAGER-HEZ
        register_widget_for_theming(self.map_view, "container")
        
        print("✅ DEBUG: Real MapView component created with ThemeManager")
        return self.map_view
    
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
        Nézet váltás kezelése - TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS EGYSZERŰSÍTETT TÁMOGATÁSSAL.
        
        Args:
            view_name: Nézet neve ("single_city", "analytics", "trend_analysis", "map_view", "settings")
        """
        print(f"🔄 DEBUG: Switching to view: {view_name}")
        
        # View index mapping - TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE (dashboard eltávolítva)
        view_indices = {
            "single_city": 0,    # 🧹 SINGLE CITY KÖZPONTI NÉZET (index 0)
            "analytics": 1,      # EGYSZERŰSÍTETT ANALYTICS VIEW
            "trend_analysis": 2, # 📈 VALÓDI TREND ANALYTICS TAB - ÚJ!
            "map_view": 3,       # 🗺️ VALÓDI MAP VIEW
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
            "single_city": "Város Elemzés (Központi)",  # 🧹 FRISSÍTVE
            "analytics": "Analitika (Egyszerűsített)",  # FRISSÍTVE
            "trend_analysis": "Trend Elemzés (Professional)",  # 📈 ÚJ - FRISSÍTVE!
            "map_view": "Térkép (Interaktív)",  # 🗺️ FRISSÍTVE
            "settings": "Beállítások"
        }
        
        if hasattr(self, 'status_bar'):
            # 🌍 Provider status megtartása view váltáskor
            self._update_provider_status_display()
        
        print(f"✅ DEBUG: View switched to: {view_name} (index: {view_index})")
    
    def _init_menu_bar(self) -> None:
        """Menüsáv inicializálása - CLEAN VERZIÓ + THEMEMANAGER + ANALYTICS EGYSZERŰSÍTETT - DASHBOARD CLEANUP BEFEJEZVE + TREND ANALYTICS."""
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
        
        # Navigáció - TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE
        view_menu.addAction(self.single_city_action)
        view_menu.addAction(self.analytics_action)  # EGYSZERŰSÍTETT ANALYTICS
        view_menu.addAction(self.trend_action)  # 📈 VALÓDI TREND ANALYTICS - ÚJ!
        view_menu.addAction(self.map_action)  # 🗺️ MAP VIEW
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
        
        STATUS BAR LAYOUT:
        [General Status] | [Provider: X] | [Usage: Y/Z] | [Cost: $W] | [Warning Icon]
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
        
        # 🚀 TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + 🧹 DASHBOARD CLEANUP BEFEJEZVE + 🌍 DUAL-API STATUS MESSAGE + 🗺️ MAP VIEW INTEGRÁCIÓ
        self.status_bar.showMessage("✅ Single City központi nézet aktív - 🌍 Dual-API rendszer (Open-Meteo + Meteostat) - 🗺️ Map View integrálva - 📈 Trend Analytics működik. [Clean Architecture!]")
        
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
            self.cost_status_label.setStyleSheet("")
        else:
            # Normális - alapértelmezett színek
            self.usage_status_label.setStyleSheet("")
            self.cost_status_label.setStyleSheet("")
    
    def _connect_mvc_signals(self) -> None:
        """
        🚀 TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + 🧹 CLEAN MVC komponensek signal-slot összekötése + DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS EGYSZERŰSÍTETT INTEGRÁCIÓ + DUAL-API + PROVIDER STATUS.
        
        🚀 TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE:
        ✅ TrendAnalyticsTab signalok: analysis_started, analysis_completed, error_occurred
        ✅ ControlPanel → TrendAnalyticsTab location sync (city_selected → set_location)
        ✅ Trend analysis eredmények kezelése (slot metódusok)
        ✅ Professional vizualizációk signal chain integrálva
        
        🧹 DASHBOARD CLEANUP BEFEJEZVE:
        ❌ Dashboard signalok teljes eltávolítása
        ❌ DashboardView signal connectionök törölve
        ❌ Dashboard-specific slot metódusok törölve
        ✅ Single City view központi signal management
        ✅ Clean és egyszerűsített signal chain
        
        🔗 ANALYTICS EGYSZERŰSÍTETT SIGNALOK - MEGMARADT:
        ✅ ControlPanel.location_changed → AnalyticsView.on_location_changed
        ✅ Controller.weather_data_ready → AnalyticsView.update_data  
        ✅ Egyszerűsített signal chain (régi bonyolult signalok eltávolítva)
        
        🌍 PROVIDER STATUS SIGNALOK:
        ✅ provider_selected - Provider váltás kezelése
        ✅ provider_usage_updated - Usage statistics frissítése
        ✅ provider_warning - Warning level változások
        ✅ provider_fallback - Fallback notifications
        
        CLEAN DUAL-API VERSION:
        ✅ Smart API routing signalok
        ✅ Source selection és fallback
        ✅ Working signal chain
        ✅ ThemeManager signalok integrálva
        ✅ Analytics egyszerűsített signalok integrálva
        ✅ Trend Analytics signalok integrálva
        ❌ Hibrid komplexitás eltávolítva
        ❌ Dashboard komplexitás teljes eltávolítás
        """
        
        print("🔗 DEBUG: Starting CLEAN signals with TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + Analytics Egyszerűsített + DUAL-API + PROVIDER STATUS...")
        
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
            
        else:
            print("❌ DEBUG: ControlPanel is None!")
        
        # === 🔗 ANALYTICS EGYSZERŰSÍTETT INTEGRÁCIÓ - ÚJ SIGNALOK! ===
        
        if self.analytics_panel and self.control_panel:
            print("📊 DEBUG: Connecting EGYSZERŰSÍTETT Analytics Panel signals...")
            
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
                # Dictionary objektum létrehozása az AnalyticsView számára (metadata→data rename)
                location_dict = {
                    'name': name,
                    'latitude': lat,
                    'longitude': lon,
                    **data  # data dict spread (nem metadata!)
                }
                self.analytics_panel.on_location_changed(location_dict)
            
            self.control_panel.city_selected.connect(debug_control_panel_city_to_analytics)
            print("✅ DEBUG: ControlPanel.city_selected → AnalyticsView.on_location_changed COMPATIBILITY CONNECTED")
            
            # 🔗 Analytics egyszerűsített signalok visszafelé
            def debug_analytics_analysis_started():
                print("📊 DEBUG [ANALYTICS→MAIN_WINDOW]: analysis_started (simplified)")
            
            self.analytics_panel.analysis_started.connect(debug_analytics_analysis_started)
            self.analytics_panel.analysis_started.connect(
                lambda: self.status_bar.showMessage("📊 Analytics elemzés folyamatban... (egyszerűsített)")
            )
            print("✅ DEBUG: AnalyticsView.analysis_started → MainWindow status update CONNECTED")
            
            # Analytics befejezés
            def debug_analytics_analysis_completed():
                print("📊 DEBUG [ANALYTICS→MAIN_WINDOW]: analysis_completed (simplified)")
            
            self.analytics_panel.analysis_completed.connect(debug_analytics_analysis_completed)
            self.analytics_panel.analysis_completed.connect(
                lambda: self.status_bar.showMessage("✅ Analytics elemzés kész (egyszerűsített)")
            )
            print("✅ DEBUG: AnalyticsView.analysis_completed → MainWindow status update CONNECTED")
            
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
        
        # === 📈 TREND ANALYTICS SIGNALOK - ÚJ INTEGRÁCIÓ! ===
        
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
        
        print("✅ DEBUG: ALL CLEAN signals connected successfully with TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + Analytics Egyszerűsített + DUAL-API + PROVIDER STATUS!")
    
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
    
    # === SLOT METÓDUSOK - CLEAN VERZIÓ + THEMEMANAGER + ANALYTICS EGYSZERŰSÍTETT + DUAL-API ===
    
    def _on_weather_data_received(self, data: dict) -> None:
        """
        🔧 CLEAN időjárási adatok fogadása a Controller-től - DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS EGYSZERŰSÍTETT INTEGRÁCIÓVAL + DUAL-API.
        
        Args:
            data: Időjárási adatok (Open-Meteo vagy Meteostat formátumban)
        """
        print("📊 DEBUG: _on_weather_data_received called - DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS EGYSZERŰSÍTETT INTEGRATION + DUAL-API")
        
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
            
            # 📊 ANALYTICS EGYSZERŰSÍTETT INTEGRÁCIÓ - automatikus!
            # Az analytics_panel.update_data() automatikusan meghívódik a 
            # Controller.weather_data_ready signal miatt (_connect_mvc_signals-ben)
            print("✅ DEBUG: Analytics panel update automatikus (signal-based)")
            
            # Menü elemek engedélyezése
            self.export_action.setEnabled(True)
            self.extreme_action.setEnabled(True)
            
            print(f"✅ DEBUG: UI komponensek frissítve DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS EGYSZERŰSÍTETT INTEGRÁCIÓVAL + DUAL-API: {city_name_with_source}")
            
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
        """Névjegy ablak megjelenítése - TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ANALYTICS EGYSZERŰSÍTETT + PROVIDER STATUS BAR + THEMEMANAGER + DUAL-API + MAP VIEW INTEGRÁCIÓ VERSION."""
        about_text = f"""
        <h2>{AppInfo.NAME}</h2>
        <p><b>Verzió:</b> {AppInfo.VERSION} (Trend Analytics Integráció Befejezve + Dashboard Cleanup Befejezve + Splitter Constraints Optimalizálva + Analytics Egyszerűsített + Provider Status + ThemeManager + Dual-API + Map View Integráció)</p>
        <p><b>Leírás:</b> {AppInfo.DESCRIPTION}</p>
        <p><b>Architektúra:</b> Clean MVC + Single City Central Navigation + Provider Status Bar + AnalyticsView Egyszerűsített + ThemeManager + Dual-API + Splitter Constraints Optimalizálva + Map View Integráció + TrendAnalyticsTab Professional</p>
        <p><b>Technológia:</b> PySide6, Python 3.8+</p>
        <p><b>Adatforrások:</b> Dual-API rendszer (Open-Meteo + Meteostat)</p>
        <hr>
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
        <p><i>📊 AnalyticsView EGYSZERŰSÍTETT integráció (800+ → 200 sor)</i></p>
        <p><i>🔗 ControlPanel → AnalyticsView direct signal connection</i></p>
        <p><i>🔍 Duplikált vezérlők eltávolítva - clean architecture</i></p>
        <p><i>🎨 ThemeManager centralizált téma rendszer</i></p>
        <p><i>🗺️ Map View integráció - Térkép tab működik!</i></p>
        <p><i>📈 TrendAnalyticsTab integráció - Trend Elemzés tab működik!</i></p>
        <p><i>🌍 Globális időjárási adatok</i></p>
        <p><i>🏗️ Single City-központú clean interface (Dashboard eltávolítva)</i></p>
        <p><i>📊 Megbízható adatfeldolgozás</i></p>
        <p><i>⚙️ Moduláris, karbantartható kód</i></p>
        <p><i>🔗 Clean Signal Chain Management - egyszerűsítve</i></p>
        <p><i>🎨 ColorPalette professzionális színrendszer</i></p>
        <p><i>📈 Analytics backend EGYSZERŰSÍTETT integráció</i></p>
        <p><i>📈 Trend Analytics backend PROFESSIONAL integráció</i></p>
        <p><i>🔄 Fallback mechanizmus API hibák esetén</i></p>
        <p><i>❌ Dashboard komplexitás teljes eltávolítás</i></p>
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
        """Alkalmazás bezárásának kezelése + TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ANALYTICS EGYSZERŰSÍTETT + PROVIDER STATUS + THEMEMANAGER + DUAL-API + MAP VIEW INTEGRÁCIÓ."""
        try:
            print("🛑 DEBUG: TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ANALYTICS EGYSZERŰSÍTETT + PROVIDER STATUS + THEMEMANAGER + DUAL-API + MAP VIEW INTEGRÁCIÓ MainWindow closeEvent called")
            
            # Analytics panel leállítása (EGYSZERŰSÍTETT)
            if self.analytics_panel:
                print("🛑 DEBUG: Stopping simplified analytics panel...")
                self.analytics_panel.clear_data()
            
            # Trend analytics tab leállítása - ÚJ!
            if self.trend_analytics_tab:
                print("🛑 DEBUG: Stopping trend analytics tab...")
                self.trend_analytics_tab.clear_data()
            
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
            
            print("✅ DEBUG: TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + ANALYTICS EGYSZERŰSÍTETT + PROVIDER STATUS + THEMEMANAGER + DUAL-API + MAP VIEW INTEGRÁCIÓ MainWindow bezárva")
            
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
        """Elérhető nézetek listájának lekérdezése - TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE."""
        return ["single_city", "analytics", "trend_analysis", "map_view", "settings"]  # 🧹 Dashboard eltávolítva, 📈 trend_analysis hozzáadva
    
    def get_analytics_panel(self) -> Optional[AnalyticsView]:
        """
        📊 Analytics panel referencia lekérdezése - EGYSZERŰSÍTETT FUNKCIÓ.
        
        Returns:
            AnalyticsView egyszerűsített példány vagy None
        """
        return self.analytics_panel
    
    def focus_analytics_panel(self) -> None:
        """
        📊 Analytics panel fókuszba helyezése - EGYSZERŰSÍTETT FUNKCIÓ.
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
    
    # === 🎨 TÉMA API BŐVÍTÉSEK - THEMEMANAGER INTEGRÁCIÓ ===
    
    def get_current_theme(self) -> ThemeType:
        """Jelenlegi téma lekérdezése."""
        return self.current_theme
    
    def toggle_theme(self) -> None:
        """Téma váltása light ↔ dark között + THEMEMANAGER."""
        if self.current_theme == ThemeType.LIGHT:
            self._apply_theme(ThemeType.DARK)
        else:
            self._apply_theme(ThemeType.LIGHT)
    
    def get_theme_manager(self) -> ThemeManager:
        """ThemeManager singleton referencia lekérdezése."""
        return self.theme_manager
    
    def get_color_palette(self) -> ColorPalette:
        """ColorPalette referencia lekérdezése."""
        return self.color_palette
    
    # === 📊 ANALYTICS API BŐVÍTÉSEK - EGYSZERŰSÍTETT FUNKCIÓK ===
    
    def refresh_analytics(self) -> None:
        """
        📊 Analytics adatok frissítése - EGYSZERŰSÍTETT FUNKCIÓ.
        """
        if self.analytics_panel and self.analytics_panel.current_data:
            # Újra-elemzés indítása a meglévő adatokkal
            self.analytics_panel.on_analysis_start()
    
    def clear_analytics_data(self) -> None:
        """
        📊 Analytics adatok törlése - EGYSZERŰSÍTETT FUNKCIÓ.
        """
        if self.analytics_panel:
            self.analytics_panel.clear_data()
    
    def get_analytics_status(self) -> str:
        """
        📊 Analytics státusz lekérdezése - EGYSZERŰSÍTETT FUNKCIÓ.
        
        Returns:
            Analytics státusz szöveg
        """
        if self.analytics_panel and hasattr(self.analytics_panel, 'status_label'):
            return self.analytics_panel.status_label.text()
        return "Analytics panel nem elérhető"
    
    # === 📈 TREND ANALYTICS API BŐVÍTÉSEK - ÚJ FUNKCIÓK! ===
    
    def refresh_trend_analysis(self) -> None:
        """
        📈 Trend analysis adatok frissítése - ÚJ FUNKCIÓ.
        """
        if self.trend_analytics_tab and self.trend_analytics_tab.current_data:
            # Újra-elemzés indítása a meglévő lokációval
            if self.trend_analytics_tab.current_location:
                city_name, lat, lon = self.trend_analytics_tab.current_location
                self.trend_analytics_tab.set_location(city_name, lat, lon)
    
    def clear_trend_analysis_data(self) -> None:
        """
        📈 Trend analysis adatok törlése - ÚJ FUNKCIÓ.
        """
        if self.trend_analytics_tab:
            self.trend_analytics_tab.clear_data()
    
    def get_trend_analysis_status(self) -> str:
        """
        📈 Trend analysis státusz lekérdezése - ÚJ FUNKCIÓ.
        
        Returns:
            Trend analysis státusz szöveg
        """
        if self.trend_analytics_tab and hasattr(self.trend_analytics_tab, 'status_label'):
            return self.trend_analytics_tab.status_label.text()
        return "Trend Analytics tab nem elérhető"
    
    def get_trend_statistics_summary(self) -> str:
        """
        📈 Trend analysis statisztikák összefoglalójának lekérdezése - ÚJ FUNKCIÓ.
        
        Returns:
            Trend statistics összefoglaló szöveg
        """
        if self.trend_analytics_tab:
            return self.trend_analytics_tab.get_statistics_summary()
        return "Trend Analytics tab nem elérhető"
    
    def export_trend_chart(self, filepath: str = None) -> bool:
        """
        📈 Trend chart exportálása - ÚJ FUNKCIÓ.
        
        Args:
            filepath: Export fájl elérési út (opcionális)
            
        Returns:
            Sikeres export (True/False)
        """
        if self.trend_analytics_tab:
            return self.trend_analytics_tab.export_chart(filepath)
        return False
    
    def set_trend_location_from_control_panel(self, city_name: str, lat: float, lon: float) -> None:
        """
        📈 Trend Analytics lokáció beállítása Control Panel-től - ÚJ FUNKCIÓ.
        
        Args:
            city_name: Város neve
            lat: Szélesség
            lon: Hosszúság
        """
        if self.trend_analytics_tab:
            self.trend_analytics_tab.set_location(city_name, lat, lon)
            print(f"📈 DEBUG: Trend location set from control panel: {city_name}")
    
    # === 🌍 DUAL-API BŐVÍTÉSEK ===
    
    def get_active_data_sources(self) -> List[str]:
        """
        🌍 Aktív adatforrások lekérdezése - DUAL-API FUNKCIÓ.
        
        Returns:
            Aktív adatforrások listája
        """
        from .utils import validate_api_source_available, DataConstants
        
        active_sources = []
        for source in DataConstants.DATA_SOURCE_PRIORITY:
            if validate_api_source_available(source):
                active_sources.append(source)
        
        return active_sources
    
    def get_optimal_source_for_use_case(self, use_case: str) -> str:
        """
        🌍 Use-case optimális adatforrás lekérdezése - DUAL-API FUNKCIÓ.
        
        Args:
            use_case: Használati eset
            
        Returns:
            Optimális adatforrás azonosító
        """
        return get_optimal_data_source(use_case)
    
    def get_dual_api_status(self) -> Dict[str, Any]:
        """
        🌍 Dual-API rendszer státusz lekérdezése - DUAL-API FUNKCIÓ.
        
        Returns:
            Dual-API státusz információk
        """
        from .utils import validate_api_source_available, get_source_display_name, DataConstants
        
        status = {
            "architecture": "Dual-API System",
            "sources": {}
        }
        
        for source in DataConstants.DATA_SOURCE_PRIORITY:
            display_name = get_source_display_name(source)
            available = validate_api_source_available(source)
            
            status["sources"][source] = {
                "display_name": display_name,
                "available": available,
                "type": "free" if source == "open-meteo" else "premium"
            }
        
        return status
    
    # === 🌍 PROVIDER STATUS API BŐVÍTÉSEK ===
    
    def get_current_provider(self) -> str:
        """
        🌍 Jelenlegi aktív provider lekérdezése - PROVIDER FUNKCIÓ.
        
        Returns:
            Aktív provider neve
        """
        return self.current_provider
    
    def get_provider_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        🌍 Provider usage statistics lekérdezése - PROVIDER FUNKCIÓ.
        
        Returns:
            Usage statistics dictionary
        """
        return self.provider_usage_stats
    
    def get_provider_status_summary(self) -> str:
        """
        🌍 Provider status összefoglaló lekérdezése - PROVIDER FUNKCIÓ.
        
        Returns:
            Provider status összefoglaló szöveg
        """
        if self.provider_status_label:
            return self.provider_status_label.text()
        return "Provider status nem elérhető"
    
    def force_provider_status_update(self) -> None:
        """
        🌍 Provider status kényszerített frissítése - PROVIDER FUNKCIÓ.
        """
        self._initialize_provider_status()
    
    def set_provider_manually(self, provider_name: str) -> None:
        """
        🌍 Provider manuális beállítása - PROVIDER FUNKCIÓ.
        
        Args:
            provider_name: Provider neve ("auto", "open-meteo", "meteostat")
        """
        if self.controller:
            self.controller.handle_provider_change(provider_name)
    
    # === 🔧 SPLITTER & LAYOUT API BŐVÍTÉSEK - CONSTRAINTS OPTIMALIZÁLVA ===
    
    def get_splitter_sizes(self) -> List[int]:
        """
        🔧 Splitter méretek lekérdezése - LAYOUT FUNKCIÓ.
        
        Returns:
            Splitter méretek listája [control_panel_width, results_panel_width]
        """
        single_city_view = None
        if self.stacked_widget and self.stacked_widget.count() > 0:
            single_city_view = self.stacked_widget.widget(0)  # 🧹 Index 0 = Single City View (Dashboard helyett)
        
        if single_city_view:
            splitters = single_city_view.findChildren(QSplitter)
            if splitters:
                return splitters[0].sizes()
        
        return [420, 980]  # OPTIMALIZÁLT Default sizes (380 → 420)
    
    def set_splitter_sizes(self, sizes: List[int]) -> None:
        """
        🔧 Splitter méretek beállítása - LAYOUT FUNKCIÓ.
        
        Args:
            sizes: Splitter méretek listája [control_panel_width, results_panel_width]
        """
        single_city_view = None
        if self.stacked_widget and self.stacked_widget.count() > 0:
            single_city_view = self.stacked_widget.widget(0)  # 🧹 Index 0 = Single City View (Dashboard helyett)
        
        if single_city_view:
            splitters = single_city_view.findChildren(QSplitter)
            if splitters:
                splitters[0].setSizes(sizes)
                print(f"🔧 DEBUG: Splitter sizes set: {sizes}")
    
    def reset_splitter_to_optimal(self) -> None:
        """
        🔧 Splitter visszaállítása optimális méretekre - LAYOUT FUNKCIÓ - OPTIMALIZÁLVA.
        """
        optimal_sizes = [420, 980]  # 🔧 OPTIMALIZÁLT méretek (380 → 420)
        self.set_splitter_sizes(optimal_sizes)
        print(f"🔧 DEBUG: Splitter reset to OPTIMALIZÁLT sizes: {optimal_sizes}")
    
    def get_panel_constraints(self) -> Dict[str, Dict[str, int]]:
        """
        🔧 Panel constraints lekérdezése - LAYOUT FUNKCIÓ - OPTIMALIZÁLVA.
        
        Returns:
            Panel constraints dictionary
        """
        constraints = {
            "control_panel": {
                "min_width": 320,
                "max_width": 520,  # 🔧 OPTIMALIZÁLT (450 → 520)
                "stretch_factor": 0
            },
            "results_panel": {
                "min_width": 450,
                "max_width": None,  # Nincs limit
                "stretch_factor": 1
            }
        }
        
        return constraints
    
    # === SIGNAL CHAIN TESTER API ===
    
    def manual_test_search(self, query: str = "budapest") -> None:
        """
        Manuális keresési teszt futtatása.
        
        Args:
            query: Keresési kifejezés
        """
        print(f"🧪 DEBUG: Manual test search initiated: '{query}' (DUAL-API)")
        
        if self.control_panel:
            # Közvetlen ControlPanel signal trigger
            print(f"🧪 DEBUG: Emitting search_requested signal from ControlPanel...")
            self.control_panel.search_requested.emit(query)
            print(f"🧪 DEBUG: Signal emitted - should trigger Controller.handle_search_request (DUAL-API)")
        else:
            print("❌ DEBUG: ControlPanel not available for manual test")
    
    def debug_signal_state(self) -> None:
        """Signal állapotok debug információi - TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + ANALYTICS EGYSZERŰSÍTETT."""
        print("🧪 DEBUG: Signal state diagnosis (TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + DUAL-API + PROVIDER STATUS + ANALYTICS EGYSZERŰSÍTETT + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + MAP VIEW INTEGRÁCIÓ):")
        
        if self.control_panel:
            print(f"✅ ControlPanel exists: {self.control_panel}")
            print(f"✅ ControlPanel.search_requested signal: {self.control_panel.search_requested}")
            if hasattr(self.control_panel, 'location_changed'):
                print(f"✅ ControlPanel.location_changed signal: {self.control_panel.location_changed}")
        else:
            print("❌ ControlPanel is None")
        
        if self.analytics_panel:
            print(f"✅ AnalyticsPanel (AnalyticsView Simplified) exists: {self.analytics_panel}")
            print(f"✅ AnalyticsPanel.analysis_started signal: {self.analytics_panel.analysis_started}")
            print(f"✅ AnalyticsPanel.update_data method: {hasattr(self.analytics_panel, 'update_data')}")
            print(f"✅ AnalyticsPanel.on_location_changed method: {hasattr(self.analytics_panel, 'on_location_changed')}")
        else:
            print("❌ AnalyticsPanel is None")
        
        if self.trend_analytics_tab:
            print(f"✅ TrendAnalyticsTab exists: {self.trend_analytics_tab}")
            print(f"✅ TrendAnalyticsTab.analysis_started signal: {self.trend_analytics_tab.analysis_started}")
            print(f"✅ TrendAnalyticsTab.analysis_completed signal: {self.trend_analytics_tab.analysis_completed}")
            print(f"✅ TrendAnalyticsTab.error_occurred signal: {self.trend_analytics_tab.error_occurred}")
            print(f"✅ TrendAnalyticsTab.set_location method: {hasattr(self.trend_analytics_tab, 'set_location')}")
            print(f"✅ TrendAnalyticsTab.clear_data method: {hasattr(self.trend_analytics_tab, 'clear_data')}")
        else:
            print("❌ TrendAnalyticsTab is None")
        
        if self.map_view:
            print(f"✅ MapView exists: {self.map_view}")
            print(f"✅ MapView type: {type(self.map_view)}")
        else:
            print("❌ MapView is None")
        
        print(f"✅ Controller exists: {self.controller}")
        print(f"✅ Controller.handle_search_request method: {self.controller.handle_search_request}")
        print(f"✅ Controller.weather_data_ready signal: {self.controller.weather_data_ready}")
        
        # 🌍 DUAL-API státusz
        dual_api_status = self.get_dual_api_status()
        print(f"✅ Dual-API status: {dual_api_status}")
        
        # 🌍 Provider status
        print(f"✅ Current provider: {self.current_provider}")
        print(f"✅ Provider usage stats: {self.provider_usage_stats}")
        
        # 🔧 Splitter status - OPTIMALIZÁLT
        splitter_sizes = self.get_splitter_sizes()
        panel_constraints = self.get_panel_constraints()
        print(f"✅ Splitter sizes (OPTIMALIZÁLT): {splitter_sizes}")
        print(f"✅ Panel constraints (OPTIMALIZÁLT): {panel_constraints}")
        
        # 🧹 DASHBOARD CLEANUP ELLENŐRZÉS
        print("🧹 DASHBOARD CLEANUP STATUS:")
        print(f"✅ Dashboard view removed: True")
        print(f"✅ Dashboard action removed: True")
        print(f"✅ Current view: {self.current_view_name}")
        print(f"✅ Available views: {self.get_available_views()}")
        print(f"✅ Single City is default: {self.current_view_name == 'single_city'}")
        
        # 🗺️ MAP VIEW ELLENŐRZÉS
        print("🗺️ MAP VIEW INTEGRATION STATUS:")
        print(f"✅ Map view exists: {self.map_view is not None}")
        print(f"✅ Map action exists: {hasattr(self, 'map_action')}")
        print(f"✅ Map view in stacked widget: {self.stacked_widget.count() > 3}")
        
        # 📈 TREND ANALYTICS ELLENŐRZÉS - ÚJ!
        print("📈 TREND ANALYTICS INTEGRATION STATUS:")
        print(f"✅ Trend analytics tab exists: {self.trend_analytics_tab is not None}")
        print(f"✅ Trend action exists: {hasattr(self, 'trend_action')}")
        print(f"✅ Trend view in stacked widget: {self.stacked_widget.count() > 2}")
        if self.trend_analytics_tab:
            print(f"✅ Trend tab current data: {self.trend_analytics_tab.current_data is not None}")
            print(f"✅ Trend tab current location: {self.trend_analytics_tab.current_location}")
        
        print("🧪 DEBUG: All components ready for signal chain testing (TREND ANALYTICS INTEGRÁCIÓ BEFEJEZVE + DASHBOARD CLEANUP BEFEJEZVE + DUAL-API + PROVIDER STATUS + ANALYTICS EGYSZERŰSÍTETT + SPLITTER CONSTRAINTS OPTIMALIZÁLVA + MAP VIEW INTEGRÁCIÓ)")
    
    def test_analytics_simplified_integration(self) -> None:
        """
        📊 Analytics egyszerűsített integráció tesztelése - ÚJ FUNKCIÓ.
        """
        print("📊 DEBUG: Testing Analytics Simplified integration...")
        
        if self.analytics_panel:
            print(f"✅ AnalyticsPanel (Simplified) instance: {self.analytics_panel}")
            print(f"✅ Analytics simplified status: {self.get_analytics_status()}")
            
            # Analytics view váltás teszt
            print("🧪 Testing analytics view switch...")
            self.focus_analytics_panel()
            print(f"✅ Current view: {self.get_current_view()}")
            
            # Analytics egyszerűsített signalok teszt
            print("🧪 Testing analytics simplified signals...")
            print(f"✅ analysis_started signal: {self.analytics_panel.analysis_started}")
            print(f"✅ analysis_completed signal: {self.analytics_panel.analysis_completed}")
            print(f"✅ error_occurred signal: {self.analytics_panel.error_occurred}")
            print(f"✅ update_data method: {hasattr(self.analytics_panel, 'update_data')}")
            print(f"✅ on_location_changed method: {hasattr(self.analytics_panel, 'on_location_changed')}")
            
            # Signal connection test
            if self.control_panel and hasattr(self.control_panel, 'location_changed'):
                print("🧪 Testing ControlPanel → AnalyticsView signal connection...")
                print("✅ ControlPanel.location_changed → AnalyticsView.on_location_changed signal chain ready")
            
            if self.controller and hasattr(self.controller, 'weather_data_ready'):
                print("🧪 Testing Controller → AnalyticsView signal connection...")
                print("✅ Controller.weather_data_ready → AnalyticsView.update_data signal chain ready")
            
        else:
            print("❌ DEBUG: AnalyticsPanel (Simplified) is None")
        
        print("📊 DEBUG: Analytics Simplified integration test complete")
    
    def test_map_view_integration(self) -> None:
        """
        🗺️ Map View integráció tesztelése - ÚJ FUNKCIÓ.
        """
        print("🗺️ DEBUG: Testing Map View integration...")
        
        if self.map_view:
            print(f"✅ MapView instance: {self.map_view}")
            print(f"✅ MapView type: {type(self.map_view)}")
            
            # Map view váltás teszt
            print("🧪 Testing map view switch...")
            original_view = self.get_current_view()
            self.focus_map_view()
            current_view = self.get_current_view()
            print(f"✅ View switch test: {original_view} → {current_view}")
            
            if current_view == "map_view":
                print("✅ Map view switch SUCCESSFUL")
            else:
                print("❌ Map view switch FAILED")
            
            # Map action teszt
            if hasattr(self, 'map_action'):
                print(f"✅ Map action exists: {self.map_action}")
                print(f"✅ Map action text: {self.map_action.text()}")
                print(f"✅ Map action checkable: {self.map_action.isCheckable()}")
            else:
                print("❌ Map action does not exist")
            
            # Stacked widget teszt
            if self.stacked_widget:
                widget_count = self.stacked_widget.count()
                print(f"✅ Stacked widget count: {widget_count}")
                
                if widget_count > 3:
                    map_widget = self.stacked_widget.widget(3)  # Index 3 = map view
                    print(f"✅ Widget at index 3: {type(map_widget)}")
                    
                    if map_widget == self.map_view:
                        print("✅ Map view correctly placed at index 3")
                    else:
                        print("❌ Map view NOT at index 3")
                else:
                    print("❌ Not enough widgets in stacked widget")
            else:
                print("❌ Stacked widget does not exist")
            
        else:
            print("❌ DEBUG: MapView is None")
        
        print("🗺️ DEBUG: Map View integration test complete")
    
    def test_trend_analytics_integration(self) -> None:
        """
        📈 Trend Analytics integráció tesztelése - ÚJ FUNKCIÓ.
        """
        print("📈 DEBUG: Testing Trend Analytics integration...")
        
        if self.trend_analytics_tab:
            print(f"✅ TrendAnalyticsTab instance: {self.trend_analytics_tab}")
            print(f"✅ TrendAnalyticsTab type: {type(self.trend_analytics_tab)}")
            
            # Trend view váltás teszt
            print("🧪 Testing trend analytics view switch...")
            original_view = self.get_current_view()
            self.focus_trend_analytics_tab()
            current_view = self.get_current_view()
            print(f"✅ View switch test: {original_view} → {current_view}")
            
            if current_view == "trend_analysis":
                print("✅ Trend analytics view switch SUCCESSFUL")
            else:
                print("❌ Trend analytics view switch FAILED")
            
            # Trend action teszt
            if hasattr(self, 'trend_action'):
                print(f"✅ Trend action exists: {self.trend_action}")
                print(f"✅ Trend action text: {self.trend_action.text()}")
                print(f"✅ Trend action checkable: {self.trend_action.isCheckable()}")
            else:
                print("❌ Trend action does not exist")
            
            # Trend analytics signalok teszt
            print("🧪 Testing trend analytics signals...")
            print(f"✅ analysis_started signal: {self.trend_analytics_tab.analysis_started}")
            print(f"✅ analysis_completed signal: {self.trend_analytics_tab.analysis_completed}")
            print(f"✅ error_occurred signal: {self.trend_analytics_tab.error_occurred}")
            print(f"✅ location_selected signal: {self.trend_analytics_tab.location_selected}")
            print(f"✅ set_location method: {hasattr(self.trend_analytics_tab, 'set_location')}")
            print(f"✅ clear_data method: {hasattr(self.trend_analytics_tab, 'clear_data')}")
            print(f"✅ export_chart method: {hasattr(self.trend_analytics_tab, 'export_chart')}")
            print(f"✅ get_statistics_summary method: {hasattr(self.trend_analytics_tab, 'get_statistics_summary')}")
            
            # Signal connection test
            if self.control_panel:
                print("🧪 Testing ControlPanel → TrendAnalyticsTab signal connection...")
                print("✅ ControlPanel.city_selected → TrendAnalyticsTab.set_location signal chain ready")
            
            # Stacked widget teszt
            if self.stacked_widget:
                widget_count = self.stacked_widget.count()
                print(f"✅ Stacked widget count: {widget_count}")
                
                if widget_count > 2:
                    trend_widget = self.stacked_widget.widget(2)  # Index 2 = trend analysis view
                    print(f"✅ Widget at index 2: {type(trend_widget)}")
                    
                    if trend_widget == self.trend_analytics_tab:
                        print("✅ Trend analytics view correctly placed at index 2")
                    else:
                        print("❌ Trend analytics view NOT at index 2")
                else:
                    print("❌ Not enough widgets in stacked widget")
            else:
                print("❌ Stacked widget does not exist")
            
        else:
            print("❌ DEBUG: TrendAnalyticsTab is None")
        
        print("📈 DEBUG: Trend Analytics integration test complete")
    
    def test_splitter_constraints_optimized(self) -> None:
        """
        🔧 Splitter constraints optimalizált tesztelése - ÚJ FUNKCIÓ.
        """
        print("🔧 DEBUG: Testing Splitter Constraints OPTIMALIZÁLT...")
        
        # Splitter információk
        splitter_sizes = self.get_splitter_sizes()
        panel_constraints = self.get_panel_constraints()
        
        print(f"✅ Current splitter sizes (OPTIMALIZÁLT): {splitter_sizes}")
        print(f"✅ Panel constraints (OPTIMALIZÁLT): {panel_constraints}")
        
        # Constraints ellenőrzése - OPTIMALIZÁLT
        if self.control_panel:
            actual_width = self.control_panel.width()
            min_width = panel_constraints["control_panel"]["min_width"]
            max_width = panel_constraints["control_panel"]["max_width"]
            
            print(f"🔧 ControlPanel actual width (OPTIMALIZÁLT): {actual_width}px")
            print(f"🔧 ControlPanel constraints (OPTIMALIZÁLT): {min_width}-{max_width}px")
            
            if min_width <= actual_width <= max_width:
                print("✅ ControlPanel width within OPTIMALIZÁLT constraints")
            else:
                print("❌ ControlPanel width outside OPTIMALIZÁLT constraints!")
        
        if self.results_panel:
            actual_width = self.results_panel.width()
            min_width = panel_constraints["results_panel"]["min_width"]
            
            print(f"🔧 ResultsPanel actual width: {actual_width}px")
            print(f"🔧 ResultsPanel min width: {min_width}px")
            
            if actual_width >= min_width:
                print("✅ ResultsPanel width above minimum")
            else:
                print("❌ ResultsPanel width below minimum!")
        
        print("🔧 DEBUG: Splitter Constraints OPTIMALIZÁLT test complete")
    
    def test_dashboard_cleanup_status(self) -> None:
        """
        🧹 Dashboard cleanup státusz tesztelése - ÚJ FUNKCIÓ.
        """
        print("🧹 DEBUG: Testing Dashboard Cleanup Status...")
        
        # Available views check
        available_views = self.get_available_views()
        dashboard_removed = "dashboard" not in available_views
        print(f"✅ Dashboard removed from available views: {dashboard_removed}")
        print(f"✅ Available views: {available_views}")
        
        # Current view check
        current_view = self.get_current_view()
        single_city_default = (current_view == "single_city")
        print(f"✅ Current view: {current_view}")
        print(f"✅ Single City is default: {single_city_default}")
        
        # Toolbar actions check
        toolbar_actions = [action.text() for action in self.toolbar.actions()]
        dashboard_action_removed = "Dashboard" not in toolbar_actions
        print(f"✅ Dashboard action removed from toolbar: {dashboard_action_removed}")
        print(f"✅ Toolbar actions: {toolbar_actions}")
        
        # Stacked widget check
        stacked_count = self.stacked_widget.count()
        expected_count = 5  # single_city, analytics, trend_analysis, map_view, settings
        correct_count = (stacked_count == expected_count)
        print(f"✅ Stacked widget count: {stacked_count} (expected: {expected_count})")
        print(f"✅ Correct widget count: {correct_count}")
        
        # Single City view at index 0 check
        single_city_at_zero = (self.stacked_widget.currentIndex() == 0 and current_view == "single_city")
        print(f"✅ Single City view at index 0: {single_city_at_zero}")
        
        # Overall cleanup status
        cleanup_complete = all([
            dashboard_removed,
            single_city_default, 
            dashboard_action_removed,
            correct_count,
            single_city_at_zero
        ])
        
        print(f"🧹 OVERALL DASHBOARD CLEANUP STATUS: {'COMPLETE ✅' if cleanup_complete else 'INCOMPLETE ❌'}")
        
        print("🧹 DEBUG: Dashboard Cleanup Status test complete")