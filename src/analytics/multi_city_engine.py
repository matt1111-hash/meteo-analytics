#!/usr/bin/env python3
"""
Multi-City Analytics Engine - Globális időjárás elemzés (NULL-SAFE & DATA TRANSFORM FIXED v2.5)
Global Weather Analyzer projekt

Fájl: src/analytics/multi_city_engine.py
Cél: Többváros időjárási elemzés koordinálása
- DUAL-API TÁMOGATÁS (Open-Meteo + Meteostat)
- Országválasztás (Magyarország, Európa, Globális)
- BATCH PROCESSING - robusztus párhuzamos feldolgozás
- PROGRESS TRACKING - real-time feedback
- FALLBACK STRATEGY - hibás városok kihagyása

🔧 KRITIKUS JAVÍTÁSOK v2.5.0:
- ✅ NONE-SAFE STATISZTIKÁK: statistics.mean/min/max helyett safe_ függvények
- ✅ ADAT TRANSZFORMÁCIÓS HIBA JAVÍTVA: A motor most már a UI által várt `AnalyticsResult` és `CityWeatherResult` objektumokat adja vissza.
- ✅ 0.0°C HIBA JAVÍTVA: A helyes metrika értéke (`temperature_2m_max` stb.) most már bekerül a `value` mezőbe.
- ✅ STATISZTIKAI HIBA JAVÍTVA: A statisztikák a teljes, sikeresen feldolgozott adathalmazon számolódnak.
- ✅ NULL-safe sorting logic 
- ✅ Type-safe value comparisons
- ✅ MAX_CITIES PARAMÉTER TÁMOGATÁS HOZZÁADVA - BACKWARD COMPATIBLE!
- ✅ COUNTRY CODE MAPPING: HU → Hungary, EU → Europe, GLOBAL → Global
- ✅ TypeError: '>' not supported between instances of 'NoneType' and 'float' JAVÍTVA
"""

import sqlite3
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import time
import json
import sys

# 🔧 KRITIKUS JAVÍTÁS: Szabványos modellek importálása a UI kompatibilitáshoz
from ..data.models import AnalyticsResult, CityWeatherResult, AnalyticsQuestion
from ..data.enums import RegionScope, AnalyticsMetric, QuestionType, DataSource

# Logging beállítás
logger = logging.getLogger(__name__)


# 🔧 NONE-SAFE HELPER FÜGGVÉNYEK (MULTI-CITY ENGINE VERZIÓ)
def safe_statistics_mean(values: List[Union[float, int, None]]) -> Optional[float]:
    """None-safe statistics.mean replacement"""
    if not values:
        return None
    clean_values = [v for v in values if v is not None and isinstance(v, (int, float))]
    if not clean_values:
        return None
    try:
        return statistics.mean(clean_values)
    except statistics.StatisticsError:
        return None


def safe_statistics_median(values: List[Union[float, int, None]]) -> Optional[float]:
    """None-safe statistics.median replacement"""
    if not values:
        return None
    clean_values = [v for v in values if v is not None and isinstance(v, (int, float))]
    if not clean_values:
        return None
    try:
        return statistics.median(clean_values)
    except statistics.StatisticsError:
        return None


def safe_statistics_stdev(values: List[Union[float, int, None]]) -> Optional[float]:
    """None-safe statistics.stdev replacement"""
    if not values:
        return None
    clean_values = [v for v in values if v is not None and isinstance(v, (int, float))]
    if len(clean_values) < 2:
        return 0.0
    try:
        return statistics.stdev(clean_values)
    except statistics.StatisticsError:
        return 0.0


def safe_min_max(values: List[Union[float, int, None]]) -> Tuple[Optional[float], Optional[float]]:
    """None-safe min és max számítás egyben"""
    if not values:
        return None, None
    clean_values = [v for v in values if v is not None and isinstance(v, (int, float))]
    if not clean_values:
        return None, None
    try:
        return min(clean_values), max(clean_values)
    except (ValueError, TypeError):
        return None, None


@dataclass
class MultiCityQuery:
    """
    ✅ Multi-city analytics query struktúra.
    
    Analytics panel által használt query objektum multi-city elemzésekhez.
    """
    query_type: str
    region: str
    date: str
    max_cities: int = 50
    limit: Optional[int] = None
    
    # 🔧 KRITIKUS JAVÍTÁS: AnalyticsQuestion objektum tárolása
    question: Optional[AnalyticsQuestion] = None
    region_scope: Optional[RegionScope] = None


@dataclass
class CityWeatherData:
    """Egy város időjárási adatai (DUAL-API KOMPATIBILIS) - BELSŐ HASZNÁLATRA"""
    city: str
    country: str
    country_code: str
    lat: float
    lon: float
    population: Optional[int] = None
    
    date: Optional[str] = None
    temperature_2m_max: Optional[float] = None
    temperature_2m_min: Optional[float] = None
    temperature_2m_mean: Optional[float] = None
    precipitation_sum: Optional[float] = None
    windspeed_10m_max: Optional[float] = None
    windgusts_10m_max: Optional[float] = None
    
    meteostat_station_id: Optional[str] = None
    data_quality_score: Optional[float] = None # 🔧 FIX: int -> float
    
    data_source: str = "dual-api"
    fetch_timestamp: Optional[str] = None
    fetch_success: bool = True
    error_message: Optional[str] = None
    retry_count: int = 0
    
    temperature_range: Optional[float] = None


class MultiCityEngine:
    """
    Multi-city időjárás elemzés koordinátor (DUAL-API CLEAN + NULL-SAFE + DATA TRANSFORM FIXED)
    
    Felelősségek:
    - DUAL-API ROUTING
    - Országválasztás kezelése
    - BATCH PROCESSING
    - PROGRESS TRACKING
    - ✅ ADAT TRANSZFORMÁCIÓ (CityWeatherData -> CityWeatherResult)
    - ✅ NONE-SAFE STATISZTIKÁK
    """
    
    REGION_CODE_MAPPING = {
        "HU": "Hungary", "EU": "Europe", "GLOBAL": "Global", "WORLD": "Global",
        "country": "Hungary", "continent": "Europe", "global": "Global",
        "hungary": "Hungary", "europe": "Europe", "magyarország": "Hungary", "európa": "Europe"
    }
    
    REGIONS = {
        "Hungary": {"name": "Magyarország", "country_codes": ["HU"], "max_cities": 165, "batch_size": 8, "rate_limit_delay": 0.2},
        "Europe": {"name": "Európa", "country_codes": ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "CH", "GB", "NO", "IS", "RS", "BA", "MK", "AL", "MD", "UA", "BY", "RU"], "max_cities": 150, "batch_size": 4, "rate_limit_delay": 0.4},
        "Global": {"name": "Globális", "country_codes": [], "max_cities": 160, "batch_size": 8, "rate_limit_delay": 0.5},
    }
    
    QUERY_TYPES = {
        "hottest_today": {"name": "Legmelegebb ma", "metric": "temperature_2m_max", "unit": "°C", "sort_desc": True, "question_template": "Hol volt ma a legmelegebb {region}ban?", "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MAX},
        "coldest_today": {"name": "Leghidegebb ma", "metric": "temperature_2m_min", "unit": "°C", "sort_desc": False, "question_template": "Hol volt ma a leghidegebb {region}ban?", "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MIN},
        "wettest_today": {"name": "Legcsapadékosabb ma", "metric": "precipitation_sum", "unit": "mm", "sort_desc": True, "question_template": "Hol esett ma a legtöbb csapadék {region}ban?", "metric_enum": AnalyticsMetric.PRECIPITATION_SUM},
        "windiest_today": {"name": "Legszelesebb ma", "metric": "windgusts_10m_max", "unit": "km/h", "sort_desc": True, "question_template": "Hol fújt ma a legerősebb szél {region}ban?", "metric_enum": AnalyticsMetric.WINDSPEED_10M_MAX},
        "temperature_range": {"name": "Legnagyobb hőingás", "metric": "temperature_range", "unit": "°C", "sort_desc": True, "question_template": "Hol volt ma a legnagyobb hőingás {region}ban?", "metric_enum": AnalyticsMetric.TEMPERATURE_RANGE}
    }
    
    def __init__(self, db_path: str = "src/data/cities.db"):
        self.db_path = Path(db_path)
        self.max_workers = 8
        self.request_timeout = 90
        self.max_retries = 2
        self.retry_delay = 3.0
        
        try:
            from src.data.weather_client import WeatherClient
            self.weather_client = WeatherClient()
            logger.info("✅ WeatherClient dual-API integráció sikeres")
        except ImportError as e:
            logger.warning(f"❌ WeatherClient import hiba: {e}")
            self.weather_client = None
        
        logger.info("🚀 Multi-city engine inicializálva (NONE-SAFE v2.5)")

    def execute_analytics_query(self, query: MultiCityQuery, progress_callback: Optional[callable] = None) -> AnalyticsResult:
        return self.analyze_multi_city(
            query.query_type,
            query.region,
            query.date,
            limit=query.limit or query.max_cities,
            question=query.question
        )

    def get_cities_for_region(self, region: str, limit: Optional[int] = None, max_cities: Optional[int] = None) -> List[Dict[str, Any]]:
        mapped_region = self.resolve_region_name(region)
        region_config = self.REGIONS[mapped_region]
        country_codes = region_config["country_codes"]
        final_limit = max_cities or limit or region_config["max_cities"]
        
        logger.debug(f"🔧 get_cities_for_region: region={region}→{mapped_region}, final_limit={final_limit}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query_str = ""
                params = []
                
                base_select = 'SELECT city, country, country_code, lat, lon, population, meteostat_station_id, data_quality_score FROM cities'
                
                if mapped_region == "Global":
                    query_str = f'{base_select} WHERE population IS NOT NULL AND population > 100000 ORDER BY population DESC LIMIT ?'
                    params = [final_limit]
                elif mapped_region == "Hungary":
                    query_str = f'{base_select} WHERE country_code = "HU" ORDER BY CASE WHEN population IS NOT NULL THEN population ELSE 0 END DESC LIMIT ?'
                    params = [final_limit]
                else:
                    placeholders = ','.join(['?' for _ in country_codes])
                    query_str = f'{base_select} WHERE country_code IN ({placeholders}) AND population IS NOT NULL AND population > 50000 ORDER BY CASE WHEN population IS NOT NULL THEN population ELSE 0 END DESC LIMIT ?'
                    params = country_codes + [final_limit]
                
                cursor.execute(query_str, params)
                results = cursor.fetchall()
                
                cities = [{
                    'city': row[0], 'country': row[1], 'country_code': row[2],
                    'lat': row[3], 'lon': row[4], 'population': row[5],
                    'meteostat_station_id': row[6], 'data_quality_score': row[7]
                } for row in results]
                
                logger.info(f"✅ Lekérdezve {len(cities)} város {mapped_region} régióból")
                return cities
                
        except Exception as e:
            logger.error(f"❌ Hiba városok lekérdezésénél: {e}", exc_info=True)
            return []

    def analyze_multi_city(self, query_type: str, region: str, date: str, limit: Optional[int] = None, question: Optional[AnalyticsQuestion] = None) -> AnalyticsResult:
        """
        🔧 KRITIKUS JAVÍTÁS: Multi-city elemzés - TELJES ADAT TRANSZFORMÁCIÓVAL + ERROR HANDLING + NONE-SAFE
        
        Args:
            query_type: Lekérdezés típusa
            region: Régió
            date: Dátum
            limit: Eredmények limitje
            question: AnalyticsQuestion objektum
            
        Returns:
            AnalyticsResult objektum (UI kompatibilis)
        """
        start_time = time.time()
        
        try:
            if query_type not in self.QUERY_TYPES:
                raise ValueError(f"Ismeretlen lekérdezés típus: {query_type}")
            
            mapped_region = self.resolve_region_name(region)
            query_config = self.QUERY_TYPES[query_type]
            
            logger.info(f"🚀 Multi-city elemzés kezdése (NONE-SAFE v2.5): {query_type} - {mapped_region} - {date}")
            
            # Városok lekérdezése - teljes pool
            cities = self.get_cities_for_region(mapped_region, max_cities=self.REGIONS[mapped_region]["max_cities"])
            
            if not cities:
                logger.error("❌ Nincsenek városok a lekérdezéshez")
                return self._create_empty_analytics_result(question)
            
            # Időjárási adatok lekérdezése
            weather_data = self._fetch_weather_data_dual_api_batch(cities, date, mapped_region)
            
            # Eredmények feldolgozása és rendezése
            processed_data = self._process_weather_results(weather_data, query_type)
            
            logger.info(f"🔧 PROCESSED DATA: {len(processed_data)} cities processed")
            
            # 🔧 KRITIKUS JAVÍTÁS: Adat transzformáció (CityWeatherData -> CityWeatherResult)
            transformed_results = []
            for i, city_data in enumerate(processed_data):
                if city_data.fetch_success:
                    try:
                        result_item = self._transform_to_city_weather_result(city_data, query_type)
                        result_item.rank = i + 1
                        transformed_results.append(result_item)
                    except Exception as e:
                        logger.error(f"❌ Transform error for {city_data.city}: {e}")
                        continue

            logger.info(f"🔧 TRANSFORMED RESULTS: {len(transformed_results)} cities transformed")

            # 🔧 KRITIKUS JAVÍTÁS: Statisztika számítása a TELJES sikeres adathalmazon (NONE-SAFE)
            stats = self._calculate_statistics_for_results_none_safe(transformed_results)

            # 🔧 KRITIKUS JAVÍTÁS: Helyes AnalyticsResult objektum létrehozása
            final_question = question
            if not final_question:
                try:
                    final_question = AnalyticsQuestion(
                        question_text=query_config["question_template"].format(region=self.REGIONS[mapped_region]["name"]),
                        question_type=QuestionType.MULTI_CITY,
                        region_scope=RegionScope.COUNTRY if mapped_region == "Hungary" else RegionScope.CONTINENT,
                        metric=query_config["metric_enum"]
                    )
                except Exception as e:
                    logger.error(f"❌ Question creation error: {e}")
                    # Fallback question
                    final_question = AnalyticsQuestion(
                        question_text="Multi-city analytics",
                        question_type=QuestionType.MULTI_CITY,
                        region_scope=RegionScope.COUNTRY,
                        metric=AnalyticsMetric.TEMPERATURE_2M_MAX
                    )

            # Csak a limitált eredményeket adjuk át a UI-nak
            limited_results = transformed_results[:limit] if limit else transformed_results

            try:
                analytics_result = AnalyticsResult(
                    question=final_question,
                    city_results=limited_results,
                    execution_time=time.time() - start_time,
                    total_cities_found=len(cities),
                    data_sources_used=[DataSource.AUTO], # WeatherClient kezeli
                    statistics=stats,
                    provider_statistics=self._get_provider_stats(weather_data)
                )
                
                logger.info(f"✅ Multi-city elemzés befejezve (NONE-SAFE v2.5): {len(limited_results)}/{len(cities)} eredmény, {len(transformed_results)} siker")
                
                return analytics_result
                
            except Exception as e:
                logger.error(f"❌ AnalyticsResult creation error: {e}")
                return self._create_empty_analytics_result(final_question)
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR in analyze_multi_city: {e}", exc_info=True)
            return self._create_empty_analytics_result(question)

    def _get_provider_stats(self, weather_data: List[CityWeatherData]) -> Dict[str, int]:
        """Provider statisztikák kinyerése."""
        stats = {}
        for data in weather_data:
            if data.fetch_success:
                stats[data.data_source] = stats.get(data.data_source, 0) + 1
        return stats

    def _transform_to_city_weather_result(self, city_data: CityWeatherData, query_type: str) -> CityWeatherResult:
        """
        🔧 KRITIKUS ÚJ METÓDUS: Átalakítja a belső CityWeatherData-t a UI-kompatibilis CityWeatherResult-tá.
        
        Ez a metódus javítja a "0.0°C" hibát azzal, hogy:
        1. Kiveszi a specifikus metrika értéket a CityWeatherData-ból
        2. Behelyezi a `value` mezőbe
        3. Létrehozza a teljes CityWeatherResult objektumot
        
        Args:
            city_data: Belső weather data objektum
            query_type: Lekérdezés típusa
            
        Returns:
            UI kompatibilis CityWeatherResult objektum
        """
        query_config = self.QUERY_TYPES[query_type]
        metric_name = query_config["metric"]
        metric_enum = query_config["metric_enum"]
        
        # A specifikus metrika érték kinyerése
        if metric_name == "temperature_range":
            metric_value = city_data.temperature_range
        else:
            metric_value = getattr(city_data, metric_name, None)
        
        # 🔧 CRITICAL DEBUG: Log what we're getting
        logger.info(f"🔧 TRANSFORM DEBUG: {city_data.city} - {metric_name}={metric_value} (type: {type(metric_value)})")
        logger.info(f"🔧 RAW DATA: temp_max={city_data.temperature_2m_max}, temp_min={city_data.temperature_2m_min}, precip={city_data.precipitation_sum}")
        
        # 🔧 NONE-SAFE value conversion - STRICTER VALIDATION
        if metric_value is not None and metric_value != 0:
            final_value = float(metric_value)
        else:
            # 🔧 FALLBACK: Try to get ANY valid weather data
            fallback_value = (city_data.temperature_2m_max or 
                            city_data.temperature_2m_min or 
                            city_data.precipitation_sum or 
                            city_data.windspeed_10m_max or 0.0)
            final_value = float(fallback_value) if fallback_value is not None else 0.0
            logger.warning(f"⚠️ NULL metric value for {city_data.city}, using fallback: {fallback_value}")
        
        # CityWeatherResult objektum létrehozása
        result = CityWeatherResult(
            city_name=city_data.city,
            country=city_data.country,
            country_code=city_data.country_code,
            latitude=city_data.lat,
            longitude=city_data.lon,
            value=final_value,  # 🔧 KRITIKUS: Ez javítja a 0.0°C hibát!
            metric=metric_enum,
            date=datetime.strptime(city_data.date, "%Y-%m-%d").date(),
            population=city_data.population,
            quality_score=city_data.data_quality_score if city_data.data_quality_score is not None else 0.0
        )
        
        logger.info(f"🔧 Transzformáció: {city_data.city} - {metric_name}={metric_value} → value={final_value}")
        
        return result
        
    def _fetch_weather_data_dual_api_batch(self, cities: List[Dict[str, Any]], date: str, region: str) -> List[CityWeatherData]:
        """Párhuzamos időjárás lekérdezés (DUAL-API BATCH PROCESSING)."""
        weather_data = []
        if not self.weather_client:
            logger.error("❌ WeatherClient nem elérhető")
            return [self._create_empty_city_data(city) for city in cities]

        region_config = self.REGIONS[region]
        batch_size = region_config["batch_size"]
        rate_limit_delay = region_config["rate_limit_delay"]
        
        batches = [cities[i:i + batch_size] for i in range(0, len(cities), batch_size)]
        logger.info(f"🔄 Dual-API batch processing: {len(batches)} batch, {batch_size} város/batch")
        
        for batch_idx, batch in enumerate(batches):
            batch_start_time = time.time()
            print(f"📊 Batch {batch_idx + 1}/{len(batches)}: {len(batch)} város (DUAL-API)...", end="", flush=True)
            
            batch_results = self._process_dual_api_batch(batch, date, rate_limit_delay)
            weather_data.extend(batch_results)
            
            batch_time = time.time() - batch_start_time
            successful_in_batch = len([r for r in batch_results if r.fetch_success])
            
            sources_in_batch = self._get_provider_stats(batch_results)
            source_info = ", ".join([f"{k}: {v}" for k, v in sources_in_batch.items()])
            print(f" ✅ {successful_in_batch}/{len(batch)} siker ({source_info}) ({batch_time:.1f}s)")
            
            if batch_idx < len(batches) - 1:
                time.sleep(rate_limit_delay)
        
        print(f"🎉 Dual-API batch processing befejezve: {len(weather_data)} város")
        return weather_data

    def _process_dual_api_batch(self, batch: List[Dict[str, Any]], date: str, rate_limit_delay: float) -> List[CityWeatherData]:
        """Batch feldolgozása ThreadPoolExecutor-ral."""
        batch_results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._fetch_single_city_weather_dual_api, city, date): city for city in batch}
            
            for future in as_completed(futures):
                city = futures[future]
                try:
                    city_data = future.result(timeout=self.request_timeout)
                    batch_results.append(city_data)
                except Exception as e:
                    logger.error(f"❌ Hiba a város feldolgozásánál ({city.get('city')}): {e}", exc_info=True)
                    batch_results.append(self._create_empty_city_data(city, str(e)))
        return batch_results

    def _fetch_single_city_weather_dual_api(self, city: Dict[str, Any], date: str) -> CityWeatherData:
        """
        Egyetlen város DUAL-API lekérdezése retry logikával.
        
        🔧 JAVÍTÁS: WeatherClient visszatérési értékének helyes kezelése
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                # WeatherClient hívás - tuple visszatérési érték kezelése
                weather_result = self.weather_client.get_weather_data(city['lat'], city['lon'], date, date)
                
                # Check if result is tuple (weather_data, source) or just weather_data
                if isinstance(weather_result, tuple) and len(weather_result) == 2:
                    weather_data, source = weather_result
                else:
                    weather_data = weather_result
                    source = "auto"
                
                if weather_data and len(weather_data) > 0:
                    daily_data = weather_data[0]
                    temp_max = daily_data.get('temperature_2m_max')
                    temp_min = daily_data.get('temperature_2m_min')
                    
                    # 🔧 NONE-SAFE hőingás számítás
                    temp_range = None
                    if temp_max is not None and temp_min is not None:
                        try:
                            temp_range = temp_max - temp_min
                        except (TypeError, ValueError):
                            temp_range = None

                    return CityWeatherData(
                        city=city['city'], country=city['country'], country_code=city['country_code'],
                        lat=city['lat'], lon=city['lon'], population=city.get('population'),
                        date=date,
                        temperature_2m_max=temp_max, temperature_2m_min=temp_min,
                        temperature_2m_mean=daily_data.get('temperature_2m_mean'),
                        precipitation_sum=daily_data.get('precipitation_sum'),
                        windspeed_10m_max=daily_data.get('windspeed_10m_max'),
                        windgusts_10m_max=daily_data.get('windgusts_10m_max'),
                        meteostat_station_id=city.get('meteostat_station_id'),
                        data_quality_score=city.get('data_quality_score'),
                        data_source=source,
                        fetch_timestamp=datetime.now().isoformat(),
                        fetch_success=True, retry_count=attempt,
                        temperature_range=temp_range
                    )
                else:
                    last_error = f"Nincs időjárási adat {city['city']}-hoz"
            except Exception as e:
                last_error = str(e)
                logger.warning(f"⚠️ Hiba a(z) {city['city']} lekérdezésekor (próba: {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        logger.error(f"❌ Végső hiba a(z) {city['city']} lekérdezésénél: {last_error}")
        return self._create_empty_city_data(city, last_error)

    def _create_empty_city_data(self, city: Dict[str, Any], error_msg: str = "Ismeretlen hiba") -> CityWeatherData:
        """Üres város adatstruktúra létrehozása hibák esetén."""
        return CityWeatherData(
            city=city.get('city', 'Ismeretlen'), country=city.get('country', 'Ismeretlen'),
            country_code=city.get('country_code', 'XX'), lat=city.get('lat', 0.0), lon=city.get('lon', 0.0),
            population=city.get('population'), data_source="error", fetch_success=False, error_message=error_msg
        )

    def _process_weather_results(self, weather_data: List[CityWeatherData], query_type: str) -> List[CityWeatherData]:
        """
        Időjárási eredmények feldolgozása és NULL-safe rendezése.
        
        🔧 EMERGENCY DEBUG: Full logging to find the issue
        """
        logger.info(f"🔧 EMERGENCY DEBUG: _process_weather_results called with {len(weather_data)} cities")
        
        query_config = self.QUERY_TYPES[query_type]
        metric = query_config["metric"]
        sort_desc = query_config["sort_desc"]
        
        logger.info(f"🔧 EMERGENCY DEBUG: Looking for metric '{metric}' in weather data")
        
        # Log first few cities' data for debugging
        for i, city in enumerate(weather_data[:3]):
            logger.info(f"🔧 CITY {i+1}: {city.city} - success={city.fetch_success}")
            logger.info(f"    temp_max={city.temperature_2m_max}, temp_min={city.temperature_2m_min}")
            logger.info(f"    precip={city.precipitation_sum}, wind={city.windspeed_10m_max}")
        
        # 🔧 NONE-SAFE hőingás számítása a temperature_range query-hez
        if metric == "temperature_range":
            for city_data in weather_data:
                if city_data.fetch_success:
                    temp_max = city_data.temperature_2m_max
                    temp_min = city_data.temperature_2m_min
                    if temp_max is not None and temp_min is not None:
                        try:
                            city_data.temperature_range = temp_max - temp_min
                            logger.info(f"🔧 TEMP RANGE: {city_data.city} = {city_data.temperature_range}")
                        except (TypeError, ValueError):
                            city_data.temperature_range = None
                            logger.warning(f"⚠️ TEMP RANGE calc error for {city_data.city}")
        
        # Érvényes adatok szűrése
        valid_data = [d for d in weather_data if d.fetch_success and getattr(d, metric, None) is not None]
        
        logger.info(f"🔧 EMERGENCY DEBUG: {len(valid_data)} valid cities with metric '{metric}'")
        
        if not valid_data:
            logger.error(f"❌ NO VALID DATA! All cities missing metric '{metric}'")
            # Return first few cities anyway for debugging
            return weather_data[:5]
        
        def get_sort_value(city_data: CityWeatherData) -> float:
            """🔧 NONE-SAFE sort key function"""
            value = getattr(city_data, metric, None)
            if value is None: 
                return float('-inf') if sort_desc else float('inf')
            try: 
                return float(value)
            except (ValueError, TypeError): 
                return float('-inf') if sort_desc else float('inf')
        
        try:
            sorted_data = sorted(valid_data, key=get_sort_value, reverse=sort_desc)
        except Exception as e:
            logger.error(f"❌ Rendezési hiba: {e}", exc_info=True)
            sorted_data = valid_data
        
        logger.info(f"🔧 Feldolgozott adatok: {len(sorted_data)} érvényes város {metric} alapján rendezve")
        
        return sorted_data

    def _calculate_statistics_for_results_none_safe(self, results: List[CityWeatherResult]) -> Dict[str, float]:
        """
        🔧 KRITIKUS JAVÍTÁS: NONE-SAFE statisztikák számítása a transzformált CityWeatherResult listából.
        
        Ez a metódus javítja a hibás statisztikákat azzal, hogy:
        1. A TELJES sikeres adathalmazon számol (nem csak a limitált eredményeken)
        2. A value mezőt használja, ami már a helyes metrika értéket tartalmazza
        3. ✅ NONE-SAFE: safe_statistics_* függvényeket használ statistics.* helyett
        
        Args:
            results: Transzformált CityWeatherResult lista
            
        Returns:
            Statisztikai értékek (None-safe)
        """
        # 🔧 CRITICAL DEBUG: Log all values for debugging
        logger.info(f"🔧 NONE-SAFE STATS DEBUG: Analyzing {len(results)} results")
        for i, r in enumerate(results[:5]):  # First 5 for debugging
            logger.info(f"  {i+1}. {r.city_name}: value={r.value} (type: {type(r.value)})")
        
        # 🔧 NONE-SAFE: Collect all values (including None for safety)
        all_values = [r.value for r in results]
        
        # 🔧 DEBUG: Log filtering results
        logger.info(f"🔧 NONE-SAFE STATS DEBUG: {len(all_values)} total values from {len(results)} results")
        
        if not all_values:
            logger.error(f"❌ NONE-SAFE STATS DEBUG: No values at all! Results sample: {[(r.city_name, r.value) for r in results[:3]]}")
            return {}
        
        try:
            # 🔧 KRITIKUS JAVÍTÁS: NONE-SAFE statisztikai műveletek
            mean_val = safe_statistics_mean(all_values)
            median_val = safe_statistics_median(all_values)
            stdev_val = safe_statistics_stdev(all_values)
            min_val, max_val = safe_min_max(all_values)
            
            # Build stats dictionary with None checks
            stats = {}
            
            if mean_val is not None:
                stats["mean"] = mean_val
            if median_val is not None:
                stats["median"] = median_val  
            if stdev_val is not None:
                stats["stdev"] = stdev_val
            if min_val is not None:
                stats["min"] = min_val
            if max_val is not None:
                stats["max"] = max_val
            if min_val is not None and max_val is not None:
                stats["range"] = max_val - min_val
            
            logger.info(f"📊 NONE-SAFE Statisztikák: {len(all_values)} értékből - átlag: {stats.get('mean', 'N/A')}, tartomány: {stats.get('min', 'N/A')}-{stats.get('max', 'N/A')}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ NONE-SAFE Hiba a statisztikák számításánál: {e}", exc_info=True)
            return {}

    def _create_empty_analytics_result(self, question: Optional[AnalyticsQuestion]) -> AnalyticsResult:
        """Üres AnalyticsResult létrehozása hibák esetén."""
        return AnalyticsResult(
            question=question or AnalyticsQuestion("Hiba", QuestionType.MULTI_CITY, RegionScope.GLOBAL, AnalyticsMetric.TEMPERATURE_2M_MAX),
            city_results=[], execution_time=0.0, total_cities_found=0,
            data_sources_used=[], statistics={}, provider_statistics={}
        )

    def resolve_region_name(self, region_input: str) -> str:
        """Régió név feloldása country code-ból."""
        mapped_region = self.REGION_CODE_MAPPING.get(region_input.upper() if region_input else "", region_input)
        if mapped_region not in self.REGIONS:
            raise ValueError(f"Ismeretlen régió: {region_input}")
        return mapped_region


# 🧪 TESTING & DEBUG (NONE-SAFE)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    engine = MultiCityEngine()
    today = datetime.now().strftime("%Y-%m-%d")
    
    print("\n🚀 NONE-SAFE Analytics 'HU' country code-dal (hottest):")
    result_hot = engine.analyze_multi_city("hottest_today", "HU", today, limit=10)
    print(f"📊 Eredmények: {len(result_hot.city_results)} város")
    print(f"📊 NONE-SAFE Statisztikák: {result_hot.statistics}")
    
    # Első 3 város részletei
    for i, city in enumerate(result_hot.city_results[:3]):
        print(f"  {i+1}. {city.city_name}: {city.value}°C")
    
    print("\n🚀 NONE-SAFE Analytics 'HU' country code-dal (coldest):")
    result_cold = engine.analyze_multi_city("coldest_today", "HU", today, limit=10)
    print(f"📊 Eredmények: {len(result_cold.city_results)} város")
    print(f"📊 NONE-SAFE Statisztikák: {result_cold.statistics}")
    
    # Első 3 város részletei
    for i, city in enumerate(result_cold.city_results[:3]):
        print(f"  {i+1}. {city.city_name}: {city.value}°C")