#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialogs - Theme Handler

🎨 Téma kezelés

Képességek:
- Widget regisztráció
- Téma alkalmazás

Fájl: src/presentation/gui/dialogs/theme_handler.py
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..theme_manager import register_widget_for_theming


def _register_widgets_for_theming(self) -> None:
    """
    Widget-ek regisztrálása ThemeManager-ben.

    🔧 JAVÍTÁS: self.close_button most már létezik

    Args:
        self: ExtremeWeatherDialog instance
    """
    print("🎨 DEBUG: Registering ExtremeWeatherDialog widgets for theming...")

    # Container widgets
    register_widget_for_theming(self, "dialog")

    # Radio button widgets (chart style)
    register_widget_for_theming(self.daily_radio, "chart")
    register_widget_for_theming(self.monthly_radio, "chart")

    # Table widget
    register_widget_for_theming(self.extreme_table, "table")

    # Button widget - JAVÍTVA: self.close_button referencia OK
    register_widget_for_theming(self.close_button, "button")

    print("✅ DEBUG: ExtremeWeatherDialog widgets registered for theming")


def apply_theme(self, dark_theme: bool) -> None:
    """
    Téma alkalmazása - THEMEMANAGER DELEGÁLÓ VERZIÓ.

    Args:
        self: ExtremeWeatherDialog instance
        dark_theme: True, ha sötét téma
    """
    from .calculation import _calculate_extremes

    print(f"🎨 DEBUG: ExtremeWeatherDialog applying theme via ThemeManager: {'dark' if dark_theme else 'light'}")

    # ThemeManager automatikus widget styling
    theme_name = "dark" if dark_theme else "light"
    self._theme_manager.set_theme(theme_name)

    # Ha van extrém adat, újrarajzoljuk a táblázatot ThemeManager színekkel
    if hasattr(self, 'extreme_table') and self.extreme_table.rowCount() > 0:
        # Re-populate with current data to apply new colors
        _calculate_extremes(self)

    print(f"✅ DEBUG: ExtremeWeatherDialog theme applied via ThemeManager: {'dark' if dark_theme else 'light'}")
