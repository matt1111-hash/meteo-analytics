#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Location Widget - Theme styling.
"""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLabel

from src.presentation.gui.theme_manager import register_widget_for_theming

if TYPE_CHECKING:
    from .core import LocationWidget


class ThemeHandler:
    """Theme handler a LocationWidget számára."""

    def __init__(self, widget: "LocationWidget"):
        """
        ThemeHandler inicializálása.

        Args:
            widget: LocationWidget instance
        """
        self.widget = widget

    def apply(self) -> None:
        """Theme manager regisztráció."""
        register_widget_for_theming(self.widget, "container")
        register_widget_for_theming(self.widget.ui.group, "container")
        register_widget_for_theming(self.widget.ui.location_selector, "container")
        register_widget_for_theming(self.widget.ui.clear_btn, "button")

        # Info label styling
        self._apply_label_styling(self.widget.ui.info_label, "secondary")

    def _apply_label_styling(self, label: QLabel, style_type: str) -> None:
        """Label styling alkalmazása."""
        color_palette = self.widget.theme_manager.get_color_scheme()
        if not color_palette:
            return

        if style_type == "secondary":
            color = color_palette.get_color("info", "light") or "#9ca3af"
            font_size = "11px"
        elif style_type == "primary":
            color = color_palette.get_color("primary", "base") or "#2563eb"
            font_size = "12px"
        else:
            return

        css = f"QLabel {{ color: {color}; font-size: {font_size}; }}"
        label.setStyleSheet(css)

        register_widget_for_theming(label, "text")
