#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Window Layout - Ablak layout és nézetek létrehozása.

FÁJL: src/presentation/gui/windows/window_layout.py
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from .main_window import MainWindow


def setup_window(window: 'MainWindow') -> None:
    """
    🪟 Ablak alapbeállításai.

    Args:
        window: MainWindow példány
    """
    from src.config import AppInfo

    from ..theme_manager import register_widget_for_theming
    from ..utils import GUIConstants

    window.setWindowTitle(f"{AppInfo.NAME} - THREAD CLEANUP FIX")
    window.setGeometry(
        GUIConstants.MAIN_WINDOW_X,
        GUIConstants.MAIN_WINDOW_Y,
        1400,
        900
    )
    window.setMinimumSize(1200, 700)
    register_widget_for_theming(window, "navigation")


def create_stacked_views(window: 'MainWindow') -> QStackedWidget:
    """
    📚 QStackedWidget inicializálása különböző nézetekkel.

    Args:
        window: MainWindow példány

    Returns:
        Létrehozott stacked widget
    """
    from ..theme_manager import register_widget_for_theming

    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    register_widget_for_theming(central_widget, "container")

    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(5, 5, 5, 5)
    main_layout.setSpacing(0)

    stacked_widget = QStackedWidget()
    register_widget_for_theming(stacked_widget, "container")
    main_layout.addWidget(stacked_widget)

    # VIEW-K LÉTREHOZÁSA
    single_city_view = create_single_city_view(window)
    stacked_widget.addWidget(single_city_view)  # INDEX 0

    analytics_view = create_analytics_view(window)
    stacked_widget.addWidget(analytics_view)  # INDEX 1

    trend_view = create_trend_analysis_view(window)
    stacked_widget.addWidget(trend_view)  # INDEX 2

    map_view = create_hungarian_map_view(window)
    stacked_widget.addWidget(map_view)  # INDEX 3

    settings_view = create_settings_placeholder(window)
    stacked_widget.addWidget(settings_view)  # INDEX 4

    stacked_widget.setCurrentIndex(0)  # Single City View alapértelmezett

    return stacked_widget


def create_single_city_view(window: 'MainWindow') -> QWidget:
    """Single City View létrehozása."""
    from ..control_panel import ControlPanel
    from ..results_panel import ResultsPanel
    from ..theme_manager import register_widget_for_theming

    view = QWidget()
    register_widget_for_theming(view, "container")

    layout = QVBoxLayout(view)
    layout.setContentsMargins(2, 2, 2, 2)
    layout.setSpacing(0)

    main_splitter = QSplitter(Qt.Horizontal)
    main_splitter.setHandleWidth(18)
    main_splitter.setChildrenCollapsible(False)
    main_splitter.setOpaqueResize(True)
    register_widget_for_theming(main_splitter, "splitter")

    # Control Panel
    window.control_panel = ControlPanel(window.worker_manager)
    register_widget_for_theming(window.control_panel, "container")
    window.control_panel.setMinimumWidth(320)
    window.control_panel.setMaximumWidth(520)
    window.control_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
    main_splitter.addWidget(window.control_panel)

    # Results Panel
    window.results_panel = ResultsPanel()
    register_widget_for_theming(window.results_panel, "container")
    window.results_panel.setMinimumWidth(450)
    window.results_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    main_splitter.addWidget(window.results_panel)

    main_splitter.setStretchFactor(0, 0)
    main_splitter.setStretchFactor(1, 1)

    total_width = 1400
    control_width = 420
    results_width = total_width - control_width - 20
    main_splitter.setSizes([control_width, results_width])

    layout.addWidget(main_splitter)
    return view


def create_analytics_view(window: 'MainWindow') -> QWidget:
    """Analytics View létrehozása."""
    from ..analytics import AnalyticsView
    from ..theme_manager import register_widget_for_theming

    window.analytics_panel = AnalyticsView()
    register_widget_for_theming(window.analytics_panel, "container")
    return window.analytics_panel


def create_trend_analysis_view(window: 'MainWindow') -> QWidget:
    """Trend Analysis view létrehozása."""
    from ..theme_manager import register_widget_for_theming
    from ..trend_analytics import TrendAnalyticsTab

    window.trend_analytics_tab = TrendAnalyticsTab()
    register_widget_for_theming(window.trend_analytics_tab, "container")
    return window.trend_analytics_tab


def create_hungarian_map_view(window: 'MainWindow') -> QWidget:
    """Hungarian Map view létrehozása."""
    from ..hungarian_map_tab import HungarianMapTab
    from ..theme_manager import register_widget_for_theming

    window.hungarian_map_tab = HungarianMapTab()
    register_widget_for_theming(window.hungarian_map_tab, "container")

    # Magyar megyék automatikus konfigurálása
    if window.state.hungarian_counties.geodataframe is not None:
        if hasattr(window.hungarian_map_tab, 'map_visualizer'):
            map_visualizer = window.hungarian_map_tab.map_visualizer
            if hasattr(map_visualizer, 'set_counties_geodataframe'):
                map_visualizer.set_counties_geodataframe(window.state.hungarian_counties.geodataframe)

    return window.hungarian_map_tab


def create_settings_placeholder(window: 'MainWindow') -> QWidget:
    """Settings placeholder view létrehozása."""
    from ..theme_manager import register_widget_for_theming

    view = QWidget()
    register_widget_for_theming(view, "container")
    return view


def create_status_bar_provider_widgets(window: 'MainWindow') -> tuple:
    """
    🌍 Status bar provider widgetek létrehozása.

    Returns:
        (provider_status_label, usage_status_label, cost_status_label)
    """
    provider_status_label = QLabel("Provider: auto")
    usage_status_label = QLabel("Használat: 0/1000")
    cost_status_label = QLabel("Költség: $0.00")

    return provider_status_label, usage_status_label, cost_status_label


# Export
__all__ = [
    'setup_window',
    'create_stacked_views',
    'create_single_city_view',
    'create_analytics_view',
    'create_trend_analysis_view',
    'create_hungarian_map_view',
    'create_settings_placeholder',
    'create_status_bar_provider_widgets',
]
