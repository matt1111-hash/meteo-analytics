"""
AnalysisWorker Core - Main worker class with signals and state management.
"""

import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal

from .component_initializer import ComponentInitializer
from .analysis_runners import AnalysisRunners
from .data_converter import DataConverter
from .interrupt_handler import InterruptHandler


# Import checks (CA compliant - uses ports and Domain layer)
try:
    from src.analytics.ports import get_multi_city_engine_port, MultiCityEnginePort
    from src.domain.ports import get_weather_client_port, WeatherClientPort
    from src.domain.value_objects.enums import AnalysisType, DataProvider
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ AnalysisWorker import error: {e}")
    IMPORTS_OK = False
    get_multi_city_engine_port = None
    get_weather_client_port = None
    MultiCityEnginePort = None
    WeatherClientPort = None


class AnalysisWorker(QThread):
    """
    HÁTTÉRSZÁL WORKER - UI Thread Felszabadítása

    JELZÉSEK:
    - progress_updated(str, int): Progress szöveg + százalék
    - analysis_completed(dict): Sikeres elemzés eredménye
    - analysis_failed(str): Hiba üzenet
    - analysis_cancelled(): Megszakítás megerősítése

    INTERRUPT TÁMOGATÁS:
    - QThread.requestInterruption() használata
    - Periodikus isInterruptionRequested() ellenőrzés
    - Graceful shutdown minden lépésnél
    """

    # === WORKER SIGNALS ===
    progress_updated = Signal(str, int)
    analysis_completed = Signal(dict)
    analysis_failed = Signal(str)
    analysis_cancelled = Signal()

    def __init__(self, parent=None):
        """
        Initialize AnalysisWorker.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)

        # === WORKER STATE ===
        self._request_data: Optional[Dict[str, Any]] = None
        self._mutex = QMutex()

        # === ANALYTICS COMPONENTS (using ports - CA compliant) ===
        self._multi_city_engine: Optional[MultiCityEnginePort] = None
        self._weather_client: Optional[WeatherClientPort] = None

        # === LOGGING ===
        self._logger = logging.getLogger(__name__)

        # === HELPERS ===
        self._component_initializer = ComponentInitializer(self)
        self._analysis_runners = AnalysisRunners(self)
        self._data_converter = DataConverter(self)
        self._interrupt_handler = InterruptHandler(self)

    def setup_analysis_request(self, request_data: Dict[str, Any]):
        """
        ELEMZÉSI KÉRÉS BEÁLLÍTÁSA

        Args:
            request_data: Teljes kérés paraméterek
        """
        with QMutexLocker(self._mutex):
            self._request_data = request_data.copy()
            self._logger.info(f"Worker setup: {request_data.get('analysis_type', 'unknown')}")

    def run(self):
        """FŐSZÁL FUTÁS - Itt történik a tényleges munka"""
        try:
            self._logger.info("AnalysisWorker futás elkezdve")

            # === 1. PARAMÉTER VALIDÁCIÓ ===
            if not self._validate_request():
                return

            # === 2. KOMPONENSEK INICIALIZÁLÁSA ===
            if not self._component_initializer.initialize():
                return

            # === 3. ELEMZÉS TÍPUS ALAPJÁN DISPATCH ===
            analysis_type = self._request_data.get('analysis_type', '')
            self._analysis_runners.run_analysis(analysis_type)

        except Exception as e:
            self._logger.error(f"Worker kritikus hiba: {str(e)}")
            import traceback
            self._logger.error(traceback.format_exc())
            self._emit_error(f"Váratlan hiba: {str(e)}")

    def _validate_request(self) -> bool:
        """Kérés paraméterek validálása"""
        if self._interrupt_handler.check("Validáció"):
            return False

        with QMutexLocker(self._mutex):
            if not self._request_data:
                self._emit_error("Hiányzó kérés adatok")
                return False

            required_fields = ['analysis_type', 'date_range']
            for field in required_fields:
                if field not in self._request_data:
                    self._emit_error(f"Hiányzó kötelező mező: {field}")
                    return False

        self._emit_progress("Paraméterek validálva", 10)
        return True

    def _emit_progress(self, message: str, percentage: int):
        """Thread-safe progress jelzés"""
        self.progress_updated.emit(message, percentage)

        # Qt esemény feldolgozás (responsive UI)
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

    def _emit_error(self, error_message: str):
        """Thread-safe error jelzés"""
        self._logger.error(f"Worker hiba: {error_message}")
        self.analysis_failed.emit(error_message)

    # === PUBLIC CONTROL METHODS ===

    def start_analysis(self, request_data: Dict[str, Any]):
        """
        ELEMZÉS INDÍTÁSA

        Args:
            request_data: Teljes elemzési kérés
        """
        if self.isRunning():
            self._logger.warning("Worker már fut, nem lehet újat indítani")
            return False

        self.setup_analysis_request(request_data)
        self.start()
        return True

    def stop_analysis(self):
        """
        ELEMZÉS MEGSZAKÍTÁSA
        Graceful shutdown - nem brutális kill
        """
        if self.isRunning():
            self._logger.info("Worker megszakítás kérve...")
            self.requestInterruption()

            if not self.wait(5000):
                self._logger.warning("Worker nem állt le 5 másodperc alatt, terminálás...")
                self.terminate()
                self.wait(1000)

    def is_running_analysis(self) -> bool:
        """Worker futási állapot lekérdezése"""
        return self.isRunning()
