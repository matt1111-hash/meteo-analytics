#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Background Threads Module (PROVIDER ROUTING + WIND GUSTS + CANCEL FIX)
Háttérszálak és aszinkron munkák modulja provider routing támogatással és teljes cancel mechanizmussal.

🌍 PROVIDER ROUTING JAVÍTÁS: WorkerManager és WeatherDataWorker bővítése
✅ Provider parameter támogatás worker-ekben
✅ Provider validation & fallback logic
✅ Provider change signal emission
✅ WorkerManager provider state tracking
✅ Signal routing app_controller-hez

🌪️ KRITIKUS JAVÍTÁS: WindDataWorker API paraméter módosítás
✅ Hourly wind_gusts_10m paraméter hozzáadva
✅ Napi maximum széllökés számítás támogatás
✅ Backward compatibility windspeed_10m_max-szal
✅ Élethű 130+ km/h széllökések támogatása

🔧 CRITICAL FIX: Worker Completion Signal javítás
✅ Explicit completion_signal emission minden worker-ben
✅ Comprehensive cancellation support HTTP request szinten
✅ Progress bar auto-hide mechanizmus
✅ UI state management proper cleanup
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import httpx
from pathlib import Path

from PySide6.QtCore import QThread, Signal, QObject, QMutex, QWaitCondition, QTimer

# Provider routing imports
try:
    from ...utils import (
        get_optimal_data_source, validate_api_source_available,
        get_fallback_source_chain, get_source_display_name,
        log_provider_usage_event, APIConstants
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


class BaseWorkerThread(QThread):
    """
    🔧 CRITICAL FIX: Base worker thread class teljes cancellation support-tal.
    
    ÚJ FUNKCIÓK:
    ✅ Explicit completion_signal minden esetben
    ✅ Comprehensive cancellation support
    ✅ Periodic interruption checks
    ✅ Proper thread lifecycle management
    ✅ Progress tracking standardizálva
    """
    
    # 🚨 FIX: Teljes signal set minden worker-hez
    finished = Signal()
    completion_signal = Signal()  # ← ÚJ: Explicit completion jelzés UI-nak
    error_occurred = Signal(str)
    progress_updated = Signal(int)  # 0-100 százalék
    cancellation_requested = Signal()  # ← ÚJ: Cancel signal internal tracking
    status_updated = Signal(str)  # ← ÚJ: Status message updates
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.is_cancelled = False
        self._error_message = ""
        self._status_message = ""
        
        # 🔧 Periodic interruption check timer
        self._check_timer = QTimer()
        self._check_timer.timeout.connect(self._check_interruption)
        self._check_timer.moveToThread(self)
        
        print("🔧 DEBUG: BaseWorkerThread initialized with comprehensive cancellation support")
    
    def cancel(self) -> None:
        """
        🚨 FIX: Worker megszakítása teljes interrupt mechanizmussal.
        
        Ez a metódus:
        1. is_cancelled flag beállítása
        2. QThread interruption request
        3. Cancellation signal emission
        4. Timer leállítása
        """
        print(f"🛑 DEBUG: Worker cancel requested - thread: {self.currentThreadId()}")
        
        self.is_cancelled = True
        self.requestInterruption()  # QThread built-in interrupt
        self.cancellation_requested.emit()
        
        # Timer leállítása ha fut
        if self._check_timer.isActive():
            self._check_timer.stop()
        
        print(f"🛑 DEBUG: Worker cancel signals sent - thread: {self.currentThreadId()}")
    
    def _check_interruption(self) -> None:
        """
        🔧 Periodic interruption check.
        
        Ez a metódus rendszeresen ellenőrzi, hogy a worker meg lett-e szakítva,
        és ha igen, graceful módon leáll.
        """
        if self.isInterruptionRequested() or self.is_cancelled:
            print("🛑 DEBUG: Interruption detected in periodic check")
            self._check_timer.stop()
            # Graceful exit a következő iteration-ben
            
    def emit_error(self, message: str) -> None:
        """Hibajel kibocsátása thread-safe módon."""
        self._error_message = message
        self.error_occurred.emit(message)
        print(f"❌ DEBUG: Worker error emitted: {message}")
    
    def emit_status(self, message: str) -> None:
        """Status update kibocsátása thread-safe módon."""
        self._status_message = message
        self.status_updated.emit(message)
        print(f"📊 DEBUG: Worker status: {message}")
    
    def run(self) -> None:
        """
        🚨 CRITICAL FIX: Thread run metódus teljes completion signal emission-nel.
        
        Ez a metódus biztosítja, hogy:
        1. Minden esetben completion_signal emission
        2. Proper exception handling
        3. Graceful cancellation support
        4. Thread cleanup
        """
        print(f"🚀 DEBUG: Worker thread started - ID: {self.currentThreadId()}")
        
        try:
            # Interruption check az elején
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: Worker interrupted before execution")
                return
            
            # Periodic check timer indítása
            self._check_timer.start(1000)  # 1 másodpercenként check
            
            # Tényleges munka végrehajtása
            self.execute()
            
            # Timer leállítása
            if self._check_timer.isActive():
                self._check_timer.stop()
            
            if not self.is_cancelled:
                print("✅ DEBUG: Worker execution completed successfully")
                self.emit_status("✅ Befejezve")
            else:
                print("🛑 DEBUG: Worker execution cancelled")
                self.emit_status("🛑 Megszakítva")
                
        except Exception as e:
            # Timer leállítása error esetén
            if self._check_timer.isActive():
                self._check_timer.stop()
                
            if not self.is_cancelled:
                print(f"❌ DEBUG: Worker execution failed: {e}")
                self.emit_error(f"Worker hiba: {str(e)}")
                self.emit_status(f"❌ Hiba: {str(e)[:50]}...")
        finally:
            # 🚨 CRITICAL FIX: Completion signalok MINDEN esetben
            print("🔧 DEBUG: Emitting completion signals...")
            self.finished.emit()
            self.completion_signal.emit()  # ← ÚJ: Explicit completion UI-nak
            print("✅ DEBUG: Worker thread completed - all signals emitted")
    
    def execute(self) -> None:
        """Tényleges munkát végző metódus - override-olni kell."""
        raise NotImplementedError("A execute() metódust override-olni kell!")


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
    
    def __init__(self, search_query: str, parent: Optional[QObject] = None):
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
                 parent: Optional[QObject] = None):
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
    
    def _build_api_request(self, provider: str) -> tuple[str, Dict[str, Any]]:
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
    
    def _build_openmeteo_request(self) -> tuple[str, Dict[str, Any]]:
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
    
    def _build_meteostat_request(self) -> tuple[str, Dict[str, Any]]:
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
                print(f"❌ DEBUG: Nincs érvényes széllökés adat!")
        else:
            print(f"❌ DEBUG: Nincs széllökés adat az API válaszban!")


class SQLQueryWorker(BaseWorkerThread):
    """
    🔧 FIX: SQL lekérdezéseket végző worker thread cancellation support-tal.
    
    FUNKCIÓK:
    ✅ SQLite adatbázis safe querying
    ✅ SQL injection védelem
    ✅ Pandas integration
    ✅ Cancellation support
    """
    
    # Specifikus signalok
    query_completed = Signal(object)  # pandas DataFrame vagy list
    
    def __init__(self, query: str, db_path: Union[str, Path], 
                 parent: Optional[QObject] = None):
        super().__init__(parent)
        self.query = query.strip()
        self.db_path = Path(db_path)
        self.result: Optional[Any] = None
    
    def execute(self) -> None:
        """
        🔧 FIX: SQL lekérdezés végrehajtása cancellation support-tal.
        """
        if not self.query:
            self.emit_error("Üres SQL lekérdezés")
            return
        
        if not self.db_path.exists():
            self.emit_error(f"Adatbázis fájl nem található: {self.db_path}")
            return
        
        try:
            self.emit_status("🗄️ Adatbázis kapcsolat...")
            self.progress_updated.emit(20)
            
            # 🚨 FIX: Cancellation check
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: SQL query cancelled before DB connection")
                return
            
            # Adatbázis kapcsolat
            conn = sqlite3.connect(str(self.db_path))
            
            if self.is_cancelled:
                conn.close()
                return
            
            self.progress_updated.emit(50)
            
            # Biztonsági ellenőrzés (SQL injection védelem)
            dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
            query_upper = self.query.upper()
            
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    conn.close()
                    self.emit_error(f"Tiltott SQL kulcsszó: {keyword}")
                    return
            
            self.emit_status("📊 SQL lekérdezés végrehajtása...")
            self.progress_updated.emit(70)
            
            # 🚨 FIX: Cancellation check before query execution
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: SQL query cancelled before execution")
                conn.close()
                return
            
            # Pandas használata a jobb adatkezeléshez
            try:
                import pandas as pd
                result = pd.read_sql_query(self.query, conn)
                self.result = result
            except ImportError:
                # Fallback pandas nélkül
                cursor = conn.cursor()
                cursor.execute(self.query)
                
                if self.query.upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    self.result = {"columns": columns, "rows": rows}
                else:
                    self.result = {"affected_rows": cursor.rowcount}
            
            conn.close()
            
            self.progress_updated.emit(100)
            
            # Eredmény kibocsátása (ha nem cancelled)
            if self.result is not None and not self.is_cancelled:
                self.query_completed.emit(self.result)
                self.emit_status("✅ SQL lekérdezés befejezve")
            
        except sqlite3.Error as e:
            if not self.is_cancelled:
                self.emit_error(f"SQL hiba: {str(e)}")
        except Exception as e:
            if not self.is_cancelled:
                self.emit_error(f"Váratlan hiba az SQL lekérdezés során: {str(e)}")


class WorkerManager(QObject):
    """
    🔧 CRITICAL FIX: WorkerManager teljes completion signal routing-gal.
    🌍 PROVIDER ROUTING + 🌪️ WIND GUSTS támogatás megtartva.
    
    ÚJ FUNKCIÓK:
    ✅ Explicit worker_completed és worker_cancelled signalok
    ✅ Comprehensive worker tracking és cleanup
    ✅ Provider state management
    ✅ Emergency shutdown procedures
    ✅ Thread-safe operations
    """
    
    # Központi signalok
    error_occurred = Signal(str)
    progress_updated = Signal(str, int)  # worker_type, progress
    worker_started = Signal(str)         # worker_type
    worker_finished = Signal(str)        # worker_type
    
    # 🚨 FIX: Explicit completion signalok UI auto-hide-hoz
    worker_completed = Signal(str)       # ← ÚJ: Worker befejezve (success)
    worker_cancelled = Signal(str)       # ← ÚJ: Worker megszakítva
    all_workers_completed = Signal()     # ← ÚJ: Összes worker befejezve
    
    # Specifikus worker signalok
    geocoding_completed = Signal(list)
    weather_data_completed = Signal(dict)  # 🌪️ Wind gusts data támogatás
    sql_query_completed = Signal(object)
    
    # 🌍 Provider routing signalok
    provider_changed = Signal(str)  # Új provider név
    provider_fallback_occurred = Signal(str, str)  # eredeti, fallback provider
    provider_validation_failed = Signal(str, str)  # provider, error message
    provider_usage_tracked = Signal(str, bool)  # provider, success
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Aktív worker threadek tárolása
        self.active_workers: Dict[str, BaseWorkerThread] = {}
        self.worker_counter = 0
        
        # 🌍 Provider state tracking
        self.provider_states: Dict[str, Dict[str, Any]] = {}
        self.last_successful_provider: Optional[str] = None
        
        # Thread safe mutex - PySide6 kompatibilis
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()
        
        print("✅ DEBUG: WorkerManager inicializálva (COMPLETION SIGNAL FIX + PROVIDER ROUTING + WIND GUSTS)")
    
    def _get_worker_id(self, worker_type: str) -> str:
        """Egyedi worker ID generálása."""
        self.worker_counter += 1
        return f"{worker_type}_{self.worker_counter}"
    
    def start_geocoding(self, worker: GeocodingWorker) -> str:
        """
        🔧 FIX: Geocoding worker indítása completion signal routing-gal.
        """
        worker_id = self._get_worker_id("geocoding")
        
        # Signal kapcsolatok
        worker.geocoding_completed.connect(self.geocoding_completed.emit)
        worker.error_occurred.connect(self._on_worker_error)
        worker.finished.connect(lambda worker_id=worker_id: self._on_worker_finished(worker_id))
        worker.completion_signal.connect(lambda worker_id=worker_id: self._on_worker_completion(worker_id))  # ← ÚJ
        worker.progress_updated.connect(lambda p: self.progress_updated.emit("geocoding", p))
        
        # Thread safe worker tárolása és indítása
        self.mutex.lock()
        try:
            self.active_workers[worker_id] = worker
        finally:
            self.mutex.unlock()
        
        worker.start()
        self.worker_started.emit("geocoding")
        print(f"✅ DEBUG: Geocoding worker indítva COMPLETION SIGNAL FIX-szel - {worker_id}")
        return worker_id
    
    def start_weather_data_fetch(self, worker: WeatherDataWorker) -> str:
        """
        🔧 CRITICAL FIX: Weather data worker indítása teljes completion signal routing-gal.
        🌍 PROVIDER ROUTING + 🌪️ WIND GUSTS támogatás megtartva.
        """
        worker_id = self._get_worker_id("weather_data")
        
        # 🚨 FIX: Teljes signal kapcsolatok + completion
        worker.weather_data_completed.connect(self.weather_data_completed.emit)
        worker.error_occurred.connect(self._on_worker_error)
        worker.finished.connect(lambda worker_id=worker_id: self._on_worker_finished(worker_id))
        worker.completion_signal.connect(lambda worker_id=worker_id: self._on_worker_completion(worker_id))  # ← ÚJ
        worker.progress_updated.connect(lambda p: self.progress_updated.emit("weather_data", p))
        worker.status_updated.connect(lambda s: print(f"📊 Weather worker status: {s}"))  # ← ÚJ
        
        # 🌍 Provider routing signal kapcsolatok
        worker.provider_changed.connect(self._on_provider_changed)
        worker.provider_fallback_occurred.connect(self._on_provider_fallback)
        worker.provider_validation_failed.connect(self._on_provider_validation_failed)
        
        # Thread safe worker tárolása és indítása
        self.mutex.lock()
        try:
            self.active_workers[worker_id] = worker
        finally:
            self.mutex.unlock()
        
        worker.start()
        self.worker_started.emit("weather_data")
        print(f"✅ DEBUG: Weather worker indítva COMPLETION SIGNAL FIX + PROVIDER ROUTING + WIND GUSTS - {worker_id}")
        return worker_id
    
    def start_sql_query(self, worker: SQLQueryWorker) -> str:
        """
        🔧 FIX: SQL query worker indítása completion signal routing-gal.
        """
        worker_id = self._get_worker_id("sql_query")
        
        # Signal kapcsolatok
        worker.query_completed.connect(self.sql_query_completed.emit)
        worker.error_occurred.connect(self._on_worker_error)
        worker.finished.connect(lambda worker_id=worker_id: self._on_worker_finished(worker_id))
        worker.completion_signal.connect(lambda worker_id=worker_id: self._on_worker_completion(worker_id))  # ← ÚJ
        worker.progress_updated.connect(lambda p: self.progress_updated.emit("sql_query", p))
        
        # Thread safe worker tárolása és indítása
        self.mutex.lock()
        try:
            self.active_workers[worker_id] = worker
        finally:
            self.mutex.unlock()
        
        worker.start()
        self.worker_started.emit("sql_query")
        print(f"✅ DEBUG: SQL query worker indítva COMPLETION SIGNAL FIX-szel - {worker_id}")
        return worker_id
    
    def _on_worker_completion(self, worker_id: str) -> None:
        """
        🚨 CRITICAL FIX: Explicit worker completion handling.
        
        Ez a metódus biztosítja, hogy a UI megkapja a completion signalt
        automatikus progress bar hide-hoz.
        
        Args:
            worker_id: Worker azonosító
        """
        print(f"🔧 DEBUG: Worker completion signal received - {worker_id}")
        
        self.mutex.lock()
        try:
            if worker_id in self.active_workers:
                worker_type = worker_id.split('_')[0]
                worker = self.active_workers[worker_id]
                
                # 🚨 FIX: Completion signal emission
                if worker.is_cancelled:
                    self.worker_cancelled.emit(worker_type)
                    print(f"🛑 DEBUG: Worker cancelled completion - {worker_id}")
                else:
                    self.worker_completed.emit(worker_type)
                    print(f"✅ DEBUG: Worker successful completion - {worker_id}")
                
                # Ellenőrizzük, hogy van-e még aktív worker
                if len(self.active_workers) <= 1:  # Ez az utolsó
                    # Kis delay után all_workers_completed signal
                    QTimer.singleShot(100, self.all_workers_completed.emit)
                
        finally:
            self.mutex.unlock()
    
    def _on_worker_finished(self, worker_id: str) -> None:
        """
        🔧 FIX: Worker befejezés kezelése comprehensive cleanup-pal.
        
        Args:
            worker_id: Worker azonosító
        """
        print(f"🔧 DEBUG: Worker finished signal received - {worker_id}")
        
        self.mutex.lock()
        try:
            if worker_id in self.active_workers:
                worker_type = worker_id.split('_')[0]
                
                # Worker eltávolítása
                worker = self.active_workers.pop(worker_id)
                
                # 🌍 Provider usage tracking finalizálása
                if hasattr(worker, 'actual_provider') and worker.actual_provider:
                    self._track_provider_usage(worker.actual_provider, True)
                
                # Thread cleanup
                if worker.isRunning():
                    worker.quit()
                    worker.wait(3000)  # 3 másodperc timeout
                
                self.worker_finished.emit(worker_type)
                print(f"✅ DEBUG: Worker befejezve és cleanup: {worker_id}")
        finally:
            self.mutex.unlock()
    
    def cancel_worker(self, worker_id: str) -> bool:
        """
        🔧 FIX: Specifikus worker megszakítása explicit cancel-lel.
        
        Args:
            worker_id: Worker azonosító
            
        Returns:
            bool: Sikerült-e a cancel
        """
        print(f"🛑 DEBUG: Cancel worker requested - {worker_id}")
        
        self.mutex.lock()
        try:
            if worker_id in self.active_workers:
                worker = self.active_workers[worker_id]
                worker.cancel()  # ← Ez triggereli a BaseWorkerThread.cancel() metódust
                print(f"🛑 DEBUG: Worker cancel signal sent - {worker_id}")
                return True
            else:
                print(f"⚠️ DEBUG: Worker not found for cancel - {worker_id}")
                return False
        finally:
            self.mutex.unlock()
    
    def cancel_all_workers(self) -> None:
        """
        🔧 CRITICAL FIX: Összes aktív worker megszakítása.
        
        Ez a metódus minden aktív worker-re meghívja a cancel() metódust,
        ami graceful shutdown-t indít minden thread-ben.
        """
        print("🛑 DEBUG: Cancel all workers requested")
        
        self.mutex.lock()
        try:
            worker_ids = list(self.active_workers.keys())
            for worker_id in worker_ids:
                worker = self.active_workers[worker_id]
                worker.cancel()
                print(f"🛑 DEBUG: Cancel signal sent to worker: {worker_id}")
        finally:
            self.mutex.unlock()
        
        print(f"🛑 DEBUG: Cancel signals sent to {len(worker_ids)} workers")
    
    def stop_all_workers(self) -> None:
        """
        🔧 FIX: Alias a cancel_all_workers-hez backward compatibility-ért.
        """
        self.cancel_all_workers()
    
    # === 🌍 PROVIDER ROUTING METHODS (UNCHANGED) ===
    
    def _on_provider_changed(self, new_provider: str) -> None:
        """Provider változás kezelése."""
        print(f"🔄 DEBUG: Provider changed to: {get_source_display_name(new_provider)}")
        self.last_successful_provider = new_provider
        self.provider_changed.emit(new_provider)
    
    def _on_provider_fallback(self, original_provider: str, fallback_provider: str) -> None:
        """Provider fallback kezelése."""
        print(f"🔄 DEBUG: Provider fallback: {original_provider} → {fallback_provider}")
        
        # Provider state update
        self.provider_states[original_provider] = {
            "status": "failed",
            "last_attempt": datetime.now(),
            "fallback_used": fallback_provider
        }
        
        self.provider_fallback_occurred.emit(original_provider, fallback_provider)
    
    def _on_provider_validation_failed(self, provider: str, error_message: str) -> None:
        """Provider validálási hiba kezelése."""
        print(f"❌ DEBUG: Provider validation failed: {provider} - {error_message}")
        
        # Provider state update
        self.provider_states[provider] = {
            "status": "validation_failed",
            "last_attempt": datetime.now(),
            "error": error_message
        }
        
        self.provider_validation_failed.emit(provider, error_message)
    
    def _track_provider_usage(self, provider: str, success: bool) -> None:
        """Provider használat tracking."""
        print(f"📊 DEBUG: Provider usage tracked: {provider} - {'SUCCESS' if success else 'FAILED'}")
        
        # Provider state update
        if provider not in self.provider_states:
            self.provider_states[provider] = {}
        
        self.provider_states[provider].update({
            "last_usage": datetime.now(),
            "last_result": "success" if success else "failed"
        })
        
        if success:
            self.last_successful_provider = provider
        
        self.provider_usage_tracked.emit(provider, success)
    
    def _on_worker_error(self, error_message: str) -> None:
        """Worker hiba kezelése."""
        print(f"❌ DEBUG: Worker error: {error_message}")
        self.error_occurred.emit(error_message)
    
    # === 🌍 PROVIDER STATE MANAGEMENT METHODS ===
    
    def get_provider_states(self) -> Dict[str, Dict[str, Any]]:
        """Provider állapotok lekérdezése."""
        self.mutex.lock()
        try:
            return self.provider_states.copy()
        finally:
            self.mutex.unlock()
    
    def get_last_successful_provider(self) -> Optional[str]:
        """Utolsó sikeres provider lekérdezése."""
        return self.last_successful_provider
    
    def reset_provider_states(self) -> None:
        """Provider állapotok resetelése."""
        self.mutex.lock()
        try:
            self.provider_states.clear()
            self.last_successful_provider = None
            print("🔄 DEBUG: Provider states reset")
        finally:
            self.mutex.unlock()
    
    # === PUBLIC API ===
    
    def get_active_workers(self) -> List[str]:
        """Aktív worker ID-k listája."""
        self.mutex.lock()
        try:
            return list(self.active_workers.keys())
        finally:
            self.mutex.unlock()
    
    def is_worker_active(self, worker_type: str) -> bool:
        """Adott típusú worker aktív-e."""
        self.mutex.lock()
        try:
            return any(wid.startswith(worker_type) for wid in self.active_workers.keys())
        finally:
            self.mutex.unlock()
    
    def get_worker_count(self) -> int:
        """Aktív worker-ek száma."""
        self.mutex.lock()
        try:
            return len(self.active_workers)
        finally:
            self.mutex.unlock()
    
    def emergency_terminate_all(self) -> None:
        """
        🚨 EMERGENCY: Összes worker kényszerű leállítása.
        
        Ez a metódus csak emergency esetekre van, amikor a graceful
        cancel nem működik és kényszerű terminate szükséges.
        """
        print("🚨 DEBUG: Emergency terminate all workers requested")
        
        self.mutex.lock()
        try:
            for worker_id, worker in list(self.active_workers.items()):
                print(f"🚨 DEBUG: Emergency terminating worker: {worker_id}")
                
                if worker.isRunning():
                    worker.terminate()
                    worker.wait(1000)  # 1 sec timeout
                
                # Worker eltávolítása
                self.active_workers.pop(worker_id, None)
            
            # Provider states cleanup
            self.provider_states.clear()
            self.last_successful_provider = None
            
        finally:
            self.mutex.unlock()
        
        print("🚨 DEBUG: Emergency terminate completed")
    
    def shutdown(self) -> None:
        """
        🔧 CRITICAL FIX: WorkerManager proper shutdown.
        
        Graceful shutdown:
        1. Cancel all workers
        2. Wait for completion
        3. Emergency terminate if needed
        4. Cleanup
        """
        print("🛑 DEBUG: WorkerManager shutdown initiated...")
        
        # 1. Graceful cancel
        self.cancel_all_workers()
        
        # 2. Várakozás a worker-ek leállására
        self.mutex.lock()
        try:
            # Maximum 10 másodperc várakozás
            total_wait = 0
            while self.active_workers and total_wait < 10000:
                self.mutex.unlock()
                QThread.msleep(100)  # 100ms sleep
                total_wait += 100
                self.mutex.lock()
            
            # 3. Ha még vannak aktív worker-ek, emergency terminate
            if self.active_workers:
                print("⚠️ DEBUG: Some workers didn't stop gracefully, emergency terminating...")
                self.mutex.unlock()
                self.emergency_terminate_all()
                self.mutex.lock()
            
            # 4. Final cleanup
            self.active_workers.clear()
            self.provider_states.clear()
            self.last_successful_provider = None
            
        finally:
            self.mutex.unlock()
        
        print("✅ DEBUG: WorkerManager shutdown completed")


# === UTILITY FÜGGVÉNYEK ===

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Koordináták validálása."""
    return (-90.0 <= latitude <= 90.0) and (-180.0 <= longitude <= 180.0)


def validate_date_string(date_str: str) -> bool:
    """Dátum string validálása YYYY-MM-DD formátumban."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def calculate_date_range_days(start_date: str, end_date: str) -> int:
    """Dátum tartomány napokban."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return (end - start).days
    except ValueError:
        return 0


def format_api_error(status_code: int, response_text: str) -> str:
    """API hiba formázása user-friendly módon."""
    error_messages = {
        400: "Hibás kérés - ellenőrizze a paramétereket",
        401: "Hitelesítési hiba - ellenőrizze az API kulcsot",
        403: "Hozzáférés megtagadva",
        404: "API endpoint nem található",
        429: "Túl sok kérés - próbálja újra később",
        500: "Szerver hiba - próbálja újra később",
        502: "Bad Gateway - szolgáltatás átmenetileg nem elérhető",
        503: "Szolgáltatás nem elérhető"
    }
    
    user_message = error_messages.get(status_code, f"HTTP {status_code} hiba")
    
    if len(response_text) < 200:
        user_message += f" ({response_text})"
    
    return user_message


# === 🌍 PROVIDER ROUTING UTILITY FUNCTIONS ===

def create_weather_worker_with_provider(latitude: float, longitude: float,
                                       start_date: str, end_date: str,
                                       preferred_provider: str = "auto") -> WeatherDataWorker:
    """
    🌍 Weather data worker létrehozása provider routing támogatással.
    
    Args:
        latitude: Szélességi fok
        longitude: Hosszúsági fok
        start_date: Kezdő dátum (YYYY-MM-DD)
        end_date: Befejező dátum (YYYY-MM-DD)
        preferred_provider: Preferált provider ("auto", "open-meteo", "meteostat")
        
    Returns:
        Konfigurált WeatherDataWorker instance
    """
    worker = WeatherDataWorker(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
        preferred_provider=preferred_provider
    )
    
    print(f"🌍 DEBUG: Weather worker created with provider: {preferred_provider}")
    return worker


def get_worker_manager_provider_summary(manager: WorkerManager) -> Dict[str, Any]:
    """
    🌍 WorkerManager provider összefoglaló lekérdezése.
    
    Args:
        manager: WorkerManager instance
        
    Returns:
        Provider summary dictionary
    """
    provider_states = manager.get_provider_states()
    last_successful = manager.get_last_successful_provider()
    
    summary = {
        "provider_states": provider_states,
        "last_successful_provider": last_successful,
        "active_workers": manager.get_active_workers(),
        "total_providers_tracked": len(provider_states),
        "worker_count": manager.get_worker_count()
    }
    
    return summary


def create_comprehensive_worker_manager() -> WorkerManager:
    """
    🔧 Comprehensive WorkerManager létrehozása teljes funkcionalitással.
    
    Returns:
        Fully configured WorkerManager instance
    """
    manager = WorkerManager()
    
    print("✅ DEBUG: Comprehensive WorkerManager created with:")
    print("  🔧 Completion signal routing")
    print("  🌍 Provider routing support")
    print("  🌪️ Wind gusts functionality")
    print("  🛑 Full cancellation support")
    print("  📊 Provider state tracking")
    print("  🚨 Emergency shutdown procedures")
    
    return manager
