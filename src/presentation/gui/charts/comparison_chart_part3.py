# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 3 for MultiYearComparisonChart."""

from __future__ import annotations

from .comparison_chart_support import *


class MultiYearComparisonChartPart3Mixin:  # noqa: D101
    def _plot_comparison_placeholder(self) -> None:
        """Placeholder ha nincs elég valódi adat az összehasonlításhoz - MOCK ADATOK NÉLKÜL + SIMPLIFIED THEMEMANAGER."""
        # Biztosítjuk, hogy az ax standard subplot legyen
        if not hasattr(self, "ax") or self.ax is None:
            self.ax = self.figure.add_subplot(111)

        # 🔧 SIMPLIFIED THEMEMANAGER SZÍNEK
        current_colors = get_current_colors()
        text_color = current_colors.get("on_surface", "#1f2937")
        surface_color = current_colors.get("surface_variant", "#f9fafb")

        placeholder_text = "📊 Évek Közötti Összehasonlítás\n\n"
        placeholder_text += "❌ Nincs elég valódi adat\n\n"
        placeholder_text += "Legalább 2 különböző év\n"
        placeholder_text += "valódi adataira van szükség az\n"
        placeholder_text += "összehasonlításhoz.\n\n"
        placeholder_text += "🚨 Mock adatok használata TILOS!"

        self.ax.text(
            0.5,
            0.5,
            placeholder_text,
            ha="center",
            va="center",
            transform=self.ax.transAxes,
            fontsize=14,
            color=text_color,
            bbox={
                "boxstyle": "round,pad=0.5",
                "facecolor": surface_color,
                "edgecolor": current_colors.get("border", "#d1d5db"),
                "alpha": 0.8,
            },
        )

        self.ax.set_title(
            self.chart_title, fontsize=16, fontweight="bold", pad=20, color=text_color
        )

        # Tengelyek elrejtése placeholder módban
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)
