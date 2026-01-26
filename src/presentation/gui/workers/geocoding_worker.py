#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Geocoding Worker - OpenMeteo Geocoding API worker

Település keresést végző worker OpenMeteo Geocoding API használatával.
"""

import json
import httpx
from typing import Dict, List, Any, Optional
from PySide6.QtCore import Signal

from .base_worker import BaseWorkerThread


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

    def __init__(self, search_query: str, parent: Optional['QObject'] = None):
        super().__init__(parent)
        self.search_query = search_query.strip()
        self.results: List[Dict[str, Any]] = []

    def execute(self) -> None:
        """
        🔧 FIX: Geocoding lekérdezés teljes cancellation support-tal.

        Minden HTTP request előtt és után cancellation check.
        """
        if not self.search_query or len(self.search_query) < 2:
            self.emit_error("Legalább 2 karakter szükséges a kereséshez")
            return

        try:
            self.emit_status("🔍 Geocoding keresés indítása...")
            self.progress_updated.emit(10)

            # 🚨 FIX: Cancellation check
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: Geocoding cancelled at start")
                return

            # OpenMeteo Geocoding API konfiguráció
            url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {
                "name": self.search_query,
                "count": 10,
                "language": "hu",
                "format": "json"
            }

            self.emit_status(f"🌍 Keresés: {self.search_query}")
            self.progress_updated.emit(30)

            # 🚨 FIX: Cancellation check before HTTP request
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: Geocoding cancelled before HTTP request")
                return

            # HTTP kérés httpx-szel comprehensive timeout-tal
            with httpx.Client(timeout=30.0) as client:
                self.emit_status("📡 API kérés küldése...")

                response = client.get(url, params=params)

                self.progress_updated.emit(70)

                # 🚨 FIX: Cancellation check after HTTP request
                if self.isInterruptionRequested() or self.is_cancelled:
                    print("🛑 DEBUG: Geocoding cancelled after HTTP request")
                    return

                if response.status_code != 200:
                    self.emit_error(f"Geocoding API hiba: HTTP {response.status_code}")
                    return

                self.emit_status("📄 Válasz feldolgozása...")
                data = response.json()
                self.results = data.get("results", [])

                self.progress_updated.emit(100)

                # Eredmények kibocsátása (ha nem cancelled)
                if not self.is_cancelled:
                    self.geocoding_completed.emit(self.results)
                    self.emit_status(f"✅ {len(self.results)} találat")
                    print(f"✅ DEBUG: Geocoding completed - {len(self.results)} results")

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
