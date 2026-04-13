#!/usr/bin/env python3
# mypy: ignore-errors

"""
Precipitation Chart - Core

🎯 PrecipitationChart main class

Képességek:
- Main class
- Inicializáció
- Public API

Fájl: src/presentation/gui/charts/precipitation_chart/core.py
"""

from PySide6.QtWidgets import QWidget

from ..base_chart import WeatherChart
from ..tooltip_mixin import WeatherTooltipMixin


class PrecipitationChart(WeatherChart, WeatherTooltipMixin):
    """
    Csapadék grafikon widget - EREDETI MEGTARTVA + DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER + TOOLTIP INTEGRÁCIÓ.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette precipitation színek használata
    🎯 TOOLTIP ENHANCEMENT: WeatherTooltipMixin integráció - BAR CHART HOVER FUNKCIÓK
    """

    def __init__(self, parent: QWidget | None = None):  # noqa: D107
        super().__init__(figsize=(12, 6), parent=parent)
        self.chart_title = "🌧️ Napi csapadék mennyisége"
        self.y_label = "Csapadék (mm)"

        # 🎯 TOOLTIP AKTIVÁLÁS - OPT-IN RENDSZER
        self.enable_tooltips(hover_tolerance=20)  # Bar chart-hoz nagyobb tolerance
        print("🎯 DEBUG: PrecipitationChart tooltip-ok aktiválva!")

    # Public API methods
    def update_data(self, data) -> None:  # noqa: D102
        from .data_handler import update_data

        update_data(self, data)

    # Private methods (imported from modules)
    def _extract_precipitation_data(self, data):
        from .data_handler import _extract_precipitation_data

        return _extract_precipitation_data(self, data)

    def _plot_precipitation(self, df) -> None:
        from .plotting import _plot_precipitation

        _plot_precipitation(self, df)

    def _format_precipitation_chart(self, df) -> None:
        from .formatting import _format_precipitation_chart

        _format_precipitation_chart(self, df)

    def _find_closest_chart_point(self, event):
        from .tooltip import _find_closest_chart_point

        return _find_closest_chart_point(self, event)

    def _format_tooltip_text(self, point_data) -> str:
        from .tooltip import _format_tooltip_text

        return _format_tooltip_text(self, point_data)

    def _show_tooltip(self, event, point_data) -> None:
        from .tooltip import _show_tooltip

        _show_tooltip(self, event, point_data)

    def _hide_tooltip(self) -> None:
        from .tooltip import _hide_tooltip

        _hide_tooltip(self)
