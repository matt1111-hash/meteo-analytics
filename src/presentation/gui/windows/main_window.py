#!/usr/bin/env python3
# mypy: ignore-errors

"""
Universal Weather Research Platform - Main Window
🧹 Clean Architecture Refactor - Modular Design

FÁJL: src/presentation/gui/windows/main_window.py
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from PySide6.QtCore import QSettings, Qt, Signal
from PySide6.QtWidgets import (
    QMainWindow,
)
from src.config import AppInfo

from ..color_palette import ColorPalette
from ..controller import AppController
from ..theme_manager import get_theme_manager, register_widget_for_theming
from ..utils import ThemeType
from .main_window_actions import (
    cleanup_all_threads,
    cleanup_all_timers,
    cleanup_all_web_engines,
    cleanup_all_workers,
)
from .main_window_actions_mixin import MainWindowActionsMixin
from .main_window_analysis_mixin import MainWindowAnalysisMixin
from .main_window_state import MainWindowState
from .main_window_theme_settings_mixin import MainWindowThemeSettingsMixin
from .menu_builder import create_menu_bar
from .toolbar_manager import create_navigation_toolbar
from .window_layout import (
    create_stacked_views,
    create_status_bar_provider_widgets,
    setup_window,
)


def _resolve_project_path(relative_path: str) -> Path:
    """Resolve path relative to the project root (where pyproject.toml lives)."""
    candidates = [
        Path(__file__).resolve().parents[4] / relative_path,
        Path.cwd() / relative_path,
    ]
    for p in candidates:
        if p.is_file():
            return p
    return candidates[0]


class MainWindow(
    MainWindowAnalysisMixin,
    MainWindowThemeSettingsMixin,
    MainWindowActionsMixin,
    QMainWindow,
):
    """
    🪟 Főablak - Clean Architecture Refactor.

    SIGNALOK:
    - theme_changed: Téma változás
    """

    theme_changed = Signal(str)

    # 📧 QUERY TYPE → TÉRKÉP PARAMÉTER MAPPING
    QUERY_TYPE_TO_PARAMETER = {  # noqa: RUF012
        "hottest_today": "Hőmérséklet",
        "coldest_today": "Hőmérséklet",
        "windiest_today": "Szél",
        "wettest_today": "Csapadék",
        "rainiest_today": "Csapadék",
        "sunniest_today": "Hőmérséklet",
        "temperature_range": "Hőmérséklet",
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
        self.provider_status_label, self.usage_status_label, self.cost_status_label = (
            create_status_bar_provider_widgets(self)
        )
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
        geojson_path = _resolve_project_path("data/geojson/counties.geojson")
        if not geojson_path.is_file():
            self.state.hungarian_counties.loaded = False
            self.state.hungarian_counties.geodataframe = None
            return

        try:
            import geopandas as gpd  # noqa: PLC0415

            gdf = gpd.read_file(geojson_path)
            self.state.hungarian_counties.geodataframe = gdf
            self.state.hungarian_counties.loaded = True
        except Exception:
            self.state.hungarian_counties.loaded = False
            self.state.hungarian_counties.geodataframe = None

    def _initialize_provider_status(self) -> None:
        """Provider státusz inicializálása."""
        self.state.provider.current_provider = self.settings.value("current_provider", "auto")
        self._update_provider_status_display()

    def _cleanup_embedded_map(self) -> None:
        """Térképes nézet saját háttérszálainak leállítása."""
        map_tab = getattr(self, "hungarian_map_tab", None)
        map_visualizer = getattr(map_tab, "map_visualizer", None)
        if map_visualizer and hasattr(map_visualizer, "cleanup"):
            map_visualizer.cleanup()

    # === CLOSE EVENT ===

    def closeEvent(self, event) -> None:
        """Ablak bezárása."""
        self._save_settings()
        self._cleanup_embedded_map()
        cleanup_all_timers(self)
        cleanup_all_web_engines(self)
        cleanup_all_workers(self)
        cleanup_all_threads(self)
        event.accept()


# Export
__all__ = ["MainWindow"]
