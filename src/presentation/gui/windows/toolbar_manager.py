#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Toolbar Manager - Navigációs eszköztár létrehozása.

FÁJL: src/presentation/gui/windows/toolbar_manager.py
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QToolBar

if TYPE_CHECKING:
    from .main_window import MainWindow


def create_navigation_toolbar(window: 'MainWindow') -> QToolBar:
    """
    🧭 Navigációs eszköztár létrehozása.

    Args:
        window: MainWindow példány

    Returns:
        Létrehozott eszköztár
    """
    from ..theme_manager import register_widget_for_theming

    toolbar = QToolBar("Navigáció")
    toolbar.setMovable(False)
    toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    toolbar.setIconSize(QSize(24, 24))

    register_widget_for_theming(toolbar, "navigation")

    # === NAVIGÁCIÓS AKCIÓK - 5 TAB VERZIÓ ===

    # 🏙️ Pontszerű Elemzés
    single_city_action = QAction("Város Elemzés", window)
    single_city_action.setToolTip("Egyetlen város részletes időjárási elemzése")
    single_city_action.triggered.connect(lambda: window._switch_view("single_city"))
    single_city_action.setCheckable(True)
    single_city_action.setChecked(True)
    toolbar.addAction(single_city_action)

    # 📊 Analytics
    analytics_action = QAction("Analitika", window)
    analytics_action.setToolTip("Időjárási elemzések és statisztikák")
    analytics_action.triggered.connect(lambda: window._switch_view("analytics"))
    analytics_action.setCheckable(True)
    toolbar.addAction(analytics_action)

    # 📈 Trend Elemző
    trend_action = QAction("Trend Elemzés", window)
    trend_action.setToolTip("Hosszú távú klimatikus trendek elemzése")
    trend_action.triggered.connect(lambda: window._switch_view("trend_analysis"))
    trend_action.setCheckable(True)
    toolbar.addAction(trend_action)

    # 🗺️ Interaktív Térkép
    map_action = QAction("Térkép", window)
    map_action.setToolTip("Interaktív időjárási térkép magyar megyékkel")
    map_action.triggered.connect(lambda: window._switch_view("map_view"))
    map_action.setCheckable(True)
    toolbar.addAction(map_action)

    toolbar.addSeparator()

    # ⚙️ Beállítások
    settings_action = QAction("Beállítások", window)
    settings_action.setToolTip("Alkalmazás beállítások")
    settings_action.triggered.connect(lambda: window._switch_view("settings"))
    settings_action.setCheckable(True)
    toolbar.addAction(settings_action)

    # === AKCIÓK CSOPORTOSÍTÁSA ===

    view_action_group = QActionGroup(window)
    view_action_group.addAction(single_city_action)
    view_action_group.addAction(analytics_action)
    view_action_group.addAction(trend_action)
    view_action_group.addAction(map_action)
    view_action_group.addAction(settings_action)

    # Store references
    window.single_city_action = single_city_action
    window.analytics_action = analytics_action
    window.trend_action = trend_action
    window.map_action = map_action
    window.settings_action = settings_action
    window.view_action_group = view_action_group

    return toolbar


# Export
__all__ = [
    'create_navigation_toolbar',
]
