# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for MultiYearComparisonChart."""

from __future__ import annotations

from .comparison_chart_support import *


class MultiYearComparisonChartPart2Mixin:
    def _get_trend_colors(self) -> Dict[str, Any]:
        """Build comparison and trend color palette."""
        return {
            "year_comparison": [
                self.color_palette.get_color("primary", "base") or "#C43939",
                self.color_palette.get_color("success", "base") or "#10b981",
                self.color_palette.get_color("warning", "base") or "#f59e0b",
                self.color_palette.get_color("error", "base") or "#dc2626",
                self.color_palette.get_color("info", "base") or "#6366f1",
                self.color_palette.get_color("primary", "light") or "#3b82f6",
            ],
            "average_trend": self.color_palette.get_color("info", "dark") or "#4338ca",
        }

    def _plot_year_series(
        self, df: pd.DataFrame, years: list[Any], trend_colors: Dict[str, Any]
    ) -> None:
        """Plot yearly comparison lines and fill bands."""
        for index, year in enumerate(years):
            year_data = df[df["year"] == year].copy()
            color = trend_colors["year_comparison"][
                index % len(trend_colors["year_comparison"])
            ]
            self.ax.plot(
                year_data["day_of_year"],
                year_data["temp_mean"],
                color=color,
                linewidth=2.5,
                alpha=0.8,
                label=f"{year}",
            )
            if index < 2:
                self.ax.fill_between(
                    year_data["day_of_year"],
                    year_data["temp_min"],
                    year_data["temp_max"],
                    color=color,
                    alpha=0.1,
                )

    def _plot_average_trend(self, df: pd.DataFrame, trend_color: str) -> None:
        """Plot average trend line when enough data is available."""
        if len(df) <= 30:
            return
        trend_data = df.groupby("day_of_year")["temp_mean"].mean().reset_index()
        self.ax.plot(
            trend_data["day_of_year"],
            trend_data["temp_mean"],
            "--",
            linewidth=3,
            alpha=0.6,
            label="Átlagos trend",
            color=trend_color,
        )

    def _get_seasonal_colors(self) -> Dict[str, str]:
        """Build seasonal marker colors."""
        return {
            "spring": self.color_palette.get_color("success", "light") or "#86efac",
            "summer": self.color_palette.get_color("warning", "light") or "#fde047",
            "autumn": self.color_palette.get_color("error", "light") or "#fb7185",
            "winter": self.color_palette.get_color("info", "light") or "#a5b4fc",
        }

    def _plot_season_markers(self, seasonal_colors: Dict[str, str]) -> None:
        """Plot seasonal boundary markers."""
        season_markers = {
            "spring": (79, "Tavasz"),
            "summer": (172, "Nyár"),
            "autumn": (266, "Ősz"),
            "winter": (355, "Tél"),
        }
        for season, (day, label) in season_markers.items():
            self.ax.axvline(
                x=day,
                color=seasonal_colors[season],
                linestyle=":",
                alpha=0.7,
                label=label,
            )

    def _configure_axes(
        self, years: list[Any], current_colors: Dict[str, str], text_color: str
    ) -> None:
        """Configure axis titles, labels and ticks."""
        self.ax.set_title(
            f"{self.chart_title} ({min(years)}-{max(years)})",
            fontsize=16,
            fontweight="bold",
            pad=20,
            color=text_color,
        )
        self.ax.set_xlabel("Nap az évben", fontsize=12, color=text_color)
        self.ax.set_ylabel("Átlag hőmérséklet (°C)", fontsize=12, color=text_color)
        self.ax.tick_params(colors=text_color)
        month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
        month_names = [
            "Jan",
            "Feb",
            "Már",
            "Ápr",
            "Máj",
            "Jún",
            "Júl",
            "Aug",
            "Szep",
            "Okt",
            "Nov",
            "Dec",
        ]
        self.ax.set_xticks(month_starts)
        self.ax.set_xticklabels(month_names)
        self.ax.set_xlim(1, 366)

        if self.grid_enabled:
            grid_color = current_colors.get("border", "#d1d5db")
            grid_alpha = (
                0.3 if self.theme_manager.get_current_theme() == "light" else 0.2
            )
            self.ax.grid(True, alpha=grid_alpha, color=grid_color)

    def _configure_legend_and_stats(
        self,
        years: list[Any],
        df: pd.DataFrame,
        current_colors: Dict[str, str],
        text_color: str,
    ) -> None:
        """Configure legend and statistics box."""
        if self.legend_enabled:
            legend = self.ax.legend(
                bbox_to_anchor=(1.05, 1),
                loc="upper left",
                ncol=1,
                fontsize=10,
                framealpha=0.9,
            )
            legend.get_frame().set_facecolor(current_colors.get("surface", "#ffffff"))
            legend.get_frame().set_edgecolor(current_colors.get("border", "#d1d5db"))

        stats_text = (
            f"📊 {len(years)} év összehasonlítva\n"
            f"📅 Időszak: {years[0]}-{years[-1]}\n"
            f"📈 Rekordok száma: {len(df)}"
        )
        self.ax.text(
            0.02,
            0.98,
            stats_text,
            transform=self.ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            color=text_color,
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor=current_colors.get("surface_variant", "#f9fafb"),
                edgecolor=current_colors.get("border", "#d1d5db"),
                alpha=0.8,
            ),
        )

    def _plot_multi_year_comparison(self, df: pd.DataFrame) -> None:
        """
        Többévi összehasonlítás megrajzolása - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: ColorPalette trend színek használata
        """
        print(
            "🎨 DEBUG: _plot_multi_year_comparison() - DUPLIKÁCIÓ MENTES + SIMPLIFIED THEMEMANAGER"
        )

        # Évek azonosítása
        years = sorted(df["year"].unique())

        if len(years) < 2:
            self._plot_comparison_placeholder()
            return

        trend_colors = self._get_trend_colors()
        current_colors = get_current_colors()
        text_color = current_colors.get("on_surface", "#1f2937")
        print(f"🎨 DEBUG: Using SimplifiedThemeManager trend colors: {trend_colors}")
        self._plot_year_series(df, years, trend_colors)
        self._plot_average_trend(df, trend_colors["average_trend"])
        self._plot_season_markers(self._get_seasonal_colors())
        self._configure_axes(years, current_colors, text_color)
        self._configure_legend_and_stats(years, df, current_colors, text_color)
        self.figure.tight_layout(rect=[0, 0, 0.85, 1])
