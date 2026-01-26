"""
AnalysisWorker - Háttérszálon Futó Elemzési Worker

FELELŐSSÉG: 
- MultiCityEngine és WeatherClient futtatása háttérszálon
- UI thread felszabadítása (nem fagy le a felület)
- Interrupt támogatás (megszakítható műveletek)
- Progress reporting (állapot jelzések)
- Error handling (hibakezelés)
- 🎯 KRITIKUS JAVÍTÁS: ADATKONVERZIÓŚ FIX - List[Dict] → Dict[List]
- 🌹 VÉGSŐ FIX: SZÉLIRÁNY KOMPATIBILITÁS - WindChart/WindRose támogatás!

CLEAN ARCHITECTURE:
- Nem ismeri a UI-t
- Csak az elemzési logikát futtatja
- Signal-ekkel kommunikál kifelé

🔧 KRITIKUS JAVÍTÁS v4.6.3: SZÉLIRÁNY KOMPATIBILITÁSI FIX!
❌ PROBLÉMA: WindChart "wind_gusts_max" és "winddirection" kulcsokat keres
✅ JAVÍTÁS: AnalysisWorker többszörös kulcs mapping - API nevek + Chart kompatibilitás!
✅ Working directory független működés
✅ WeatherClient.get_weather_data() KOORDINÁTA PARAMÉTER FIX!
❌ HIBÁS: get_weather_data(lat=..., lon=...)
✅ JAVÍTOTT: get_weather_data(latitude=..., longitude=...)
"""

import traceback
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker
from PySide6.QtWidgets import QApplication

# Analytics imports
try:
    from ...analytics.multi_city_engine import MultiCityEngine
    from ...data.weather_client import WeatherClient
    from ...data.enums import AnalysisType, DataProvider
    IMPORTS_OK = True
    print("✅ AnalysisWorker imports successful")
except ImportError as e:
    print(f"❌ AnalysisWorker import error: {e}")
    IMPORTS_OK = False
    # Fallback imports
    try:
        import sys
        from pathlib import Path
        
        # Add project root to Python path
        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        from src.analytics.multi_city_engine import MultiCityEngine
        from src.data.weather_client import WeatherClient
        from src.data.enums import AnalysisType, DataProvider
        IMPORTS_OK = True
        print("✅ AnalysisWorker fallback imports successful")
    except ImportError as e2:
        print(f"❌ AnalysisWorker fallback import error: {e2}")
        IMPORTS_OK = False
        MultiCityEngine = None
        WeatherClient = None
        AnalysisType = None
        DataProvider = None


class AnalysisWorker(QThread):
    """
    HÁTTÉRSZÁL WORKER - UI Thread Felszabadítása
    
    JELZÉSEK:
    - progress_updated(str, int): Progress szöveg + százalék
    - analysis_completed(dict): Sikeres elemzés eredménye
    - analysis_failed(str): Hiba üzenet
    - analysis_cancelled(): Megszakítás megerősítése
    
    INTERRUPT TÁMOGATÁS:
    - QThread.requestInterruption() használata
    - Periodikus isInterruptionRequested() ellenőrzés
    - Graceful shutdown minden lépésnél
    """
    
    # === WORKER SIGNALS ===
    progress_updated = Signal(str, int)    # (szöveg, százalék)
    analysis_completed = Signal(dict)      # Eredmény dictionary
    analysis_failed = Signal(str)          # Hiba üzenet
    analysis_cancelled = Signal()          # Megszakítás megerősítése
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # === WORKER STATE ===
        self._request_data: Optional[Dict[str, Any]] = None
        self._mutex = QMutex()  # Thread-safe hozzáférés
        
        # === ANALYTICS COMPONENTS ===
        self._multi_city_engine: Optional[MultiCityEngine] = None
        self._weather_client: Optional[WeatherClient] = None
        
        # === LOGGING ===
        self._logger = logging.getLogger(__name__)
        
    def setup_analysis_request(self, request_data: Dict[str, Any]):
        """
        ELEMZÉSI KÉRÉS BEÁLLÍTÁSA
        
        Args:
            request_data (dict): Teljes kérés paraméterek
                - analysis_type: 'single_location', 'multi_city', 'county_analysis'
                - location_data: lokáció információk
                - date_range: kezdő/végdátum
                - provider: adatforrás
                - api_settings: API beállítások
        """
        with QMutexLocker(self._mutex):
            self._request_data = request_data.copy()
            self._logger.info(f"Worker setup: {request_data.get('analysis_type', 'unknown')}")
    
    def run(self):
        """
        FŐSZÁL FUTÁS - Itt történik a tényleges munka
        
        KRITIKUS: Periodikus interrupt ellenőrzés minden lépésnél!
        """
        try:
            self._logger.info("AnalysisWorker futás elkezdve")
            
            # === 1. PARAMÉTER VALIDÁCIÓ ===
            if not self._validate_request():
                return
                
            # === 2. KOMPONENSEK INICIALIZÁLÁSA ===
            if not self._initialize_components():
                return
                
            # === 3. ELEMZÉS TÍPUS ALAPJÁN DISPATCH ===
            analysis_type = self._request_data.get('analysis_type', '')
            
            if analysis_type == 'multi_city':
                self._run_multi_city_analysis()
            elif analysis_type == 'single_location':
                self._run_single_location_analysis()
            elif analysis_type == 'county_analysis':
                self._run_county_analysis()
            else:
                self._emit_error(f"Ismeretlen elemzés típus: {analysis_type}")
                
        except Exception as e:
            self._logger.error(f"Worker kritikus hiba: {str(e)}")
            self._logger.error(traceback.format_exc())
            self._emit_error(f"Váratlan hiba: {str(e)}")
    
    def _validate_request(self) -> bool:
        """Kérés paraméterek validálása"""
        if self._check_interruption("Validáció"):
            return False
            
        with QMutexLocker(self._mutex):
            if not self._request_data:
                self._emit_error("Hiányzó kérés adatok")
                return False
                
            required_fields = ['analysis_type', 'date_range']
            for field in required_fields:
                if field not in self._request_data:
                    self._emit_error(f"Hiányzó kötelező mező: {field}")
                    return False
                    
        self._emit_progress("Paraméterek validálva", 10)
        return True
    
    def _initialize_components(self):
        """
        🔧 KRITIKUS JAVÍTÁS v4.6.1: Analytics komponensek inicializálása ABSOLUTE PATH FIX-szel!
        
        ✅ JAVÍTOTT: WeatherClient helyes paraméter név!
        ✅ JAVÍTOTT: MultiCityEngine abszolút path-okkal
        ✅ JAVÍTOTT: Import ellenőrzés
        """
        if self._check_interruption("Inicializálás"):
            return False
        
        # Import ellenőrzés
        if not IMPORTS_OK:
            self._emit_error("Analytics komponensek importálása sikertelen")
            return False
            
        try:
            self._emit_progress("Komponensek inicializálása...", 20)
            
            # 🔧 KRITIKUS JAVÍTÁS v4.6.1: ABSOLUTE PATH CALCULATION
            # Script location: src/gui/workers/analysis_worker.py
            # Project root: src/gui/workers → src/gui → src → project_root
            project_root = Path(__file__).parent.parent.parent.parent
            
            self._logger.info(f"🔧 ABSOLUTE PATH FIX v4.6.1:")
            self._logger.info(f"   Script location: {Path(__file__).absolute()}")
            self._logger.info(f"   Calculated project root: {project_root.absolute()}")
            self._logger.info(f"   Current working dir: {Path.cwd().absolute()}")
            
            # Database paths
            global_db_path = project_root / "data" / "cities.db"
            hungarian_db_path = project_root / "data" / "hungarian_settlements.db"
            
            self._logger.info(f"🔧 Target database paths:")
            self._logger.info(f"   Global DB: {global_db_path.absolute()}")
            self._logger.info(f"   Hungarian DB: {hungarian_db_path.absolute()}")
            self._logger.info(f"   Global DB exists: {global_db_path.exists()}")
            self._logger.info(f"   Hungarian DB exists: {hungarian_db_path.exists()}")
            
            # Weather Client setup - 🔧 KRITIKUS FIX: HELYES PARAMÉTER NÉV!
            provider = self._request_data.get('provider', 'open_meteo')  # String fallback
            api_settings = self._request_data.get('api_settings', {})
            
            # ✅ JAVÍTOTT: WeatherClient safe inicializálás
            self._logger.info(f"🔧 WeatherClient inicializálás: provider='{provider}'")
            
            if WeatherClient is None:
                self._emit_error("WeatherClient osztály nem elérhető")
                return False
            
            # Try different initialization methods
            try:
                # Method 1: No parameters (default)
                self._weather_client = WeatherClient()
                self._logger.info("✅ WeatherClient default inicializálás sikeres")
            except Exception as e1:
                try:
                    # Method 2: With preferred_provider
                    self._weather_client = WeatherClient(preferred_provider=provider)
                    self._logger.info("✅ WeatherClient preferred_provider inicializálás sikeres")
                except Exception as e2:
                    self._logger.error(f"❌ WeatherClient inicializálás minden módszer sikertelen: {e1}, {e2}")
                    self._emit_error(f"WeatherClient inicializálás sikertelen: {e1}")
                    return False
            
            # API settings külön beállítása (ha szükséges)
            if api_settings:
                self._logger.info(f"🔧 API settings: {api_settings}")
            
            # MultiCity Engine setup (ha szükséges) - 🔧 ABSOLUTE PATH FIX!
            analysis_type = self._request_data.get('analysis_type')
            if analysis_type in ['multi_city', 'county_analysis']:
                self._logger.info("🏙️ MultiCityEngine inicializálása ABSOLUTE PATH-okkal...")
                
                if MultiCityEngine is None:
                    self._emit_error("MultiCityEngine osztály nem elérhető")
                    return False
                
                # ✅ JAVÍTOTT: Explicit absolute path-ok átadása
                self._multi_city_engine = MultiCityEngine(
                    db_path=str(global_db_path.absolute()),
                    hungarian_db_path=str(hungarian_db_path.absolute())
                )
                
                self._logger.info("✅ MultiCityEngine absolute path-okkal inicializálva")
                
            self._emit_progress("Komponensek inicializálva", 30)
            self._logger.info("✅ AnalysisWorker komponensek sikeresen inicializálva (ABSOLUTE PATH FIX v4.6.1)")
            return True
            
        except Exception as e:
            self._logger.error(f"❌ Inicializálási hiba: {str(e)}")
            self._logger.error(traceback.format_exc())
            self._emit_error(f"Inicializálási hiba: {str(e)}")
            return False
    
    def _run_multi_city_analysis(self):
        """MULTI-CITY ELEMZÉS FUTTATÁSA"""
        if self._check_interruption("Multi-city elemzés"):
            return
            
        try:
            self._emit_progress("Multi-city elemzés indítása...", 40)
            
            # Régió vagy megye adatok kinyerése
            region_name = self._request_data.get('region_name')
            county_name = self._request_data.get('county_name')
            
            # Dátum range
            date_range = self._request_data.get('date_range', {})
            start_date = date_range.get('start_date')
            end_date = date_range.get('end_date')
            
            # === INTERRUPT CHECK BEFORE HEAVY WORK ===
            if self._check_interruption("Multi-city engine indítás előtt"):
                return
            
            self._emit_progress("Városok elemzése folyamatban...", 60)
            
            # A tényleges elemzés - ez a hosszú művelet!
            # ✅ JAVÍTOTT: MultiCityEngine.analyze_multi_city helyes paraméterezéssel
            region_or_county = region_name or county_name
            if not region_or_county:
                self._emit_error("Hiányzó régió vagy megye név")
                return
            
            # ✅ HELYES: analyze_multi_city paraméterek a MultiCityEngine API szerint
            result = self._multi_city_engine.analyze_multi_city(
                query_type="hottest_today",  # Query type a QUERY_TYPES-ból
                region=region_or_county,     # Régió név
                date=start_date,             # Egyetlen dátum string formátumban
                limit=None                   # Nincs limit, vagy később paraméterezhetjük
            )
                
            # === FINAL INTERRUPT CHECK ===
            if self._check_interruption("Eredmény feldolgozás előtt"):
                return
                
            self._emit_progress("Eredmények feldolgozása...", 90)
            
            # Eredmény strukturálása
            structured_result = {
                'analysis_type': 'multi_city',
                'request_params': self._request_data,
                'result_data': result,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
            self._emit_progress("Multi-city elemzés befejezve", 100)
            self.analysis_completed.emit(structured_result)
            
        except Exception as e:
            self._logger.error(f"Multi-city elemzés hiba: {str(e)}")
            self._emit_error(f"Multi-city elemzés sikertelen: {str(e)}")
    
    def _run_single_location_analysis(self):
        """
        🎯 KRITIKUS JAVÍTÁS: EGYEDI LOKÁCIÓ ELEMZÉSE - ADATKONVERZIÓŚ FIX!
        
        Ez a metódus most már:
        1. Meghívja a WeatherClient-et (List[Dict] formátum)
        2. KONVERTÁLJA Dict[List] formátumra
        3. Továbbítja az app_controller-nek
        """
        if self._check_interruption("Single location elemzés"):
            return
            
        try:
            self._emit_progress("Egyedi lokáció elemzése...", 50)
            
            # 🔧 KOORDINÁTA KINYERÉS: AppController többféle formátumot küldhet
            # 1. location_data objektumban: 'lat'/'lon' VAGY 'latitude'/'longitude'
            # 2. Direkt paraméterként: 'latitude'/'longitude'
            
            location_data = self._request_data.get('location_data', {})
            date_range = self._request_data.get('date_range', {})
            
            # 🔧 KRITIKUS FIX: Koordináták rugalmas kinyerése mindkét formátumból
            latitude = None
            longitude = None
            
            # 1. location_data objektumból - mindkét kulcs formátum támogatása
            if location_data:
                latitude = location_data.get('latitude') or location_data.get('lat')
                longitude = location_data.get('longitude') or location_data.get('lon')
                self._logger.info(f"🔧 Koordináták location_data-ból: lat={latitude}, lon={longitude}")
            
            # 2. Direkt paraméterekből (fallback)
            if latitude is None or longitude is None:
                latitude = self._request_data.get('latitude')
                longitude = self._request_data.get('longitude')
                self._logger.info(f"🔧 Koordináták direkt paraméterekből: lat={latitude}, lon={longitude}")
            
            # 3. Validálás
            if latitude is None or longitude is None:
                error_msg = f"Hiányzó koordináták: latitude={latitude}, longitude={longitude}"
                self._logger.error(f"🔧 {error_msg}")
                self._logger.error(f"🔧 location_data: {location_data}")
                self._logger.error(f"🔧 request_data keys: {list(self._request_data.keys())}")
                self._emit_error(error_msg)
                return
            
            self._logger.info(f"🔧 WeatherClient hívás előkészítése: latitude={latitude}, longitude={longitude}")
            
            # === INTERRUPT CHECK BEFORE API CALL ===
            if self._check_interruption("Weather API hívás előtt"):
                return
            
            # 🔧 KRITIKUS JAVÍTÁS: HELYES PARAMÉTER NEVEK A WEATHERCLIENT.GET_WEATHER_DATA() HÍVÁSBAN!
            # ❌ HIBÁS VOLT: lat=..., lon=...
            # ✅ JAVÍTOTT: latitude=..., longitude=...
            self._logger.info(f"🔧 WeatherClient.get_weather_data() hívás JAVÍTOTT paraméterekkel...")
            
            weather_data = self._weather_client.get_weather_data(
                latitude=latitude,           # ✅ HELYES PARAMÉTER NÉV!
                longitude=longitude,         # ✅ HELYES PARAMÉTER NÉV!
                start_date=date_range.get('start_date'),
                end_date=date_range.get('end_date')
            )
            
            self._logger.info(f"✅ WeatherClient.get_weather_data() sikeresen lefutott")
            self._logger.info(f"🎯 Nyers weather_data típus: {type(weather_data)}")
            
            if isinstance(weather_data, list) and weather_data:
                self._logger.info(f"🎯 Első elem típus: {type(weather_data[0])}")
                self._logger.info(f"🎯 Első elem kulcsok: {list(weather_data[0].keys()) if isinstance(weather_data[0], dict) else 'Not dict'}")
            
            if self._check_interruption("Single location feldolgozás"):
                return
            
            # 🎯 KRITIKUS JAVÍTÁS: ADATKONVERZIÓ List[Dict] → Dict[List]
            self._emit_progress("Adatok konvertálása...", 80)
            converted_weather_data = self._convert_to_legacy_format(weather_data)
            
            if not converted_weather_data:
                self._emit_error("Adatkonverzió sikertelen")
                return
            
            self._logger.info(f"🎯 Konvertált adatok típus: {type(converted_weather_data)}")
            if isinstance(converted_weather_data, dict) and 'daily' in converted_weather_data:
                daily_keys = list(converted_weather_data['daily'].keys())
                self._logger.info(f"🎯 Konvertált daily kulcsok: {daily_keys}")
                if 'time' in converted_weather_data['daily']:
                    time_count = len(converted_weather_data['daily']['time'])
                    self._logger.info(f"🎯 Time records count: {time_count}")
                    
            result = {
                'analysis_type': 'single_location',
                'request_params': self._request_data,
                'result_data': converted_weather_data,  # 🎯 KONVERTÁLT ADATOK!
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
            self._emit_progress("Egyedi elemzés befejezve", 100)
            self.analysis_completed.emit(result)
            
        except Exception as e:
            self._logger.error(f"Single location elemzés hiba: {str(e)}")
            self._logger.error(traceback.format_exc())
            self._emit_error(f"Egyedi elemzés sikertelen: {str(e)}")
    
    def _convert_to_legacy_format(self, weather_data: List[Dict]) -> Optional[Dict]:
        """
        🎯 KRITIKUS JAVÍTÁS: ADATKONVERZIÓ List[Dict] → Dict[List] + 🌹 SZÉLIRÁNY KOMPATIBILITÁS!
        
        WeatherClient formátum (List[Dict]):
        [{"date": "2024-01-01", "winddirection_10m_dominant": 310, "windgusts_10m_max": 39.2}, ...]
        
        AppController várt formátum (Dict[List]):
        {"daily": {"time": ["2024-01-01"], "winddirection_10m_dominant": [310], "windgusts_10m_max": [39.2]}}
        
        🌹 ÚJ: CHART KOMPATIBILITÁSI KULCSOK HOZZÁADÁSA:
        - winddirection_10m_dominant → winddirection (WindRoseChart-nak)
        - windgusts_10m_max → wind_gusts_max (WindChart-nak)
        
        Args:
            weather_data: WeatherClient által visszaadott List[Dict] adatok
            
        Returns:
            AppController által várt Dict[List] formátum vagy None
        """
        try:
            self._logger.info(f"🎯 ADATKONVERZIÓ kezdés: {type(weather_data)} → Dict[List] + SZÉLIRÁNY KOMPATIBILITÁS")
            
            if not weather_data:
                self._logger.warning("🎯 Üres weather_data")
                return None
            
            if not isinstance(weather_data, list):
                self._logger.warning(f"🎯 Váratlan weather_data típus: {type(weather_data)}")
                return None
            
            if not weather_data or not isinstance(weather_data[0], dict):
                self._logger.warning("🎯 Weather_data nem List[Dict] formátum")
                return None
            
            # 🎯 KONVERZIÓ: List[Dict] → Dict[List]
            result = {"daily": {}}
            
            # Első rekord kulcsainak felmérése
            sample_keys = list(weather_data[0].keys())
            self._logger.info(f"🎯 Konvertálandó kulcsok: {sample_keys}")
            
            for key in sample_keys:
                if key == 'date':
                    # 'date' kulcs → 'time' kulcs (AppController elvárás)
                    result["daily"]["time"] = [record.get("date") for record in weather_data]
                    self._logger.info(f"🎯 Konvertálva: date → time ({len(result['daily']['time'])} elem)")
                else:
                    # Minden más kulcs 1:1 átvétele
                    result["daily"][key] = [record.get(key) for record in weather_data]
                    self._logger.info(f"🎯 Konvertálva: {key} ({len(result['daily'][key])} elem)")
            
            # 🌹 KRITIKUS: CHART KOMPATIBILITÁSI KULCSOK HOZZÁADÁSA!
            self._logger.info("🌹 Chart kompatibilitási kulcsok hozzáadása...")
            
            # 1. winddirection_10m_dominant → winddirection (WindRoseChart kompatibilitás)
            if 'winddirection_10m_dominant' in result["daily"]:
                result["daily"]["winddirection"] = result["daily"]["winddirection_10m_dominant"]
                self._logger.info("🌹 ✅ Kompatibilitási kulcs hozzáadva: winddirection_10m_dominant → winddirection")
            
            # 2. windgusts_10m_max → wind_gusts_max (WindChart kompatibilitás)
            if 'windgusts_10m_max' in result["daily"]:
                result["daily"]["wind_gusts_max"] = result["daily"]["windgusts_10m_max"]
                self._logger.info("🌹 ✅ Kompatibilitási kulcs hozzáadva: windgusts_10m_max → wind_gusts_max")
            
            # 3. OPCIONÁLIS: wind_direction_10m_dominant aliasz (ha szükséges)
            if 'winddirection_10m_dominant' in result["daily"]:
                result["daily"]["wind_direction_10m_dominant"] = result["daily"]["winddirection_10m_dominant"]
                self._logger.info("🌹 ✅ Kompatibilitási kulcs hozzáadva: winddirection_10m_dominant → wind_direction_10m_dominant")
            
            # Extra metaadatok hozzáadása (ha vannak)
            if weather_data:
                first_record = weather_data[0]
                # WeatherClient metadata keresése
                for meta_key in ['latitude', 'longitude', 'timezone', 'elevation']:
                    if meta_key in first_record:
                        result[meta_key] = first_record[meta_key]
                        self._logger.info(f"🎯 Metadata hozzáadva: {meta_key} = {first_record[meta_key]}")
            
            # Eredmény validálás
            if not result.get("daily", {}).get("time"):
                self._logger.error("🎯 KONVERZIÓ HIBA: Nincs 'time' mező!")
                return None
            
            record_count = len(result["daily"]["time"])
            self._logger.info(f"🎯 KONVERZIÓ SIKERES: {record_count} rekord konvertálva")
            self._logger.info(f"🎯 Végső daily kulcsok: {list(result['daily'].keys())}")
            
            # 🌹 SZÉLIRÁNY KOMPATIBILITÁSI CHECK
            if 'winddirection_10m_dominant' in result['daily']:
                wind_directions = result['daily']['winddirection_10m_dominant']
                valid_directions = [d for d in wind_directions if d is not None]
                if valid_directions:
                    self._logger.info(f"🌹 Szélirány adatok konvertálva: {len(valid_directions)} érvényes érték")
                    self._logger.info(f"🌹 Szélirány tartomány: {min(valid_directions):.0f}° → {max(valid_directions):.0f}°")
                    
                    # KOMPATIBILITÁSI ELLENŐRZÉS
                    if 'winddirection' in result['daily']:
                        compat_count = len([d for d in result['daily']['winddirection'] if d is not None])
                        self._logger.info(f"🌹 ✅ WindRoseChart kompatibilitási kulcs 'winddirection': {compat_count} érvényes érték")
            
            # 🌪️ SZÉLLÖKÉS KOMPATIBILITÁSI CHECK
            if 'windgusts_10m_max' in result['daily']:
                wind_gusts = result['daily']['windgusts_10m_max']
                valid_gusts = [g for g in wind_gusts if g is not None and g > 0]
                if valid_gusts:
                    max_gust = max(valid_gusts)
                    self._logger.info(f"🌪️ Széllökés adatok konvertálva: {len(valid_gusts)} érvényes érték")
                    self._logger.info(f"🌪️ Maximum széllökés: {max_gust:.1f} km/h")
                    
                    # KOMPATIBILITÁSI ELLENŐRZÉS
                    if 'wind_gusts_max' in result['daily']:
                        compat_count = len([g for g in result['daily']['wind_gusts_max'] if g is not None and g > 0])
                        self._logger.info(f"🌪️ ✅ WindChart kompatibilitási kulcs 'wind_gusts_max': {compat_count} érvényes érték")
            
            return result
            
        except Exception as e:
            self._logger.error(f"🎯 ADATKONVERZIÓ HIBA: {e}")
            self._logger.error(traceback.format_exc())
            return None
    
    def _run_county_analysis(self):
        """MEGYE ELEMZÉSE"""
        # Hasonló logika mint multi_city, de megyére specializálva
        self._run_multi_city_analysis()  # Egyszerűsítés miatt
    
    def _progress_callback(self, message: str, percentage: int):
        """
        PROGRESS CALLBACK - MultiCityEngine-ből érkező jelzések
        FONTOS: Interrupt ellenőrzés a callback-ben is!
        """
        if self._check_interruption("Progress callback"):
            return False  # Jelzi a hívónak, hogy álljon le
            
        self._emit_progress(message, percentage)
        return True  # Folytatás
    
    def _check_interruption(self, operation: str) -> bool:
        """
        INTERRUPT ELLENŐRZÉS
        
        Args:
            operation (str): Jelenlegi művelet neve (debugging)
            
        Returns:
            bool: True ha meg kell szakítani
        """
        if self.isInterruptionRequested():
            self._logger.info(f"Megszakítás kérve művelet közben: {operation}")
            self._emit_progress("Megszakítás...", 0)
            self.analysis_cancelled.emit()
            return True
        return False
    
    def _emit_progress(self, message: str, percentage: int):
        """Thread-safe progress jelzés"""
        self.progress_updated.emit(message, percentage)
        
        # Qt esemény feldolgozás (responsive UI)
        QApplication.processEvents()
    
    def _emit_error(self, error_message: str):
        """Thread-safe error jelzés"""
        self._logger.error(f"Worker hiba: {error_message}")
        self.analysis_failed.emit(error_message)
    
    # === PUBLIC CONTROL METHODS ===
    
    def start_analysis(self, request_data: Dict[str, Any]):
        """
        ELEMZÉS INDÍTÁSA
        
        Args:
            request_data (dict): Teljes elemzési kérés
        """
        if self.isRunning():
            self._logger.warning("Worker már fut, nem lehet újat indítani")
            return False
            
        self.setup_analysis_request(request_data)
        self.start()  # QThread.start()
        return True
    
    def stop_analysis(self):
        """
        ELEMZÉS MEGSZAKÍTÁSA
        Graceful shutdown - nem brutális kill
        """
        if self.isRunning():
            self._logger.info("Worker megszakítás kérve...")
            self.requestInterruption()
            
            # Várunk a tiszta leállásra (max 5 másodperc)
            if not self.wait(5000):
                self._logger.warning("Worker nem állt le 5 másodperc alatt, terminálás...")
                self.terminate()
                self.wait(1000)
    
    def is_running_analysis(self) -> bool:
        """Worker futási állapot lekérdezése"""
        return self.isRunning()


# === USAGE EXAMPLE ===
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
    
    class WorkerTestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("AnalysisWorker Test (SZÉLIRÁNY KOMPATIBILITÁS FIX v4.6.3)")
            self.setGeometry(100, 100, 600, 400)
            
            # UI Setup
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            self.status_label = QLabel("Worker készenlétben...")
            self.start_button = QPushButton("Test Elemzés Indítása")
            self.stop_button = QPushButton("Megszakítás")
            
            layout.addWidget(self.status_label)
            layout.addWidget(self.start_button)
            layout.addWidget(self.stop_button)
            
            # Worker setup
            self.worker = AnalysisWorker()
            self.worker.progress_updated.connect(self._on_progress)
            self.worker.analysis_completed.connect(self._on_completed)
            self.worker.analysis_failed.connect(self._on_failed)
            self.worker.analysis_cancelled.connect(self._on_cancelled)
            
            # Button connections
            self.start_button.clicked.connect(self._start_test)
            self.stop_button.clicked.connect(self._stop_test)
            
        def _start_test(self):
            test_request = {
                'analysis_type': 'single_location',
                'location_data': {
                    'latitude': 55.7558,
                    'longitude': 37.6176,
                    'name': 'Moscow'
                },
                'date_range': {
                    'start_date': '2024-01-01',
                    'end_date': '2024-01-02'
                },
                'provider': 'open_meteo'
            }
            
            self.worker.start_analysis(test_request)
            self.status_label.setText("Worker elindítva...")
            
        def _stop_test(self):
            self.worker.stop_analysis()
            
        def _on_progress(self, message: str, percentage: int):
            self.status_label.setText(f"{message} ({percentage}%)")
            
        def _on_completed(self, result: dict):
            self.status_label.setText("✅ Elemzés sikeresen befejezve!")
            
        def _on_failed(self, error: str):
            self.status_label.setText(f"❌ Hiba: {error}")
            
        def _on_cancelled(self):
            self.status_label.setText("ℹ️ Elemzés megszakítva")
    
    app = QApplication(sys.argv)
    window = WorkerTestWindow()
    window.show()
    sys.exit(app.exec())