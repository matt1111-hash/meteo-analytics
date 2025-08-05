#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Application Controller - PROVIDER ROUTING SUPPORT
Alkalmazás központi logikai vezérlője - PROVIDER SELECTOR támogatással.

🌍 PROVIDER ROUTING FUNKCIÓK:
✅ Smart provider routing (Open-Meteo vs Meteostat)
✅ User preference kezelés (Automatikus/Kényszerített)
✅ Usage tracking és cost monitoring
✅ Provider status signalok GUI-nak
✅ Rate limiting és fallback logic
✅ Wind gusts támogatás minden providernél
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import pandas as pd

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QMessageBox

from ..config import DATA_DIR, APIConfig, ProviderConfig, UserPreferences, UsageTracker
from .workers.data_fetch_worker import WorkerManager, GeocodingWorker, WeatherDataWorker


class AppController(QObject):
    """
    Az alkalmazás logikai vezérlője - PROVIDER ROUTING támogatással.
    
    🌍 PROVIDER ROUTING FUNKCIÓK:
    ✅ Smart provider selection (Open-Meteo vs Meteostat)
    ✅ User preference override support
    ✅ Usage tracking és cost monitoring
    ✅ Provider fallback strategies
    ✅ Wind gusts támogatás minden providernél
    """
    
    # Signalok a GUI komponensek felé
    geocoding_results_ready = Signal(list)      # List[Dict] - település találatok
    weather_data_ready = Signal(dict)           # Dict - API válasz adatok
    error_occurred = Signal(str)                # str - hibaüzenet
    status_updated = Signal(str)                # str - státusz üzenet
    progress_updated = Signal(str, int)         # worker_type, progress
    
    # Adatbázis műveletek eredményei
    city_saved_to_db = Signal(dict)             # Dict - elmentett település adatok
    weather_saved_to_db = Signal(bool)          # bool - sikeres mentés
    
    # 🌍 PROVIDER ROUTING SIGNALOK
    provider_selected = Signal(str)             # str - választott provider neve
    provider_usage_updated = Signal(dict)       # Dict - usage statistics
    provider_warning = Signal(str, int)         # provider_name, usage_percent
    provider_fallback = Signal(str, str)        # from_provider, to_provider
    
    def __init__(self, parent: Optional[QObject] = None):
        """Controller inicializálása PROVIDER ROUTING támogatással."""
        super().__init__(parent)
        
        print("🌍 DEBUG: AppController __init__ started (PROVIDER ROUTING support)")
        
        # Állapot változók
        self.current_city_data: Optional[Dict[str, Any]] = None
        self.current_weather_data: Optional[Dict[str, Any]] = None
        self.active_search_query: Optional[str] = None
        
        # 🌍 PROVIDER ROUTING KOMPONENSEK
        self.provider_config = ProviderConfig()
        self.user_preferences = UserPreferences()
        self.usage_tracker = UsageTracker()
        
        print("🌍 DEBUG: Provider routing komponensek betöltve:")
        print(f"🌍 DEBUG: - Default provider: {self.user_preferences.get_selected_provider()}")
        print(f"🌍 DEBUG: - Available providers: {list(self.provider_config.PROVIDERS.keys())}")
        
        # WorkerManager központi használata
        self.worker_manager = WorkerManager()
        print("🌍 DEBUG: WorkerManager created with PROVIDER ROUTING support")
        
        # Adatbázis kapcsolat inicializálása
        self.db_path = DATA_DIR / "meteo_data.db"
        self._init_database_connection()
        
        # Signal kapcsolások
        self._connect_worker_signals()
        
        # Provider preferences betöltése
        self._load_user_preferences()
        
        print("✅ DEBUG: AppController inicializálva (PROVIDER ROUTING support)")
    
    def _load_user_preferences(self) -> None:
        """User preferences betöltése és signalok küldése."""
        try:
            selected_provider = self.user_preferences.get_selected_provider()
            print(f"🌍 DEBUG: User selected provider: {selected_provider}")
            
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
            
            print("✅ DEBUG: User preferences betöltve és signalok elküldve")
            
        except Exception as e:
            print(f"⚠️ DEBUG: User preferences betöltési hiba: {e}")
    
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
            
            print(f"✅ DEBUG: Adatbázis kapcsolat OK (WIND GUSTS support): {self.db_path}")
            
        except Exception as e:
            print(f"❌ DEBUG: Adatbázis kapcsolat hiba: {e}")
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
                print("🌪️ DEBUG: wind_gusts_max oszlop nem létezik - hozzáadás...")
                
                # Új oszlop hozzáadása
                cursor.execute("""
                    ALTER TABLE weather_data 
                    ADD COLUMN wind_gusts_max REAL
                """)
                
                print("✅ DEBUG: wind_gusts_max oszlop sikeresen hozzáadva")
                
                # Index létrehozása a gyorsabb lekérdezésekhez
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_weather_data_wind_gusts_max 
                    ON weather_data(wind_gusts_max)
                """)
                
                print("✅ DEBUG: wind_gusts_max index sikeresen létrehozva")
                
            else:
                print("✅ DEBUG: wind_gusts_max oszlop már létezik")
            
            # 🌍 Provider tracking oszlop hozzáadása
            if 'data_provider' not in columns:
                print("🌍 DEBUG: data_provider oszlop nem létezik - hozzáadás...")
                
                cursor.execute("""
                    ALTER TABLE weather_data 
                    ADD COLUMN data_provider TEXT DEFAULT 'open-meteo'
                """)
                
                print("✅ DEBUG: data_provider oszlop sikeresen hozzáadva")
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ DEBUG: Adatbázis séma frissítés hiba: {e}")
            # Nem kritikus hiba, folytatjuk a működést
    
    def _connect_worker_signals(self) -> None:
        """Worker signal kapcsolások."""
        print("🔗 DEBUG: Worker signals kapcsolása...")
        
        # Geocoding worker signalok
        self.worker_manager.geocoding_completed.connect(self._on_geocoding_completed)
        print("🔗 DEBUG: geocoding_completed signal connected")
        
        # Weather data worker signalok
        self.worker_manager.weather_data_completed.connect(self._on_weather_data_completed)
        print("🔗 DEBUG: weather_data_completed signal connected")
        
        # Általános worker signalok
        self.worker_manager.error_occurred.connect(self._on_worker_error)
        self.worker_manager.progress_updated.connect(self.progress_updated.emit)
        
        print("✅ DEBUG: Signal kapcsolások kész")
    
    # === PROVIDER ROUTING METÓDUSOK ===
    
    def _select_provider_for_request(self, latitude: float, longitude: float, 
                                   start_date: str, end_date: str) -> str:
        """
        🌍 Smart provider selection a kérés alapján.
        
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
                print(f"🌍 DEBUG: User forced provider: {user_provider}")
                
                # Rate limiting ellenőrzés premium providereknél
                if user_provider != 'open-meteo':
                    usage_summary = self.usage_tracker.get_usage_summary()
                    if usage_summary.get('warning_level') == 'critical':
                        print(f"⚠️ DEBUG: Provider {user_provider} rate limit exceeded, fallback to open-meteo")
                        self.provider_fallback.emit(user_provider, 'open-meteo')
                        return 'open-meteo'
                
                return user_provider
            
            # Automatikus provider routing
            print("🌍 DEBUG: Automatic provider routing...")
            
            # Dátum tartomány ellenőrzése
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days_requested = (end - start).days + 1
            
            # Historikus adat ellenőrzése (2 hónapnál régebbi)
            historical_threshold = datetime.now() - timedelta(days=60)
            is_historical = start < historical_threshold
            
            # Nagy dátum tartomány (3+ hónap)
            is_large_request = days_requested > 90
            
            print(f"🌍 DEBUG: Request analysis:")
            print(f"🌍 DEBUG: - Days requested: {days_requested}")
            print(f"🌍 DEBUG: - Is historical: {is_historical}")
            print(f"🌍 DEBUG: - Is large request: {is_large_request}")
            
            # Smart routing logic
            if is_historical or is_large_request:
                # Meteostat jobb historikus adatokhoz
                usage_summary = self.usage_tracker.get_usage_summary()
                if usage_summary.get('warning_level') != 'critical':
                    print("🌍 DEBUG: Selected Meteostat for historical/large request")
                    return 'meteostat'
                else:
                    print("🌍 DEBUG: Meteostat rate limited, fallback to Open-Meteo")
                    self.provider_fallback.emit('meteostat', 'open-meteo')
                    return 'open-meteo'
            else:
                # Aktuális/közelmúlt adatokhoz Open-Meteo
                print("🌍 DEBUG: Selected Open-Meteo for recent data")
                return 'open-meteo'
                
        except Exception as e:
            print(f"❌ DEBUG: Provider selection error: {e}")
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
                print(f"🌍 DEBUG: Tracked usage for {provider_name}")
                
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
                        print(f"🚨 DEBUG: Provider {provider_name} usage critical: {usage_percent:.1f}%")
                        self.provider_warning.emit(provider_name, int(usage_percent))
                    elif warning_level == 'warning':
                        print(f"⚠️ DEBUG: Provider {provider_name} usage warning: {usage_percent:.1f}%")
                        self.provider_warning.emit(provider_name, int(usage_percent))
            else:
                print(f"⚠️ DEBUG: Failed to track usage for {provider_name}")
                
        except Exception as e:
            print(f"❌ DEBUG: Usage tracking error: {e}")
    
    @Slot(str)
    def handle_provider_change(self, provider_name: str) -> None:
        """
        Provider változás kezelése GUI-ból.
        
        Args:
            provider_name: Új provider neve
        """
        try:
            print(f"🌍 DEBUG: Provider change request: {provider_name}")
            
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
                status_msg = f"🌍 Provider beállítva: {provider_display}"
            
            self.status_updated.emit(status_msg)
            
            print(f"✅ DEBUG: Provider changed to: {provider_name}")
            
        except Exception as e:
            print(f"❌ DEBUG: Provider change error: {e}")
            self.error_occurred.emit(f"Provider váltási hiba: {e}")
    
    # === TELEPÜLÉS KERESÉS LOGIKA ===
    
    @Slot(str)
    def handle_search_request(self, search_query: str) -> None:
        """
        Település keresési kérés kezelése a ControlPanel-től.
        
        Args:
            search_query: Keresési kifejezés
        """
        print(f"🔍 DEBUG: handle_search_request called with: '{search_query}'")
        
        # Alapszintű validáció
        if not search_query or len(search_query.strip()) < 2:
            error_msg = "Legalább 2 karakter szükséges a kereséshez"
            print(f"❌ DEBUG: Validation error: {error_msg}")
            self.error_occurred.emit(error_msg)
            return
        
        # Jelenlegi keresés tárolása
        self.active_search_query = search_query.strip()
        print(f"🔍 DEBUG: Active search query set: '{self.active_search_query}'")
        
        # Státusz frissítése
        search_info = f"Keresés: {self.active_search_query}"
        self.status_updated.emit(search_info + "...")
        print(f"📝 DEBUG: Status updated: {search_info}")
        
        # Geocoding worker indítása
        try:
            print("🚀 DEBUG: Creating GeocodingWorker...")
            worker = GeocodingWorker(self.active_search_query)
            print(f"✅ DEBUG: GeocodingWorker created for query: '{self.active_search_query}'")
            
            # WorkerManager központi használata
            print("🚀 DEBUG: Starting worker via WorkerManager...")
            worker_id = self.worker_manager.start_geocoding(worker)
            print(f"✅ DEBUG: GeocodingWorker started via WorkerManager with ID: {worker_id}")
            
        except Exception as e:
            error_msg = f"Geocoding worker indítási hiba: {e}"
            print(f"❌ DEBUG: {error_msg}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(error_msg)
            return
        
        print(f"✅ DEBUG: handle_search_request completed successfully for '{search_query}'")
    
    @Slot(list)
    def _on_geocoding_completed(self, results: List[Dict[str, Any]]) -> None:
        """
        Geocoding befejezésének kezelése.
        
        Args:
            results: Település találatok listája
        """
        print(f"📍 DEBUG: _on_geocoding_completed called with {len(results)} results")
        
        try:
            if not results:
                msg = "Nem található település ezzel a névvel"
                print(f"📍 DEBUG: No results found")
                self.status_updated.emit(msg)
                self.geocoding_results_ready.emit([])
                return
            
            print(f"📍 DEBUG: Processing {len(results)} geocoding results...")
            
            # Eredmények feldolgozása és gazdagítása
            processed_results = self._process_geocoding_results(results)
            print(f"📍 DEBUG: Processed {len(processed_results)} results")
            
            # Státusz frissítése
            status_msg = f"{len(processed_results)} település találat"
            self.status_updated.emit(status_msg)
            print(f"📝 DEBUG: Status updated: {status_msg}")
            
            # Eredmények továbbítása a GUI-nak
            print(f"📡 DEBUG: Emitting geocoding_results_ready signal...")
            self.geocoding_results_ready.emit(processed_results)
            
            print(f"✅ DEBUG: Geocoding befejezve: {len(processed_results)} találat")
            
        except Exception as e:
            print(f"❌ DEBUG: Geocoding feldolgozási hiba: {e}")
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
        
        print(f"📍 DEBUG: Processing {len(raw_results)} raw results")
        
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
                    
                    # Megjegzítések a GUI számára
                    'display_name': self._create_display_name(result),
                    'search_rank': result.get('rank', 999),
                    'original_query': self.active_search_query,
                }
                
                processed.append(processed_result)
                
                # Debug információ minden 5. eredményhez
                if i < 5 or i % 5 == 0:
                    name = processed_result['name']
                    country = processed_result['country']
                    print(f"📍 DEBUG: Result {i}: {name}, {country}")
                
            except Exception as e:
                print(f"⚠️ DEBUG: Eredmény {i} feldolgozási hiba: {e}")
                continue
        
        # Rendezés relevancia szerint
        processed.sort(key=lambda x: x['search_rank'])
        print(f"📍 DEBUG: Results sorted by relevance")
        
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
    
    # === TELEPÜLÉS KIVÁLASZTÁS LOGIKA ===
    
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
        print(f"📍 DEBUG: handle_city_selection called: {city_name} ({latitude:.4f}, {longitude:.4f})")
        
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
            print(f"📝 DEBUG: City selection status: {status_msg}")
            
            # Adatbázisba mentés (aszinkron)
            self._save_city_to_database(self.current_city_data)
            
            print(f"✅ DEBUG: Település kiválasztva: {city_name} ({latitude:.4f}, {longitude:.4f})")
            
        except Exception as e:
            print(f"❌ DEBUG: Település kiválasztási hiba: {e}")
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
            
            print(f"✅ DEBUG: Település mentve adatbázisba: {city_data['name']}")
            
        except Exception as e:
            print(f"❌ DEBUG: Adatbázis mentési hiba: {e}")
            # Nem kritikus hiba, nem szakítjuk meg a folyamatot
    
    # === IDŐJÁRÁSI ADATOK LEKÉRDEZÉS LOGIKA (PROVIDER ROUTING + WIND GUSTS) ===
    
    @Slot(float, float, str, str, dict)
    def handle_weather_data_request(self, latitude: float, longitude: float, 
                                   start_date: str, end_date: str, params: Dict[str, Any]) -> None:
        """
        🌍🌪️ KRITIKUS JAVÍTÁS: Időjárási adatok lekérdezés PROVIDER ROUTING + WIND GUSTS támogatással.
        
        Args:
            latitude: Földrajzi szélesség
            longitude: Földrajzi hosszúság
            start_date: Kezdő dátum (YYYY-MM-DD)
            end_date: Befejező dátum (YYYY-MM-DD)
            params: API paraméterek
        """
        print(f"🌍🌪️ DEBUG: Weather data request (PROVIDER ROUTING + WIND GUSTS): {latitude:.4f}, {longitude:.4f}")
        
        try:
            if not self.current_city_data:
                error_msg = "Nincs kiválasztva település"
                print(f"❌ DEBUG: {error_msg}")
                self.error_occurred.emit(error_msg)
                return
            
            # Állapot tisztítás
            self.current_weather_data = None
            
            # Kérés validálása
            if not self._validate_weather_request(latitude, longitude, start_date, end_date):
                return
            
            # 🌍 PROVIDER ROUTING: Smart provider selection
            selected_provider = self._select_provider_for_request(latitude, longitude, start_date, end_date)
            print(f"🌍 DEBUG: Selected provider: {selected_provider}")
            
            # Provider selection signal küldése
            self.provider_selected.emit(selected_provider)
            
            # Usage tracking
            self._track_provider_usage(selected_provider)
            
            city_name = self.current_city_data.get('name', 'Ismeretlen')
            
            print(f"🌍🌪️ DEBUG: {selected_provider.upper()} WIND GUSTS kérés - {city_name}, {start_date} - {end_date}")
            
            # Provider-specifikus kérés indítása
            provider_display = self.provider_config.PROVIDERS.get(selected_provider, {}).get('name', selected_provider)
            self.status_updated.emit(f"🌍🌪️ Időjárási adatok lekérdezése ({provider_display}): {city_name}")
            
            self._start_weather_request_with_provider(
                latitude, longitude, start_date, end_date, selected_provider
            )
            
        except Exception as e:
            print(f"❌ DEBUG: Weather data kérési hiba: {e}")
            self.error_occurred.emit(f"Lekérdezési hiba: {e}")
    
    def _start_weather_request_with_provider(self, latitude: float, longitude: float, 
                                           start_date: str, end_date: str, provider: str) -> None:
        """
        🌍🌪️ KRITIKUS JAVÍTÁS: Időjárási adatok lekérdezése megadott providerrel WIND GUSTS támogatással.
        
        Args:
            latitude: Földrajzi szélesség
            longitude: Földrajzi hosszúság
            start_date: Kezdő dátum
            end_date: Befejező dátum
            provider: Provider neve
        """
        try:
            print(f"🌍🌪️ DEBUG: Starting weather request with provider: {provider}")
            
            # Weather data worker létrehozása provider specifikus konfigurációval
            worker = WeatherDataWorker(
                latitude=latitude,
                longitude=longitude, 
                start_date=start_date,
                end_date=end_date,
                preferred_provider=provider  # 🌍 Provider routing parameter (javított!)
            )
            
            # WorkerManager központi használata
            print(f"🚀 DEBUG: Starting {provider.upper()} WIND GUSTS worker via WorkerManager...")
            worker_id = self.worker_manager.start_weather_data_fetch(worker)
            print(f"✅ DEBUG: {provider.upper()} WIND GUSTS worker started via WorkerManager with ID: {worker_id}")
            
        except Exception as e:
            print(f"❌ DEBUG: {provider} WIND GUSTS worker indítási hiba: {e}")
            
            # Fallback strategy - ha a kiválasztott provider sikertelen
            if provider != 'open-meteo':
                print(f"🌍 DEBUG: Fallback to Open-Meteo due to {provider} failure")
                self.provider_fallback.emit(provider, 'open-meteo')
                
                try:
                    # Retry with Open-Meteo
                    fallback_worker = WeatherDataWorker(
                        latitude=latitude,
                        longitude=longitude,
                        start_date=start_date,
                        end_date=end_date,
                        preferred_provider='open-meteo'  # 🌍 Javított paraméter név!
                    )
                    
                    worker_id = self.worker_manager.start_weather_data_fetch(fallback_worker)
                    print(f"✅ DEBUG: Open-Meteo fallback worker started with ID: {worker_id}")
                    
                except Exception as fallback_error:
                    print(f"❌ DEBUG: Fallback worker indítási hiba: {fallback_error}")
                    self.error_occurred.emit(f"Időjárási adatok lekérdezése sikertelen: {e}")
            else:
                self.error_occurred.emit(f"Időjárási adatok lekérdezése sikertelen: {e}")
    
    def _validate_weather_request(self, latitude: float, longitude: float, 
                                 start_date: str, end_date: str) -> bool:
        """
        Weather data kérés validálása.
        
        Args:
            latitude: Földrajzi szélesség
            longitude: Földrajzi hosszúság  
            start_date: Kezdő dátum
            end_date: Befejező dátum
            
        Returns:
            Érvényes-e a kérés
        """
        # Koordináták validálása
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            self.error_occurred.emit("Érvénytelen koordináták")
            return False
        
        # Dátumok validálása
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start > end:
                self.error_occurred.emit("A kezdő dátum nem lehet nagyobb a befejező dátumnál")
                return False
            
            # Maximum 60 éves tartomány
            if (end - start).days > 60 * 365:
                self.error_occurred.emit("Maximum 60 éves időszak kérdezhető le")
                return False
            
        except ValueError:
            self.error_occurred.emit("Érvénytelen dátum formátum")
            return False
        
        return True
    
    @Slot(dict)
    def _on_weather_data_completed(self, data: Dict[str, Any]) -> None:
        """
        🌍🌪️ KRITIKUS JAVÍTÁS: Időjárási adatok lekérdezésének befejezése PROVIDER ROUTING + WIND GUSTS támogatással.
        
        Args:
            data: API válasz adatok
        """
        print(f"🌍🌪️ DEBUG: _on_weather_data_completed called (PROVIDER ROUTING + WIND GUSTS support)")
        
        try:
            # Provider információ kinyerése az adatokból
            used_provider = data.get('provider', 'unknown')
            print(f"🌍 DEBUG: Weather data received from provider: {used_provider}")
            
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
            
            # 🌪️ KRITIKUS JAVÍTÁS: Széllökés statisztika a státuszban
            wind_gusts_info = ""
            if 'wind_gusts_max' in processed_data.get('daily', {}):
                wind_gusts_max = processed_data['daily']['wind_gusts_max']
                if wind_gusts_max:
                    max_gust = max([g for g in wind_gusts_max if g is not None])
                    wind_gusts_info = f", max széllökés: {max_gust:.1f} km/h"
            
            # 🌍 Provider info a státuszban
            provider_display = self.provider_config.PROVIDERS.get(used_provider, {}).get('name', used_provider)
            
            self.status_updated.emit(
                f"🌍🌪️ Adatok sikeresen lekérdezve ({provider_display}): {city_name} ({record_count} nap{wind_gusts_info})"
            )
            
            # Eredmények továbbítása a GUI komponenseknek
            print(f"📡 DEBUG: Emitting weather_data_ready signal...")
            self.weather_data_ready.emit(processed_data)
            
            print(f"✅ DEBUG: Weather data befejezve: {record_count} napi rekord (PROVIDER ROUTING + WIND GUSTS support)")
            
        except Exception as e:
            print(f"❌ DEBUG: Weather data feldolgozási hiba: {e}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"Adatok feldolgozási hiba: {e}")
    
    def _process_weather_data(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        🌪️ KRITIKUS JAVÍTÁS: Időjárási adatok feldolgozása WIND GUSTS támogatással.
        
        Args:
            raw_data: Nyers API adatok
            
        Returns:
            Feldolgozott adatok vagy None
        """
        try:
            print(f"🌪️ DEBUG: Processing weather data (WIND GUSTS support)...")
            
            if not raw_data or 'daily' not in raw_data:
                print(f"⚠️ DEBUG: Invalid weather data structure")
                return None
            
            daily_data = raw_data['daily']
            hourly_data = raw_data.get('hourly', {})
            
            # Alapvető mezők ellenőrzése
            required_fields = ['time', 'temperature_2m_max', 'temperature_2m_min', 'precipitation_sum']
            for field in required_fields:
                if field not in daily_data or not daily_data[field]:
                    print(f"⚠️ DEBUG: Hiányzó mező: {field}")
                    return None
            
            record_count = len(daily_data['time'])
            print(f"🌪️ DEBUG: Weather data valid - {record_count} records")
            
            # 🌪️ KRITIKUS JAVÍTÁS: Óránkénti széllökések → napi maximum számítás
            daily_wind_gusts_max = self._calculate_daily_max_wind_gusts(
                hourly_data.get('wind_gusts_10m', []),
                hourly_data.get('time', []),
                daily_data.get('time', [])
            )
            
            # Feldolgozott adatok összeállítása
            processed = {
                'daily': daily_data.copy(),
                'hourly': hourly_data,  # Óránkénti adatok megtartása
                'latitude': raw_data.get('latitude'),
                'longitude': raw_data.get('longitude'),
                'timezone': raw_data.get('timezone', 'UTC'),
                'elevation': raw_data.get('elevation'),
                
                # Metaadatok
                'data_source': raw_data.get('provider', 'unknown'),
                'source_type': raw_data.get('provider', 'unknown'),
                'provider': raw_data.get('provider', 'unknown'),  # 🌍 Provider info biztosítása
                'processed_at': datetime.now().isoformat(),
                'city_data': self.current_city_data.copy() if self.current_city_data else None,
                'record_count': record_count
            }
            
            # 🌪️ KRITIKUS JAVÍTÁS: Napi maximum széllökések hozzáadása
            if daily_wind_gusts_max:
                processed['daily']['wind_gusts_max'] = daily_wind_gusts_max
                print(f"🌪️ DEBUG: Added {len(daily_wind_gusts_max)} daily wind gusts max values")
                
                # Statisztika
                valid_gusts = [g for g in daily_wind_gusts_max if g is not None and g > 0]
                if valid_gusts:
                    max_gust = max(valid_gusts)
                    print(f"🌪️ DEBUG: Maximum napi széllökés: {max_gust:.1f} km/h")
                    
                    # Kritikus ellenőrzés - életveszélyes alulbecslés detektálása
                    if max_gust > 100:
                        print(f"⚠️  DEBUG: KRITIKUS: Extrém széllökés detektálva: {max_gust:.1f} km/h")
                    elif max_gust > 80:
                        print(f"⚠️  DEBUG: Viharos széllökés detektálva: {max_gust:.1f} km/h")
                    elif max_gust > 60:
                        print(f"✅ DEBUG: Erős széllökés detektálva: {max_gust:.1f} km/h")
                    else:
                        print(f"✅ DEBUG: Mérsékelt széllökés: {max_gust:.1f} km/h")
            else:
                print(f"⚠️ DEBUG: Nincs széllökés adat az óránkénti adatokban")
            
            print(f"✅ DEBUG: Weather data processed successfully with WIND GUSTS - {record_count} records")
            
            return processed
            
        except Exception as e:
            print(f"❌ DEBUG: Weather data feldolgozási hiba: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _calculate_daily_max_wind_gusts(self, hourly_gusts: List[float], 
                                       hourly_times: List[str], 
                                       daily_times: List[str]) -> List[float]:
        """
        🌪️ KRITIKUS JAVÍTÁS: Óránkénti széllökések → napi maximum konverzió.
        
        Args:
            hourly_gusts: Óránkénti széllökések (km/h)
            hourly_times: Óránkénti időpontok (ISO format)
            daily_times: Napi időpontok (YYYY-MM-DD format)
            
        Returns:
            Napi maximum széllökések listája
        """
        try:
            print(f"🌪️ DEBUG: Calculating daily max wind gusts...")
            print(f"🌪️ DEBUG: Hourly gusts count: {len(hourly_gusts)}")
            print(f"🌪️ DEBUG: Hourly times count: {len(hourly_times)}")
            print(f"🌪️ DEBUG: Daily times count: {len(daily_times)}")
            
            if not hourly_gusts or not hourly_times or not daily_times:
                print(f"⚠️ DEBUG: Missing data for wind gusts calculation")
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
                                print(f"🌪️ DEBUG: Day {daily_time}: max gust {daily_max:.1f} km/h")
                        else:
                            # Nincs érvényes széllökés adat erre a napra
                            daily_max_gusts.append(None)
                    else:
                        # Nincs óránkénti adat erre a napra
                        daily_max_gusts.append(None)
                        
                except Exception as e:
                    print(f"⚠️ DEBUG: Error processing day {daily_time}: {e}")
                    daily_max_gusts.append(None)
            
            # Eredmény validálás
            valid_gusts = [g for g in daily_max_gusts if g is not None and g > 0]
            
            if valid_gusts:
                max_overall = max(valid_gusts)
                avg_gusts = sum(valid_gusts) / len(valid_gusts)
                
                print(f"🌪️ DEBUG: Daily wind gusts calculation complete:")
                print(f"🌪️ DEBUG: - Valid days: {len(valid_gusts)}/{len(daily_max_gusts)}")
                print(f"🌪️ DEBUG: - Maximum overall: {max_overall:.1f} km/h")
                print(f"🌪️ DEBUG: - Average gusts: {avg_gusts:.1f} km/h")
                
                # Kritikus ellenőrzés - életveszélyes alulbecslés detektálása
                if max_overall > 120:
                    print(f"🚨 DEBUG: KRITIKUS: Hurrikán erősségű széllökés: {max_overall:.1f} km/h")
                elif max_overall > 100:
                    print(f"⚠️  DEBUG: KRITIKUS: Extrém széllökés: {max_overall:.1f} km/h")
                elif max_overall > 80:
                    print(f"⚠️  DEBUG: Viharos széllökés: {max_overall:.1f} km/h")
                else:
                    print(f"✅ DEBUG: Mérsékelt széllökés: {max_overall:.1f} km/h")
                    
            else:
                print(f"⚠️ DEBUG: Nincs érvényes széllökés adat")
            
            return daily_max_gusts
            
        except Exception as e:
            print(f"❌ DEBUG: Daily wind gusts calculation error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _save_weather_to_database(self, weather_data: Dict[str, Any]) -> None:
        """
        🌍🌪️ KRITIKUS JAVÍTÁS: Időjárási adatok mentése adatbázisba PROVIDER ROUTING + WIND GUSTS támogatással.
        
        Args:
            weather_data: Feldolgozott időjárási adatok
        """
        try:
            if not self.current_city_data:
                print("⚠️ DEBUG: Nincs város adat az időjárási adatok mentéséhez")
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
                print("⚠️ DEBUG: Város nem található az adatbázisban")
                conn.close()
                return
            
            city_id = city_result[0]
            daily_data = weather_data['daily']
            
            # 🌍 Provider információ
            data_provider = weather_data.get('provider', 'unknown')
            
            # Időjárási adatok mentése
            saved_count = 0
            for i, date in enumerate(daily_data['time']):
                try:
                    # 🌪️ KRITIKUS JAVÍTÁS: wind_gusts_max oszlop hozzáadása
                    wind_gusts_max = None
                    if 'wind_gusts_max' in daily_data and i < len(daily_data['wind_gusts_max']):
                        wind_gusts_max = daily_data['wind_gusts_max'][i]
                    
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
                        daily_data.get('windspeed_10m_max', [None] * len(daily_data['time']))[i] if 'windspeed_10m_max' in daily_data else None,
                        wind_gusts_max,  # 🌪️ KRITIKUS JAVÍTÁS: Új wind_gusts_max oszlop
                        data_provider   # 🌍 Provider tracking
                    ))
                    saved_count += 1
                    
                    # Debug logolás széllökésekhez
                    if wind_gusts_max is not None and wind_gusts_max > 80:
                        print(f"🌪️ DEBUG: Saved extreme wind gust ({data_provider}): {date} - {wind_gusts_max:.1f} km/h")
                        
                except Exception as e:
                    print(f"⚠️ DEBUG: Rekord mentési hiba: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            # Sikeres mentés jelzése
            self.weather_saved_to_db.emit(True)
            
            print(f"✅ DEBUG: Weather data mentve adatbázisba ({data_provider}): {saved_count} rekord")
            
        except Exception as e:
            print(f"❌ DEBUG: Weather data adatbázis hiba: {e}")
            self.weather_saved_to_db.emit(False)
    
    # === HIBA KEZELÉS ===
    
    @Slot(str)
    def _on_worker_error(self, error_message: str) -> None:
        """
        Worker hibák kezelése.
        
        Args:
            error_message: Hibaüzenet
        """
        print(f"❌ DEBUG: Worker error: {error_message}")
        
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
        🌍 Provider információk lekérdezése GUI számára.
        
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
            print(f"❌ DEBUG: Provider info hiba: {e}")
            return {}
    
    def cancel_all_operations(self) -> None:
        """
        Összes aktív művelet megszakítása.
        """
        try:
            print("🛑 DEBUG: Cancelling all operations...")
            
            # WorkerManager központi cancel
            self.worker_manager.cancel_all()
            
            self.status_updated.emit("Műveletek megszakítva")
            print("✅ DEBUG: Összes művelet megszakítva via WorkerManager")
            
        except Exception as e:
            print(f"❌ DEBUG: Műveletek megszakítási hiba: {e}")
    
    def shutdown(self) -> None:
        """Controller leállítása és cleanup."""
        try:
            print("🛑 DEBUG: AppController leállítása...")
            
            # Összes művelet megszakítása
            self.cancel_all_operations()
            
            # WorkerManager központi leállítás
            self.worker_manager.shutdown()
            
            # User preferences mentése
            self.user_preferences.save()
            self.usage_tracker.save()
            
            # Állapot tisztítása
            self.current_city_data = None
            self.current_weather_data = None
            self.active_search_query = None
            
            print("✅ DEBUG: AppController leállítva (PROVIDER ROUTING support)")
            
        except Exception as e:
            print(f"⚠️ DEBUG: Controller leállítási hiba: {e}")
            import traceback
            traceback.print_exc()