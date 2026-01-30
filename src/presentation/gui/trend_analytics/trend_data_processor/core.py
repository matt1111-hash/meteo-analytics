"""Trend Data Processor Core - API-based trend data processing."""
import logging
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal

from src.domain.ports import CityManagerPort, WeatherClientPort, get_city_manager_port, get_weather_client_port

from src.presentation.gui.trend_analytics.trend_data_processor.calculator import calculate_trend_statistics
from src.presentation.gui.trend_analytics.trend_data_processor.constants import (
    TIME_RANGES,
    TREND_PARAMETERS,
)
from src.presentation.gui.trend_analytics.trend_data_processor.fetcher import (
    calculate_date_range,
    fetch_trend_data_batch,
    get_api_field,
    get_settlement_coordinates,
)

logger = logging.getLogger(__name__)


class TrendDataProcessor(QObject):
    """
    API-based trend data processor.

    Capabilities:
    - 3178 Hungarian settlement coordinate lookup
    - Multi-year API calls (5-10-55 years)
    - Professional trend calculation
    - Confidence interval calculation
    - Statistical significance testing
    """

    progress_updated = Signal(int)
    data_received = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.city_manager = get_city_manager_port()
        self.weather_client = get_weather_client_port()
        self.trend_parameters = TREND_PARAMETERS
        self.time_ranges = TIME_RANGES

        logger.info("TrendDataProcessor initialized")

    def get_settlement_coordinates(self, settlement_name: str) -> Optional[tuple]:
        """Get settlement coordinates from CityManager."""
        return get_settlement_coordinates(self.city_manager, settlement_name)

    def fetch_trend_data(self, settlement_name: str, parameter: str, time_range: str) -> None:
        """Fetch trend data via API (background thread)."""
        try:
            self.progress_updated.emit(10)

            coordinates = self.get_settlement_coordinates(settlement_name)
            if not coordinates:
                self.error_occurred.emit(f"Coordinates not found: {settlement_name}")
                return

            lat, lon = coordinates
            self.progress_updated.emit(20)

            start_date, end_date = calculate_date_range(time_range)
            years = self.time_ranges.get(time_range, 5)

            self.progress_updated.emit(30)

            # Multi-year API fetch
            def progress_callback(progress: int) -> None:
                self.progress_updated.emit(progress)

            weather_data = fetch_trend_data_batch(
                self.weather_client, lat, lon, start_date, end_date, progress_callback
            )

            if not weather_data:
                self.error_occurred.emit("No data available for selected period")
                return

            self.progress_updated.emit(70)

            api_field = get_api_field(parameter)
            if not api_field:
                self.error_occurred.emit(f"Unknown parameter: {parameter}")
                return

            trend_results = calculate_trend_statistics(
                weather_data, api_field, settlement_name, parameter, time_range, years
            )

            self.progress_updated.emit(90)

            if trend_results:
                self.data_received.emit(trend_results)
            else:
                self.error_occurred.emit("Trend calculation error")

            self.progress_updated.emit(100)

        except Exception as e:
            logger.error(f"Trend fetch error: {e}")
            self.error_occurred.emit(f"Critical error: {str(e)}")
