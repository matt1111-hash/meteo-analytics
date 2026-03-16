# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for AnalysisRunners."""

from __future__ import annotations

from .analysis_runners_support import *


class AnalysisRunnersPart1Mixin:
    def __init__(self, worker: "AnalysisWorker"):
        """
        Initialize analysis runners.

        Args:
            worker: AnalysisWorker instance
        """
        self._worker = worker
        self._logger = logging.getLogger(__name__)

    def run_analysis(self, analysis_type: str) -> None:
        """
        Dispatch analysis based on type.

        Args:
            analysis_type: Type of analysis to run
        """
        if analysis_type == "multi_city":
            self._run_multi_city_analysis()
        elif analysis_type == "single_location":
            self._run_single_location_analysis()
        elif analysis_type == "county_analysis":
            self._run_county_analysis()
        else:
            self._worker._emit_error(f"Ismeretlen elemzés típus: {analysis_type}")

    def _run_multi_city_analysis(self):
        """MULTI-CITY ELEMZÉS FUTTATÁSA"""
        if self._worker._interrupt_handler.check("Multi-city elemzés"):
            return

        try:
            self._worker._emit_progress("Multi-city elemzés indítása...", 40)

            # Extract parameters
            region_name = self._worker._request_data.get("region_name")
            county_name = self._worker._request_data.get("county_name")
            date_range = self._worker._request_data.get("date_range", {})
            start_date = date_range.get("start_date")
            date_range.get("end_date")

            # Interrupt check before heavy work
            if self._worker._interrupt_handler.check("Multi-city engine indítás előtt"):
                return

            self._worker._emit_progress("Városok elemzése folyamatban...", 60)

            # Run analysis
            region_or_county = region_name or county_name
            if not region_or_county:
                self._worker._emit_error("Hiányzó régió vagy megye név")
                return

            result = self._worker._multi_city_engine.analyze_multi_city(
                query_type="hottest_today",
                region=region_or_county,
                date=start_date,
                limit=None,
            )

            # Final interrupt check
            if self._worker._interrupt_handler.check("Eredmény feldolgozás előtt"):
                return

            self._worker._emit_progress("Eredmények feldolgozása...", 90)

            # Structure result
            structured_result = {
                "analysis_type": "multi_city",
                "request_params": self._worker._request_data,
                "result_data": result,
                "timestamp": datetime.now().isoformat(),
                "success": True,
            }

            self._worker._emit_progress("Multi-city elemzés befejezve", 100)
            self._worker.analysis_completed.emit(structured_result)

        except Exception as e:
            self._logger.error(f"Multi-city elemzés hiba: {str(e)}")
            self._worker._emit_error(f"Multi-city elemzés sikertelen: {str(e)}")
