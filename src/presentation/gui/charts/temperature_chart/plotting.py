#!/usr/bin/env python3
# mypy: ignore-errors

"""
Temperature Chart - Plotting

🎨 Hőmérséklet grafikon rajzolása

Képességek:
- Színes zónák rajzolása
- Hőmérséklet vonalak rajzolása
- Trend vonalak
- Extrém értékek annotálása

Fájl: src/presentation/gui/charts/temperature_chart/plotting.py
"""

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import pandas as pd


class TemperaturePlottingMixin:
    """
    🎨 Hőmérséklet grafikon rajzolása keverék osztály.
    """

    def _get_temperature_colors(self) -> dict[str, str]:
        """Resolve temperature chart colors."""
        temp_colors = {
            "cold": self.color_palette.get_color("info", "dark") or "#6366f1",
            "moderate": self.color_palette.get_color("primary", "base") or "#C43939",
            "warm": self.color_palette.get_color("warning", "base") or "#f59e0b",
            "hot": self.color_palette.get_color("error", "base") or "#dc2626",
            "comfort": self.color_palette.get_color("success", "light") or "#22c55e",
            "trend_up": self.color_palette.get_color("error", "light") or "#ef4444",
            "trend_down": self.color_palette.get_color("info", "light") or "#8b5cf6",
            "annotation_hot": self.color_palette.get_color("error", "light") or "#fef2f2",
            "annotation_cold": self.color_palette.get_color("info", "light") or "#eff6ff",
        }
        temp_colors["moderate"] = self.weather_colors.get("temperature", "#C43939")
        return temp_colors

    def _plot_temperature_zones(self, temp_colors: dict[str, str]) -> None:
        """Plot background comfort and threshold zones."""
        self.ax.axhspan(-50, 0, alpha=0.1, color=temp_colors["cold"], label="Fagyzóna")
        self.ax.axhspan(25, 50, alpha=0.1, color=temp_colors["hot"], label="Forró zóna")
        self.ax.axhspan(15, 25, alpha=0.05, color=temp_colors["comfort"], label="Komfort zóna")
        for value, color_key, label in [
            (0, "cold", "Fagypont"),
            (25, "warm", "Nyári meleg"),
            (30, "hot", "Hőhullám"),
        ]:
            self.ax.axhline(
                y=value,
                color=temp_colors[color_key],
                linestyle="--",
                alpha=0.7,
                linewidth=2,
                label=label,
            )

    def _plot_temperature_series(self, df: "pd.DataFrame", temp_colors: dict[str, str]) -> None:
        """Plot min, max and mean temperature lines."""
        series_config = [
            ("temp_min", "cold", "Minimum", "o-", 3, 6, 2),
            ("temp_max", "hot", "Maximum", "o-", 3, 6, 2),
            ("temp_mean", "moderate", "Átlag", "s-", 2.5, 5, 1.5),
        ]
        for (
            column,
            color_key,
            label,
            style,
            linewidth,
            markersize,
            markeredgewidth,
        ) in series_config:
            self.ax.plot(
                df["date"],
                df[column],
                style,
                color=temp_colors[color_key],
                linewidth=linewidth,
                markersize=markersize,
                alpha=0.9 if column != "temp_mean" else 0.8,
                label=label,
                markerfacecolor="white",
                markeredgewidth=markeredgewidth,
            )
        self.ax.fill_between(
            df["date"],
            df["temp_min"],
            df["temp_max"],
            alpha=0.2,
            color=temp_colors["warm"],
            label="Napi hőingás",
        )

    def _plot_temperature_trends(self, df: "pd.DataFrame", temp_colors: dict[str, str]) -> None:
        """Plot temperature trend lines."""
        if len(df) <= 3:  # noqa: PLR2004
            return
        x_numeric = np.arange(len(df))
        for column, color_key, label in [
            ("temp_max", "trend_up", "Max trend"),
            ("temp_min", "trend_down", "Min trend"),
        ]:
            trend_line = np.poly1d(np.polyfit(x_numeric, df[column], 1))(x_numeric)
            self.ax.plot(
                df["date"],
                trend_line,
                "--",
                color=temp_colors[color_key],
                alpha=0.6,
                linewidth=2,
                label=label,
            )

    def _annotate_extremes(self, df: "pd.DataFrame", temp_colors: dict[str, str]) -> None:
        """Annotate hottest and coldest visible points."""
        annotations = [
            (
                "temp_max",
                df["temp_max"].idxmax(),
                "🔥 {value:.1f}°C",
                (10, 20),
                temp_colors["annotation_hot"],
                temp_colors["hot"],
                "arc3,rad=0.2",
            ),
            (
                "temp_min",
                df["temp_min"].idxmin(),
                "🧊 {value:.1f}°C",
                (10, -30),
                temp_colors["annotation_cold"],
                temp_colors["cold"],
                "arc3,rad=-0.2",
            ),
        ]
        for (
            column,
            idx,
            label_template,
            offset,
            facecolor,
            edgecolor,
            connection,
        ) in annotations:
            value = df.loc[idx, column]
            date = df.loc[idx, "date"]
            self.ax.annotate(
                label_template.format(value=value),
                xy=(date, value),
                xytext=offset,
                textcoords="offset points",
                bbox={"boxstyle": "round,pad=0.5", "fc": facecolor, "ec": edgecolor, "alpha": 0.8},
                arrowprops={
                    "arrowstyle": "->",
                    "connectionstyle": connection,
                    "color": edgecolor,
                },
            )

    def _plot_enhanced_temperature(self, df: "pd.DataFrame") -> None:
        """
        Fejlett hőmérséklet grafikon rajzolása - PROFESSZIONÁLIS STÍLUS + SIMPLIFIED THEMEMANAGER SZÍNEK.
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: ColorPalette használata professzionális színválasztáshoz
        🔧 KRITIKUS JAVÍTÁS: Az ax.clear() már megtörtént a update_data()-ban.
        """
        print(
            "🎨 DEBUG: _plot_enhanced_temperature() - DUPLIKÁCIÓ MENTES + SIMPLIFIED THEMEMANAGER"
        )
        temp_colors = self._get_temperature_colors()
        print(f"🎨 DEBUG: Using SimplifiedThemeManager colors: {temp_colors}")
        self._plot_temperature_zones(temp_colors)
        self._plot_temperature_series(df, temp_colors)
        self._plot_temperature_trends(df, temp_colors)
        self._annotate_extremes(df, temp_colors)
        self._format_enhanced_temperature_chart(df)
