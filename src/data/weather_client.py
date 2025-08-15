#!/usr/bin/env python3
"""
Weather Client - Multi-Provider API integráció (EGYSÉGES API VERZIÓ)
Global Weather Analyzer projekt

🔥 KRITIKUS JAVÍTÁS: HELYES API PARAMÉTER NEVEK!
🚀 BATCHING LOGIC: Open-Meteo 1 éves limit megkerülése
📈 TREND ANALYTICS READY: 5-10-55 éves trend elemzések támogatása
🌪️ SZÉLIRÁNY JAVÍTÁS: winddirection_10m_dominant hozzáadva a daily paraméterekhez!

🔧 JAVÍTÁS v4.6 - SZÉLIRÁNY API PARAMÉTER FIX:
- ✅ wind_direction_10m_dominant ➜ winddirection_10m_dominant (HELYES API NÉV!)
- ✅ WindRose chart támogatás biztosítva
- ✅ API PARAMÉTER NÉVJAVÍTÁS: windspeed → wind_speed, windgusts → wind_gusts  
- ✅ get_weather_data() MINDIG List[Dict] visszatérés (nem tuple!)
- ✅ data_source minden rekordba beépítve
- ✅ Konzisztens API - nincs többé tuple unpacking hiba
- ✅ Backward compatibility megőrizve
- 🔧 KRITIKUS FIX: Daily paraméterek listában maradnak (nem string!)
- 🌪️ API PARAMÉTER SZÉLIRÁNY FIX: wind_direction_10m_dominant ➜ winddirection_10m_dominant

Új funkciók:
- get_weather_data_batched() - többéves időszakok darabolása
- Automatikus 1 éves batch-ek generálása 
- Seamless adatkapcsolás eredmény listájában
- Professional progress tracking
- Rate limiting minden batch-hez
"""

import requests
import logging
import time
import os
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
import statistics
from abc import ABC, abstractmethod

# 🌍 Provider routing imports
from ..gui.utils import (
    get_optimal_data_source, validate_api_source_available,
    get_fallback_source_chain, get_source_display_name,
    log_provider_usage_event, APIConstants
)

# ✅ CONFIG IMPORT JAVÍTÁS
from ..config import APIConfig

# Logging beállítás - MULTI-YEAR támogatással
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    """Időjárási adat struktúra - MULTI-YEAR READY"""
    date: str
    temperature_2m_max: Optional[float] = None
    temperature_2m_min: Optional[float] = None
    temperature_2m_mean: Optional[float] = None
    apparent_temperature_max: Optional[float] = None
    apparent_temperature_min: Optional[float] = None
    precipitation_sum: Optional[float] = None
    rain_sum: Optional[float] = None
    snowfall_sum: Optional[float] = None
    precipitation_hours: Optional[int] = None
    wind_speed_10m_max: Optional[float] = None  # ✅ JAVÍTOTT NÉV
    wind_gusts_10m_max: Optional[float] = None  # ✅ JAVÍTOTT NÉV
    winddirection_10m_dominant: Optional[float] = None
    shortwave_radiation_sum: Optional[float] = None
    sunshine_duration: Optional[float] = None
    uv_index_max: Optional[float] = None
    uv_index_clear_sky_max: Optional[float] = None
    
    # 🌍 Provider tracking
    data_source: Optional[str] = None
    
    # Számított értékek
    temperature_range: Optional[float] = None
    
    def __post_init__(self):
        """Számított értékek automatikus számítása"""
        if self.temperature_2m_max is not None and self.temperature_2m_min is not None:
            self.temperature_range = self.temperature_2m_max - self.temperature_2m_min
        
        if self.temperature_2m_max is not None and self.temperature_2m_min is not None and self.temperature_2m_mean is None:
            self.temperature_2m_mean = (self.temperature_2m_max + self.temperature_2m_min) / 2


class WeatherAPIError(Exception):
    """Weather API specifikus hibák"""
    pass


class ProviderNotAvailableError(WeatherAPIError):
    """Provider nem elérhető hiba"""
    pass


class ProviderValidationError(WeatherAPIError):
    """Provider validációs hiba"""
    pass


class WeatherProvider(ABC):
    """Abstract base class minden weather provider-hez."""
    
    def __init__(self, provider_id: str, display_name: str):
        self.provider_id = provider_id
        self.display_name = display_name
        self.session = requests.Session()
        self.request_count = 0
        self.last_request_time = 0
        self.min_request_interval = 0.1
        
        logger.info(f"Weather provider inicializálva: {display_name}")
    
    @abstractmethod
    def get_weather_data(self, latitude: float, longitude: float,
                        start_date: str, end_date: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def validate_provider(self) -> bool:
        pass
    
    def _rate_limit_check(self) -> None:
        """Rate limiting ellenőrzés és késleltetés."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
    
    def _update_request_tracking(self) -> None:
        """Request tracking frissítése."""
        self.request_count += 1
        self.last_request_time = time.time()
    
    def get_request_count(self) -> int:
        return self.request_count
    
    def reset_request_count(self) -> None:
        self.request_count = 0


class OpenMeteoProvider(WeatherProvider):
    """🔥 MULTI-YEAR TÁMOGATÁS: Open-Meteo API provider batching logikával."""
    
    def __init__(self):
        super().__init__("open-meteo", "🌍 Open-Meteo API")
        self.base_url = APIConfig.OPEN_METEO_ARCHIVE
        self.session.headers.update({
            "User-Agent": APIConfig.USER_AGENT,
            "Accept": "application/json"
        })
        
        # 🔥 BATCHING KONFIGURÁCIÓ - 55 ÉVES RATE LIMIT OPTIMALIZÁLÁS
        self.max_days_per_request = 90   # OPTIMALIZÁLT: 365 → 90 nap (3 hónap/batch)
        self.batch_delay = 0.6  # OPTIMALIZÁLT: 2.0 → 0.6 sec (100 batch/min, biztonsági margin)
        
        logger.info(f"🔥 OpenMeteoProvider - 55 ÉVES RATE LIMIT OPTIMALIZÁLÁS aktiválva")
        logger.info(f"📅 Max days/request: {self.max_days_per_request} (rate limit optimalizált)")
        logger.info(f"⏱️ Batch delay: {self.batch_delay}s (100 batch/min limit)")
        logger.info(f"📊 55 év ≈ 223 batch × 0.6s ≈ 2.2 perc lekérdezés")
    
    def validate_provider(self) -> bool:
        """Open-Meteo mindig elérhető (nincs API kulcs szükséges)."""
        return True
    
    def get_weather_data(self, latitude: float, longitude: float,
                        start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        🔥 SMART DISPATCH: Automatikus batching vs single request
        
        Ha > 90 nap, akkor batched lekérdezés
        Ha <= 90 nap, akkor single request
        
        🔧 JAVÍTÁS v4.5: MINDIG List[Dict] visszatérés (nem tuple!)
        """
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days_diff = (end_dt - start_dt).days
        
        logger.info(f"📊 Lekérdezési időszak: {days_diff} nap ({start_date} → {end_date})")
        
        if days_diff > self.max_days_per_request:
            logger.info(f"🔥 MULTI-YEAR BATCHING: {days_diff} nap > {self.max_days_per_request} nap limit")
            return self.get_weather_data_batched(latitude, longitude, start_date, end_date)
        else:
            logger.info(f"📅 SINGLE REQUEST: {days_diff} nap <= {self.max_days_per_request} nap limit")
            return self.get_weather_data_single(latitude, longitude, start_date, end_date)
    
    def get_weather_data_single(self, latitude: float, longitude: float,
                               start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Egyszeri Open-Meteo API lekérdezés (max 90 nap) - RATE LIMIT OPTIMALIZÁLT
        
        🔧 JAVÍTÁS v4.6: HELYES API PARAMÉTER NEVEK + SZÉLIRÁNY + MINDIG List[Dict] visszatérés
        """
        # 🔥 JAVÍTOTT PARAMÉTEREK - HELYES API NEVEK + SZÉLIRÁNY
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            # 🎯 VALÓS API MEZŐK - DEBUG ALAPJÁN JAVÍTOTT NEVEK + SZÉLIRÁNY HOZZÁADVA
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min", 
                "temperature_2m_mean",
                "precipitation_sum",
                "windspeed_10m_max",         # ✅ VALÓS API NÉV
                "windgusts_10m_max",         # 🔧 JAVÍTÁS: wind_gusts_max → windgusts_10m_max
                "winddirection_10m_dominant" # 🌪️ KRITIKUS JAVÍTÁS: HELYES API NÉV! (nem wind_direction_10m_dominant!)
            ],
            "timezone": "auto",
            "models": "best_match"  # 🎯 EGYETLEN MODELL (nem többszörös)
        }
        
        return self._make_api_request(params)
    
    def get_weather_data_batched(self, latitude: float, longitude: float,
                                start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        🔥 TÖBBÉVES LEKÉRDEZÉS BATCHING LOGIKÁVAL
        
        Felbontja a hosszú időszakot 90 napos batch-ekre,
        lekérdezi egyesével, és összekapcsolja az eredményeket.
        
        🔧 JAVÍTÁS v4.5: MINDIG List[Dict] visszatérés
        
        Args:
            latitude, longitude: Koordináták
            start_date, end_date: Teljes időszak (YYYY-MM-DD)
        
        Returns:
            Összes nap adatai egyetlen listában időrendi sorrendben
        """
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        total_days = (end_dt - start_dt).days
        
        logger.info(f"🔥 BATCHING START: {total_days} nap → batch-ekre bontása")
        
        # Batch-ek generálása
        batches = self._generate_batches(start_dt, end_dt)
        logger.info(f"📦 Generált batch-ek: {len(batches)} db")
        
        all_weather_data = []
        successful_batches = 0
        failed_batches = 0
        
        for i, (batch_start, batch_end) in enumerate(batches, 1):
            batch_start_str = batch_start.strftime("%Y-%m-%d")
            batch_end_str = batch_end.strftime("%Y-%m-%d")
            batch_days = (batch_end - batch_start).days + 1
            
            logger.info(f"📦 Batch {i}/{len(batches)}: {batch_start_str} → {batch_end_str} ({batch_days} nap)")
            
            try:
                # Single batch lekérdezése
                batch_data = self.get_weather_data_single(
                    latitude, longitude, batch_start_str, batch_end_str
                )
                
                if batch_data:
                    all_weather_data.extend(batch_data)
                    successful_batches += 1
                    logger.info(f"  ✅ Siker: {len(batch_data)} nap hozzáadva")
                else:
                    failed_batches += 1
                    logger.warning(f"  ⚠️ Üres batch: {batch_start_str} → {batch_end_str}")
                
                # Rate limiting batch-ek között
                if i < len(batches):  # Utolsó batch után nincs késleltetés
                    logger.debug(f"  ⏳ Batch delay: {self.batch_delay}s")
                    time.sleep(self.batch_delay)
                
            except WeatherAPIError as e:
                failed_batches += 1
                logger.error(f"  ❌ Batch hiba: {e}")
                # Folytatjuk a következő batch-csel
                continue
            except Exception as e:
                failed_batches += 1
                logger.error(f"  ❌ Váratlan batch hiba: {e}")
                continue
        
        # Eredmények rendezése dátum szerint (biztonsági intézkedés)
        all_weather_data.sort(key=lambda x: x.get('date', ''))
        
        # Összesítő jelentés
        success_rate = (successful_batches / len(batches)) * 100 if batches else 0
        
        logger.info("=" * 60)
        logger.info("🔥 BATCHING BEFEJEZVE - ÖSSZESÍTÉS")
        logger.info("=" * 60)
        logger.info(f"📦 Összes batch: {len(batches)}")
        logger.info(f"✅ Sikeres batch-ek: {successful_batches}")
        logger.info(f"❌ Sikertelen batch-ek: {failed_batches}")
        logger.info(f"📊 Sikerességi arány: {success_rate:.1f}%")
        logger.info(f"📅 Összes nap: {len(all_weather_data)}")
        logger.info(f"🎯 Várt napok: {total_days}")
        logger.info("=" * 60)
        
        if len(all_weather_data) == 0:
            logger.error("❌ KRITIKUS: Nincs adat egyik batch-ből sem!")
            raise WeatherAPIError("Batch lekérdezés teljesen sikertelen - nincs adat")
        
        if len(all_weather_data) < total_days * 0.8:  # 80% alatti lefedettség
            logger.warning(f"⚠️ FIGYELEM: Alacsony adatlefedettség {len(all_weather_data)}/{total_days} ({len(all_weather_data)/total_days*100:.1f}%)")
        
        return all_weather_data
    
    def _generate_batches(self, start_dt: datetime, end_dt: datetime) -> List[Tuple[datetime, datetime]]:
        """
        Időszak felbontása batch-ekre
        
        Args:
            start_dt, end_dt: Teljes időszak datetime objektumokként
            
        Returns:
            [(batch_start, batch_end), ...] tuple-ök listája
        """
        batches = []
        current_start = start_dt
        
        while current_start <= end_dt:
            # Batch végének számítása (max 90 nap vagy az end_dt)
            current_end = min(
                current_start + timedelta(days=self.max_days_per_request - 1),
                end_dt
            )
            
            batches.append((current_start, current_end))
            
            # Következő batch kezdete
            current_start = current_end + timedelta(days=1)
        
        return batches
    
    def _make_api_request(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Open-Meteo API kérés végrehajtása (SINGLE REQUEST)
        
        🔧 KRITIKUS JAVÍTÁS v4.5: Daily paraméterek LISTÁBAN maradnak!
        """
        self._rate_limit_check()
        
        # 🔧 KRITIKUS FIX: NE alakítsd át string-gé a daily paramétereket!
        # Az Open-Meteo API a lista formátumot várja!
        # TÖRŐLT HIBÁS KÓD:
        # if isinstance(params.get("daily"), list):
        #     daily_params = ",".join(params["daily"])
        #     params["daily"] = daily_params
        
        try:
            logger.debug(f"🌍 API REQUEST: {params['start_date']} → {params['end_date']}")
            logger.debug(f"🌍 Daily params (LIST): {params['daily']}")
            
            response = self.session.get(self.base_url, params=params, timeout=APIConfig.REQUEST_TIMEOUT)
            self._update_request_tracking()
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if "daily" not in data:
                        logger.error(f"❌ MISSING 'daily' key in response: {data}")
                        raise WeatherAPIError(f"Érvénytelen Open-Meteo API válasz: {data}")
                    
                    return self._process_response(data)
                    
                except json.JSONDecodeError as je:
                    logger.error(f"❌ JSON DECODE ERROR: {je}")
                    raise WeatherAPIError(f"JSON decode error: {je}")
            
            elif response.status_code == 400:
                logger.error(f"❌ 400 BAD REQUEST: {response.text}")
                raise WeatherAPIError(f"Open-Meteo hibás paraméterek: {response.text}")
            elif response.status_code == 429:
                raise WeatherAPIError("Open-Meteo rate limit túllépve")
            elif response.status_code == 500:
                raise WeatherAPIError("Open-Meteo szerver hiba")
            else:
                logger.error(f"❌ Unexpected status code: {response.status_code}")
                raise WeatherAPIError(f"Open-Meteo API hiba: {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise WeatherAPIError("Open-Meteo API timeout")
        except requests.exceptions.ConnectionError:
            raise WeatherAPIError("Open-Meteo kapcsolódási hiba")
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Open-Meteo kérés hiba: {str(e)}")
    
    def _process_response(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Open-Meteo API válasz feldolgozása
        
        🔧 JAVÍTÁS v4.6: data_source minden rekordba beépítve + SZÉLIRÁNY FELDOLGOZÁS
        """
        daily_data = response_data.get("daily", {})
        dates = daily_data.get("time", [])
        
        if not dates:
            logger.warning("⚠️ Nincs dátum a válaszban")
            return []
        
        # Metrikák kinyerése
        metrics = {}
        for key, values in daily_data.items():
            if key != "time" and isinstance(values, list):
                metrics[key] = values
        
        # 🌪️ SZÉLIRÁNY ELLENŐRZÉS
        if "winddirection_10m_dominant" in metrics:
            wind_directions = metrics["winddirection_10m_dominant"]
            valid_directions = [d for d in wind_directions if d is not None]
            logger.info(f"🌪️ Szélirány adatok feldolgozva: {len(valid_directions)}/{len(wind_directions)} érvényes értékek")
        else:
            logger.warning("⚠️ Nincs szélirány adat a válaszban!")
        
        # 🌪️ SZÉLLÖKÉS ELLENŐRZÉS
        if "windgusts_10m_max" in metrics:
            wind_gusts = metrics["windgusts_10m_max"]
            valid_gusts = [g for g in wind_gusts if g is not None]
            logger.info(f"🌪️ Széllökés adatok feldolgozva: {len(valid_gusts)}/{len(wind_gusts)} érvényes értékek")
        else:
            logger.warning("⚠️ Nincs széllökés adat a válaszban!")
        
        # Napi adatok összeállítása
        weather_data = []
        for i, date in enumerate(dates):
            # 🔧 JAVÍTÁS v4.5: data_source MINDEN rekordba beépítve
            daily_record = {
                "date": date, 
                "data_source": self.provider_id  # ✅ KRITIKUS: Itt kerül be a forrás!
            }
            
            for metric_name, metric_values in metrics.items():
                if i < len(metric_values):
                    value = metric_values[i]
                    daily_record[metric_name] = value if value is not None else None
            
            weather_data.append(daily_record)
        
        logger.debug(f"✅ Feldolgozva: {len(weather_data)} nap (data_source: {self.provider_id})")
        return weather_data


class MeteostatProvider(WeatherProvider):
    """🌍 Meteostat API provider implementáció - 55+ éves adatok támogatással."""
    
    def __init__(self):
        super().__init__("meteostat", "💎 Meteostat API")
        self.base_url = APIConfig.METEOSTAT_BASE
        self.api_key = os.getenv("METEOSTAT_API_KEY")
        
        if self.api_key:
            self.session.headers.update({
                "User-Agent": APIConfig.USER_AGENT,
                "Accept": "application/json",
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "meteostat.p.rapidapi.com"
            })
        
        self.min_request_interval = APIConfig.METEOSTAT_RATE_LIMIT
        
        # 🔥 METEOSTAT MAX RANGE: 10 év per request
        self.max_years_per_request = 10
        logger.info(f"💎 MeteostatProvider - MAX {self.max_years_per_request} év/request")
    
    def validate_provider(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) >= 32)
    
    def get_weather_data(self, latitude: float, longitude: float,
                        start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        🔥 METEOSTAT SMART DISPATCH
        
        🔧 JAVÍTÁS v4.5: MINDIG List[Dict] visszatérés
        
        Meteostat támogatja a hosszabb időszakokat (akár 10 év),
        de nagy időszakok esetén batch-elni érdemes.
        """
        if not self.validate_provider():
            raise ProviderValidationError("Meteostat API kulcs hiányzik vagy érvénytelen")
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        years_diff = (end_dt - start_dt).days / 365.25
        
        logger.info(f"💎 Meteostat lekérdezés: {years_diff:.1f} év ({start_date} → {end_date})")
        
        if years_diff > self.max_years_per_request:
            logger.info(f"🔥 METEOSTAT BATCHING: {years_diff:.1f} év > {self.max_years_per_request} év limit")
            return self.get_weather_data_batched(latitude, longitude, start_date, end_date)
        else:
            logger.info(f"📅 METEOSTAT SINGLE: {years_diff:.1f} év <= {self.max_years_per_request} év limit")
            return self.get_weather_data_single(latitude, longitude, start_date, end_date)
    
    def get_weather_data_single(self, latitude: float, longitude: float,
                               start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Egyszeri Meteostat lekérdezés
        
        🔧 JAVÍTÁS v4.5: MINDIG List[Dict] visszatérés
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "start": start_date,
            "end": end_date
        }
        
        return self._make_api_request(params)
    
    def get_weather_data_batched(self, latitude: float, longitude: float,
                                start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        🔥 METEOSTAT BATCHING - 10 éves batch-ek
        
        🔧 JAVÍTÁS v4.5: MINDIG List[Dict] visszatérés
        """
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        batches = []
        current_start = start_dt
        
        while current_start <= end_dt:
            # 10 éves batch
            current_end = min(
                current_start.replace(year=current_start.year + self.max_years_per_request),
                end_dt
            )
            
            batches.append((current_start, current_end))
            current_start = current_end + timedelta(days=1)
        
        logger.info(f"💎 METEOSTAT BATCHES: {len(batches)} db")
        
        all_data = []
        for i, (batch_start, batch_end) in enumerate(batches, 1):
            try:
                batch_start_str = batch_start.strftime("%Y-%m-%d")
                batch_end_str = batch_end.strftime("%Y-%m-%d")
                
                logger.info(f"💎 Batch {i}/{len(batches)}: {batch_start_str} → {batch_end_str}")
                
                batch_data = self.get_weather_data_single(
                    latitude, longitude, batch_start_str, batch_end_str
                )
                
                if batch_data:
                    all_data.extend(batch_data)
                    logger.info(f"  ✅ Meteostat batch siker: {len(batch_data)} nap")
                
                # Rate limiting
                if i < len(batches):
                    time.sleep(self.min_request_interval)
                    
            except Exception as e:
                logger.error(f"  ❌ Meteostat batch hiba: {e}")
                continue
        
        return sorted(all_data, key=lambda x: x.get('date', ''))
    
    def _make_api_request(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        🔧 JAVÍTÁS v4.5: MINDIG List[Dict] visszatérés
        """
        self._rate_limit_check()
        
        endpoint = f"{self.base_url}/point/daily"
        
        try:
            response = self.session.get(endpoint, params=params, timeout=APIConfig.REQUEST_TIMEOUT)
            self._update_request_tracking()
            
            if response.status_code == 200:
                data = response.json()
                if "data" not in data:
                    raise WeatherAPIError(f"Érvénytelen Meteostat API válasz: {data}")
                return self._process_response(data)
            
            elif response.status_code == 401:
                raise ProviderValidationError("Meteostat API hitelesítési hiba")
            elif response.status_code == 403:
                raise WeatherAPIError("Meteostat API hozzáférés megtagadva")
            elif response.status_code == 429:
                raise WeatherAPIError("Meteostat rate limit túllépve")
            elif response.status_code == 500:
                raise WeatherAPIError("Meteostat szerver hiba")
            else:
                raise WeatherAPIError(f"Meteostat API hiba: {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise WeatherAPIError("Meteostat API timeout")
        except requests.exceptions.ConnectionError:
            raise WeatherAPIError("Meteostat kapcsolódási hiba")
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Meteostat kérés hiba: {str(e)}")
        except json.JSONDecodeError:
            raise WeatherAPIError("Meteostat JSON dekódolási hiba")
    
    def _process_response(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        🔧 JAVÍTÁS v4.6: data_source minden rekordba beépítve + HELYES FIELD MAPPING + SZÉLIRÁNY
        """
        raw_data = response_data.get("data", [])
        
        if not raw_data:
            logger.warning("Nincs adat a Meteostat válaszban")
            return []
        
        # ✅ JAVÍTOTT FIELD MAPPING - HELYES API NEVEK + SZÉLIRÁNY
        field_mapping = {
            "date": "date",
            "tavg": "temperature_2m_mean",
            "tmin": "temperature_2m_min",
            "tmax": "temperature_2m_max",
            "prcp": "precipitation_sum",
            "wspd": "windspeed_10m_max",        # ✅ JAVÍTOTT: windspeed → windspeed_10m_max
            "wpgt": "windgusts_10m_max",       # ✅ JAVÍTOTT: windgusts → windgusts_10m_max
            "wdir": "winddirection_10m_dominant",  # 🌪️ SZÉLIRÁNY MAPPING
            "tsun": "sunshine_duration"
        }
        
        weather_data = []
        for record in raw_data:
            # 🔧 JAVÍTÁS v4.5: data_source MINDEN rekordba beépítve
            daily_record = {
                "data_source": self.provider_id  # ✅ KRITIKUS: Itt kerül be a forrás!
            }
            
            for meteostat_field, openmeteo_field in field_mapping.items():
                if meteostat_field in record:
                    value = record[meteostat_field]
                    daily_record[openmeteo_field] = value if value is not None else None
            
            if "temperature_2m_max" in daily_record and daily_record["temperature_2m_max"]:
                daily_record["apparent_temperature_max"] = daily_record["temperature_2m_max"]
            if "temperature_2m_min" in daily_record and daily_record["temperature_2m_min"]:
                daily_record["apparent_temperature_min"] = daily_record["temperature_2m_min"]
            
            weather_data.append(daily_record)
        
        logger.debug(f"✅ Meteostat feldolgozva: {len(weather_data)} nap (data_source: {self.provider_id})")
        return weather_data


class WeatherClient:
    """🔥 MULTI-YEAR Weather Client - 55 éves trend elemzések támogatásával."""
    
    def __init__(self, preferred_provider: str = "auto"):
        self.preferred_provider = preferred_provider
        self.current_provider: Optional[str] = None
        self.provider_usage_stats: Dict[str, int] = {}
        
        self.providers: Dict[str, WeatherProvider] = {
            "open-meteo": OpenMeteoProvider(),
            "meteostat": MeteostatProvider()
        }
        
        self.max_retries = APIConfig.MAX_RETRIES
        self.retry_delay = 1.0
        
        self.provider_change_callback: Optional[Callable[[str, str], None]] = None
        self.provider_fallback_callback: Optional[Callable[[str, str], None]] = None
        
        logger.info(f"🔥 MULTI-YEAR WeatherClient v4.6 inicializálva (SZÉLIRÁNY JAVÍTÁS)")
    
    def set_provider_change_callback(self, callback: Callable[[str, str], None]) -> None:
        self.provider_change_callback = callback
    
    def set_provider_fallback_callback(self, callback: Callable[[str, str], None]) -> None:
        self.provider_fallback_callback = callback
    
    def get_weather_data(self, latitude: float, longitude: float,
                        start_date: str, end_date: str,
                        user_override_provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        🔥 MULTI-YEAR: Időjárási adatok lekérdezése automatikus batching-gal.
        
        🔧 KRITIKUS JAVÍTÁS v4.5: EGYSÉGES API - MINDIG List[Dict] visszatérés!
        ❌ RÉGI: Tuple[List[Dict], str] - ez okozta a tuple unpacking hibát
        ✅ ÚJ: List[Dict] - data_source minden rekordba beépítve
        
        Args:
            latitude, longitude: Koordináták
            start_date, end_date: Időszak (YYYY-MM-DD)
            user_override_provider: Kényszerített provider
            
        Returns:
            List[Dict]: Napi adatok, data_source minden rekordban
        """
        
        logger.info(f"🔥 MULTI-YEAR WEATHER REQUEST v4.6:")
        logger.info(f"  📍 Koordináták: {latitude:.4f}, {longitude:.4f}")
        logger.info(f"  📅 Időszak: {start_date} → {end_date}")
        logger.info(f"  🎛️ Provider override: {user_override_provider}")
        
        # Input validálás
        self._validate_inputs(latitude, longitude, start_date, end_date)
        
        # 🌍 Provider selection logic
        selected_provider = self._select_provider(user_override_provider)
        logger.info(f"🎯 SELECTED PROVIDER: {selected_provider}")
        
        if not selected_provider:
            raise ProviderNotAvailableError("Egyik provider sem elérhető")
        
        # 🌍 Provider fallback chain
        fallback_chain = self._get_provider_fallback_chain(selected_provider)
        logger.info(f"🔄 FALLBACK CHAIN: {fallback_chain}")
        
        last_error = None
        for attempt_provider in fallback_chain:
            try:
                logger.info(f"🔍 TRYING PROVIDER: {attempt_provider} ({get_source_display_name(attempt_provider)})")
                
                # Provider instance lekérdezése
                provider = self.providers.get(attempt_provider)
                if not provider or not provider.validate_provider():
                    logger.warning(f"⚠️ PROVIDER NOT AVAILABLE: {attempt_provider}")
                    continue
                
                logger.info(f"✅ PROVIDER VALIDATED: {attempt_provider}")
                
                # Retry logika provider-specifikusan
                weather_data = self._retry_weather_request(
                    provider, latitude, longitude, start_date, end_date
                )
                
                # Response analysis
                logger.info(f"📊 PROVIDER RESPONSE ANALYSIS:")
                logger.info(f"  📅 Records returned: {len(weather_data)}")
                
                if weather_data:
                    first_record = weather_data[0]
                    last_record = weather_data[-1]
                    logger.info(f"  📅 Date range: {first_record.get('date')} → {last_record.get('date')}")
                    
                    # Data source tracking
                    data_sources = set(record.get('data_source', 'unknown') for record in weather_data)
                    logger.info(f"  🌍 Data sources: {data_sources}")
                    
                    # Wind data analysis - ✅ JAVÍTOTT NEVEK + SZÉLIRÁNY
                    wind_speed_values = [r.get('windspeed_10m_max') for r in weather_data if r.get('windspeed_10m_max') is not None]
                    wind_gusts_values = [r.get('windgusts_10m_max') for r in weather_data if r.get('windgusts_10m_max') is not None]
                    wind_direction_values = [r.get('winddirection_10m_dominant') for r in weather_data if r.get('winddirection_10m_dominant') is not None]
                    
                    if wind_speed_values:
                        logger.info(f"  💨 Wind speed range: {min(wind_speed_values):.1f} → {max(wind_speed_values):.1f} km/h")
                        logger.info(f"  📊 Valid wind speed records: {len(wind_speed_values)}/{len(weather_data)} ({len(wind_speed_values)/len(weather_data)*100:.1f}%)")
                    
                    if wind_gusts_values:
                        logger.info(f"  🌪️ Wind gusts range: {min(wind_gusts_values):.1f} → {max(wind_gusts_values):.1f} km/h")
                        logger.info(f"  📊 Valid wind gusts records: {len(wind_gusts_values)}/{len(weather_data)} ({len(wind_gusts_values)/len(weather_data)*100:.1f}%)")
                    
                    if wind_direction_values:
                        logger.info(f"  🧭 Wind direction range: {min(wind_direction_values):.0f}° → {max(wind_direction_values):.0f}°")
                        logger.info(f"  📊 Valid wind direction records: {len(wind_direction_values)}/{len(weather_data)} ({len(wind_direction_values)/len(weather_data)*100:.1f}%)")
                    
                    # Temperature analysis
                    temp_max_values = [r.get('temperature_2m_max') for r in weather_data if r.get('temperature_2m_max') is not None]
                    if temp_max_values:
                        logger.info(f"  🌡️ Temperature range: {min(temp_max_values):.1f}°C → {max(temp_max_values):.1f}°C")
                        logger.info(f"  📊 Valid temp records: {len(temp_max_values)}/{len(weather_data)} ({len(temp_max_values)/len(weather_data)*100:.1f}%)")
                
                # Sikeres lekérdezés kezelése
                self._handle_successful_request(attempt_provider, selected_provider)
                
                # Provider usage tracking
                self.provider_usage_stats[attempt_provider] = self.provider_usage_stats.get(attempt_provider, 0) + 1
                log_provider_usage_event(attempt_provider, "weather_data", True)
                
                logger.info(f"🎉 SUCCESS: {len(weather_data)} nap ({get_source_display_name(attempt_provider)})")
                
                # 🔧 KRITIKUS JAVÍTÁS v4.5: EGYSÉGES VISSZATÉRÉS - CSAK List[Dict]!
                return weather_data  # ✅ Nincs tuple, csak tiszta lista!
                
            except (WeatherAPIError, ProviderValidationError) as e:
                last_error = e
                logger.error(f"❌ PROVIDER FAILED: {attempt_provider} - {e}")
                log_provider_usage_event(attempt_provider, "weather_data", False)
                continue
        
        # Minden provider sikertelen
        logger.error(f"❌ ALL PROVIDERS FAILED. Last error: {last_error}")
        raise ProviderNotAvailableError(f"Minden provider sikertelen. Utolsó hiba: {last_error}")
    
    def _select_provider(self, user_override: Optional[str] = None) -> Optional[str]:
        if user_override:
            if user_override in self.providers and self.providers[user_override].validate_provider():
                logger.info(f"👤 USER OVERRIDE: {get_source_display_name(user_override)}")
                return user_override
            else:
                logger.warning(f"⚠️ USER OVERRIDE FAILED: {user_override}")
        
        if self.preferred_provider == "auto":
            optimal = get_optimal_data_source("single_city", prefer_free=True)
            if optimal in self.providers and self.providers[optimal].validate_provider():
                logger.info(f"🤖 AUTO SELECTED: {optimal}")
                return optimal
            
            for provider_id, provider in self.providers.items():
                if provider.validate_provider():
                    logger.info(f"🔄 FALLBACK SELECTED: {provider_id}")
                    return provider_id
            
            return None
        else:
            if self.preferred_provider in self.providers:
                if self.providers[self.preferred_provider].validate_provider():
                    return self.preferred_provider
                else:
                    logger.warning(f"⚠️ PREFERRED FAILED, AUTO FALLBACK: {self.preferred_provider}")
                    return self._select_provider(None)
            else:
                logger.error(f"❌ UNKNOWN PREFERRED: {self.preferred_provider}")
                return None
    
    def _get_provider_fallback_chain(self, primary_provider: str) -> List[str]:
        available_providers = [
            provider_id for provider_id, provider in self.providers.items()
            if provider.validate_provider()
        ]
        
        if primary_provider in available_providers:
            available_providers.remove(primary_provider)
            available_providers.insert(0, primary_provider)
        
        return available_providers
    
    def _retry_weather_request(self, provider: WeatherProvider, latitude: float, longitude: float,
                              start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        🔧 JAVÍTÁS v4.5: MINDIG List[Dict] visszatérés
        """
        logger.info(f"🔄 STARTING RETRY SEQUENCE for {provider.provider_id}")
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 ATTEMPT {attempt + 1}/{self.max_retries}")
                result = provider.get_weather_data(latitude, longitude, start_date, end_date)
                logger.info(f"✅ ATTEMPT SUCCESS: {len(result)} records")
                return result
            
            except WeatherAPIError as e:
                logger.error(f"❌ ATTEMPT {attempt + 1} FAILED: {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (attempt + 1)
                    logger.info(f"⏳ RETRYING in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"❌ MAX RETRIES REACHED")
                    raise
        
        return []
    
    def _handle_successful_request(self, used_provider: str, requested_provider: str) -> None:
        self.current_provider = used_provider
        
        if used_provider != requested_provider:
            if self.provider_fallback_callback:
                self.provider_fallback_callback(requested_provider, used_provider)
        
        if used_provider != self.preferred_provider and self.preferred_provider != "auto":
            if self.provider_change_callback:
                self.provider_change_callback(self.preferred_provider, used_provider)
    
    def _validate_inputs(self, latitude: float, longitude: float, start_date: str, end_date: str) -> None:
        if not (-90 <= latitude <= 90):
            raise ValueError("Érvénytelen szélesség: -90 és 90 között kell lennie")
        
        if not (-180 <= longitude <= 180):
            raise ValueError("Érvénytelen hosszúság: -180 és 180 között kell lennie")
        
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Érvénytelen dátum formátum - YYYY-MM-DD szükséges")
        
        if start_dt > end_dt:
            raise ValueError("Kezdő dátum nem lehet nagyobb, mint a befejező dátum")
    
    # Provider management methods
    def set_preferred_provider(self, provider: str) -> None:
        if provider == "auto" or provider in self.providers:
            self.preferred_provider = provider
            logger.info(f"Preferred provider változott: {get_source_display_name(provider)}")
        else:
            raise ValueError(f"Ismeretlen provider: {provider}")
    
    def get_current_provider(self) -> Optional[str]:
        return self.current_provider
    
    def get_available_providers(self) -> List[str]:
        return [
            provider_id for provider_id, provider in self.providers.items()
            if provider.validate_provider()
        ]
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        status = {}
        
        for provider_id, provider in self.providers.items():
            available = provider.validate_provider()
            status[provider_id] = {
                "display_name": provider.display_name,
                "available": available,
                "request_count": provider.get_request_count(),
                "usage_count": self.provider_usage_stats.get(provider_id, 0),
                "is_current": self.current_provider == provider_id
            }
        
        return status
    
    def reset_provider_usage_stats(self) -> None:
        self.provider_usage_stats.clear()
        for provider in self.providers.values():
            provider.reset_request_count()
        logger.info("Provider usage stats reset")
    
    # 🔧 BACKWARD COMPATIBILITY methods - JAVÍTOTT VERZIÓ
    def get_current_weather(self, latitude: float, longitude: float,
                          user_override_provider: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        🔧 JAVÍTÁS v4.5: Backward compatibility megőrizve 
        
        Ez a metódus még mindig tuple-t ad vissza a kompatibilitás miatt,
        de belül az új egységes API-t használja.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        try:
            weather_data = self.get_weather_data(
                latitude, longitude, today, today, user_override_provider
            )
            
            if weather_data:
                source = weather_data[0].get('data_source', 'unknown')
                return (weather_data[0], source)
            return (None, "no_data")
            
        except Exception as e:
            logger.error(f"Hiba aktuális időjárás lekérdezésénél: {e}")
            return (None, "error")
    
    def get_weather_for_date_range(self, latitude: float, longitude: float,
                                  days_back: int = 7,
                                  user_override_provider: Optional[str] = None) -> Tuple[List[Dict[str, Any]], str]:
        """
        🔧 JAVÍTÁS v4.5: Backward compatibility megőrizve
        
        Ez a metódus még mindig tuple-t ad vissza a kompatibilitás miatt,
        de belül az új egységes API-t használja.
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        weather_data = self.get_weather_data(
            latitude, longitude,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            user_override_provider
        )
        
        # Source kinyerése az első rekordból
        source = weather_data[0].get('data_source', 'unknown') if weather_data else 'no_data'
        
        return (weather_data, source)


if __name__ == "__main__":
    # 🔥 MULTI-YEAR Test v4.6
    logger.info("🔥 STARTING MULTI-YEAR TEST v4.6 (SZÉLIRÁNY JAVÍTÁS)")
    
    client = WeatherClient(preferred_provider="auto")
    
    # Test 5 year trend
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=5*365)).strftime("%Y-%m-%d")
    
    logger.info(f"🔥 TESTING MULTI-YEAR: {start_date} → {end_date}")
    
    try:
        # 🔧 JAVÍTÁS v4.5: EGYSÉGES API - csak List[Dict] visszatérés
        weather_data = client.get_weather_data(47.4979, 19.0402, start_date, end_date)
        logger.info(f"🔥 MULTI-YEAR TEST RESULT: {len(weather_data)} records")
        
        if weather_data:
            first_record = weather_data[0]
            last_record = weather_data[-1]
            source = first_record.get('data_source', 'unknown')
            logger.info(f"🔥 DATE RANGE: {first_record.get('date')} → {last_record.get('date')}")
            logger.info(f"🔥 DATA SOURCE: {source}")
            
            # ✅ JAVÍTOTT: Szél adatok ellenőrzése + SZÉLIRÁNY
            wind_speed_count = sum(1 for r in weather_data if r.get('windspeed_10m_max') is not None)
            wind_gusts_count = sum(1 for r in weather_data if r.get('windgusts_10m_max') is not None)
            wind_direction_count = sum(1 for r in weather_data if r.get('winddirection_10m_dominant') is not None)
            logger.info(f"🔥 WIND DATA: speed={wind_speed_count}, gusts={wind_gusts_count}, direction={wind_direction_count}")
        
    except Exception as e:
        logger.error(f"🔥 MULTI-YEAR TEST FAILED: {e}")
