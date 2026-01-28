"""
AnalysisWorker Component Initializer - Initialize WeatherClient and MultiCityEngine.
"""

import logging
import traceback
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import AnalysisWorker


class ComponentInitializer:
    """Initialize analytics components with proper path handling."""

    def __init__(self, worker: 'AnalysisWorker'):
        """
        Initialize component initializer.

        Args:
            worker: AnalysisWorker instance
        """
        self._worker = worker
        self._logger = logging.getLogger(__name__)

    def initialize(self) -> bool:
        """
        Initialize analytics components.

        Returns:
            True if initialization successful
        """
        if self._worker._interrupt_handler.check("Inicializálás"):
            return False

        # Import ellenőrzés
        from .core import IMPORTS_OK, WeatherClient, MultiCityEngine

        if not IMPORTS_OK:
            self._worker._emit_error("Analytics komponensek importálása sikertelen")
            return False

        try:
            self._worker._emit_progress("Komponensek inicializálása...", 20)

            # Path calculation
            project_root = Path(__file__).parent.parent.parent.parent

            self._logger.info("🔧 ABSOLUTE PATH FIX v4.6.1:")
            self._logger.info(f"   Script location: {Path(__file__).absolute()}")
            self._logger.info(f"   Calculated project root: {project_root.absolute()}")

            # Database paths
            global_db_path = project_root / "data" / "cities.db"
            hungarian_db_path = project_root / "data" / "hungarian_settlements.db"

            self._logger.info("🔧 Target database paths:")
            self._logger.info(f"   Global DB: {global_db_path.absolute()}")
            self._logger.info(f"   Hungarian DB: {hungarian_db_path.absolute()}")

            # Weather Client setup
            if not self._init_weather_client():
                return False

            # MultiCity Engine setup (ha szükséges)
            if not self._init_multi_city_engine(global_db_path, hungarian_db_path):
                return False

            self._worker._emit_progress("Komponensek inicializálva", 30)
            return True

        except Exception as e:
            self._logger.error(f"❌ Inicializálási hiba: {str(e)}")
            self._logger.error(traceback.format_exc())
            self._worker._emit_error(f"Inicializálási hiba: {str(e)}")
            return False

    def _init_weather_client(self) -> bool:
        """
        Initialize WeatherClient.

        Returns:
            True if successful
        """
        from .core import WeatherClient

        if WeatherClient is None:
            self._worker._emit_error("WeatherClient osztály nem elérhető")
            return False

        provider = self._worker._request_data.get('provider', 'open_meteo')
        api_settings = self._worker._request_data.get('api_settings', {})

        self._logger.info(f"🔧 WeatherClient inicializálás: provider='{provider}'")

        # Try different initialization methods
        try:
            self._worker._weather_client = WeatherClient()
            self._logger.info("✅ WeatherClient default inicializálás sikeres")
        except Exception as e1:
            try:
                self._worker._weather_client = WeatherClient(preferred_provider=provider)
                self._logger.info("✅ WeatherClient preferred_provider inicializálás sikeres")
            except Exception as e2:
                self._logger.error(f"❌ WeatherClient inicializálás sikertelen: {e1}, {e2}")
                self._worker._emit_error(f"WeatherClient inicializálás sikertelen: {e1}")
                return False

        return True

    def _init_multi_city_engine(self, global_db_path: Path, hungarian_db_path: Path) -> bool:
        """
        Initialize MultiCityEngine if needed.

        Args:
            global_db_path: Path to global cities database
            hungarian_db_path: Path to Hungarian settlements database

        Returns:
            True if successful or not needed
        """
        from .core import MultiCityEngine

        analysis_type = self._worker._request_data.get('analysis_type')

        if analysis_type not in ['multi_city', 'county_analysis']:
            return True

        self._logger.info("🏙️ MultiCityEngine inicializálása...")

        if MultiCityEngine is None:
            self._worker._emit_error("MultiCityEngine osztály nem elérhető")
            return False

        self._worker._multi_city_engine = MultiCityEngine(
            db_path=str(global_db_path.absolute()),
            hungarian_db_path=str(hungarian_db_path.absolute())
        )

        self._logger.info("✅ MultiCityEngine inicializálva")
        return True
