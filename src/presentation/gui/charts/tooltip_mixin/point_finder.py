#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
WeatherTooltipMixin Point Finder - Find closest chart point.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

import matplotlib.dates as mdates
import numpy as np

if TYPE_CHECKING:
    from .core import WeatherTooltipMixin


class PointFinder:
    """Find closest data point to mouse event."""

    def __init__(self, mixin: "WeatherTooltipMixin"):
        """
        Initialize point finder.

        Args:
            mixin: WeatherTooltipMixin instance
        """
        self._mixin = mixin

    def find_closest(self, event) -> Optional[Dict[str, Any]]:
        """
        Find closest chart point algorithm.

        Args:
            event: Mouse event

        Returns:
            Point data dictionary or None
        """
        if not hasattr(self._mixin, "ax") or not hasattr(self._mixin, "current_data"):
            return None

        # Chart-specific implementation required
        return self.find_closest_temperature(event)

    def _get_temperature_columns(self, df: Any) -> list[str]:
        """Return available temperature columns."""
        return [
            col for col in ["temp_mean", "temp_max", "temp_min"] if col in df.columns
        ]

    def _find_closest_index(
        self, plot_dates: Any, temperatures: Any, mouse_coords: tuple[float, float]
    ) -> tuple[Optional[int], float]:
        """Find closest index for a single temperature series."""
        mouse_x_display, mouse_y_display = mouse_coords
        closest_idx: Optional[int] = None
        min_distance = float("inf")
        for index, (x_val, y_val) in enumerate(zip(plot_dates, temperatures)):
            point_x_display, point_y_display = self._mixin.ax.transData.transform(
                (x_val, y_val)
            )
            distance = np.sqrt(
                (mouse_x_display - point_x_display) ** 2
                + (mouse_y_display - point_y_display) ** 2
            )
            if distance < min_distance:
                min_distance = distance
                closest_idx = index
        return closest_idx, min_distance

    @staticmethod
    def _build_point_data(
        df: Any,
        closest_idx: int,
        primary_temp_col: str,
        temperatures: Any,
        min_distance: float,
        temp_columns: list[str],
    ) -> Dict[str, Any]:
        """Build point payload for tooltip rendering."""
        point_data = {
            "index": closest_idx,
            "date": df.iloc[closest_idx]["date"],
            "primary_temp": temperatures.iloc[closest_idx],
            "primary_temp_column": primary_temp_col,
            "pixel_distance": min_distance,
        }
        for col in temp_columns:
            if col != primary_temp_col:
                point_data[col] = df.iloc[closest_idx][col]
        return point_data

    def find_closest_temperature(self, event) -> Optional[Dict[str, Any]]:
        """
        Find closest temperature chart point.

        Args:
            event: Mouse event

        Returns:
            Point data dictionary or None
        """
        try:
            if (
                not hasattr(self._mixin, "current_data")
                or self._mixin.current_data is None
                or self._mixin.current_data.empty
            ):
                return None

            df = self._mixin.current_data

            if "date" not in df.columns:
                return None

            plot_dates = mdates.date2num(df["date"])
            temp_columns = self._get_temperature_columns(df)
            if not temp_columns:
                return None

            primary_temp_col = temp_columns[0]
            temperatures = df[primary_temp_col]
            closest_idx, min_distance = self._find_closest_index(
                plot_dates,
                temperatures,
                self._mixin.ax.transData.transform((event.xdata, event.ydata)),
            )

            # Tolerance check
            if closest_idx is not None and min_distance <= self._mixin._hover_tolerance:
                return self._build_point_data(
                    df,
                    closest_idx,
                    primary_temp_col,
                    temperatures,
                    min_distance,
                    temp_columns,
                )

        except Exception as e:
            print(f"⚠️ DEBUG: Point calculation error: {e}")

        return None
