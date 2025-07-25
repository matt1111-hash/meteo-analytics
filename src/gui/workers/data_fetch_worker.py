#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Background Threads Module (PROVIDER ROUTING + WIND GUSTS)
Háttérszálak és aszinkron munkák modulja provider routing támogatással.

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
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import httpx
from pathlib import Path

from PySide6.QtCore import QThread, Signal, QObject, QMutex, QWaitCondition

# 🌍 ÚJ: Provider routing imports
from ..utils import (
    get_optimal_data_source, validate_api_source_available,
    get_fallback_source_chain, get_source_display_name,
    log_provider_usage_event, APIConstants
)


class BaseWorkerThread(QThread):
    """
    Base worker thread class közös hibakezeléssel és signalokkal.
    Professzionális thread lifecycle management.
    """
    
    # Közös signalok minden worker számára
    finished = Signal()
    error_occurred = Signal(str)
    progress_updated = Signal(int)  # 0-100 százalék
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.is_cancelled = False
        self._error_message = ""
    
    def cancel(self) -> None:
        """Worker megszakítása."""
        self.is_cancelled = True
    
    def emit_error(self, message: str) -> None:
        """Hibajel kibocsátása."""
        self._error_message = message
        self.error_occurred.emit(message)
    
    def run(self) -> None:
        """Override-olni kell a leszármazott osztályokban."""
        try:
            self.execute()
        except Exception as e:
            if not self.is_cancelled:
                self.emit_error(f"Worker hiba: {str(e)}")
        finally:
            self.finished.emit()
    
    def execute(self) -> None:
        """Tényleges munkát végző metódus - override-olni kell."""
        raise NotImplementedError("A execute() metódust override-olni kell!")


class GeocodingWorker(BaseWorkerThread):
    """
    Geocoding API lekérdezést végző worker.
    Települések keresése koordináták lekérdezéséhez.
    Professzionális hibakezelés és timeout management.
    """
    
    # Specifikus signalok
    geocoding_completed = Signal(list)  # List[Dict] - találatok
    
    def __init__(self, search_query: str, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.search_query = search_query.strip()
        self.results: List[Dict[str, Any]] = []
    
    def execute(self) -> None:
        """Geocoding lekérdezés végrehajtása - professzionális implementáció."""
        if not self.search_query or len(self.search_query) < 2:
            self.emit_error("Legalább 2 karakter szükséges a kereséshez")
            return
        
        try:
            self.progress_updated.emit(10)
            
            # Open-Meteo Geocoding API (provider-független)
            url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {
                "name": self.search_query,
                "count": 10,
                "language": "hu",
                "format": "json"
            }
            
            self.progress_updated.emit(30)
            
            # HTTP kérés httpx-szel - professzionális timeout és retry
            with httpx.Client(timeout=30.0) as client:
                if self.is_cancelled:
                    return
                
                response = client.get(url, params=params)
                
                self.progress_updated.emit(70)
                
                if response.status_code != 200:
                    self.emit_error(f"Geocoding API hiba: {response.status_code}")
                    return
                
                data = response.json()
                self.results = data.get("results", [])
                
                self.progress_updated.emit(100)
                
                # Eredmények kibocsátása
                self.geocoding_completed.emit(self.results)
                
        except httpx.TimeoutException:
            self.emit_error("Geocoding API timeout - próbálja újra később")
        except httpx.RequestError as e:
            self.emit_error(f"Hálózati hiba a geocoding során: {str(e)}")
        except json.JSONDecodeError:
            self.emit_error("Érvénytelen válasz a geocoding API-tól")
        except Exception as e:
            self.emit_error(f"Váratlan hiba a geocoding során: {str(e)}")


class WeatherDataWorker(BaseWorkerThread):
    """
    🌍 PROVIDER ROUTING + 🌪️ WIND GUSTS: Open-Meteo időjárási adatok lekérdezés 
    provider routing támogatással és wind gusts funkcionalitással.
    
    ÚJ PROVIDER FUNKCIÓK:
    ✅ Provider parameter támogatás
    ✅ Provider validation & fallback logic
    ✅ Provider change signal emission
    ✅ API endpoint dinamikus választás
    
    WIND GUSTS FUNKCIÓK:
    ✅ Hourly wind_gusts_10m paraméter hozzáadva
    ✅ Napi maximum széllökés számítás
    ✅ 130+ km/h széllökések accurate reporting
    ✅ Backward compatibility windspeed_10m_max-szal
    """
    
    # Specifikus signalok
    weather_data_completed = Signal(dict)  # API válasz dictionary
    
    # 🌍 ÚJ: Provider routing signalok
    provider_changed = Signal(str)  # Új provider név
    provider_fallback_occurred = Signal(str, str)  # eredeti, fallback provider
    provider_validation_failed = Signal(str, str)  # provider, error message
    
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
    
    def execute(self) -> None:
        """
        🌍 PROVIDER ROUTING + 🌪️ WIND GUSTS: Időjárási adatok lekérdezése 
        provider routing és wind gusts támogatással.
        """
        try:
            self.progress_updated.emit(5)
            
            # 🌍 PROVIDER ROUTING: Optimal provider meghatározása
            selected_provider = self._select_optimal_provider()
            if not selected_provider:
                self.emit_error("Egyik provider sem elérhető")
                return
            
            self.progress_updated.emit(10)
            
            # 🌍 PROVIDER-SPECIFIC API ENDPOINT VÁLASZTÁS
            api_url, api_params = self._build_api_request(selected_provider)
            
            self.progress_updated.emit(20)
            
            print(f"🌍 DEBUG: Provider routing - {get_source_display_name(selected_provider)}")
            print(f"🌪️ DEBUG: Wind gusts kérés: {self.latitude:.4f}, {self.longitude:.4f}")
            print(f"📅 DEBUG: Időszak: {self.start_date} - {self.end_date}")
            print(f"🔗 DEBUG: API URL: {api_url}")
            
            # 🌍 HTTP REQUEST WITH PROVIDER FALLBACK
            success = False
            fallback_chain = get_fallback_source_chain(selected_provider)
            
            for provider in fallback_chain:
                if self.is_cancelled:
                    return
                
                try:
                    self.progress_updated.emit(30 + (fallback_chain.index(provider) * 20))
                    
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
                        break
                    
                except Exception as e:
                    print(f"❌ DEBUG: Provider {provider} failed: {e}")
                    log_provider_usage_event(provider, "weather_data", False)
                    continue
            
            if not success:
                self.emit_error("Minden provider API hívás sikertelen")
                return
            
            self.progress_updated.emit(90)
            
            # 🌪️ WIND GUSTS VALIDATION & RESPONSE PROCESSING
            if self.weather_data:
                self._validate_wind_gusts_data()
                self.progress_updated.emit(100)
                self.weather_data_completed.emit(self.weather_data)
            else:
                self.emit_error("Érvénytelen API válasz struktúra")
                
        except Exception as e:
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
        🌍 Provider-specific API request végrehajtása.
        
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
                if self.is_cancelled:
                    return False
                
                response = client.get(api_url, params=params)
                
                if response.status_code != 200:
                    print(f"❌ DEBUG: {provider} API hiba: {response.status_code}")
                    return False
                
                self.weather_data = response.json()
                
                # Provider change notification
                if provider != self.preferred_provider and self.preferred_provider != "auto":
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
    SQL lekérdezéseket végző worker thread SQLite adatbázishoz.
    SQL injection védelem és professzionális adatbázis kezelés.
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
        """SQL lekérdezés végrehajtása - professzionális biztonsági intézkedésekkel."""
        if not self.query:
            self.emit_error("Üres SQL lekérdezés")
            return
        
        if not self.db_path.exists():
            self.emit_error(f"Adatbázis fájl nem található: {self.db_path}")
            return
        
        try:
            self.progress_updated.emit(20)
            
            # Adatbázis kapcsolat
            conn = sqlite3.connect(str(self.db_path))
            
            if self.is_cancelled:
                conn.close()
                return
            
            self.progress_updated.emit(50)
            
            # Biztonságos lekérdezés (SQL injection védelem)
            dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
            query_upper = self.query.upper()
            
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    conn.close()
                    self.emit_error(f"Tiltott SQL kulcsszó: {keyword}")
                    return
            
            self.progress_updated.emit(70)
            
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
            
            # Eredmény kibocsátása
            if self.result is not None:
                self.query_completed.emit(self.result)
            
        except sqlite3.Error as e:
            self.emit_error(f"SQL hiba: {str(e)}")
        except Exception as e:
            self.emit_error(f"Váratlan hiba az SQL lekérdezés során: {str(e)}")


class WorkerManager(QObject):
    """
    🌍 PROVIDER ROUTING + 🌪️ WIND GUSTS: Worker threadek központi kezelője 
    provider routing támogatással és wind gusts funkcionalitással.
    
    ÚJ PROVIDER FUNKCIÓK:
    ✅ Provider state tracking
    ✅ Provider fallback coordination
    ✅ Signal routing app_controller-hez
    ✅ Provider usage monitoring
    """
    
    # Központi signalok
    error_occurred = Signal(str)
    progress_updated = Signal(str, int)  # worker_type, progress
    worker_started = Signal(str)         # worker_type
    worker_finished = Signal(str)        # worker_type
    
    # Specifikus worker signalok
    geocoding_completed = Signal(list)
    weather_data_completed = Signal(dict)  # 🌪️ Wind gusts data támogatás
    sql_query_completed = Signal(object)
    
    # 🌍 ÚJ: Provider routing signalok
    provider_changed = Signal(str)  # Új provider név
    provider_fallback_occurred = Signal(str, str)  # eredeti, fallback provider
    provider_validation_failed = Signal(str, str)  # provider, error message
    provider_usage_tracked = Signal(str, bool)  # provider, success
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Aktív worker threadek tárolása
        self.active_workers: Dict[str, BaseWorkerThread] = {}
        self.worker_counter = 0
        
        # 🌍 ÚJ: Provider state tracking
        self.provider_states: Dict[str, Dict[str, Any]] = {}
        self.last_successful_provider: Optional[str] = None
        
        # Thread safe mutex - PySide6 kompatibilis
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()
        
        print("✅ DEBUG: WorkerManager inicializálva (PROVIDER ROUTING + WIND GUSTS támogatással)")
    
    def _get_worker_id(self, worker_type: str) -> str:
        """Egyedi worker ID generálása."""
        self.worker_counter += 1
        return f"{worker_type}_{self.worker_counter}"
    
    def start_geocoding(self, worker: GeocodingWorker) -> str:
        """Geocoding worker indítása."""
        worker_id = self._get_worker_id("geocoding")
        
        # Signal kapcsolatok
        worker.geocoding_completed.connect(self.geocoding_completed.emit)
        worker.error_occurred.connect(self._on_worker_error)
        worker.finished.connect(lambda worker_id=worker_id: self._on_worker_finished(worker_id))
        worker.progress_updated.connect(lambda p: self.progress_updated.emit("geocoding", p))
        
        # Thread safe worker tárolása és indítása
        self.mutex.lock()
        try:
            self.active_workers[worker_id] = worker
        finally:
            self.mutex.unlock()
        
        worker.start()
        self.worker_started.emit("geocoding")
        print(f"✅ DEBUG: Geocoding worker indítva - {worker_id}")
        return worker_id
    
    def start_weather_data_fetch(self, worker: WeatherDataWorker) -> str:
        """
        🌍 PROVIDER ROUTING + 🌪️ WIND GUSTS: Weather data worker indítása 
        provider routing és wind gusts támogatással.
        """
        worker_id = self._get_worker_id("weather_data")
        
        # Signal kapcsolatok
        worker.weather_data_completed.connect(self.weather_data_completed.emit)
        worker.error_occurred.connect(self._on_worker_error)
        worker.finished.connect(lambda worker_id=worker_id: self._on_worker_finished(worker_id))
        worker.progress_updated.connect(lambda p: self.progress_updated.emit("weather_data", p))
        
        # 🌍 ÚJ: Provider routing signal kapcsolatok
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
        print(f"✅ DEBUG: Weather worker indítva PROVIDER ROUTING + WIND GUSTS támogatással - {worker_id}")
        return worker_id
    
    def start_sql_query(self, worker: SQLQueryWorker) -> str:
        """SQL query worker indítása."""
        worker_id = self._get_worker_id("sql_query")
        
        # Signal kapcsolatok
        worker.query_completed.connect(self.sql_query_completed.emit)
        worker.error_occurred.connect(self._on_worker_error)
        worker.finished.connect(lambda worker_id=worker_id: self._on_worker_finished(worker_id))
        worker.progress_updated.connect(lambda p: self.progress_updated.emit("sql_query", p))
        
        # Thread safe worker tárolása és indítása
        self.mutex.lock()
        try:
            self.active_workers[worker_id] = worker
        finally:
            self.mutex.unlock()
        
        worker.start()
        self.worker_started.emit("sql_query")
        print(f"✅ DEBUG: SQL query worker indítva - {worker_id}")
        return worker_id
    
    def _on_worker_error(self, error_message: str) -> None:
        """Worker hiba kezelése."""
        print(f"❌ DEBUG: Worker error: {error_message}")
        self.error_occurred.emit(error_message)
    
    def _on_worker_finished(self, worker_id: str) -> None:
        """Worker befejezés kezelése."""
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
                print(f"✅ DEBUG: Worker befejezve: {worker_id}")
        finally:
            self.mutex.unlock()
    
    # 🌍 ÚJ: Provider routing event handlers
    
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
    
    # 🌍 ÚJ: Provider state management methods
    
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
    
    # Eredeti methods továbbra is megtartva
    
    def cancel_worker(self, worker_id: str) -> bool:
        """Specifikus worker megszakítása."""
        self.mutex.lock()
        try:
            if worker_id in self.active_workers:
                worker = self.active_workers[worker_id]
                worker.cancel()
                print(f"🛑 DEBUG: Worker megszakítva: {worker_id}")
                return True
            return False
        finally:
            self.mutex.unlock()
    
    def cancel_all(self) -> None:
        """Összes aktív worker megszakítása."""
        self.mutex.lock()
        try:
            for worker_id, worker in self.active_workers.items():
                worker.cancel()
                print(f"🛑 DEBUG: Worker cancel: {worker_id}")
        finally:
            self.mutex.unlock()
        
        print("🛑 DEBUG: Összes worker megszakítva")
    
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
    
    def shutdown(self) -> None:
        """🌍 PROVIDER ROUTING + 🌪️ WIND GUSTS: WorkerManager leállítása."""
        print("🛑 DEBUG: WorkerManager leállítása...")
        
        # Összes worker megszakítása
        self.cancel_all()
        
        # Várakozás a worker-ek leállására
        self.mutex.lock()
        try:
            for worker_id, worker in list(self.active_workers.items()):
                print(f"  ⏳ Worker leállítása: {worker_id}")
                
                if worker.isRunning():
                    worker.quit()
                    if not worker.wait(5000):  # 5 másodperc timeout
                        print(f"  ⚠️ Worker kényszerű leállítása: {worker_id}")
                        worker.terminate()
                        worker.wait(1000)
                
                # Worker eltávolítása
                self.active_workers.pop(worker_id, None)
            
            # Provider states cleanup
            self.provider_states.clear()
            self.last_successful_provider = None
            
        finally:
            self.mutex.unlock()
        
        print("✅ DEBUG: WorkerManager leállítva (PROVIDER ROUTING + WIND GUSTS)")


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


# 🌍 ÚJ: Provider routing utility functions

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
        "total_providers_tracked": len(provider_states)
    }
    
    return summary
