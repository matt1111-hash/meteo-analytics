#!/usr/bin/env python3
# mypy: ignore-errors

"""
Wind Chart Plotter - Plot wind data with Hungarian categories.
🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY: 43-61-90-119 km/h küszöbök
"""

from typing import TYPE_CHECKING

import pandas as pd

from src.presentation.gui.theme_manager import get_current_colors

from .wind_categories import (
    HUNGARIAN_WIND_THRESHOLDS,
    get_wind_category,
)

if TYPE_CHECKING:
    from .core import WindChart


class WindPlotter:
    """
    Plot wind data with Hungarian meteorological categories.

    🌪️ MAGYAR SZÉLKATEGÓRIÁK:
    - Erős szél (43 km/h)
    - Viharos szél (61 km/h)
    - Erős vihar (90 km/h)
    - Orkán (119 km/h)
    """

    def __init__(self, chart: "WindChart"):
        """
        Initialize wind plotter.

        Args:
            chart: WindChart instance
        """
        self.chart = chart

    def plot(self, df: pd.DataFrame) -> None:
        """
        Plot wind data with Hungarian categories.

        Args:
            df: DataFrame with date and windspeed columns
        """
        # Get wind colors from theme
        wind_colors = self._get_wind_colors()

        # Get data source
        data_source = df["_data_source"].iloc[0] if "_data_source" in df.columns else "unknown"

        # Plot wind line and fill
        line_label = (
            "Max széllökések"
            if data_source == "wind_gusts_10m_max"
            else "Max szélsebesség (fallback)"
        )
        self.chart.ax.plot(
            df["date"],
            df["windspeed"],
            color=wind_colors["moderate"],
            linewidth=2.5,
            alpha=0.9,
            label=line_label,
        )
        self.chart.ax.fill_between(
            df["date"], 0, df["windspeed"], alpha=0.3, color=wind_colors["light"]
        )

        # Draw Hungarian threshold lines
        self._draw_threshold_lines(wind_colors, df)

        # Annotate maximum with category
        self._annotate_maximum(wind_colors, df)

    def _get_wind_colors(self) -> dict:
        """Get wind colors from theme palette."""
        color_palette = self.chart.color_palette
        weather_colors = self.chart.weather_colors

        wind_colors = {
            "moderate": color_palette.get_color("success", "base") or "#10b981",
            "light": color_palette.get_color("success", "light") or "#86efac",
            "strong": color_palette.get_color("warning", "base") or "#f59e0b",
            "stormy": color_palette.get_color("warning", "dark") or "#d97706",
            "severe_storm": color_palette.get_color("error", "light") or "#f87171",
            "hurricane": color_palette.get_color("error", "base") or "#dc2626",
        }

        # Weather wind color integration
        weather_wind_color = weather_colors.get("wind", "#10b981")
        wind_colors["moderate"] = weather_wind_color

        return wind_colors

    def _draw_threshold_lines(self, wind_colors: dict, df: pd.DataFrame) -> None:
        """
        Draw Hungarian meteorological threshold lines.

        Args:
            wind_colors: Color dictionary for wind categories
            df: DataFrame with wind data
        """
        max_wind = df["windspeed"].max() if not df.empty else 50

        # 43 km/h - Erős szél
        if max_wind >= 30:  # noqa: PLR2004
            self.chart.ax.axhline(
                y=HUNGARIAN_WIND_THRESHOLDS["strong_wind"],
                color=wind_colors["strong"],
                linestyle="--",
                alpha=0.8,
                linewidth=2,
                label="🌬️ Erős szél (43 km/h)",
            )

        # 61 km/h - Viharos szél
        if max_wind >= 45:  # noqa: PLR2004
            self.chart.ax.axhline(
                y=HUNGARIAN_WIND_THRESHOLDS["stormy_wind"],
                color=wind_colors["stormy"],
                linestyle="--",
                alpha=0.8,
                linewidth=2,
                label="🌪️ Viharos szél (61 km/h)",
            )

        # 90 km/h - Erős vihar
        if max_wind >= 70:  # noqa: PLR2004
            self.chart.ax.axhline(
                y=HUNGARIAN_WIND_THRESHOLDS["severe_storm"],
                color=wind_colors["severe_storm"],
                linestyle="--",
                alpha=0.8,
                linewidth=2,
                label="⚠️ Erős vihar (90 km/h)",
            )

        # 119 km/h - Orkán
        if max_wind >= 100:  # noqa: PLR2004
            self.chart.ax.axhline(
                y=HUNGARIAN_WIND_THRESHOLDS["hurricane"],
                color=wind_colors["hurricane"],
                linestyle="--",
                alpha=0.9,
                linewidth=2.5,
                label="🚨 Orkán (119 km/h)",
            )

    def _annotate_maximum(self, wind_colors: dict, df: pd.DataFrame) -> None:
        """
        Annotate maximum wind value with Hungarian category.

        Args:
            wind_colors: Color dictionary for wind categories
            df: DataFrame with wind data
        """
        if df.empty:
            return

        max_wind_idx = df["windspeed"].idxmax()
        max_wind_date = df.loc[max_wind_idx, "date"]
        max_wind_val = df.loc[max_wind_idx, "windspeed"]

        # Get category info
        category = get_wind_category(max_wind_val)
        annotation_color = wind_colors[category["color_key"]]

        # Current colors
        current_colors = get_current_colors()

        # Annotate
        self.chart.ax.annotate(
            f"{category['icon']} {max_wind_val:.1f} km/h\n({category['name']})",
            xy=(max_wind_date, max_wind_val),
            xytext=(15, 25),
            textcoords="offset points",
            bbox={
                "boxstyle": "round,pad=0.5",
                "facecolor": current_colors.get("surface_variant", "#f9fafb"),
                "edgecolor": annotation_color,
                "alpha": 0.9,
            },
            arrowprops={
                "arrowstyle": "->",
                "connectionstyle": "arc3,rad=0.2",
                "color": annotation_color,
                "lw": 2,
            },
        )
