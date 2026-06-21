# mypy: ignore-errors
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

    def __init__(self, worker: "AnalysisWorker"):
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

        # Port import ellenőrzés (Clean Architecture)
        try:
            from src.analytics.ports import get_multi_city_engine_port  # noqa: F401, PLC0415

            self._worker._emit_progress("Portok ellenőrzése...", 10)
        except ImportError as e:
            self._worker._emit_error(f"Portok importálása sikertelen: {e}")
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
            self._logger.error(f"❌ Inicializálási hiba: {e!s}")
            self._logger.error(traceback.format_exc())
            self._worker._emit_error(f"Inicializálási hiba: {e!s}")
            return False

    def _init_weather_client(self) -> bool:
        """
        Validate the WeatherClient port injected via the worker constructor.

        FIX-05: the client is no longer resolved here from infrastructure; it is
        supplied by the composition root through AnalysisWorker.__init__.

        Returns:
            True if successful
        """
        try:
            if self._worker._weather_client is None:
                raise RuntimeError("WeatherClient port was not injected into the worker")
            self._logger.info("✅ WeatherClient port inicializálás sikeres")
            return True
        except Exception as e:
            self._logger.error(f"❌ WeatherClient port inicializálás sikertelen: {e}")
            self._worker._emit_error(f"WeatherClient inicializálás sikertelen: {e}")
            return False

    def _init_multi_city_engine(
        self,
        global_db_path: Path,  # noqa: ARG002
        hungarian_db_path: Path,  # noqa: ARG002
    ) -> bool:
        """
        Initialize MultiCityEngine via port (CA compliant).

        Args:
            global_db_path: Path to global cities database
            hungarian_db_path: Path to Hungarian settlements database

        Returns:
            True if successful or not needed
        """
        from src.analytics.ports import get_multi_city_engine_port  # noqa: PLC0415

        analysis_type = self._worker._request_data.get("analysis_type")

        if analysis_type not in ["multi_city", "county_analysis"]:
            return True

        self._logger.info("🏙️ MultiCityEngine inicializálása porton keresztül...")

        try:
            self._worker._multi_city_engine = get_multi_city_engine_port()
            self._logger.info("✅ MultiCityEngine port inicializálva")
            return True
        except Exception as e:
            self._logger.error(f"❌ MultiCityEngine port inicializálás sikertelen: {e}")
            self._worker._emit_error(f"MultiCityEngine inicializálás sikertelen: {e}")
            return False
