# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Merged part1+part3 for TemperatureTooltipHandlerMixin."""

from __future__ import annotations

from .tooltip_handler_support import *


class TemperatureTooltipHandlerMixinPart1Mixin:  # noqa: D101
    def _get_temperature_columns(self, df: pd.DataFrame) -> list[str]:
        """Return available temperature columns in priority order."""
        return [column for column in ["temp_mean", "temp_max", "temp_min"] if column in df.columns]

    def _get_mouse_display_coordinates(self, event) -> tuple[float, float]:
        """Convert mouse data coordinates to display coordinates."""
        return self.ax.transData.transform((event.xdata, event.ydata))

    def _find_closest_temperature_point(
        self,
        df: pd.DataFrame,
        plot_dates: Any,
        temp_columns: list[str],
        mouse_coords: tuple[float, float],
    ) -> tuple[Optional[int], float, Optional[str], Any]:
        """Find closest temperature point across all lines."""
        mouse_x_display, mouse_y_display = mouse_coords
        closest_idx: Optional[int] = None
        min_distance = float("inf")
        closest_temp_col: Optional[str] = None
        closest_temp_value: Any = None

        for temp_col in temp_columns:
            for index, (x_val, y_val) in enumerate(zip(plot_dates, df[temp_col], strict=False)):
                if pd.isna(y_val):
                    continue
                point_x_display, point_y_display = self.ax.transData.transform((x_val, y_val))
                distance = np.sqrt(
                    (mouse_x_display - point_x_display) ** 2
                    + (mouse_y_display - point_y_display) ** 2
                )
                if distance < min_distance:
                    min_distance = distance
                    closest_idx = index
                    closest_temp_col = temp_col
                    closest_temp_value = y_val

        return closest_idx, min_distance, closest_temp_col, closest_temp_value

    @staticmethod
    def _build_point_data(
        df: pd.DataFrame,
        closest_idx: int,
        min_distance: float,
        closest_temp_col: str,
        closest_temp_value: Any,
        temp_columns: list[str],
    ) -> Dict[str, Any]:
        """Build tooltip point payload."""
        point_data = {
            "index": closest_idx,
            "date": df.iloc[closest_idx]["date"],
            "primary_temp": closest_temp_value,
            "primary_temp_column": closest_temp_col,
            "pixel_distance": min_distance,
            "closest_line": closest_temp_col,
        }
        for column in temp_columns:
            point_data[column] = df.iloc[closest_idx][column]
        return point_data

    def _find_closest_chart_point(self, event) -> Optional[Dict[str, Any]]:
        """
        Multi-line tooltip detection - all temperature lines.

        Enhanced logic:
        - temp_mean, temp_max, temp_min all lines checked
        - Closest point from any line
        """
        try:
            if (
                not hasattr(self, "current_data")
                or self.current_data is None
                or self.current_data.empty
            ):
                return None

            df = self.current_data

            if "date" not in df.columns:
                return None

            import matplotlib.dates as mdates  # noqa: PLC0415

            plot_dates = mdates.date2num(df["date"])
            temp_columns = self._get_temperature_columns(df)
            if not temp_columns:
                return None

            closest_idx, min_distance, closest_temp_col, closest_temp_value = (
                self._find_closest_temperature_point(
                    df,
                    plot_dates,
                    temp_columns,
                    self._get_mouse_display_coordinates(event),
                )
            )

            if closest_idx is not None and min_distance <= self._hover_tolerance:
                return self._build_point_data(
                    df,
                    closest_idx,
                    min_distance,
                    closest_temp_col,
                    closest_temp_value,
                    temp_columns,
                )

        except Exception as e:
            print(f"⚠️ DEBUG: Temperature point calculation error: {e}")

        return None

    def _show_tooltip(self, event, point_data: Dict[str, Any]) -> None:  # noqa: ARG002
        """
        Smart tooltip positioning - dynamic placement.

        Intelligent tooltip:
        - Professional design
        - Weather-specific formatting
        - Smart positioning: automatically avoids chart edges
        """
        if not hasattr(self, "ax"):
            return

        # Clear previous tooltip
        self._hide_tooltip()

        # Format tooltip text
        tooltip_text = self._format_tooltip_text(point_data)

        # Determine coordinates
        import matplotlib.dates as mdates  # noqa: PLC0415

        x_pos = mdates.date2num(point_data["date"])
        y_pos = point_data["primary_temp"]

        # Smart positioning logic
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        x_relative = (x_pos - xlim[0]) / (xlim[1] - xlim[0])
        y_relative = (y_pos - ylim[0]) / (ylim[1] - ylim[0])

        # Dynamic offset calculation
        if y_relative > 0.7:  # noqa: PLR2004
            offset_y = -80
            va_align = "top"
        else:
            offset_y = 50
            va_align = "bottom"

        if x_relative > 0.8:  # noqa: PLR2004
            offset_x = -100
            ha_align = "right"
        else:
            offset_x = 40
            ha_align = "left"

        current_colors = get_current_colors()

        self.tooltip_annotation = self.ax.annotate(
            tooltip_text,
            xy=(x_pos, y_pos),
            xytext=(offset_x, offset_y),
            textcoords="offset points",
            bbox={
                "boxstyle": "round,pad=1.0",
                "facecolor": "lightyellow",
                "edgecolor": current_colors.get("border", "#34495E"),
                "linewidth": 2,
                "alpha": 0.95,
            },
            arrowprops={
                "arrowstyle": "->",
                "color": current_colors.get("border", "#34495E"),
                "lw": 2,
                "alpha": 0.8,
            },
            fontsize=10,
            fontweight="bold",
            ha=ha_align,
            va=va_align,
            zorder=1000,
        )

        self._tooltip_visible = True
        self._tooltip_annotation = self.tooltip_annotation

        if hasattr(self, "draw_idle"):
            self.draw_idle()

    def _hide_tooltip(self) -> None:
        """Tooltip hiding - clean removal."""
        if self._tooltip_annotation:
            try:
                self._tooltip_annotation.remove()
            except Exception as e:
                print(f"⚠️ DEBUG: Tooltip remove error: {e}")

            self._tooltip_annotation = None
            self._tooltip_visible = False

            if hasattr(self, "draw_idle"):
                self.draw_idle()
