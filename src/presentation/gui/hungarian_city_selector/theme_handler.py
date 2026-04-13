#!/usr/bin/env python3
# mypy: ignore-errors

"""
Hungarian City Selector - Theme Handler Module
Téma kezelési logika a HungarianCitySelector widgethez.
"""

import logging

from PySide6.QtWidgets import QPushButton, QWidget
from src.presentation.gui.theme_manager import (
    get_current_colors,
    get_theme_manager,
    register_widget_for_theming,
)

logger = logging.getLogger(__name__)


class HungarianCityThemeHandler:
    """
    Téma kezelő osztály a HungarianCitySelector widgethez.
    """

    def __init__(self, widget: QWidget, theme_changed_callback: callable):
        """
        Inicializálás.

        Args:
            widget: Fő widget
            theme_changed_callback: Téma változási callback
        """
        self.widget = widget
        self.theme_manager = get_theme_manager()

        # Téma változás figyelése
        self.theme_manager.theme_changed.connect(theme_changed_callback)

    def register_widgets(
        self,
        search_box,
        region_combo,
        city_list,
        quick_access_buttons: list[QPushButton],
    ) -> None:
        """
        Widgetek regisztrálása theminghez.

        Args:
            search_box: Keresőmező
            region_combo: Régió választó
            city_list: Városok lista
            quick_access_buttons: Gyors hozzáférés gombok
        """
        # Widget regisztrációk ThemeManager-hez
        register_widget_for_theming(self.widget, "container")
        register_widget_for_theming(search_box, "input")
        register_widget_for_theming(region_combo, "input")
        register_widget_for_theming(city_list, "table")

        # Quick access gombok regisztrálása
        for btn in quick_access_buttons:
            register_widget_for_theming(btn, "button")

        logger.debug("🎨 Widgetek regisztrálva a theminghez")

    def apply_initial_theme(self) -> None:
        """Kezdeti téma alkalmazása."""
        self._apply_current_theme()

    def _apply_current_theme(self) -> None:
        """Jelenlegi téma alkalmazása."""
        colors = get_current_colors()

        # Fő widget háttér
        self.widget.setStyleSheet(f"""
            QWidget {{
                background-color: {colors.get("surface", "#ffffff")};
                color: {colors.get("on_surface", "#000000")};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {colors.get("border", "#ccc")};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 6px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px 0 6px;
                color: {colors.get("primary", "#0066cc")};
            }}
        """)
