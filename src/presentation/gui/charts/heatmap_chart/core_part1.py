# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for HeatmapCalendarChart."""

from __future__ import annotations

from .core_support import *


class HeatmapCalendarChartPart1Mixin:  # noqa: D101
    def __init__(self, parent: Optional[QWidget] = None):  # noqa: D107
        super().__init__(figsize=(20, 12), parent=parent)
        self.chart_title = "📅 Konstans Heatmap"
        self.parameter = "temperature_2m_mean"

        # Colorbar tracking
        self._colorbar = None

        # Custom colormap support
        self._custom_cmap = None
        self._custom_norm = None

        # Calendar data
        self._calendar_matrix = None
        self._min_date = None
        self._max_date = None
        self._total_days = 0
        self._first_day_weekday = 0

        logger.info("HeatmapCalendarChart inicializálva - CLEAN VERZIÓ")

    def update_data(self, data: Dict[str, Any]) -> None:
        """Data update"""
        logger.info(f"📅 HeatmapCalendarChart.update_data() (param: {self.parameter})")

        try:
            if self._is_updating:
                logger.debug("⚠️ Heatmap update már folyamatban, skip")
                return

            self._is_updating = True

            # Extract daily data
            df = extract_daily_data(self, data)
            if df.empty:
                logger.warning(f"⚠️ Üres DataFrame ({self.parameter}), heatmap törlése")
                self.clear_chart()
                return

            self.current_data = df

            # Clear figure
            logger.debug("🧹 Figure.clear() - DUPLIKÁCIÓ ELLENI VÉDELEM")
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            self._colorbar = None

            # Apply theme
            self._apply_theme_to_chart()

            # Plot heatmap
            self._plot_365_constant_heatmap(df)

            self.draw()
            self._is_updating = False

            logger.info(f"✅ HeatmapCalendarChart frissítés kész - {self.parameter}")

        except Exception as e:
            logger.error(f"❌ Heatmap calendar chart hiba ({self.parameter}): {e}", exc_info=True)
            self._is_updating = False
            self.clear_chart()

    def _plot_365_constant_heatmap(self, df: pd.DataFrame) -> None:
        """Plot 365 constant heatmap"""
        logger.info(f"🎨 _plot_365_constant_heatmap() ({self.parameter})")

        if df.empty or self.parameter not in df.columns:
            self._plot_heatmap_placeholder()
            return

        # Date range analysis
        self._min_date = df["date"].min()
        self._max_date = df["date"].max()
        self._total_days = (self._max_date - self._min_date).days + 1
        self._first_day_weekday = self._min_date.weekday()

        logger.info(f"🗓️ Időszak: {self._min_date} - {self._max_date} ({self._total_days} nap)")

        # Aggregate to 365 values
        values_365 = aggregate_to_365(self, df[self.parameter].tolist(), self._total_days)

        # Build calendar matrix
        self._calendar_matrix = build_calendar_matrix(self, values_365, self._min_date)

        logger.debug(f"🎯 Kalendár mátrix shape: {self._calendar_matrix.shape}")
        logger.debug("📅 Valódi dátum címkék használata")

        # Validate data
        valid_data_count = np.sum(~np.isnan(self._calendar_matrix))

        if valid_data_count < 10:  # noqa: PLR2004
            logger.warning(f"⚠️ Túl kevés valódi adat ({valid_data_count})")
            self._plot_heatmap_placeholder()
            return

        # Get colormap
        cmap, norm = get_colormap_and_norm(self, self._calendar_matrix)

        # Render pcolormesh
        x_edges = np.arange(54) - 0.5
        y_edges = np.arange(8) - 0.5

        im = self.ax.pcolormesh(
            x_edges,
            y_edges,
            self._calendar_matrix,
            cmap=cmap,
            norm=norm,
            shading="flat",
            edgecolors="lightgray",
            linewidths=0.5,
        )

        # Setup axes and labels
        setup_axes_and_labels(self, self._min_date, self._max_date)

        # Create colorbar
        create_colorbar(self, im)

        # Formatting
        current_colors = get_current_colors()
        text_color = current_colors.get("on_surface", "#1f2937")

        period_text = format_period_text(self, self._min_date, self._max_date, self._total_days)
        full_title = f"{self.chart_title}{period_text}"

        self.ax.set_title(full_title, fontsize=18, fontweight="bold", pad=20, color=text_color)
        self.ax.grid(False)
        self.figure.tight_layout()

        logger.info(f"✅ 365 konstans heatmap kész - {valid_data_count} adat")
