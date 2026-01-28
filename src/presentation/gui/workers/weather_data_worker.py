#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weather Data Worker - Weather data API worker

Időjárási adatok lekérését végző worker provider routing
és wind gusts támogatással.
"""

import json
from typing import Any, Dict, Optional

import httpx
from PySide6.QtCore import Signal

from .base_worker import BaseWorkerThread

# Provider routing imports
try:
    from ...utils import (
        APIConstants,
        get_fallback_source_chain,
        get_optimal_data_source,
        get_source_display_name,
        log_provider_usage_event,
        validate_api_source_available,
    )
except ImportError:
    # Fallback ha utils nem elérhető
    def get_optimal_data_source(*args, **kwargs):
        return "open-meteo"

    def validate_api_source_available(provider):
        return provider == "open-meteo"

    def get_fallback_source_chain(provider):
        return ["open-meteo"]

    def get_source_display_name(provider):
        return f"{provider.title().replace('-', ' ')}"

    def log_provider_usage_event(provider, event_type, success):
        print(f"📊 Provider usage: {provider} - {event_type} - {'SUCCESS' if success else 'FAILED'}")

    class APIConstants:
        OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
        DEFAULT_TIMEOUT = 30.0
        USER_AGENT = "GlobalWeatherAnalyzer/1.0"


class WeatherDataWorker(BaseWorkerThread):
    """
    🔧 CRITICAL FIX: Weather data worker teljes cancellation support + completion signal.
    🌪️ WIND GUSTS + 🌍 PROVIDER ROUTING támogatás megtartva.

    ÚJ FUNKCIÓK:
    ✅ Teljes cancellation support minden HTTP request-nél
    ✅ Explicit completion_signal UI auto-hide-hoz
    ✅ Comprehensive progress tracking
    ✅ Provider fallback cancellation support
    ✅ Status message updates
    """

    # Specifikus signalok
    weather_data_completed = Signal(dict)  # API válasz dictionary

    # Provider routing signalok
    provider_changed = Signal(str)
    provider_fallback_occurred = Signal(str, str)
    provider_validation_failed = Signal(str, str)

    def __init__(self, latitude: float, longitude: float,
                 start_date: str, end_date: str,
                 preferred_provider: str = "auto",
                 parent: Optional['QObject'] = None):
        super().__init__(parent)
        self.latitude = latitude
        self.longitude = longitude
        self.start_date = start_date
        self.end_date = end_date
        self.preferred_provider = preferred_provider
        self.actual_provider: Optional[str] = None
        self.weather_data: Optional[Dict[str, Any]] = None

        print(f"🌍 DEBUG: WeatherDataWorker created - {preferred_provider} provider")

    def execute(self) -> None:
        """
        🔧 CRITICAL FIX: Weather data lekérdezés teljes cancellation support-tal.
        🌪️ WIND GUSTS + 🌍 PROVIDER ROUTING megtartva.

        Minden főbb lépésnél cancellation check:
        1. Provider selection
        2. API request building
        3. HTTP requests (minden provider-nél)
        4. Response processing
        """
        try:
            self.emit_status("🌍 Provider kiválasztása...")
            self.progress_updated.emit(5)

            # 🚨 FIX: Cancellation check at start
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: Weather data fetch cancelled at start")
                return

            # 🌍 PROVIDER ROUTING: Optimal provider meghatározása
            selected_provider = self._select_optimal_provider()
            if not selected_provider:
                self.emit_error("Egyik provider sem elérhető")
                return

            self.progress_updated.emit(10)

            # 🚨 FIX: Cancellation check after provider selection
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: Weather data fetch cancelled after provider selection")
                return

            # 🌍 PROVIDER-SPECIFIC API ENDPOINT VÁLASZTÁS
            api_url, api_params = self._build_api_request(selected_provider)

            self.progress_updated.emit(20)

            print(f"🌍 DEBUG: Provider routing - {get_source_display_name(selected_provider)}")
            print(f"🌪️ DEBUG: Wind gusts kérés: {self.latitude:.4f}, {self.longitude:.4f}")
            print(f"📅 DEBUG: Időszak: {self.start_date} - {self.end_date}")
            print(f"🔗 DEBUG: API URL: {api_url}")

            # 🚨 FIX: Cancellation check before HTTP requests
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: Weather data fetch cancelled before HTTP requests")
                return

            # 🌍 HTTP REQUEST WITH PROVIDER FALLBACK + CANCELLATION SUPPORT
            success = False
            fallback_chain = get_fallback_source_chain(selected_provider)

            for provider_index, provider in enumerate(fallback_chain):
                # 🚨 FIX: Cancellation check in fallback loop
                if self.isInterruptionRequested() or self.is_cancelled:
                    print("🛑 DEBUG: Weather data fetch cancelled in fallback loop")
                    return

                try:
                    self.emit_status(f"📡 {get_source_display_name(provider)} API kérés...")
                    self.progress_updated.emit(30 + (provider_index * 20))

                    # Provider-specific request
                    api_url, api_params = self._build_api_request(provider)
                    success = self._execute_api_request(provider, api_url, api_params)

                    if success:
                        # Provider sikeresen használva
                        if provider != selected_provider:
                            print(f"🔄 DEBUG: Provider fallback: {selected_provider} → {provider}")
                            self.provider_fallback_occurred.emit(selected_provider, provider)

                        self.actual_provider = provider
                        log_provider_usage_event(provider, "weather_data", True)
                        self.emit_status(f"✅ {get_source_display_name(provider)} sikeres")
                        break

                except Exception as e:
                    print(f"❌ DEBUG: Provider {provider} failed: {e}")
                    log_provider_usage_event(provider, "weather_data", False)

                    # Ha nem az utolsó provider, folytatjuk
                    if provider_index < len(fallback_chain) - 1:
                        self.emit_status(f"⚠️ {get_source_display_name(provider)} sikertelen, fallback...")
                        continue

            if not success:
                self.emit_error("Minden provider API hívás sikertelen")
                return

            self.progress_updated.emit(90)

            # 🚨 FIX: Final cancellation check
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: Weather data fetch cancelled before completion")
                return

            # 🌪️ WIND GUSTS VALIDATION & RESPONSE PROCESSING
            if self.weather_data:
                self.emit_status("🌪️ Széllökés adatok validálása...")
                self._validate_wind_gusts_data()
                self.progress_updated.emit(100)

                # 🚨 FIX: Emit csak ha nem cancelled
                if not self.is_cancelled:
                    self.weather_data_completed.emit(self.weather_data)
                    self.emit_status("✅ Időjárási adatok sikeresen lekérdezve")
                    print("✅ DEBUG: Weather data completed and emitted")
            else:
                self.emit_error("Érvénytelen API válasz struktúra")

        except Exception as e:
            if not self.is_cancelled:
                self.emit_error(f"Váratlan hiba az időjárási adatok lekérdezése során: {str(e)}")

    def _select_optimal_provider(self) -> Optional[str]:
        """
        🌍 Optimális provider kiválasztása user preferencia és elérhetőség alapján.

        Returns:
            Kiválasztott provider név vagy None
        """
        if self.preferred_provider == "auto":
            # Automatikus routing - use case alapján
            optimal = get_optimal_data_source("single_city", prefer_free=True)

            # Validálás és fallback
            if validate_api_source_available(optimal):
                return optimal
            else:
                # Fallback első elérhető provider-re
                fallback_chain = get_fallback_source_chain(optimal)
                for provider in fallback_chain:
                    if validate_api_source_available(provider):
                        return provider
                return None
        else:
            # Explicit provider választás
            if validate_api_source_available(self.preferred_provider):
                return self.preferred_provider
            else:
                self.provider_validation_failed.emit(
                    self.preferred_provider,
                    "Provider nem elérhető vagy API kulcs hiányzik"
                )
                # Auto fallback
                return self._select_optimal_provider() if self.preferred_provider != "auto" else None

    def _build_api_request(self, provider: str):
        """
        🌍 Provider-specific API request építése.

        Args:
            provider: Provider azonosító

        Returns:
            (api_url, params) tuple
        """
        if provider == "open-meteo":
            return self._build_openmeteo_request()
        elif provider == "meteostat":
            return self._build_meteostat_request()
        else:
            raise ValueError(f"Ismeretlen provider: {provider}")

    def _build_openmeteo_request(self):
        """🌪️ Open-Meteo API request építése wind gusts támogatással."""
        url = APIConstants.OPEN_METEO_ARCHIVE

        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": self.start_date,
            "end_date": self.end_date,

            # 🌪️ WIND GUSTS: Daily paraméterek - windspeed_10m_max MEGTARTVA backward compatibility-ért
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,windspeed_10m_max,winddirection_10m_dominant",

            # 🌪️ WIND GUSTS: Hourly paraméterek - wind_gusts_10m a valódi széllökésekhez!
            "hourly": "wind_gusts_10m,windspeed_10m",

            "timezone": "auto"
        }

        return url, params

    def _build_meteostat_request(self):
        """🌍 Meteostat API request építése (jövőbeli bővítéshez)."""
        # PLACEHOLDER - Meteostat API implementation jövőbeli verzióban
        # Jelenleg Open-Meteo fallback
        return self._build_openmeteo_request()

    def _execute_api_request(self, provider: str, api_url: str, params: Dict[str, Any]) -> bool:
        """
        🔧 CRITICAL FIX: API request végrehajtása teljes cancellation support-tal.

        Args:
            provider: Provider azonosító
            api_url: API endpoint URL
            params: Request paraméterek

        Returns:
            Sikeres volt-e a request
        """
        try:
            headers = self._get_provider_headers(provider)
            timeout = APIConstants.DEFAULT_TIMEOUT

            with httpx.Client(timeout=timeout, headers=headers) as client:
                # 🚨 FIX: Cancellation check before HTTP call
                if self.isInterruptionRequested() or self.is_cancelled:
                    print(f"🛑 DEBUG: {provider} API request cancelled before send")
                    return False

                self.emit_status(f"📡 {get_source_display_name(provider)} HTTP kérés...")
                response = client.get(api_url, params=params)

                # 🚨 FIX: Cancellation check after HTTP call
                if self.isInterruptionRequested() or self.is_cancelled:
                    print(f"🛑 DEBUG: {provider} API response cancelled after receive")
                    return False

                if response.status_code != 200:
                    print(f"❌ DEBUG: {provider} API hiba: HTTP {response.status_code}")
                    return False

                self.emit_status(f"📄 {get_source_display_name(provider)} válasz feldolgozása...")
                self.weather_data = response.json()

                # Provider change notification
                if provider != self.preferred_provider and self.preferred_provider != "auto":
                    if not self.is_cancelled:
                        self.provider_changed.emit(provider)

                return True

        except httpx.TimeoutException:
            print(f"⏱️ DEBUG: {provider} API timeout")
            return False
        except httpx.RequestError as e:
            print(f"🌐 DEBUG: {provider} network error: {e}")
            return False
        except json.JSONDecodeError:
            print(f"📄 DEBUG: {provider} JSON decode error")
            return False
        except Exception as e:
            print(f"❌ DEBUG: {provider} unexpected error: {e}")
            return False

    def _get_provider_headers(self, provider: str) -> Dict[str, str]:
        """
        🌍 Provider-specific HTTP headers.

        Args:
            provider: Provider azonosító

        Returns:
            HTTP headers dictionary
        """
        base_headers = {
            "User-Agent": APIConstants.USER_AGENT
        }

        if provider == "meteostat":
            # Meteostat API key (jövőbeli implementáció)
            import os
            api_key = os.getenv("METEOSTAT_API_KEY")
            if api_key:
                base_headers["X-RapidAPI-Key"] = api_key
                base_headers["X-RapidAPI-Host"] = "meteostat.p.rapidapi.com"

        return base_headers

    def _validate_wind_gusts_data(self) -> None:
        """🌪️ Wind gusts adatok validálása és debug információ."""
        if not self.weather_data:
            return

        daily_data = self.weather_data.get("daily", {})
        hourly_data = self.weather_data.get("hourly", {})

        daily_record_count = len(daily_data.get('time', []))
        hourly_record_count = len(hourly_data.get('time', []))
        wind_gusts_count = len(hourly_data.get('wind_gusts_10m', []))

        print(f"✅ DEBUG: {daily_record_count} napi rekord lekérdezve")
        print(f"✅ DEBUG: {hourly_record_count} óránkénti rekord lekérdezve")
        print(f"🌪️ DEBUG: {wind_gusts_count} széllökés rekord lekérdezve")

        # Széllökés adatok minőség ellenőrzés
        if wind_gusts_count > 0:
            wind_gusts = hourly_data.get('wind_gusts_10m', [])
            valid_gusts = [g for g in wind_gusts if g is not None and g > 0]
            if valid_gusts:
                max_gust = max(valid_gusts)
                print(f"🌪️ DEBUG: Maximum széllökés: {max_gust:.1f} km/h")

                # Kritikus figyelmeztetés ha még mindig alacsony az érték
                if max_gust < 60:
                    print(f"⚠️  DEBUG: Széllökés még mindig alacsony: {max_gust:.1f} km/h")
                else:
                    print(f"✅ DEBUG: Realistic széllökés értékek: {max_gust:.1f} km/h")
            else:
                print("❌ DEBUG: Nincs érvényes széllökés adat!")
        else:
            print("❌ DEBUG: Nincs széllökés adat az API válaszban!")
