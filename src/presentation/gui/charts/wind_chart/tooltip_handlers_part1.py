# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for WindTooltipHandler."""

from __future__ import annotations

from .tooltip_handlers_support import *


class WindTooltipHandlerPart1Mixin:  # noqa: D101
    def __init__(self, ax, hover_tolerance: int = 15):
        """
        Initialize tooltip handler.

        Args:
            ax: Matplotlib axes
            hover_tolerance: Pixel distance tolerance for hover detection
        """
        self.ax = ax
        self._hover_tolerance = hover_tolerance
        self._tooltip_annotation = None
        self._tooltip_visible = False

    def find_closest_point(self, event, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Find closest data point to mouse event.

        Args:
            event: Mouse event
            df: Current data DataFrame

        Returns:
            Point data dictionary or None
        """
        try:
            if df is None or df.empty:
                return None

            if "date" not in df.columns or "windspeed" not in df.columns:
                return None

            import matplotlib.dates as mdates  # noqa: PLC0415

            plot_dates = mdates.date2num(df["date"])
            windspeeds = df["windspeed"]
            mouse_coords = self.ax.transData.transform((event.xdata, event.ydata))
            closest_idx, min_distance = self._find_closest_index(
                plot_dates, windspeeds, mouse_coords
            )

            # Tolerance check
            if closest_idx is not None and min_distance <= self._hover_tolerance:
                point_data = {
                    "index": closest_idx,
                    "date": df.iloc[closest_idx]["date"],
                    "windspeed": df.iloc[closest_idx]["windspeed"],
                    "pixel_distance": min_distance,
                    "data_source": df.iloc[closest_idx]["_data_source"]
                    if "_data_source" in df.columns
                    else "unknown",
                }
                return point_data

        except Exception as e:
            print(f"⚠️ DEBUG: Wind point calculation error: {e}")

        return None

    def _find_closest_index(
        self, plot_dates: Any, windspeeds: Any, mouse_coords: tuple[float, float]
    ) -> tuple[Optional[int], float]:
        """Find closest visible wind point."""
        mouse_x_display, mouse_y_display = mouse_coords
        closest_idx: Optional[int] = None
        min_distance = float("inf")
        for index, (x_val, y_val) in enumerate(zip(plot_dates, windspeeds, strict=False)):
            if pd.isna(y_val):
                continue
            point_x_display, point_y_display = self.ax.transData.transform((x_val, y_val))
            distance = np.sqrt(
                (mouse_x_display - point_x_display) ** 2 + (mouse_y_display - point_y_display) ** 2
            )
            if distance < min_distance:
                min_distance = distance
                closest_idx = index
        return closest_idx, min_distance

    def format_tooltip_text(self, point_data: Dict[str, Any]) -> str:
        """
        Format tooltip text for wind data.

        Args:
            point_data: Point data dictionary

        Returns:
            Formatted tooltip text
        """
        date = point_data["date"]
        windspeed = point_data["windspeed"]
        data_source = point_data.get("data_source", "unknown")

        # Date formatting
        if isinstance(date, datetime):
            date_str = date.strftime("%Y-%m-%d (%A)")
        else:
            date_str = str(date)

        # Get wind category
        category = get_wind_category(windspeed)
        recommendations = get_wind_recommendations(windspeed)

        # Measurement type
        measurement_type = (
            "Széllökések" if data_source == "wind_gusts_10m_max" else "Szélsebesség (átlag)"
        )

        # Build tooltip lines
        tooltip_lines = [
            f"📅 {date_str}",
            "",
            f"{category['icon']} {measurement_type}: {windspeed:.1f} km/h",
            f"🏷️ {category['name']}",
            f"📊 Beaufort skála: {category['beaufort']}",
            f"🌬️ {category['description']}",
            "",
            f"📈 Intenzitás: {category['intensity']}",
            category["effects"],
        ]

        # Add recommendations
        if recommendations:
            tooltip_lines.append("")
            tooltip_lines.extend(recommendations)

        # Fallback indicator
        if data_source == "windspeed_10m_max":
            tooltip_lines.extend(["", "ℹ️ Fallback adatforrás (átlag szélsebesség)"])  # noqa: RUF001

        return "\n".join(tooltip_lines)
