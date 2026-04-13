# mypy: ignore-errors
"""Wind Rose Chart - Széllökés rózsadiagram."""

from typing import Any

from PySide6.QtWidgets import QWidget
from src.presentation.gui.charts.base_chart import WeatherChart
from src.presentation.gui.charts.wind_rose_chart.data_handler import extract_wind_data
from src.presentation.gui.charts.wind_rose_chart.plotting import (
    plot_wind_rose,
    plot_wind_rose_placeholder,
)


class WindRoseChart(WeatherChart):
    """Szélirány és széllökés erősség kombinált megjelenítése."""

    def __init__(self, parent: QWidget | None = None):  # noqa: D107
        super().__init__(figsize=(10, 10), parent=parent)
        self.chart_title = "🌹 Széllökés Rózsadiagram"

    def update_data(self, data: dict[str, Any]) -> None:
        """Wind rose adatfrissítés."""
        if self._is_updating:
            return

        try:
            self._is_updating = True

            df = extract_wind_data(data)

            if df.empty:
                self.clear_chart()
                self._is_updating = False
                return

            self.current_data = df

            # Teljes figure törlése
            self.figure.clear()

            # Téma alkalmazása
            from src.presentation.gui.theme_manager import get_current_colors

            current_colors = get_current_colors()
            self.figure.patch.set_facecolor(current_colors.get("surface", "#ffffff"))

            # Wind rose megrajzolása
            plot_wind_rose(self.ax, self.figure, self.chart_title, df, self.legend_enabled)

            self.draw()
            self._is_updating = False

        except Exception:
            self._is_updating = False
            self.clear_chart()
            plot_wind_rose_placeholder(self.ax, self.figure, self.chart_title)

    def has_valid_data(self) -> bool:
        """Van-e érvényes wind rose adat."""
        if not hasattr(self, "current_data") or self.current_data is None:
            return False

        if isinstance(self.current_data, type(None).__class__):
            return False

        return hasattr(self.current_data, "empty") and not self.current_data.empty
