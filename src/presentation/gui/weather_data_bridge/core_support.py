# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
"""Weather Data Bridge - Multi-City Engine → Folium Map Integration."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.domain.entities.analytics_models import AnalyticsResult
from src.domain.entities.weather import CityWeatherResult
from src.domain.value_objects.enums import AnalyticsMetric
from src.presentation.gui.weather_data_bridge.constants import (
    DISPLAY_PARAMETER_MAP,
    METRIC_MAP,
    OVERLAY_CONFIGS,
)
from src.presentation.gui.weather_data_bridge.data import WeatherOverlayData

logger = logging.getLogger(__name__)
