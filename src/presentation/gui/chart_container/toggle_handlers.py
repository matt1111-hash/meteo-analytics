#!/usr/bin/env python3
# mypy: ignore-errors

"""
ChartContainer Toggle Handlers - Handle grid and legend toggles.
"""

from typing import TYPE_CHECKING

from ..theme_manager import get_current_colors

if TYPE_CHECKING:
    from .core import ChartsContainer


def _iter_container_charts(container: "ChartsContainer") -> list:
    """Return charts participating in grid/legend toggles."""
    return [
        container.temp_chart,
        container.precip_chart,
        container.wind_chart,
        container.heatmap_chart,
        container.windrose_chart,
        container.comparison_chart,
    ]


def _apply_grid_state(chart, enabled: bool, theme_manager) -> None:
    """Apply grid state to one chart axis."""
    if not hasattr(chart, "ax") or not chart.ax:
        return
    if enabled:
        current_colors = get_current_colors()
        grid_color = current_colors.get("border", "#d1d5db")
        grid_alpha = 0.3 if theme_manager.get_current_theme() == "light" else 0.2
        chart.ax.grid(
            True,
            alpha=grid_alpha,
            linestyle="-",
            linewidth=0.8,
            color=grid_color,
        )
    else:
        chart.ax.grid(False)
    chart.draw()


def _apply_legend_state(chart, enabled: bool, current_colors: dict[str, str]) -> None:
    """Apply legend state to one chart axis."""
    if not hasattr(chart, "ax") or not chart.ax:
        return
    legend = chart.ax.get_legend()
    if enabled:
        _show_legend(chart, legend, current_colors)
    else:
        _hide_legend(legend)
    chart.draw()


def _show_legend(chart, legend, current_colors: dict[str, str]) -> None:
    """Ensure legend exists and is visible with themed frame colors."""
    themed_legend = legend or chart.ax.legend(
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        framealpha=0.95,
        fancybox=True,
        shadow=True,
        fontsize=11,
    )
    themed_legend.set_visible(True)
    themed_legend.get_frame().set_facecolor(current_colors.get("surface", "#ffffff"))
    themed_legend.get_frame().set_edgecolor(current_colors.get("border", "#d1d5db"))


def _hide_legend(legend) -> None:
    """Hide legend when it exists."""
    if legend:
        legend.set_visible(False)


class ToggleHandlers:
    """Handle grid and legend toggle operations."""

    def __init__(self, container: "ChartsContainer"):
        """
        Initialize toggle handlers.

        Args:
            container: ChartsContainer instance
        """
        self._container = container

    def toggle_grid(self, enabled: bool) -> None:
        """
        Toggle grid display on all charts.

        Args:
            enabled: Whether grid should be enabled
        """
        print(f"🔧 DEBUG: _toggle_grid_optimized({enabled})")

        try:
            for chart in _iter_container_charts(self._container):
                chart.grid_enabled = enabled
                _apply_grid_state(chart, enabled, self._container.theme_manager)

            print(f"✅ DEBUG: Grid toggle optimalizálva: {enabled}")

        except Exception as e:
            print(f"❌ DEBUG: Grid toggle hiba: {e}")

    def toggle_legend(self, enabled: bool) -> None:
        """
        Toggle legend display on all charts.

        Args:
            enabled: Whether legend should be enabled
        """
        print(f"🔧 DEBUG: _toggle_legend_optimized({enabled})")

        try:
            current_colors = get_current_colors()
            for chart in _iter_container_charts(self._container):
                chart.legend_enabled = enabled
                _apply_legend_state(chart, enabled, current_colors)

            print(f"✅ DEBUG: Legend toggle optimalizálva: {enabled}")

        except Exception as e:
            print(f"❌ DEBUG: Legend toggle hiba: {e}")
