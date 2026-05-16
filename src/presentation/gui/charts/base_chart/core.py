# mypy: ignore-errors
"""Base Weather Chart class."""

from typing import Any

import matplotlib

matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from src.presentation.gui.charts.base_chart.constants import (
    CHART_DEFAULTS,
    DEFAULT_DPI,
    DEFAULT_FIGSIZE,
)
from src.presentation.gui.charts.base_chart.style import setup_matplotlib_style
from src.presentation.gui.charts.base_chart.theme import apply_theme_to_axis
from src.presentation.gui.color_palette import ColorPalette
from src.presentation.gui.theme_manager import (
    get_current_colors,
    get_theme_manager,
    register_widget_for_theming,
)


class WeatherChart(FigureCanvas):
    """Base weather chart widget with matplotlib and theme support."""

    chart_clicked = Signal(float, float)
    export_requested = Signal(str)

    def __init__(  # noqa: D107
        self, figsize: tuple = DEFAULT_FIGSIZE, parent: QWidget | None = None
    ) -> None:
        current_colors = get_current_colors()
        figure_bg = current_colors.get("surface", "#ffffff")

        self.figure = Figure(figsize=figsize, dpi=DEFAULT_DPI, facecolor=figure_bg)
        super().__init__(self.figure)
        self.setParent(parent)

        self.theme_manager = get_theme_manager()
        self.color_palette = ColorPalette()
        self.weather_colors = self.color_palette.generate_weather_palette("#C43939")

        self.current_data = None
        self.chart_title = CHART_DEFAULTS["chart_title"]
        self.x_label = CHART_DEFAULTS["x_label"]
        self.y_label = CHART_DEFAULTS["y_label"]
        self.grid_enabled = CHART_DEFAULTS["grid_enabled"]
        self.legend_enabled = CHART_DEFAULTS["legend_enabled"]

        self._is_updating = False
        self._last_update_data = None
        self._font_cache_rebuilt = False

        setup_matplotlib_style()

        self.ax = self.figure.add_subplot(111)

        apply_theme_to_axis(self.ax, self.theme_manager, self.grid_enabled)

        self.mpl_connect("button_press_event", self._on_click)

        register_widget_for_theming(self, "chart")
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str) -> None:  # noqa: ARG002
        """Handle theme change."""
        self.weather_colors = self.color_palette.generate_weather_palette("#C43939")
        self._redraw_with_new_theme()

    def _redraw_with_new_theme(self) -> None:
        """Redraw chart with new theme colors."""
        if self._is_updating:
            return

        try:
            apply_theme_to_axis(self.ax, self.theme_manager, self.grid_enabled)

            current_colors = get_current_colors()
            text_color = current_colors.get("on_surface", "#1f2937")

            for line in self.ax.get_lines():
                if line.get_color() in ["#1f77b4", "blue", "b"]:
                    line.set_color(current_colors.get("primary", "#C43939"))

            for text in self.ax.texts:
                text.set_color(text_color)

            self.draw()
        except Exception as e:
            print(f"Theme redraw error: {e}")

    def _apply_theme_to_chart(self) -> None:
        """Apply current theme colors to the active axes and figure."""
        current_colors = get_current_colors()
        self.figure.patch.set_facecolor(current_colors.get("surface", "#ffffff"))
        apply_theme_to_axis(self.ax, self.theme_manager, self.grid_enabled)

    def _on_click(self, event: Any) -> None:
        """Handle chart click."""
        if event.inaxes and event.xdata and event.ydata:
            self.chart_clicked.emit(event.xdata, event.ydata)

    def clear_chart(self) -> None:
        """Clear chart completely."""
        try:
            self._is_updating = True
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            apply_theme_to_axis(self.ax, self.theme_manager, self.grid_enabled)
            self.draw()
            self.current_data = None
            self._last_update_data = None
            self._is_updating = False
        except Exception as e:
            print(f"Chart clear error: {e}")
            self._is_updating = False

    def export_chart(self, filepath: str, format: str = "png", dpi: int = 300) -> bool:
        """Export chart to file."""
        try:
            self.figure.savefig(filepath, format=format, dpi=dpi, bbox_inches="tight")
            return True
        except Exception as e:
            print(f"Chart export error: {e}")
            return False

    def update_style(self, dark_theme: bool = False) -> None:
        """Update chart style (deprecated, use theme manager)."""
        print("update_style() deprecated - use theme_manager.set_theme() instead")
        theme_name = "dark" if dark_theme else "light"
        self.theme_manager.set_theme(theme_name)
