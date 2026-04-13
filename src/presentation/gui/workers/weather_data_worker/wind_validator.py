#!/usr/bin/env python3
# mypy: ignore-errors

"""
WeatherDataWorker Wind Validator - Validate wind gusts data.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import WeatherDataWorker


class WindValidator:
    """Validate wind gusts data."""

    def __init__(self, worker: "WeatherDataWorker"):
        """
        Initialize wind validator.

        Args:
            worker: WeatherDataWorker instance
        """
        self._worker = worker

    def validate(self) -> None:
        """Validate wind gusts data and log debug info."""
        if not self._worker.weather_data:
            return

        daily_data = self._worker.weather_data.get("daily", {})
        hourly_data = self._worker.weather_data.get("hourly", {})

        daily_record_count = len(daily_data.get("time", []))
        hourly_record_count = len(hourly_data.get("time", []))
        wind_gusts_count = len(hourly_data.get("wind_gusts_10m", []))

        print(f"✅ DEBUG: {daily_record_count} napi rekord lekérdezve")
        print(f"✅ DEBUG: {hourly_record_count} óránkénti rekord lekérdezve")
        print(f"🌪️ DEBUG: {wind_gusts_count} széllökés rekord lekérdezve")

        # Quality check
        if wind_gusts_count > 0:
            wind_gusts = hourly_data.get("wind_gusts_10m", [])
            valid_gusts = [g for g in wind_gusts if g is not None and g > 0]

            if valid_gusts:
                max_gust = max(valid_gusts)
                print(f"🌪️ DEBUG: Maximum széllökés: {max_gust:.1f} km/h")

                if max_gust < 60:  # noqa: PLR2004
                    print(f"⚠️  DEBUG: Széllökés még mindig alacsony: {max_gust:.1f} km/h")
                else:
                    print(f"✅ DEBUG: Realistic széllökés értékek: {max_gust:.1f} km/h")
            else:
                print("❌ DEBUG: Nincs érvényes széllökés adat!")
        else:
            print("❌ DEBUG: Nincs széllökés adat az API válaszban!")
