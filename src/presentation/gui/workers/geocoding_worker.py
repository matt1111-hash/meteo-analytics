#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Geocoding Worker - OpenMeteo Geocoding API worker

Település keresést végző worker OpenMeteo Geocoding API használatával.
"""

import json
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import httpx
from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    pass

from .base_worker import BaseWorkerThread


def _is_cancelled(worker: "GeocodingWorker") -> bool:
    """Return whether the geocoding operation has been cancelled."""
    return worker.isInterruptionRequested() or worker.is_cancelled


def _build_geocoding_params(search_query: str) -> Dict[str, Any]:
    """Build Open-Meteo geocoding query parameters."""
    return {
        "name": search_query,
        "count": 10,
        "language": "hu",
        "format": "json",
    }


def _validate_search_query(worker: "GeocodingWorker") -> bool:
    """Validate the geocoding search query."""
    if worker.search_query and len(worker.search_query) >= 2:
        return True
    worker.emit_error("Legalább 2 karakter szükséges a kereséshez")
    return False


def _prepare_geocoding_request(
    worker: "GeocodingWorker",
) -> tuple[str, Dict[str, Any]] | None:
    """Prepare request metadata unless cancelled."""
    worker.emit_status("🔍 Geocoding keresés indítása...")
    worker.progress_updated.emit(10)
    if _is_cancelled(worker):
        print("🛑 DEBUG: Geocoding cancelled at start")
        return None
    worker.emit_status(f"🌍 Keresés: {worker.search_query}")
    worker.progress_updated.emit(30)
    if _is_cancelled(worker):
        print("🛑 DEBUG: Geocoding cancelled before HTTP request")
        return None
    return "https://geocoding-api.open-meteo.com/v1/search", _build_geocoding_params(
        worker.search_query
    )


def _fetch_geocoding_results(
    worker: "GeocodingWorker", url: str, params: Dict[str, Any]
) -> bool:
    """Fetch geocoding results from the API."""
    with httpx.Client(timeout=30.0) as client:
        worker.emit_status("📡 API kérés küldése...")
        response = client.get(url, params=params)
        worker.progress_updated.emit(70)
        if _is_cancelled(worker):
            print("🛑 DEBUG: Geocoding cancelled after HTTP request")
            return False
        if response.status_code != 200:
            worker.emit_error(f"Geocoding API hiba: HTTP {response.status_code}")
            return False
        worker.emit_status("📄 Válasz feldolgozása...")
        data = response.json()
        worker.results = data.get("results", [])
        worker.progress_updated.emit(100)
        return True


def _run_geocoding(worker: "GeocodingWorker") -> None:
    """Run the geocoding workflow."""
    request_metadata = _prepare_geocoding_request(worker)
    if request_metadata is None:
        return
    url, params = request_metadata
    if not _fetch_geocoding_results(worker, url, params):
        return
    if not worker.is_cancelled:
        worker.geocoding_completed.emit(worker.results)
        worker.emit_status(f"✅ {len(worker.results)} találat")
        print(f"✅ DEBUG: Geocoding completed - {len(worker.results)} results")


class GeocodingWorker(BaseWorkerThread):
    """
    🔧 FIX: Geocoding worker teljes cancellation support-tal.

    FUNKCIÓK:
    ✅ OpenMeteo Geocoding API
    ✅ Comprehensive cancellation checks
    ✅ Progress tracking
    ✅ Error handling minden HTTP phase-ben
    """

    # Specifikus signalok
    geocoding_completed = Signal(list)  # List[Dict] - találatok

    def __init__(self, search_query: str, parent: Optional["QObject"] = None):
        super().__init__(parent)
        self.search_query = search_query.strip()
        self.results: List[Dict[str, Any]] = []

    def execute(self) -> None:
        """
        🔧 FIX: Geocoding lekérdezés teljes cancellation support-tal.

        Minden HTTP request előtt és után cancellation check.
        """
        if not _validate_search_query(self):
            return

        try:
            _run_geocoding(self)

        except httpx.TimeoutException:
            if not self.is_cancelled:
                self.emit_error("Geocoding API timeout - próbálja újra később")
        except httpx.RequestError as e:
            if not self.is_cancelled:
                self.emit_error(f"Hálózati hiba a geocoding során: {str(e)}")
        except json.JSONDecodeError:
            if not self.is_cancelled:
                self.emit_error("Érvénytelen válasz a geocoding API-tól")
        except Exception as e:
            if not self.is_cancelled:
                self.emit_error(f"Váratlan hiba a geocoding során: {str(e)}")
