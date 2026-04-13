#!/usr/bin/env python3
# mypy: ignore-errors

"""
WeatherTooltipMixin - Tooltip functionality for weather charts.

🎯 TOOLTIP MIXIN - CONSERVATIVE INTEGRATION
🛡️ ZERO RISK - Reusable tooltip functionality
"""

# Core mixin class
from .core import WeatherTooltipMixin


# Helper function
def add_tooltips_to_chart(chart_instance, hover_tolerance: int = 15) -> None:
    """
    🎯 TOOLTIP AKTIVÁLÁS HELPER - KONZERVATÍV INTEGRÁCIÓ

    Args:
        chart_instance: WeatherChart instance (+ WeatherTooltipMixin)
        hover_tolerance: Hover érzékenység pixelekben

    Usage:
        ```python
        add_tooltips_to_chart(my_temperature_chart, hover_tolerance=20)
        ```
    """
    if hasattr(chart_instance, "enable_tooltips"):
        chart_instance.enable_tooltips(hover_tolerance)
        print(f"✅ DEBUG: Tooltips aktiválva - {chart_instance.__class__.__name__}")
    else:
        print(f"⚠️ DEBUG: {chart_instance.__class__.__name__} nem támogatja a tooltip-okat")


__all__ = ["WeatherTooltipMixin", "add_tooltips_to_chart"]
