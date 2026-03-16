#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Menu Builder - Menüsor létrehozása a MainWindow számára.

FÁJL: src/presentation/gui/windows/menu_builder.py
"""

from typing import TYPE_CHECKING

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar

if TYPE_CHECKING:
    from .main_window import MainWindow


def create_menu_bar(window: "MainWindow") -> QMenuBar:
    """
    📔 Menüsor létrehozása.

    Args:
        window: MainWindow példány

    Returns:
        Létrehozott menüsor
    """
    menu_bar = window.menuBar()
    menu_bar.setNativeMenuBar(True)

    # === FILE MENÜ ===
    file_menu = menu_bar.addMenu("Fájl")

    export_action = QAction("Adatok Exportálása", window)
    export_action.setShortcut("Ctrl+E")
    export_action.triggered.connect(lambda: window._handle_export_request("csv"))
    file_menu.addAction(export_action)

    file_menu.addSeparator()

    exit_action = QAction("Kilépés", window)
    exit_action.setShortcut("Ctrl+Q")
    exit_action.triggered.connect(window.close)
    file_menu.addAction(exit_action)

    # === VIEW MENÜ ===
    view_menu = menu_bar.addMenu("Nézet")

    single_city_action = QAction("Város Elemzés", window)
    single_city_action.triggered.connect(lambda: window._switch_view("single_city"))
    view_menu.addAction(single_city_action)

    analytics_action = QAction("Analitika", window)
    analytics_action.triggered.connect(lambda: window._switch_view("analytics"))
    view_menu.addAction(analytics_action)

    trend_action = QAction("Trend Elemzés", window)
    trend_action.triggered.connect(lambda: window._switch_view("trend_analysis"))
    view_menu.addAction(trend_action)

    map_action = QAction("Térkép", window)
    map_action.triggered.connect(lambda: window._switch_view("map_view"))
    view_menu.addAction(map_action)

    view_menu.addSeparator()

    settings_action = QAction("Beállítások", window)
    settings_action.triggered.connect(lambda: window._switch_view("settings"))
    view_menu.addAction(settings_action)

    # === TOOLS MENÜ ===
    tools_menu = menu_bar.addMenu("Eszközök")

    extreme_action = QAction("Szélsőséges Időjárás", window)
    extreme_action.triggered.connect(window._show_extreme_weather)
    tools_menu.addAction(extreme_action)

    # === THEME MENÜ ===
    theme_menu = menu_bar.addMenu("Téma")

    light_action = QAction("Világos", window)
    light_action.triggered.connect(
        lambda: window._apply_theme(window._theme_from_str("light"))
    )
    theme_menu.addAction(light_action)

    dark_action = QAction("Sötét", window)
    dark_action.triggered.connect(
        lambda: window._apply_theme(window._theme_from_str("dark"))
    )
    theme_menu.addAction(dark_action)

    # === HELP MENÜ ===
    help_menu = menu_bar.addMenu("Súgó")

    about_action = QAction("Névjegy", window)
    about_action.triggered.connect(window._show_about)
    help_menu.addAction(about_action)

    return menu_bar


# Export
__all__ = [
    "create_menu_bar",
]
