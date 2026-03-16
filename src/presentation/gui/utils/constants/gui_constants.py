#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Constants - GUI dimensions, margins, colors.
"""


class GUIConstants:
    """GUI constants - window sizes, positions, fonts."""

    # Main window
    MAIN_WINDOW_WIDTH = 1200
    MAIN_WINDOW_HEIGHT = 800
    MAIN_WINDOW_MIN_WIDTH = 900
    MAIN_WINDOW_MIN_HEIGHT = 600
    MAIN_WINDOW_X = 100
    MAIN_WINDOW_Y = 100

    # Dialog
    DIALOG_MIN_WIDTH = 600
    DIALOG_MIN_HEIGHT = 400

    # Panel settings
    CONTROL_PANEL_MIN_WIDTH = 280
    CONTROL_PANEL_MAX_WIDTH = 400
    CONTROL_PANEL_MARGINS = (10, 10, 10, 10)
    RESULTS_PANEL_MARGINS = (10, 10, 10, 10)

    # Layout
    LAYOUT_SPACING = 10
    MAIN_LAYOUT_MARGINS = (10, 10, 10, 10)

    # Widgets
    BUTTON_HEIGHT = 32
    SPLITTER_HANDLE_WIDTH = 8
    SPLITTER_MIN_SIZE = 200
    CHART_MIN_HEIGHT = 300
    TABLE_MIN_HEIGHT = 200
    CONTROL_BAR_HEIGHT = 50

    # Fonts
    DEFAULT_FONT_FAMILY = "Segoe UI, Arial, sans-serif"
    DEFAULT_FONT_SIZE = 10
    TITLE_FONT_SIZE = 12
    HEADER_FONT_SIZE = 14

    # Semantic colors
    PRIMARY_COLOR = "#2563eb"
    SUCCESS_COLOR = "#10b981"
    WARNING_COLOR = "#f59e0b"
    ERROR_COLOR = "#dc2626"
    INFO_COLOR = "#6b7280"

    # Surface colors
    SURFACE_LIGHT = "#ffffff"
    SURFACE_DARK = "#1f2937"
    ON_SURFACE_LIGHT = "#1f2937"
    ON_SURFACE_DARK = "#f9fafb"
