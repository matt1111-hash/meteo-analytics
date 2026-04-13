# mypy: ignore-errors
"""Weather Data Bridge - re-export for backward compatibility."""

from src.presentation.gui.weather_data_bridge import (
    WeatherDataBridge,
    WeatherOverlayData,
)

__all__ = ["WeatherDataBridge", "WeatherOverlayData"]
