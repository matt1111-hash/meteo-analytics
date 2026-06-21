#!/usr/bin/env python3
# mypy: ignore-errors
"""
Trend Worker Module

🔥 Background worker thread for trend analytics

Képességek:
- Háttérszálas futtatás a UI blokkolás elkerülésére
- Multi-year API hívások kezelése
- Signal-alapú kommunikáció

Fájl: src/presentation/gui/trend_analytics/trend_worker.py
"""

import logging

from PySide6.QtCore import QThread, Signal

from src.domain.ports import CityManagerPort, WeatherClientPort

from .trend_data_processor import TrendDataProcessor

# Logging beállítás
logger = logging.getLogger(__name__)


class TrendAnalyticsWorker(QThread):
    """
    🔥 BACKGROUND WORKER THREAD - API HÍVÁSOK HÁTTÉRBEN

    A trend elemzés hosszú ideig tart (multi-year API hívások),
    ezért háttérszálban futtatjuk a UI blokkolás elkerülésére.
    """

    # Signals
    progress_updated = Signal(int)
    data_received = Signal(dict)
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(  # noqa: D107
        self,
        settlement_name: str,
        parameter: str,
        time_range: str,
        city_manager: CityManagerPort,
        weather_client: WeatherClientPort,
    ):
        super().__init__()
        self.settlement_name = settlement_name
        self.parameter = parameter
        self.time_range = time_range
        self.processor = TrendDataProcessor(city_manager, weather_client)

        # Signal routing
        self.processor.progress_updated.connect(self.progress_updated.emit)
        self.processor.data_received.connect(self.data_received.emit)
        self.processor.error_occurred.connect(self.error_occurred.emit)

    def run(self) -> None:
        """Háttérszál futtatása"""
        try:
            logger.info(
                f"🔥 WORKER THREAD START: {self.settlement_name} - {self.parameter} - {self.time_range}"
            )

            self.processor.fetch_trend_data(self.settlement_name, self.parameter, self.time_range)

        except Exception as e:
            logger.error(f"❌ Worker thread hiba: {e}")
            self.error_occurred.emit(f"Háttérszál hiba: {e!s}")
        finally:
            self.finished.emit()
