#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Data Widgets - Weather Data Table Core
Fő WeatherDataTable widget - ThemeManager integrált verzió.
"""

from typing import Optional

import pandas as pd
from PySide6.QtWidgets import QWidget

from ..theme_manager import get_theme_manager
from .mixins import (
    DataHandlingMixin,
    DisplayMixin,
    ExportMixin,
    FilteringMixin,
    SortingMixin,
)


class WeatherDataTable(
    QWidget,
    SortingMixin,
    FilteringMixin,
    ExportMixin,
    DataHandlingMixin,
    DisplayMixin,
):
    """
    Időjárási adatok táblázatos megjelenítése - THEMEMANAGER INTEGRÁLT VERZIÓ.

    🎨 VÁLTOZÁSOK:
    - Hardcoded CSS-ek eltávolítva
    - Manual dark theme logika → ThemeManager delegálás
    - Widget regisztrációk automatikus styling-hoz

    🔧 KRITIKUS JAVÍTÁS:
    - _convert_to_dataframe() robust hibakezelés
    - Adathossz validálás
    - Üres adatok kezelése

    FUNKCIÓK MEGTARTVA:
    - Numerikus rendezés
    - Kattintással rendezhető oszlopok
    - KÖZÉPHŐMÉRSÉKLET OSZLOP
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Javított táblázat widget inicializálása."""
        super().__init__(parent)

        self._theme_manager = get_theme_manager()

        self.current_data: Optional[pd.DataFrame] = None
        self.filtered_data: Optional[pd.DataFrame] = None

        # Mixin inicializálás
        self._setup_sorting()
        self._setup_filtering()

        # UI setup
        self._init_ui()
        self._connect_signals()
        self._register_widgets_for_theming()

        # Export progress UI - use info_bar layout
        if hasattr(self, "info_bar") and self.info_bar.layout():
            self._setup_export_ui(self.info_bar.layout())
