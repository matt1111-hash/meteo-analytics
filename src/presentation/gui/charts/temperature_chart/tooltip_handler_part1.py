# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for TemperatureTooltipHandlerMixin."""

from __future__ import annotations

from .tooltip_handler_support import *


class TemperatureTooltipHandlerMixinPart1Mixin:
    def _get_temperature_columns(self, df: pd.DataFrame) -> list[str]:
        """Return available temperature columns in priority order."""
        return [
            column
            for column in ["temp_mean", "temp_max", "temp_min"]
            if column in df.columns
        ]

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
            for index, (x_val, y_val) in enumerate(zip(plot_dates, df[temp_col])):
                if pd.isna(y_val):
                    continue
                point_x_display, point_y_display = self.ax.transData.transform(
                    (x_val, y_val)
                )
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
        🎯 MULTI-LINE TOOLTIP DETECTION - MINDEN VONALRA REAGÁL!

        🔧 ENHANCED LOGIC:
        - temp_mean, temp_max, temp_min ÖSSZES vonal ellenőrzése
        - Legközelebbi pont bármelyik vonalról
        - Professional tooltip adatok minden hőmérséklet típussal
        """
        try:
            if (
                not hasattr(self, "current_data")
                or self.current_data is None
                or self.current_data.empty
            ):
                return None

            df = self.current_data

            # Matplotlib dátum koordináták
            if "date" not in df.columns:
                return None

            import matplotlib.dates as mdates

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
