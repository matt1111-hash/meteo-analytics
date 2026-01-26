#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Main Window
🧹 Clean Architecture Refactor - Modular Design

FÁJL: src/presentation/gui/windows/main_window.py
"""

from typing import Optional, Dict, Any
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter,
    QStatusBar, QToolBar, QLabel, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QSettings, Signal, QSize, QThread, QTimer
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWebEngineWidgets import QWebEngineView

from ...config import AppInfo
from ..utils import GUIConstants, ThemeType
from ..theme_manager import get_theme_manager, register_widget_for_theming
from ..color_palette import ColorPalette
from ..app_controller import AppController
from ..control_panel import ControlPanel
from ..results_panel import ResultsPanel
from ..dialogs import ExtremeWeatherDialog
from ..analytics_view import AnalyticsView
from ..trend_analytics import TrendAnalyticsTab
from ..hungarian_map_tab import HungarianMapTab

from .main_window_state import MainWindowState
from .menu_builder import create_menu_bar
from .toolbar_manager import create_navigation_toolbar
from .window_layout import (
    setup_window,
    create_stacked_views,
    create_status_bar_provider_widgets,
)
from .main_window_actions import (
    switch_view,
    handle_analytics_view_query,
    handle_multi_city_weather_request,
    map_query_type_to_parameter,
    handle_export_request,
    show_extreme_weather,
    show_about,
    show_error,
    register_thread,
    register_worker,
    register_web_view,
    register_timer,
    cleanup_all_threads,
    cleanup_all_workers,
    cleanup_all_web_engines,
    cleanup_all_timers,
)


class MainWindow(QMainWindow):
    """
    🪟 Főablak - Clean Architecture Refactor.

    SIGNALOK:
    - theme_changed: Téma változás
    """

    theme_changed = Signal(str)

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
        """Főablak inicializálása."""
        super().__init__()

        # Állapotkezelés
        self.state = MainWindowState()

        # QSettings
        self.settings = QSettings("Weather Analytics", AppInfo.NAME)

        # ThemeManager
        self.theme_manager = get_theme_manager()
        self.color_palette = ColorPalette()

        # Controller
        self.controller = AppController()
        self.worker_manager = self.controller.worker_manager

        # === UI INICIALIZÁLÁSA ===

        setup_window(self)
        self._init_navigation_toolbar()
        self.stacked_widget = create_stacked_views(self)
        create_menu_bar(self)

        # Status bar
        self.status_bar = self.statusBar()
        self.provider_status_label, self.usage_status_label, self.cost_status_label = \
            create_status_bar_provider_widgets(self)
        self.status_bar.addPermanentWidget(self.provider_status_label)
        self.status_bar.addPermanentWidget(self.usage_status_label)
        self.status_bar.addPermanentWidget(self.cost_status_label)

        # === SIGNAL CHAIN ÖSSZEKÖTÉSE ===

        self._connect_mvc_signals()

        # === THEMEMANAGER SETUP ===

        self.theme_manager.theme_changed.connect(self._on_theme_manager_changed)
        register_widget_for_theming(self, "navigation")
        self._apply_theme_internal(ThemeType.LIGHT)

        # === MAGYAR MEGYÉK BETÖLTÉSE ===

        self._load_hungarian_counties()

        # === BEÁLLÍTÁSOK BETÖLTÉSE ===

        self._load_settings()

    def _init_navigation_toolbar(self) -> None:
        """Navigációs eszköztár létrehozása."""
        self.toolbar = create_navigation_toolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

    def _load_hungarian_counties(self) -> None:
        """🗺️ Magyar megyék automatikus betöltése."""
        try:
            from ...analytics.hungarian_counties_integration import HungarianCountiesLoader

            counties_loader = HungarianCountiesLoader()
            self.state.hungarian_counties.geodataframe = counties_loader.load_counties_geodataframe()

            if self.state.hungarian_counties.geodataframe is not None:
                self.state.hungarian_counties.loaded = True

                # Automatikus konfiguráció ha a HungarianMapTab létezik
                if self.hungarian_map_tab and hasattr(self.hungarian_map_tab, 'map_visualizer'):
                    map_visualizer = self.hungarian_map_tab.map_visualizer
                    if hasattr(map_visualizer, 'set_counties_geodataframe'):
                        map_visualizer.set_counties_geodataframe(self.state.hungarian_counties.geodataframe)

        except ImportError:
            self.state.hungarian_counties.loaded = False
            self.state.hungarian_counties.geodataframe = None

    def _connect_mvc_signals(self) -> None:
        """MVC signal összekötések."""
        # Controller signalok
        if hasattr(self.controller, 'analysis_started'):
            self.controller.analysis_started.connect(self._on_analysis_started)

        if hasattr(self.controller, 'analysis_completed'):
            self.controller.analysis_completed.connect(self._on_analysis_completed)

        if hasattr(self.controller, 'analysis_failed'):
            self.controller.analysis_failed.connect(self._on_analysis_failed)

        if hasattr(self.controller, 'analysis_cancelled'):
            self.controller.analysis_cancelled.connect(self._on_analysis_cancelled)

        # ControlPanel signalok
        if hasattr(self.control_panel, 'provider_selected'):
            self.control_panel.provider_selected.connect(self._on_provider_selected)

        if hasattr(self.control_panel, 'provider_usage_updated'):
            self.control_panel.provider_usage_updated.connect(self._on_provider_usage_updated)

        if hasattr(self.control_panel, 'provider_warning'):
            self.control_panel.provider_warning.connect(self._on_provider_warning)

        if hasattr(self.control_panel, 'provider_fallback'):
            self.control_panel.provider_fallback.connect(self._on_provider_fallback)

        # ResultsPanel signalok
        if hasattr(self.results_panel, 'export_requested'):
            self.results_panel.export_requested.connect(self._handle_export_request)

        if hasattr(self.results_panel, 'extreme_weather_requested'):
            self.results_panel.extreme_weather_requested.connect(self._show_extreme_weather)

        # AnalyticsView signalok
        if hasattr(self.analytics_panel, 'query_requested'):
            self.analytics_panel.query_requested.connect(self._handle_analytics_view_query)

    # === PROVIDER STATUS KEZELÉS ===

    def _on_provider_selected(self, provider_name: str) -> None:
        """Provider választás kezelése."""
        self.state.provider.current_provider = provider_name
        self._update_provider_status_display()

    def _on_provider_usage_updated(self, usage_stats: Dict[str, Dict[str, Any]]) -> None:
        """Provider használat frissítése."""
        self.state.provider.provider_usage_stats = usage_stats
        self.state.update_provider_warning()
        self._update_provider_status_display()

    def _on_provider_warning(self, provider_name: str, usage_percent: int) -> None:
        """Provider warning kezelése."""
        self._update_provider_status_display()

    def _on_provider_fallback(self, from_provider: str, to_provider: str) -> None:
        """Provider fallback kezelése."""
        self.status_bar.showMessage(f"⚠️ Provider fallback: {from_provider} → {to_provider}")

    def _initialize_provider_status(self) -> None:
        """Provider státusz inicializálása."""
        self.state.provider.current_provider = self.settings.value("current_provider", "auto")
        self._update_provider_status_display()

    def _update_provider_status_display(self) -> None:
        """Provider státusz kijelző frissítése."""
        if self.provider_status_label:
            self.provider_status_label.setText(f"Provider: {self.state.provider.current_provider}")

        if self.usage_status_label and self.state.provider.provider_usage_stats:
            usage = self.state.provider.provider_usage_stats.get(self.state.provider.current_provider, {})
            daily = usage.get('daily_requests', 0)
            self.usage_status_label.setText(f"Használat: {daily}/1000")

    # === ANALYSIS SIGNAL HANDLERS ===

    def _on_analysis_started(self, analysis_type: str) -> None:
        """Elemzés kezdete."""
        self.status_bar.showMessage(f"🔄 {analysis_type} elemzés indítása...")

    def _on_analysis_completed(self, result_data: Dict[str, Any]) -> None:
        """Elemzés befejezve."""
        self.status_bar.showMessage("✅ Elemzés befejezve")
        if hasattr(self.results_panel, 'update_results'):
            self.results_panel.update_results(result_data)

    def _on_analysis_failed(self, error_message: str) -> None:
        """Elemzés hiba."""
        self.status_bar.showMessage(f"❌ Elemzés hiba: {error_message}")
        show_error(self, error_message)

    def _on_analysis_cancelled(self) -> None:
        """Elemzés megszakítva."""
        self.status_bar.showMessage("⚠️ Elemzés megszakítva")

    # === THEME HANDLERS ===

    def _on_theme_manager_changed(self, theme_name: str) -> None:
        """ThemeManager téma változás kezelése."""
        try:
            self.state.current_theme = ThemeType(theme_name)
        except ValueError:
            self.state.current_theme = ThemeType.LIGHT

        # Splitter frissítése
        if self.stacked_widget and self.stacked_widget.count() > 0:
            single_city_view = self.stacked_widget.widget(0)
            if single_city_view:
                splitters = single_city_view.findChildren(QSplitter)
                for splitter in splitters:
                    splitter_css = self.theme_manager.generate_css_for_class("splitter")
                    splitter.setStyleSheet(splitter_css)

    def _apply_theme(self, theme_type: ThemeType) -> None:
        """Téma alkalmazása."""
        self.theme_manager.set_theme(theme_type.value)

    def _apply_theme_internal(self, theme_type: ThemeType) -> None:
        """Belső téma alkalmazás."""
        self.state.current_theme = theme_type
        self.theme_manager.set_theme(theme_type.value)

    def _theme_from_str(self, theme_str: str) -> ThemeType:
        """String → ThemeType konverzió."""
        try:
            return ThemeType(theme_str)
        except ValueError:
            return ThemeType.LIGHT

    # === EXPORT HANDLERS ===

    def _handle_export_request(self, format: str) -> None:
        """Export request kezelése."""
        handle_export_request(self, format)

    def _show_extreme_weather(self) -> None:
        """Szélsőséges időjárás dialog."""
        show_extreme_weather(self)

    # === SETTINGS ===

    def _save_settings(self) -> None:
        """Beállítások mentése."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("current_view", self.state.current_view_name)
        self.settings.setValue("theme", self.state.current_theme.value)
        self.theme_manager.save_theme_preferences(self.settings)
        self.settings.setValue("current_provider", self.state.provider.current_provider)

    def _load_settings(self) -> None:
        """Beállítások betöltése."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        theme_name = self.settings.value("theme", "light")
        try:
            theme_type = ThemeType(theme_name)
            self._apply_theme_internal(theme_type)
        except ValueError:
            self._apply_theme_internal(ThemeType.LIGHT)

        self._initialize_provider_status()
        switch_view(self, "single_city")

    # === VIEW SWITCHING (wrapper) ===

    def _switch_view(self, view_name: str) -> None:
        """Nézetváltás."""
        switch_view(self, view_name)

    def _handle_analytics_view_query(self, query_type: str, region_name: str) -> None:
        """Analytics query kezelése."""
        handle_analytics_view_query(self, query_type, region_name)

    def _handle_multi_city_weather_request(self, analysis_type: str, region_id: str, start_date: str, end_date: str, params: dict) -> None:
        """Multi-city request kezelése."""
        handle_multi_city_weather_request(self, analysis_type, region_id, start_date, end_date, params)

    def _map_query_type_to_parameter(self, query_type: str) -> str:
        """Query type → Parameter mapping."""
        return map_query_type_to_parameter(query_type)

    def _on_multi_city_result_ready_for_views(self, result: 'AnalyticsResult', query_type: str = "hottest_today") -> None:
        """Multi-city result szétosztás."""
        from .main_window_actions import on_multi_city_result_ready
        on_multi_city_result_ready(self, result, query_type)

    def _show_about(self) -> None:
        """Névjegy."""
        show_about(self)

    def _show_error(self, message: str) -> None:
        """Hiba megjelenítés."""
        show_error(self, message)

    # === THREAD CLEANUP ===

    def _register_thread(self, thread: QThread) -> None:
        register_thread(self, thread)

    def _register_worker(self, worker) -> None:
        register_worker(self, worker)

    def _register_web_view(self, web_view: QWebEngineView) -> None:
        register_web_view(self, web_view)

    def _register_timer(self, timer: QTimer) -> None:
        register_timer(self, timer)

    # === CLOSE EVENT ===

    def closeEvent(self, event) -> None:
        """Ablak bezárása."""
        self._save_settings()
        cleanup_all_timers(self)
        cleanup_all_web_engines(self)
        cleanup_all_workers(self)
        cleanup_all_threads(self)
        event.accept()

    # === PUBLIC API ===

    def get_current_view(self) -> str:
        """Jelenlegi nézet lekérdezése."""
        return self.state.current_view_name

    def switch_to_view(self, view_name: str) -> None:
        """Nézetváltás (publikus API)."""
        switch_view(self, view_name)

    def get_analytics_panel(self) -> Optional[AnalyticsView]:
        """Analytics panel lekérdezése."""
        return self.analytics_panel

    def focus_analytics_panel(self) -> None:
        """Analytics panel fókuszálása."""
        if self.analytics_panel:
            switch_view(self, "analytics")


# Export
__all__ = ['MainWindow']
