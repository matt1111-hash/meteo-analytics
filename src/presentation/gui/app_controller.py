#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Application Controller - CLEAN ARCHITECTURE REFACTOR
Alkalmazás központi logikai vezérlője - REFAKTORÁLT MVC ARCHITEKTÚRÁVAL.

🎯 CLEAN ARCHITECTURE FUNKCIÓK:
✅ Központi analysis request handling
✅ Worker lifecycle management (AnalysisWorker + eredeti workerek)  
✅ Clean signal orchestration (UI ↔ Controller ↔ Workers)
✅ Provider routing integration
✅ Wind gusts támogatás minden analysis típusban
✅ Interrupt/Cancel támogatás minden workernél
🔧 KOORDINÁTA KULCSOK KOMPATIBILITÁS JAVÍTÁS: lat/lon ÉS latitude/longitude támogatás
🌪️ KRITIKUS JAVÍTÁS: SZÉLSEBESSÉG ADATOK FELDOLGOZÁSA
🌹 SZÉLIRÁNY KOMPATIBILITÁSI FIX: winddirection_10m_dominant → wind_direction_10m_dominant
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import pandas as pd
import logging

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from ..config import DATA_DIR, APIConfig, ProviderConfig, UserPreferences, UsageTracker
from .workers.data_fetch_worker import WorkerManager, GeocodingWorker, WeatherDataWorker
from .workers.analysis_worker import AnalysisWorker


class AppController(QObject):
    """
    🎯 CLEAN ARCHITECTURE CONTROLLER - Központi logikai agy
    
    FELELŐSSÉGEK:
    - Analysis request routing (single/multi-city/county)
    - Worker lifecycle management (create/start/stop/cleanup)
    - Provider selection és fallback strategies
    - Signal orchestration (UI ↔ Controller ↔ Analytics)
    - State management (current selections, active workers)
    
    🌐 PROVIDER ROUTING FUNKCIÓK:
    ✅ Smart provider selection (Open-Meteo vs Meteostat)
    ✅ User preference override support
    ✅ Usage tracking és cost monitoring
    ✅ Provider fallback strategies
    ✅ Wind gusts támogatás minden providernél
    
    🔧 KOORDINÁTA KULCSOK KOMPATIBILITÁS:
    ✅ 'lat'/'lon' ÉS 'latitude'/'longitude' kulcsok támogatása
    ✅ ControlPanel ↔ AppController kompatibilitás javítva
    
    🌪️ SZÉLSEBESSÉG KRITIKUS JAVÍTÁS:
    ✅ windspeed_10m_max adatok explicit másolása
    ✅ Napi adatok structured processing
    ✅ Teljes széladat kompatibilitás (speed + gusts)
    
    🌹 SZÉLIRÁNY KOMPATIBILITÁSI FIX:
    ✅ winddirection_10m_dominant → wind_direction_10m_dominant mapping
    ✅ WindRoseChart kompatibilitás biztosítva
    """
    
    # === CLEAN ARCHITECTURE SIGNALS ===
    
    # Analysis lifecycle signalok
    analysis_started = Signal(str)              # analysis_type
    analysis_progress = Signal(str, int)        # message, percentage
    analysis_completed = Signal(dict)           # result_data
    analysis_failed = Signal(str)               # error_message
    analysis_cancelled = Signal()               # megszakítás megerősítése
    
    # Eredeti signalok megőrzése (backwards compatibility)
    geocoding_results_ready = Signal(list)      # List[Dict] - település találatok
    weather_data_ready = Signal(dict)           # Dict - API válasz adatok
    error_occurred = Signal(str)                # str - hibaüzenet
    status_updated = Signal(str)                # str - státusz üzenet
    progress_updated = Signal(str, int)         # worker_type, progress
    
    # Adatbázis műveletek eredményei
    city_saved_to_db = Signal(dict)             # Dict - elmentett település adatok
    weather_saved_to_db = Signal(bool)          # bool - sikeres mentés
    
    # 🌐 PROVIDER ROUTING SIGNALOK
    provider_selected = Signal(str)             # str - választott provider neve
    provider_usage_updated = Signal(dict)       # Dict - usage statistics
    provider_warning = Signal(str, int)         # provider_name, usage_percent
    provider_fallback = Signal(str, str)        # from_provider, to_provider
    
    def __init__(self, parent: Optional[QObject] = None):
        """Controller inicializálása CLEAN ARCHITECTURE támogatással."""
        super().__init__(parent)
        
        self._logger = logging.getLogger(__name__)
        self._logger.info("🎯 AppController __init__ started (CLEAN ARCHITECTURE)")
        
        # === CLEAN ARCHITECTURE STATE ===
        self.current_city_data: Optional[Dict[str, Any]] = None
        self.current_weather_data: Optional[Dict[str, Any]] = None
        self.active_search_query: Optional[str] = None
        
        # 🎯 ANALYSIS WORKER MANAGEMENT
        self.active_analysis_worker: Optional[AnalysisWorker] = None
        self.analysis_state = {
            'is_running': False,
            'analysis_type': None,
            'start_time': None,
            'request_data': None
        }
        
        # 🌐 PROVIDER ROUTING KOMPONENSEK (megőrizve)
        self.provider_config = ProviderConfig()
        self.user_preferences = UserPreferences()
        self.usage_tracker = UsageTracker()
        
        self._logger.info("🌐 Provider routing komponensek betöltve:")
        self._logger.info(f"🌐 - Default provider: {self.user_preferences.get_selected_provider()}")
        self._logger.info(f"🌐 - Available providers: {list(self.provider_config.PROVIDERS.keys())}")
        
        # WorkerManager központi használata (megőrizve)
        self.worker_manager = WorkerManager()
        self._logger.info("🌐 WorkerManager created with PROVIDER ROUTING support")
        
        # Adatbázis kapcsolat inicializálása
        self.db_path = DATA_DIR / "meteo_data.db"
        self._init_database_connection()
        
        # Signal kapcsolások
        self._connect_worker_signals()
        self._connect_analysis_worker_signals()
        
        # Provider preferences betöltése
        self._load_user_preferences()
        
        self._logger.info("✅ AppController inicializálva (CLEAN ARCHITECTURE)")
    
    def _connect_analysis_worker_signals(self) -> None:
        """🎯 ANALYSIS WORKER signal bekötések."""
        self._logger.info("🔗 Analysis worker signals kapcsolása...")
        
        # Megjegyzés: Az AnalysisWorker signalok dinamikusan kerülnek bekötésre
        # amikor egy új worker létrejön a handle_analysis_request metódusban
        
        self._logger.info("✅ Analysis worker signals előkészítve")
    
    # === 🎯 CLEAN ARCHITECTURE - KÖZPONTI ANALYSIS REQUEST HANDLER ===
    
    @Slot(dict)
    def handle_analysis_request(self, request_data: Dict[str, Any]) -> None:
        """
        🎯 KÖZPONTI ELEMZÉSI KÉRÉS KEZELŐ - Clean Architecture Pattern
        
        Ez a metódus fogadja az összes elemzési kérést a ControlPanel-től
        és a megfelelő worker-ben futtatja azt háttérszálon.
        
        Args:
            request_data (dict): Teljes elemzési kérés minden paraméterre:
                - analysis_type: 'single_location', 'multi_city', 'county_analysis'
                - location_data: {'lat': float, 'lon': float, 'name': str, ...}
                - date_range: {'start_date': str, 'end_date': str}
                - provider_settings: {'provider': str, 'api_config': dict}
                - analysis_config: egyéb elemzési beállítások
        """
        self._logger.info(f"🎯 ANALYSIS REQUEST received: {request_data.get('analysis_type', 'unknown')}")
        
        try:
            # === 1. AKTUÁLIS ANALYSIS LEÁLLÍTÁSA ===
            if self.analysis_state['is_running']:
                self._logger.info("🛑 Aktuális analysis leállítása...")
                self.stop_current_analysis()
                
                # Rövid várakozás a tiszta leállásra
                QTimer.singleShot(200, lambda: self._start_new_analysis(request_data))
                return
            
            # === 2. ÚJ ANALYSIS AZONNALI INDÍTÁSA ===
            self._start_new_analysis(request_data)
            
        except Exception as e:
            self._logger.error(f"Analysis request hiba: {e}")
            self.analysis_failed.emit(f"Elemzési kérés hiba: {e}")
    
    def _start_new_analysis(self, request_data: Dict[str, Any]) -> None:
        """
        🎯 ÚJ ANALYSIS INDÍTÁSA - Worker létrehozás és konfigurálás
        
        Args:
            request_data: Elemzési kérés paraméterei
        """
        try:
            # === 1. REQUEST VALIDÁLÁS ===
            if not self._validate_analysis_request(request_data):
                return
            
            analysis_type = request_data.get('analysis_type', 'unknown')
            
            # === 2. ANALYSIS STATE INICIALIZÁLÁS ===
            self.analysis_state = {
                'is_running': True,
                'analysis_type': analysis_type,
                'start_time': datetime.now(),
                'request_data': request_data.copy()
            }
            
            # === 3. ANALYSIS WORKER LÉTREHOZÁS ===
            self.active_analysis_worker = AnalysisWorker(parent=self)
            
            # === 4. WORKER SIGNAL BEKÖTÉSEK ===
            self.active_analysis_worker.progress_updated.connect(self._on_analysis_progress)
            self.active_analysis_worker.analysis_completed.connect(self._on_analysis_completed)
            self.active_analysis_worker.analysis_failed.connect(self._on_analysis_failed)
            self.active_analysis_worker.analysis_cancelled.connect(self._on_analysis_cancelled)
            
            # === 5. PROVIDER ROUTING INTEGRÁCIÓ ===
            enhanced_request = self._enhance_request_with_provider_routing(request_data)
            
            # === 6. WORKER INDÍTÁS ===
            success = self.active_analysis_worker.start_analysis(enhanced_request)
            
            if success:
                # Indítás signalok
                self.analysis_started.emit(analysis_type)
                self.status_updated.emit(f"🎯 {analysis_type.replace('_', ' ').title()} elemzés indítva...")
                
                self._logger.info(f"✅ Analysis worker elindítva: {analysis_type}")
            else:
                self._logger.error("❌ Analysis worker indítás sikertelen")
                self.analysis_failed.emit("Worker indítási hiba")
                self._cleanup_analysis_state()
                
        except Exception as e:
            self._logger.error(f"Analysis indítási hiba: {e}")
            self.analysis_failed.emit(f"Elemzés indítási hiba: {e}")
            self._cleanup_analysis_state()
    
    def _validate_analysis_request(self, request_data: Dict[str, Any]) -> bool:
        """
        🔧 KRITIKUS JAVÍTÁS: ANALYSIS REQUEST VALIDÁLÁS - KOORDINÁTA KULCSOK KOMPATIBILITÁS
        
        Args:
            request_data: Kérés adatok
            
        Returns:
            bool: Valid-e a kérés
        """
        try:
            # Kötelező mezők ellenőrzése
            required_fields = ['analysis_type', 'date_range']
            for field in required_fields:
                if field not in request_data:
                    self.analysis_failed.emit(f"Hiányzó kötelező mező: {field}")
                    return False
            
            analysis_type = request_data.get('analysis_type')
            valid_types = ['single_location', 'multi_city', 'county_analysis']
            
            if analysis_type not in valid_types:
                self.analysis_failed.emit(f"Érvénytelen elemzés típus: {analysis_type}")
                return False
            
            # Dátum range validálás
            date_range = request_data.get('date_range', {})
            if not date_range.get('start_date') or not date_range.get('end_date'):
                self.analysis_failed.emit("Hiányzó dátum tartomány")
                return False
            try:
                start_date_value = datetime.strptime(date_range.get('start_date', ''), "%Y-%m-%d")
                end_date_value = datetime.strptime(date_range.get('end_date', ''), "%Y-%m-%d")
            except ValueError as exc:
                self.analysis_failed.emit(f"Érvénytelen dátum formátum: {exc}")
                return False
            if (end_date_value - start_date_value).days > 60 * 365:
                error_message = "Maximum 60 éves időszak kérdezhető le"
                self.error_occurred.emit(error_message)
                self.analysis_failed.emit(error_message)
                return False
            
            # 🔧 KRITIKUS JAVÍTÁS: Lokáció validálás KOORDINÁTA KULCSOK KOMPATIBILITÁSSAL
            if analysis_type == 'single_location':
                # ControlPanel többféle formátumot küldhet:
                # 1. Direkt koordináták: "latitude", "longitude" 
                # 2. location_data objektumban: "lat", "lon" VAGY "latitude", "longitude"
                
                has_direct_coords = False
                has_location_data_coords = False
                
                # 1. Direkt koordináták ellenőrzése (ControlPanel formátum)
                if 'latitude' in request_data and 'longitude' in request_data:
                    has_direct_coords = True
                    self._logger.info("🔧 Found direct coordinates: latitude/longitude")
                elif 'lat' in request_data and 'lon' in request_data:
                    has_direct_coords = True
                    self._logger.info("🔧 Found direct coordinates: lat/lon")
                
                # 2. location_data objektum ellenőrzése (AppController várt formátum)
                location_data = request_data.get('location_data', {})
                if location_data:
                    # Mindkét koordináta kulcs formátum támogatása
                    lat_keys = ['lat', 'latitude']
                    lon_keys = ['lon', 'longitude']
                    
                    has_lat = any(key in location_data for key in lat_keys)
                    has_lon = any(key in location_data for key in lon_keys)
                    
                    if has_lat and has_lon:
                        has_location_data_coords = True
                        self._logger.info("🔧 Found location_data coordinates")
                
                # Koordináták validálása
                if not (has_direct_coords or has_location_data_coords):
                    error_msg = "Hiányzó lokáció koordináták"
                    self._logger.error(f"🔧 COORDINATE VALIDATION FAILED: {error_msg}")
                    self._logger.error(f"🔧 Request keys: {list(request_data.keys())}")
                    if location_data:
                        self._logger.error(f"🔧 location_data keys: {list(location_data.keys())}")
                    
                    self.analysis_failed.emit(error_msg)
                    return False
                
                self._logger.info("✅ Single location coordinates validation passed")
            
            elif analysis_type in ['multi_city', 'county_analysis']:
                if not request_data.get('region_name') and not request_data.get('county_name'):
                    self.analysis_failed.emit("Hiányzó régió vagy megye név")
                    return False
            
            self._logger.info(f"✅ Analysis request validation OK: {analysis_type}")
            return True
            
        except Exception as e:
            self._logger.error(f"Request validation hiba: {e}")
            self.analysis_failed.emit(f"Kérés validálási hiba: {e}")
            return False
    
    def _enhance_request_with_provider_routing(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🌐 PROVIDER ROUTING INTEGRÁCIÓ - Kérés gazdagítása provider információkkal
        
        Args:
            request_data: Eredeti kérés
            
        Returns:
            Gazdagított kérés provider routing információkkal
        """
        try:
            enhanced_request = request_data.copy()
            
            # Koordináták kinyerése az elemzés típusa alapján
            latitude, longitude = self._extract_coordinates_from_request(request_data)
            
            if latitude is not None and longitude is not None:
                # Smart provider selection
                date_range = request_data.get('date_range', {})
                selected_provider = self._select_provider_for_request(
                    latitude, longitude, 
                    date_range.get('start_date', ''),
                    date_range.get('end_date', '')
                )
                
                # Provider információk hozzáadása
                enhanced_request['selected_provider'] = selected_provider
                enhanced_request['provider_config'] = self.provider_config.PROVIDERS.get(selected_provider, {})
                
                # Usage tracking
                self._track_provider_usage(selected_provider)
                
                self._logger.info(f"🌐 Provider routing: {selected_provider} selected")
            else:
                # Fallback provider
                enhanced_request['selected_provider'] = 'open-meteo'
                self._logger.warning("🌐 No coordinates found, using fallback provider")
            
            return enhanced_request
            
        except Exception as e:
            self._logger.error(f"Provider routing enhancement hiba: {e}")
            return request_data  # Return original on error
    
    def _extract_coordinates_from_request(self, request_data: Dict[str, Any]) -> tuple[Optional[float], Optional[float]]:
        """
        🔧 KOORDINÁTA KULCSOK KOMPATIBILITÁS: Koordináták kinyerése a kérésből az elemzés típusa alapján
        
        Args:
            request_data: Kérés adatok
            
        Returns:
            (latitude, longitude) tuple vagy (None, None)
        """
        analysis_type = request_data.get('analysis_type')
        
        if analysis_type == 'single_location':
            # 1. Direkt koordináták keresése (ControlPanel formátum)
            if 'latitude' in request_data and 'longitude' in request_data:
                return request_data.get('latitude'), request_data.get('longitude')
            elif 'lat' in request_data and 'lon' in request_data:
                return request_data.get('lat'), request_data.get('lon')
            
            # 2. location_data objektum ellenőrzése (AppController várt formátum)
            location_data = request_data.get('location_data', {})
            if location_data:
                # Mindkét koordináta kulcs formátum támogatása
                lat = location_data.get('latitude') or location_data.get('lat')
                lon = location_data.get('longitude') or location_data.get('lon')
                
                if lat is not None and lon is not None:
                    return lat, lon
        
        elif analysis_type in ['multi_city', 'county_analysis']:
            # Multi-city esetén használjuk a jelenlegi város koordinátáit (ha van)
            if self.current_city_data:
                return self.current_city_data.get('latitude'), self.current_city_data.get('longitude')
            
            # Vagy egy default magyar koordináta
            return 47.4979, 19.0402  # Budapest
        
        return None, None
    
    # === 🎯 ANALYSIS WORKER EVENT HANDLERS ===
    
    @Slot(str, int)
    def _on_analysis_progress(self, message: str, percentage: int):
        """Analysis progress frissítése"""
        self.analysis_progress.emit(message, percentage)
        self.status_updated.emit(f"📊 {message} ({percentage}%)")
        
        self._logger.debug(f"📊 Analysis progress: {message} - {percentage}%")
    
    @Slot(dict)
    def _on_analysis_completed(self, result_data: dict):
        """Analysis befejezése sikeresen"""
        try:
            self._logger.info("✅ Analysis completed successfully")
            
            # Eredmény feldolgozása típus alapján
            processed_result = self._process_analysis_result(result_data)
            
            # State cleanup
            analysis_type = self.analysis_state.get('analysis_type', 'unknown')
            duration = self._calculate_analysis_duration()
            
            # Success signalok
            self.analysis_completed.emit(processed_result)
            self.status_updated.emit(f"✅ {analysis_type.replace('_', ' ').title()} elemzés befejezve ({duration:.1f}s)")
            
            # Típus-specifikus eredmény továbbítás (backwards compatibility)
            if analysis_type == 'single_location':
                self.weather_data_ready.emit(processed_result)
            elif analysis_type in ['multi_city', 'county_analysis']:
                # A MultiCityEngine eredményét továbbítjuk a megfelelő GUI komponenseknek
                # Ez a MainWindow-ban fog megjelenni a térképen és az analytics nézetben
                pass
            
            # Cleanup
            self._cleanup_analysis_state()
            
        except Exception as e:
            self._logger.error(f"Analysis result processing hiba: {e}")
            self.analysis_failed.emit(f"Eredmény feldolgozási hiba: {e}")
    
    @Slot(str)
    def _on_analysis_failed(self, error_message: str):
        """Analysis hiba kezelése"""
        self._logger.error(f"❌ Analysis failed: {error_message}")
        
        self.analysis_failed.emit(error_message)
        self.status_updated.emit(f"❌ Elemzési hiba: {error_message}")
        
        self._cleanup_analysis_state()
    
    @Slot()
    def _on_analysis_cancelled(self):
        """Analysis megszakítás kezelése"""
        self._logger.info("ℹ️ Analysis cancelled")
        
        self.analysis_cancelled.emit()
        self.status_updated.emit("ℹ️ Elemzés megszakítva")
        
        self._cleanup_analysis_state()
    
    def _process_analysis_result(self, result_data: dict) -> dict:
        """
        Analysis eredmény feldolgozása és strukturálása
        
        Args:
            result_data: Nyers worker eredmény
            
        Returns:
            Feldolgozott és strukturált eredmény
        """
        try:
            analysis_type = self.analysis_state.get('analysis_type', 'unknown')
            
            processed_result = {
                'analysis_type': analysis_type,
                'request_data': self.analysis_state.get('request_data', {}),
                'result_data': result_data.get('result_data', {}),
                'metadata': {
                    'provider': result_data.get('provider', 'unknown'),
                    'timestamp': result_data.get('timestamp'),
                    'duration': self._calculate_analysis_duration(),
                    'success': result_data.get('success', True)
                }
            }
            
            # Típus-specifikus feldolgozás
            if analysis_type == 'single_location':
                # Single location eredmény további feldolgozása (ha szükséges)
                pass
            elif analysis_type in ['multi_city', 'county_analysis']:
                # Multi-city eredmény további feldolgozása
                processed_result['city_count'] = len(result_data.get('result_data', {}).get('cities', []))
            
            return processed_result
            
        except Exception as e:
            self._logger.error(f"Result processing hiba: {e}")
            return result_data  # Return original on error
    
    def _calculate_analysis_duration(self) -> float:
        """Analysis időtartam számítása másodpercben"""
        start_time = self.analysis_state.get('start_time')
        if start_time:
            return (datetime.now() - start_time).total_seconds()
        return 0.0
    
    def _cleanup_analysis_state(self):
        """Analysis state és worker cleanup"""
        try:
            # Worker cleanup
            if self.active_analysis_worker:
                if self.active_analysis_worker.isRunning():
                    self.active_analysis_worker.stop_analysis()
                
                # Disconnect signalok
                self.active_analysis_worker.progress_updated.disconnect()
                self.active_analysis_worker.analysis_completed.disconnect()
                self.active_analysis_worker.analysis_failed.disconnect()
                self.active_analysis_worker.analysis_cancelled.disconnect()
                
                # Worker törlése
                self.active_analysis_worker.deleteLater()
                self.active_analysis_worker = None
            
            # State reset
            self.analysis_state = {
                'is_running': False,
                'analysis_type': None,
                'start_time': None,
                'request_data': None
            }
            
            self._logger.info("🧹 Analysis state cleaned up")
            
        except Exception as e:
            self._logger.error(f"Cleanup hiba: {e}")
    
    # === 🎯 ANALYSIS CONTROL METHODS ===
    
    def stop_current_analysis(self) -> None:
        """
        🛑 AKTUÁLIS ANALYSIS LEÁLLÍTÁSA
        Graceful shutdown - nem brutális terminálás
        """
        try:
            if not self.analysis_state['is_running']:
                self._logger.info("🛑 Nincs futó analysis amit meg lehetne szakítani")
                return
            
            analysis_type = self.analysis_state.get('analysis_type', 'unknown')
            self._logger.info(f"🛑 Analysis megszakítása: {analysis_type}")
            
            if self.active_analysis_worker:
                self.active_analysis_worker.stop_analysis()
            
            # State update
            self.status_updated.emit("🛑 Elemzés megszakítása...")
            
        except Exception as e:
            self._logger.error(f"Analysis stop hiba: {e}")
    
    def is_analysis_running(self) -> bool:
        """Analysis futási állapot lekérdezése"""
        return self.analysis_state.get('is_running', False)
    
    def get_current_analysis_info(self) -> Dict[str, Any]:
        """Jelenlegi analysis információk lekérdezése"""
        return self.analysis_state.copy()
    
    # === EREDETI METÓDUSOK MEGŐRZÉSE (Backwards Compatibility) ===
    
    def _load_user_preferences(self) -> None:
        """User preferences betöltése és signalok küldése."""
        try:
            selected_provider = self.user_preferences.get_selected_provider()
            self._logger.info(f"🌐 User selected provider: {selected_provider}")
            
            # Provider selection signal
            self.provider_selected.emit(selected_provider)
            
            # Usage statistics signal
            usage_summary = self.usage_tracker.get_usage_summary()
            self.provider_usage_updated.emit({
                'meteostat': {
                    'requests': usage_summary.get('meteostat_requests', 0),
                    'limit': usage_summary.get('meteostat_limit', 10000)
                },
                'open-meteo': {
                    'requests': usage_summary.get('openmeteo_requests', 0),
                    'limit': float('inf')  # Unlimited
                }
            })
            
            # Warning ellenőrzés
            warning_level = usage_summary.get('warning_level', 'normal')
            usage_percent = usage_summary.get('meteostat_percentage', 0)
            
            if warning_level == 'critical':
                self.provider_warning.emit('meteostat', int(usage_percent))
            elif warning_level == 'warning':
                self.provider_warning.emit('meteostat', int(usage_percent))
            
            self._logger.info("✅ User preferences betöltve és signalok elküldve")
            
        except Exception as e:
            self._logger.error(f"User preferences betöltési hiba: {e}")
    
    def _init_database_connection(self) -> None:
        """🌪️ KRITIKUS JAVÍTÁS: Adatbázis kapcsolat inicializálása WIND GUSTS séma frissítéssel."""
        try:
            # Adatbázis mappa létrehozása ha nem létezik
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Kapcsolat tesztelése és séma frissítés
            conn = sqlite3.connect(str(self.db_path))
            
            # 🌪️ KRITIKUS JAVÍTÁS: Adatbázis séma frissítés wind_gusts_max oszloppal
            self._update_database_schema(conn)
            
            conn.close()
            
            self._logger.info(f"✅ Adatbázis kapcsolat OK (WIND GUSTS support): {self.db_path}")
            
        except Exception as e:
            self._logger.error(f"Adatbázis kapcsolat hiba: {e}")
            self.error_occurred.emit(f"Adatbázis hiba: {e}")
    
    def _update_database_schema(self, conn: sqlite3.Connection) -> None:
        """
        🌪️ KRITIKUS JAVÍTÁS: Adatbázis séma frissítés wind_gusts_max oszloppal.
        
        Args:
            conn: SQLite kapcsolat
        """
        try:
            cursor = conn.cursor()
            
            # Ellenőrizzük, hogy létezik-e a wind_gusts_max oszlop
            cursor.execute("PRAGMA table_info(weather_data)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'wind_gusts_max' not in columns:
                self._logger.info("🌪️ wind_gusts_max oszlop nem létezik - hozzáadás...")
                
                # Új oszlop hozzáadása
                cursor.execute("""
                    ALTER TABLE weather_data 
                    ADD COLUMN wind_gusts_max REAL
                """)
                
                self._logger.info("✅ wind_gusts_max oszlop sikeresen hozzáadva")
                
                # Index létrehozása a gyorsabb lekérdezésekhez
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_weather_data_wind_gusts_max 
                    ON weather_data(wind_gusts_max)
                """)
                
                self._logger.info("✅ wind_gusts_max index sikeresen létrehozva")
                
            else:
                self._logger.info("✅ wind_gusts_max oszlop már létezik")
            
            # 🌐 Provider tracking oszlop hozzáadása
            if 'data_provider' not in columns:
                self._logger.info("🌐 data_provider oszlop nem létezik - hozzáadás...")
                
                cursor.execute("""
                    ALTER TABLE weather_data 
                    ADD COLUMN data_provider TEXT DEFAULT 'open-meteo'
                """)
                
                self._logger.info("✅ data_provider oszlop sikeresen hozzáadva")
            
            conn.commit()
            
        except Exception as e:
            self._logger.error(f"Adatbázis séma frissítés hiba: {e}")
            # Nem kritikus hiba, folytatjuk a működést
    
    def _connect_worker_signals(self) -> None:
        """Worker signal kapcsolások."""
        self._logger.info("🔗 Worker signals kapcsolása...")
        
        # Geocoding worker signalok
        self.worker_manager.geocoding_completed.connect(self._on_geocoding_completed)
        self._logger.info("🔗 geocoding_completed signal connected")
        
        # Weather data worker signalok
        self.worker_manager.weather_data_completed.connect(self._on_weather_data_completed)
        self._logger.info("🔗 weather_data_completed signal connected")
        
        # Általános worker signalok
        self.worker_manager.error_occurred.connect(self._on_worker_error)
        self.worker_manager.progress_updated.connect(self.progress_updated.emit)
        
        self._logger.info("✅ Signal kapcsolások kész")
    
    # === PROVIDER ROUTING METÓDUSOK (MEGŐRIZVE) ===
    
    def _select_provider_for_request(self, latitude: float, longitude: float, 
                                   start_date: str, end_date: str) -> str:
        """
        🌐 Smart provider selection a kérés alapján.
        
        Args:
            latitude: Földrajzi szélesség
            longitude: Földrajzi hosszúság
            start_date: Kezdő dátum
            end_date: Befejező dátum
            
        Returns:
            Választott provider neve
        """
        try:
            # User preference ellenőrzése
            user_provider = self.user_preferences.get_selected_provider()
            
            if user_provider != 'auto':
                self._logger.info(f"🌐 User forced provider: {user_provider}")
                
                # Rate limiting ellenőrzés premium providereknél
                if user_provider != 'open-meteo':
                    usage_summary = self.usage_tracker.get_usage_summary()
                    if usage_summary.get('warning_level') == 'critical':
                        self._logger.warning(f"⚠️ Provider {user_provider} rate limit exceeded, fallback to open-meteo")
                        self.provider_fallback.emit(user_provider, 'open-meteo')
                        return 'open-meteo'
                
                return user_provider
            
            # Automatikus provider routing
            self._logger.info("🌐 Automatic provider routing...")
            
            # Dátum tartomány ellenőrzése
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days_requested = (end - start).days + 1
            
            # Historikus adat ellenőrzése (2 hónapnál régebbi)
            historical_threshold = datetime.now() - timedelta(days=60)
            is_historical = start < historical_threshold
            
            # Nagy dátum tartomány (3+ hónap)
            is_large_request = days_requested > 90
            
            self._logger.info(f"🌐 Request analysis:")
            self._logger.info(f"🌐 - Days requested: {days_requested}")
            self._logger.info(f"🌐 - Is historical: {is_historical}")
            self._logger.info(f"🌐 - Is large request: {is_large_request}")
            
            # Smart routing logic
            if is_historical or is_large_request:
                # Meteostat jobb historikus adatokhoz
                usage_summary = self.usage_tracker.get_usage_summary()
                if usage_summary.get('warning_level') != 'critical':
                    self._logger.info("🌐 Selected Meteostat for historical/large request")
                    return 'meteostat'
                else:
                    self._logger.info("🌐 Meteostat rate limited, fallback to Open-Meteo")
                    self.provider_fallback.emit('meteostat', 'open-meteo')
                    return 'open-meteo'
            else:
                # Aktuális/közelmúlt adatokhoz Open-Meteo
                self._logger.info("🌐 Selected Open-Meteo for recent data")
                return 'open-meteo'
                
        except Exception as e:
            self._logger.error(f"Provider selection error: {e}")
            return 'open-meteo'  # Fallback to free provider
    
    def _track_provider_usage(self, provider_name: str) -> None:
        """
        Provider használat tracking.
        
        Args:
            provider_name: Provider neve
        """
        try:
            # Usage tracking
            updated_usage = self.usage_tracker.track_request(provider_name)
            
            if updated_usage:
                self._logger.info(f"🌐 Tracked usage for {provider_name}")
                
                # Usage statistics frissítése - a track_request visszaadott adatok alapján
                usage_summary = self.usage_tracker.get_usage_summary()
                self.provider_usage_updated.emit({
                    'meteostat': {
                        'requests': usage_summary.get('meteostat_requests', 0),
                        'limit': usage_summary.get('meteostat_limit', 10000)
                    },
                    'open-meteo': {
                        'requests': usage_summary.get('openmeteo_requests', 0),
                        'limit': float('inf')  # Unlimited
                    }
                })
                
                # Warning ellenőrzés
                if provider_name != 'open-meteo':
                    warning_level = usage_summary.get('warning_level', 'normal')
                    usage_percent = usage_summary.get('meteostat_percentage', 0)
                    
                    if warning_level == 'critical':
                        self._logger.critical(f"🚨 Provider {provider_name} usage critical: {usage_percent:.1f}%")
                        self.provider_warning.emit(provider_name, int(usage_percent))
                    elif warning_level == 'warning':
                        self._logger.warning(f"⚠️ Provider {provider_name} usage warning: {usage_percent:.1f}%")
                        self.provider_warning.emit(provider_name, int(usage_percent))
            else:
                self._logger.warning(f"⚠️ Failed to track usage for {provider_name}")
                
        except Exception as e:
            self._logger.error(f"Usage tracking error: {e}")
    
    @Slot(str)
    def handle_provider_change(self, provider_name: str) -> None:
        """
        Provider változás kezelése GUI-ból.
        
        Args:
            provider_name: Új provider neve
        """
        try:
            self._logger.info(f"🌐 Provider change request: {provider_name}")
            
            # User preferences frissítése
            self.user_preferences.set_selected_provider(provider_name)
            
            # Provider selection signal
            self.provider_selected.emit(provider_name)
            
            # Státusz frissítése
            if provider_name == 'auto':
                status_msg = "🤖 Automatikus provider routing bekapcsolva"
            else:
                provider_info = self.provider_config.PROVIDERS.get(provider_name, {})
                provider_display = provider_info.get('name', provider_name)
                status_msg = f"🌐 Provider beállítva: {provider_display}"
            
            self.status_updated.emit(status_msg)
            
            self._logger.info(f"✅ Provider changed to: {provider_name}")
            
        except Exception as e:
            self._logger.error(f"Provider change error: {e}")
            self.error_occurred.emit(f"Provider váltási hiba: {e}")
    
    # === TELEPÜLÉS KERESÉS LOGIKA (MEGŐRIZVE) ===
    
    @Slot(str)
    def handle_search_request(self, search_query: str) -> None:
        """
        Település keresési kérés kezelése a ControlPanel-től.
        
        Args:
            search_query: Keresési kifejezés
        """
        self._logger.info(f"🔍 handle_search_request called with: '{search_query}'")
        
        # Alapszintű validáció
        if not search_query or len(search_query.strip()) < 2:
            error_msg = "Legalább 2 karakter szükséges a kereséshez"
            self._logger.error(f"Validation error: {error_msg}")
            self.error_occurred.emit(error_msg)
            return
        
        # Jelenlegi keresés tárolása
        self.active_search_query = search_query.strip()
        self._logger.info(f"🔍 Active search query set: '{self.active_search_query}'")
        
        # Státusz frissítése
        search_info = f"Keresés: {self.active_search_query}"
        self.status_updated.emit(search_info + "...")
        self._logger.info(f"🔍 Status updated: {search_info}")
        
        # Geocoding worker indítása
        try:
            self._logger.info("🚀 Creating GeocodingWorker...")
            worker = GeocodingWorker(self.active_search_query)
            self._logger.info(f"✅ GeocodingWorker created for query: '{self.active_search_query}'")
            
            # WorkerManager központi használata
            self._logger.info("🚀 Starting worker via WorkerManager...")
            worker_id = self.worker_manager.start_geocoding(worker)
            self._logger.info(f"✅ GeocodingWorker started via WorkerManager with ID: {worker_id}")
            
        except Exception as e:
            error_msg = f"Geocoding worker indítási hiba: {e}"
            self._logger.error(error_msg)
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(error_msg)
            return
        
        self._logger.info(f"✅ handle_search_request completed successfully for '{search_query}'")
    
    @Slot(list)
    def _on_geocoding_completed(self, results: List[Dict[str, Any]]) -> None:
        """
        Geocoding befejezésének kezelése.
        
        Args:
            results: Település találatok listája
        """
        self._logger.info(f"🔍 _on_geocoding_completed called with {len(results)} results")
        
        try:
            if not results:
                msg = "Nem található település ezzel a névvel"
                self._logger.info(f"🔍 No results found")
                self.status_updated.emit(msg)
                self.geocoding_results_ready.emit([])
                return
            
            self._logger.info(f"🔍 Processing {len(results)} geocoding results...")
            
            # Eredmények feldolgozása és gazdagítása
            processed_results = self._process_geocoding_results(results)
            self._logger.info(f"🔍 Processed {len(processed_results)} results")
            
            # Státusz frissítése
            status_msg = f"{len(processed_results)} település találat"
            self.status_updated.emit(status_msg)
            self._logger.info(f"🔍 Status updated: {status_msg}")
            
            # Eredmények továbbítása a GUI-nak
            self._logger.info(f"📡 Emitting geocoding_results_ready signal...")
            self.geocoding_results_ready.emit(processed_results)
            
            self._logger.info(f"✅ Geocoding befejezve: {len(processed_results)} találat")
            
        except Exception as e:
            self._logger.error(f"Geocoding feldolgozási hiba: {e}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"Keresési eredmények feldolgozási hiba: {e}")
    
    def _process_geocoding_results(self, raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Geocoding eredmények feldolgozása és gazdagítása.
        
        Args:
            raw_results: Nyers API eredmények
            
        Returns:
            Feldolgozott és gazdagított eredmények
        """
        processed = []
        
        self._logger.info(f"🔍 Processing {len(raw_results)} raw results")
        
        for i, result in enumerate(raw_results):
            try:
                # Alapadatok kinyerése
                processed_result = {
                    'name': result.get('name', ''),
                    'latitude': result.get('latitude', 0.0),
                    'longitude': result.get('longitude', 0.0),
                    'country': result.get('country', ''),
                    'admin1': result.get('admin1', ''),  # megye/régió
                    'admin2': result.get('admin2', ''),  # járás
                    'population': result.get('population'),
                    'timezone': result.get('timezone', 'UTC'),
                    'elevation': result.get('elevation'),
                    
                    # Megjelenítés a GUI számára
                    'display_name': self._create_display_name(result),
                    'search_rank': result.get('rank', 999),
                    'original_query': self.active_search_query,
                }
                
                processed.append(processed_result)
                
                # Debug információ minden 5. eredményhez
                if i < 5 or i % 5 == 0:
                    name = processed_result['name']
                    country = processed_result['country']
                    self._logger.debug(f"🔍 Result {i}: {name}, {country}")
                
            except Exception as e:
                self._logger.warning(f"⚠️ Eredmény {i} feldolgozási hiba: {e}")
                continue
        
        # Rendezés relevancia szerint
        processed.sort(key=lambda x: x['search_rank'])
        self._logger.info(f"🔍 Results sorted by relevance")
        
        return processed
    
    def _create_display_name(self, result: Dict[str, Any]) -> str:
        """
        Felhasználóbarát megjelenítési név létrehozása.
        
        Args:
            result: Geocoding eredmény
            
        Returns:
            Formázott megjelenítési név
        """
        name = result.get('name', 'Ismeretlen')
        admin1 = result.get('admin1', '')
        country = result.get('country', '')
        
        display_parts = [name]
        
        if admin1:
            display_parts.append(admin1)
        
        if country:
            display_parts.append(country)
        
        return ', '.join(display_parts)
    
    # === TELEPÜLÉS KIVÁLASZTÁS LOGIKA (MEGŐRIZVE) ===
    
    @Slot(str, float, float, dict)
    def handle_city_selection(self, city_name: str, latitude: float, longitude: float, metadata: Dict[str, Any]) -> None:
        """
        Település kiválasztás kezelése a ControlPanel-től.
        
        Args:
            city_name: Település neve
            latitude: Földrajzi szélesség
            longitude: Földrajzi hosszúság  
            metadata: További metaadatok
        """
        self._logger.info(f"🔍 handle_city_selection called: {city_name} ({latitude:.4f}, {longitude:.4f})")
        
        try:
            # Kiválasztott település adatainak mentése
            self.current_city_data = {
                'name': city_name,
                'latitude': latitude,
                'longitude': longitude,
                'metadata': metadata,
                'selected_at': datetime.now().isoformat(),
            }
            
            # Státusz frissítése
            status_msg = f"Kiválasztva: {city_name}"
            self.status_updated.emit(status_msg)
            self._logger.info(f"🔍 City selection status: {status_msg}")
            
            # Adatbázisba mentés (aszinkron)
            self._save_city_to_database(self.current_city_data)
            
            self._logger.info(f"✅ Település kiválasztva: {city_name} ({latitude:.4f}, {longitude:.4f})")
            
        except Exception as e:
            self._logger.error(f"Település kiválasztási hiba: {e}")
            self.error_occurred.emit(f"Település kiválasztási hiba: {e}")
    
    def _save_city_to_database(self, city_data: Dict[str, Any]) -> None:
        """
        Település adatok mentése adatbázisba.
        
        Args:
            city_data: Település adatok
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Upsert (INSERT OR REPLACE) művelet
            cursor.execute('''
                INSERT OR REPLACE INTO cities (name, latitude, longitude, country, region)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                city_data['name'],
                city_data['latitude'], 
                city_data['longitude'],
                city_data['metadata'].get('country', ''),
                city_data['metadata'].get('admin1', '')
            ))
            
            conn.commit()
            conn.close()
            
            # Sikeres mentés jelzése
            self.city_saved_to_db.emit(city_data)
            
            self._logger.info(f"✅ Település mentve adatbázisba: {city_data['name']}")
            
        except Exception as e:
            self._logger.error(f"Adatbázis mentési hiba: {e}")
            # Nem kritikus hiba, nem szakítjuk meg a folyamatot
    
    # === IDŐJÁRÁSI ADATOK LEKÉRDEZÉS LOGIKA (MEGŐRIZVE, DE DEPRECATED) ===
    
    @Slot(float, float, str, str, dict)
    def handle_weather_data_request(self, latitude: float, longitude: float, 
                                   start_date: str, end_date: str, params: Dict[str, Any]) -> None:
        """
        🌐🌪️ DEPRECATED: Időjárási adatok lekérdezés (használd handle_analysis_request-et helyette)
        
        Args:
            latitude: Földrajzi szélesség
            longitude: Földrajzi hosszúság
            start_date: Kezdő dátum (YYYY-MM-DD)
            end_date: Befejező dátum (YYYY-MM-DD)
            params: API paraméterek
        """
        self._logger.warning("🌐🌪️ DEPRECATED: handle_weather_data_request használata. Használd handle_analysis_request-et!")
        
        # Konvertálás új formátumra és továbbítás
        analysis_request = {
            'analysis_type': 'single_location',
            'location_data': {
                'lat': latitude,
                'lon': longitude,
                'name': self.current_city_data.get('name', 'Unknown') if self.current_city_data else 'Unknown'
            },
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'api_params': params
        }
        
        self.handle_analysis_request(analysis_request)
    
    @Slot(dict)
    def _on_weather_data_completed(self, data: Dict[str, Any]) -> None:
        """
        🌐🌪️ Időjárási adatok lekérdezésének befejezése (backwards compatibility).
        
        Args:
            data: API válasz adatok
        """
        self._logger.info(f"🌐🌪️ _on_weather_data_completed called (backwards compatibility)")
        
        try:
            # Provider információ kinyerése az adatokból
            used_provider = data.get('provider', 'unknown')
            self._logger.info(f"🌐 Weather data received from provider: {used_provider}")
            
            # Adatok feldolgozása és validálása
            processed_data = self._process_weather_data(data)
            
            if not processed_data:
                self.error_occurred.emit("Nincs feldolgozható időjárási adat")
                return
            
            # Provider információ hozzáadása a feldolgozott adatokhoz
            processed_data['provider'] = used_provider
            
            # Jelenlegi adatok mentése
            self.current_weather_data = processed_data
            
            # Adatbázisba mentés (aszinkron)
            self._save_weather_to_database(processed_data)
            
            # Státusz frissítése
            city_name = self.current_city_data.get('name', 'Ismeretlen') if self.current_city_data else 'Ismeretlen'
            record_count = len(processed_data.get('daily', {}).get('time', []))
            
            # 🌪️ Széllökés statisztika a státuszban
            wind_gusts_info = ""
            if 'wind_gusts_max' in processed_data.get('daily', {}):
                wind_gusts_max = processed_data['daily']['wind_gusts_max']
                if wind_gusts_max:
                    max_gust = max([g for g in wind_gusts_max if g is not None])
                    wind_gusts_info = f", max széllökés: {max_gust:.1f} km/h"
            
            # 🌐 Provider info a státuszban
            provider_display = self.provider_config.PROVIDERS.get(used_provider, {}).get('name', used_provider)
            
            self.status_updated.emit(
                f"🌐🌪️ Adatok sikeresen lekérdezve ({provider_display}): {city_name} ({record_count} nap{wind_gusts_info})"
            )
            
            # Eredmények továbbítása a GUI komponenseknek
            self._logger.info(f"📡 Emitting weather_data_ready signal...")
            self.weather_data_ready.emit(processed_data)
            
            self._logger.info(f"✅ Weather data befejezve: {record_count} napi rekord (backwards compatibility)")
            
        except Exception as e:
            self._logger.error(f"Weather data feldolgozási hiba: {e}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"Adatok feldolgozási hiba: {e}")
    
    def _process_weather_data(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        🌪️ KRITIKUS SZÉLSEBESSÉG JAVÍTÁS: Időjárási adatok feldolgozása WIND SPEED + WIND GUSTS teljes támogatással.
        🌹 SZÉLIRÁNY KOMPATIBILITÁSI FIX: winddirection_10m_dominant → wind_direction_10m_dominant mapping
        
        Args:
            raw_data: Nyers API adatok
            
        Returns:
            Feldolgozott adatok vagy None
        """
        try:
            self._logger.info(f"🌪️🌹 Processing weather data (COMPLETE WIND DATA + WIND DIRECTION FIX)...")
            
            if not raw_data or 'daily' not in raw_data:
                self._logger.warning(f"⚠️ Invalid weather data structure")
                return None
            
            daily_data = raw_data['daily']
            hourly_data = raw_data.get('hourly', {})
            
            # Alapvető mezők ellenőrzése
            required_fields = ['time', 'temperature_2m_max', 'temperature_2m_min', 'precipitation_sum']
            for field in required_fields:
                if field not in daily_data or not daily_data[field]:
                    self._logger.warning(f"⚠️ Hiányzó mező: {field}")
                    return None
            
            record_count = len(daily_data['time'])
            self._logger.info(f"🌪️🌹 Weather data valid - {record_count} records")
            
            # 🌹 DEBUG: Eredeti adatok kulcsainak ellenőrzése
            self._logger.info(f"🌹 DEBUG: daily_data keys: {list(daily_data.keys())}")
            
            # 🌹 KRITIKUS JAVÍTÁS: Szélirány adatok ellenőrzése és debug
            if 'winddirection_10m_dominant' in daily_data:
                wind_direction_data = daily_data['winddirection_10m_dominant']
                valid_directions = [d for d in wind_direction_data if d is not None]
                self._logger.info(f"🌹 DEBUG: winddirection: {len(valid_directions)} elems")
                if valid_directions:
                    self._logger.info(f"🌹 Found wind direction data: {len(valid_directions)} valid values")
                    self._logger.info(f"🌹 Wind direction range: {min(valid_directions):.0f}° → {max(valid_directions):.0f}°")
                else:
                    self._logger.warning(f"🌹 No valid wind direction data found!")
            else:
                self._logger.warning(f"🌹 No winddirection_10m_dominant field found in daily_data!")
            
            # 🌪️ KRITIKUS JAVÍTÁS: Óránkénti széllökések → napi maximum számítás
            daily_wind_gusts_max = self._calculate_daily_max_wind_gusts(
                hourly_data.get('wind_gusts_10m', []),
                hourly_data.get('time', []),
                daily_data.get('time', [])
            )
            
            # 🌪️ KRITIKUS JAVÍTÁS: Feldolgozott adatok strukturált összeállítása
            processed = {
                'daily': {},  # 🚀 KEZDETBEN ÜRES - Explicit feltöltés következik!
                'hourly': hourly_data,  # Óránkénti adatok megtartása
                'latitude': raw_data.get('latitude'),
                'longitude': raw_data.get('longitude'),
                'timezone': raw_data.get('timezone', 'UTC'),
                'elevation': raw_data.get('elevation'),
                
                # Metaadatok
                'data_source': raw_data.get('provider', 'unknown'),
                'source_type': raw_data.get('provider', 'unknown'),
                'provider': raw_data.get('provider', 'unknown'),  # 🌐 Provider info biztosítása
                'processed_at': datetime.now().isoformat(),
                'city_data': self.current_city_data.copy() if self.current_city_data else None,
                'record_count': record_count
            }
            
            # 🚀 KRITIKUS JAVÍTÁS: Napi adatok explicit másolása, beleértve a szélsebességet is!
            required_daily_fields = [
                'time', 'temperature_2m_max', 'temperature_2m_min', 'precipitation_sum',
                'windspeed_10m_max'  # 🌪️ EZ A HIÁNYZÓ LÁNCSZEM!
            ]
            
            self._logger.info(f"🌪️ Explicit copying of daily fields...")
            for field in required_daily_fields:
                if field in daily_data:
                    processed['daily'][field] = daily_data[field]
                    self._logger.debug(f"🌪️ Copied field: {field} ({len(daily_data[field])} values)")
                else:
                    self._logger.warning(f"⚠️ Missing field in daily_data: {field}")
            
            # További opcionális mezők másolása
            optional_daily_fields = [
                'windspeed_10m_mean', 'winddirection_10m_dominant', 
                'apparent_temperature_max', 'apparent_temperature_min',
                'shortwave_radiation_sum', 'et0_fao_evapotranspiration'
            ]
            
            for field in optional_daily_fields:
                if field in daily_data:
                    processed['daily'][field] = daily_data[field]
                    self._logger.debug(f"🌪️ Copied optional field: {field}")
            
            # 🌪️ KRITIKUS JAVÍTÁS: Napi maximum széllökések hozzáadása
            if daily_wind_gusts_max:
                processed['daily']['wind_gusts_max'] = daily_wind_gusts_max
                self._logger.info(f"🌪️ Added {len(daily_wind_gusts_max)} daily wind gusts max values")
                
                # Statisztika
                valid_gusts = [g for g in daily_wind_gusts_max if g is not None and g > 0]
                if valid_gusts:
                    max_gust = max(valid_gusts)
                    self._logger.info(f"🌪️ Maximum napi széllökés: {max_gust:.1f} km/h")
                    
                    # Kritikus ellenőrzés - életveszélyes alulbecslés detektálása
                    if max_gust > 100:
                        self._logger.warning(f"⚠️  KRITIKUS: Extrém széllökés detektálva: {max_gust:.1f} km/h")
                    elif max_gust > 80:
                        self._logger.warning(f"⚠️  Viharos széllökés detektálva: {max_gust:.1f} km/h")
                    elif max_gust > 60:
                        self._logger.info(f"✅ Erős széllökés detektálva: {max_gust:.1f} km/h")
                    else:
                        self._logger.info(f"✅ Mérsékelt széllökés: {max_gust:.1f} km/h")
            else:
                self._logger.warning(f"⚠️ Nincs széllökés adat az óránkénti adatokban")
            
            # 🌪️ KRITIKUS ELLENŐRZÉS: Szélsebesség adat jelenlét validálása
            if 'windspeed_10m_max' in processed['daily']:
                wind_speeds = processed['daily']['windspeed_10m_max']
                valid_speeds = [s for s in wind_speeds if s is not None and s > 0]
                if valid_speeds:
                    max_speed = max(valid_speeds)
                    avg_speed = sum(valid_speeds) / len(valid_speeds)
                    self._logger.info(f"🌪️ Szélsebesség adatok sikeresen feldolgozva:")
                    self._logger.info(f"🌪️ - Maximum szélsebesség: {max_speed:.1f} km/h")
                    self._logger.info(f"🌪️ - Átlagos szélsebesség: {avg_speed:.1f} km/h")
                    self._logger.info(f"🌪️ - Érvényes napok: {len(valid_speeds)}/{len(wind_speeds)}")
                else:
                    self._logger.warning(f"⚠️ Szélsebesség adatok üresek vagy nullák!")
            else:
                self._logger.error(f"❌ KRITIKUS: windspeed_10m_max NEM került át a feldolgozott adatokba!")
                self._logger.error(f"❌ Available daily fields: {list(processed['daily'].keys())}")
                self._logger.error(f"❌ Original daily fields: {list(daily_data.keys())}")
            
            self._logger.info(f"✅ Weather data processed successfully with COMPLETE WIND DATA - {record_count} records")
            self._logger.info(f"🌪️ Final processed daily fields: {list(processed['daily'].keys())}")

            # === 🌹 KRITIKUS SZÉLIRÁNY KOMPATIBILITÁSI FIX ===
            # Biztosítja, hogy a WindRoseChart megkapja az adatot a várt kulccsal.
            if 'winddirection_10m_dominant' in daily_data:
                processed['daily']['wind_direction_10m_dominant'] = daily_data['winddirection_10m_dominant']
                self._logger.info("✅ Wind direction data mapped for WindRoseChart compatibility.")
            
            return processed
            
        except Exception as e:
            self._logger.error(f"Weather data feldolgozási hiba: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _calculate_daily_max_wind_gusts(self, hourly_gusts: List[float], 
                                       hourly_times: List[str], 
                                       daily_times: List[str]) -> List[float]:
        """
        🌪️ KRITIKUS JAVÍTÁS: Óránkénti széllökések → napi maximum konverziója.
        
        Args:
            hourly_gusts: Óránkénti széllökések (km/h)
            hourly_times: Óránkénti időpontok (ISO format)
            daily_times: Napi időpontok (YYYY-MM-DD format)
            
        Returns:
            Napi maximum széllökések listája
        """
        try:
            self._logger.info(f"🌪️ Calculating daily max wind gusts...")
            self._logger.info(f"🌪️ Hourly gusts count: {len(hourly_gusts)}")
            self._logger.info(f"🌪️ Hourly times count: {len(hourly_times)}")
            self._logger.info(f"🌪️ Daily times count: {len(daily_times)}")
            
            if not hourly_gusts or not hourly_times or not daily_times:
                self._logger.warning(f"⚠️ Missing data for wind gusts calculation")
                return []
            
            # Óránkénti adatok DataFrame-be konvertálása
            hourly_df = pd.DataFrame({
                'time': pd.to_datetime(hourly_times),
                'wind_gusts': hourly_gusts
            })
            
            # Datum oszlop hozzáadása (óránkénti időpontokból)
            hourly_df['date'] = hourly_df['time'].dt.date
            
            # Napi maximumok számítása
            daily_max_gusts = []
            
            for daily_time in daily_times:
                try:
                    # Napi dátum konvertálása
                    daily_date = pd.to_datetime(daily_time).date()
                    
                    # Adott nap óránkénti széllökései
                    day_gusts = hourly_df[hourly_df['date'] == daily_date]['wind_gusts']
                    
                    if not day_gusts.empty:
                        # Csak érvényes értékek (nem None, nem NaN)
                        valid_gusts = day_gusts.dropna()
                        
                        if not valid_gusts.empty:
                            daily_max = valid_gusts.max()
                            daily_max_gusts.append(daily_max)
                            
                            # Debug logolás minden 10. naphoz
                            if len(daily_max_gusts) % 10 == 0:
                                self._logger.debug(f"🌪️ Day {daily_time}: max gust {daily_max:.1f} km/h")
                        else:
                            # Nincs érvényes széllökés adat erre a napra
                            daily_max_gusts.append(None)
                    else:
                        # Nincs óránkénti adat erre a napra
                        daily_max_gusts.append(None)
                        
                except Exception as e:
                    self._logger.warning(f"⚠️ Error processing day {daily_time}: {e}")
                    daily_max_gusts.append(None)
            
            # Eredmény validálás
            valid_gusts = [g for g in daily_max_gusts if g is not None and g > 0]
            
            if valid_gusts:
                max_overall = max(valid_gusts)
                avg_gusts = sum(valid_gusts) / len(valid_gusts)
                
                self._logger.info(f"🌪️ Daily wind gusts calculation complete:")
                self._logger.info(f"🌪️ - Valid days: {len(valid_gusts)}/{len(daily_max_gusts)}")
                self._logger.info(f"🌪️ - Maximum overall: {max_overall:.1f} km/h")
                self._logger.info(f"🌪️ - Average gusts: {avg_gusts:.1f} km/h")
                
                # Kritikus ellenőrzés - életveszélyes alulbecslés detektálása
                if max_overall > 120:
                    self._logger.critical(f"🚨 KRITIKUS: Hurrikán erősségű széllökés: {max_overall:.1f} km/h")
                elif max_overall > 100:
                    self._logger.warning(f"⚠️  KRITIKUS: Extrém széllökés: {max_overall:.1f} km/h")
                elif max_overall > 80:
                    self._logger.warning(f"⚠️  Viharos széllökés: {max_overall:.1f} km/h")
                else:
                    self._logger.info(f"✅ Mérsékelt széllökés: {max_overall:.1f} km/h")
                    
            else:
                self._logger.warning(f"⚠️ Nincs érvényes széllökés adat")
            
            return daily_max_gusts
            
        except Exception as e:
            self._logger.error(f"Daily wind gusts calculation error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _save_weather_to_database(self, weather_data: Dict[str, Any]) -> None:
        """
        🌐🌪️ KRITIKUS JAVÍTÁS: Időjárási adatok mentése adatbázisba PROVIDER ROUTING + WIND GUSTS támogatással.
        
        Args:
            weather_data: Feldolgozott időjárási adatok
        """
        try:
            if not self.current_city_data:
                self._logger.warning("⚠️ Nincs város adat az időjárási adatok mentéséhez")
                return
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Város ID lekérdezése
            cursor.execute('SELECT id FROM cities WHERE name = ? AND latitude = ? AND longitude = ?', 
                          (self.current_city_data['name'], 
                           self.current_city_data['latitude'],
                           self.current_city_data['longitude']))
            
            city_result = cursor.fetchone()
            if not city_result:
                self._logger.warning("⚠️ Város nem található az adatbázisban")
                conn.close()
                return
            
            city_id = city_result[0]
            daily_data = weather_data['daily']
            
            # 🌐 Provider információ
            data_provider = weather_data.get('provider', 'unknown')
            
            # Időjárási adatok mentése
            saved_count = 0
            for i, date in enumerate(daily_data['time']):
                try:
                    # 🌪️ KRITIKUS JAVÍTÁS: wind_gusts_max oszlop hozzáadása
                    wind_gusts_max = None
                    if 'wind_gusts_max' in daily_data and i < len(daily_data['wind_gusts_max']):
                        wind_gusts_max = daily_data['wind_gusts_max'][i]
                    
                    # 🌪️ KRITIKUS JAVÍTÁS: windspeed_10m_max proper handling
                    windspeed_max = None
                    if 'windspeed_10m_max' in daily_data and i < len(daily_data['windspeed_10m_max']):
                        windspeed_max = daily_data['windspeed_10m_max'][i]
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO weather_data 
                        (city_id, date, temp_max, temp_min, precipitation, windspeed_max, wind_gusts_max, data_provider)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        city_id,
                        date,
                        daily_data['temperature_2m_max'][i] if i < len(daily_data['temperature_2m_max']) else None,
                        daily_data['temperature_2m_min'][i] if i < len(daily_data['temperature_2m_min']) else None,
                        daily_data['precipitation_sum'][i] if i < len(daily_data['precipitation_sum']) else None,
                        windspeed_max,      # 🌪️ KRITIKUS JAVÍTÁS: Proper windspeed_max használata
                        wind_gusts_max,     # 🌪️ KRITIKUS JAVÍTÁS: Új wind_gusts_max oszlop
                        data_provider       # 🌐 Provider tracking
                    ))
                    saved_count += 1
                    
                    # Debug logolás szélsebesség + széllökésekhez
                    if windspeed_max is not None and windspeed_max > 40:
                        self._logger.info(f"🌪️ Saved high wind speed ({data_provider}): {date} - {windspeed_max:.1f} km/h")
                    if wind_gusts_max is not None and wind_gusts_max > 80:
                        self._logger.info(f"🌪️ Saved extreme wind gust ({data_provider}): {date} - {wind_gusts_max:.1f} km/h")
                        
                except Exception as e:
                    self._logger.warning(f"⚠️ Rekord mentési hiba: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            # Sikeres mentés jelzése
            self.weather_saved_to_db.emit(True)
            
            self._logger.info(f"✅ Weather data mentve adatbázisba ({data_provider}): {saved_count} rekord")
            
        except Exception as e:
            self._logger.error(f"Weather data adatbázis hiba: {e}")
            self.weather_saved_to_db.emit(False)
    
    # === HIBA KEZELÉS ===
    
    @Slot(str)
    def _on_worker_error(self, error_message: str) -> None:
        """
        Worker hibák kezelése.
        
        Args:
            error_message: Hibaüzenet
        """
        self._logger.error(f"Worker error: {error_message}")
        
        self.status_updated.emit(f"Hiba: {error_message}")
        self.error_occurred.emit(error_message)
    
    # === PUBLIKUS API ===
    
    def get_current_city(self) -> Optional[Dict[str, Any]]:
        """Jelenlegi kiválasztott város adatainak lekérdezése."""
        return self.current_city_data.copy() if self.current_city_data else None
    
    def get_current_weather_data(self) -> Optional[Dict[str, Any]]:
        """Jelenlegi időjárási adatok lekérdezése."""
        return self.current_weather_data.copy() if self.current_weather_data else None
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        🌐 Provider információk lekérdezése GUI számára.
        
        Returns:
            Provider információk és statistics
        """
        try:
            current_provider = self.user_preferences.get_selected_provider()
            usage_summary = self.usage_tracker.get_usage_summary()
            
            return {
                'current_provider': current_provider,
                'usage_summary': usage_summary,
                'available_providers': list(self.provider_config.PROVIDERS.keys()),
                'provider_configs': self.provider_config.PROVIDERS
            }
        except Exception as e:
            self._logger.error(f"Provider info hiba: {e}")
            return {}
    
    def cancel_all_operations(self) -> None:
        """
        🛑 Összes aktív művelet megszakítása.
        """
        try:
            self._logger.info("🛑 Cancelling all operations...")
            
            # Analysis Worker megszakítása
            if self.is_analysis_running():
                self.stop_current_analysis()
            
            # WorkerManager központi cancel
            self.worker_manager.cancel_all()
            
            self.status_updated.emit("🛑 Műveletek megszakítva")
            self._logger.info("✅ Összes művelet megszakítva")
            
        except Exception as e:
            self._logger.error(f"Műveletek megszakítási hiba: {e}")
    
    def shutdown(self) -> None:
        """Controller leállítása és cleanup."""
        try:
            self._logger.info("🛑 AppController leállítása...")
            
            # Összes művelet megszakítása
            self.cancel_all_operations()
            
            # Analysis worker cleanup
            self._cleanup_analysis_state()
            
            # WorkerManager központi leállítás
            self.worker_manager.shutdown()
            
            # User preferences mentése
            self.user_preferences.save()
            self.usage_tracker.save()
            
            # Állapot tisztítása
            self.current_city_data = None
            self.current_weather_data = None
            self.active_search_query = None
            
            self._logger.info("✅ AppController leállítva (CLEAN ARCHITECTURE)")
            
        except Exception as e:
            self._logger.warning(f"⚠️ Controller leállítási hiba: {e}")
            import traceback
            traceback.print_exc()
