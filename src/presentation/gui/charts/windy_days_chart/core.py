#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windy Days Chart - Core

🎯 WindyDaysChart main class

Képességek:
- Main class
- Inicializáció
- Public API

Fájl: src/presentation/gui/charts/windy_days_chart/core.py
"""

import logging
from typing import Dict, List, Optional

from PySide6.QtWidgets import QWidget

from ..base_chart import WeatherChart

logger = logging.getLogger(__name__)


class WindyDaysChart(WeatherChart):
    """
    Szeles napok havi oszlopdiagram chart komponens.

    Megjeleníti a havi szeles napok számát oszlopdiagramon,
    színkódolással és interaktív elemekkel.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Inicializálás."""
        super().__init__(parent)

        self.chart_title = "Havi Szeles Napok (>43 km/h)"
        self.chart_type = "windy_days"

        # Chart-specifikus adatok
        self.chart_data: Dict[str, List] = {
            'months': [],
            'counts': [],
            'percentages': [],
            'labels': []
        }

        self.threshold_kmh = 43.0
        self.location_name = "Ismeretlen helyszín"

        logger.info("WindyDaysChart inicializálva")

    # Public API methods
    def update_data(self, chart_data: Dict) -> None:
        from .data_handler import update_data
        update_data(self, chart_data)

    def clear_chart(self) -> None:
        from .helpers import clear_chart
        clear_chart(self)

    def export_chart(self, file_path: str, dpi: int = 300) -> bool:
        from .helpers import export_chart
        return export_chart(self, file_path, dpi)

    def get_chart_info(self) -> Dict:
        from .helpers import get_chart_info
        return get_chart_info(self)

    # Private methods (imported from modules)
    def _has_valid_data(self) -> bool:
        from .data_handler import _has_valid_data
        return _has_valid_data(self)

    def _plot_windy_days_chart(self) -> None:
        from .plotting import _plot_windy_days_chart
        _plot_windy_days_chart(self)

    def _get_bar_colors(self, counts: List[int]) -> List[str]:
        from .styling import _get_bar_colors
        return _get_bar_colors(self, counts)

    def _add_value_labels(self, ax, bars, counts: List[int], percentages: List[float]) -> None:
        from .styling import _add_value_labels
        _add_value_labels(self, ax, bars, counts, percentages)

    def _setup_chart_axes(self, ax, months: List[str], counts: List[int]) -> None:
        from .styling import _setup_chart_axes
        _setup_chart_axes(self, ax, months, counts)

    def _setup_chart_labels(self, ax) -> None:
        from .styling import _setup_chart_labels
        _setup_chart_labels(self, ax)

    def _apply_chart_styling(self, ax) -> None:
        from .styling import _apply_chart_styling
        _apply_chart_styling(self, ax)

    def _setup_chart_interactivity(self, bars, months: List[str], counts: List[int], percentages: List[float]) -> None:
        from .interactivity import _setup_chart_interactivity
        _setup_chart_interactivity(self, bars, months, counts, percentages)

    def _plot_no_data_message(self) -> None:
        from .helpers import _plot_no_data_message
        _plot_no_data_message(self)

    def _plot_error_message(self, error_msg: str) -> None:
        from .helpers import _plot_error_message
        _plot_error_message(self, error_msg)
