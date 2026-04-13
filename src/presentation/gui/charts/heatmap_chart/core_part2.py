# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for HeatmapCalendarChart."""

from __future__ import annotations

from .core_support import *


class HeatmapCalendarChartPart2Mixin:  # noqa: D101
    def _plot_heatmap_placeholder(self) -> None:
        """Plot placeholder when insufficient data"""
        current_colors = get_current_colors()
        text_color = current_colors.get("on_surface", "#1f2937")
        surface_color = current_colors.get("surface_variant", "#f9fafb")

        placeholder_text = "📅 Konstans Heatmap (365 téglalap)\n\n"
        placeholder_text += "❌ Nincs elegendő adat\n\n"
        placeholder_text += f"Paraméter: {self.parameter}\n\n"
        placeholder_text += (
            "A heatmap megjelenítéséhez\nlegalább 10 valódi adat\nszükséges az API-ból.\n\n"
        )
        placeholder_text += "🎯 FUNKCIÓK:\n"
        placeholder_text += "• Valódi hónap címkék\n"
        placeholder_text += "• 365 konstans felbontás\n"
        placeholder_text += "• Meteorológiai színskálák\n"
        placeholder_text += "📊 Clean heatmap!"

        self.ax.text(
            0.5,
            0.5,
            placeholder_text,
            ha="center",
            va="center",
            transform=self.ax.transAxes,
            fontsize=12,
            color=text_color,
            linespacing=1.5,
            bbox={
                "boxstyle": "round,pad=0.5",
                "facecolor": surface_color,
                "edgecolor": current_colors.get("border", "#d1d5db"),
            },
        )

        self.ax.set_title(
            f"{self.chart_title} - Nincs Adat",
            fontsize=18,
            fontweight="bold",
            pad=20,
            color=text_color,
        )

        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)

    def _apply_theme_to_chart(self) -> None:
        """Theme alkalmazása a chartre (base_chart kompatibilitás)."""
        try:
            current_colors = get_current_colors()
            text_color = current_colors.get("on_surface", "#1f2937")
            grid_color = current_colors.get("outline", "#e5e7eb")

            if hasattr(self, "ax") and self.ax:
                self.ax.tick_params(colors=text_color)
                self.ax.xaxis.label.set_color(text_color)
                self.ax.yaxis.label.set_color(text_color)
                if hasattr(self.ax, "title"):
                    self.ax.title.set_color(text_color)

                for spine in self.ax.spines.values():
                    spine.set_edgecolor(grid_color)

                self.draw()
        except Exception as e:
            logger.error(f"HeatmapChart theme apply error: {e}")
