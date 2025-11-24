#!/usr/bin/env python3
"""
Multi-City Analytics Engine - Globális időjárás elemzés (NULL-SAFE & DATA TRANSFORM FIXED v2.8.2 - DATABASE PATH ABSOLUTE FIX!)
Global Weather Analyzer projekt

Fájl: src/analytics/multi_city_engine.py
Cél: Többváros időjárási elemzés koordinálása
- DUAL-API TÁMOGATÁS (Open-Meteo + Meteostat)
- Országválasztás (Magyarország, Európa, Globális)
- BATCH PROCESSING - robusztus párhuzamos feldolgozás
- PROGRESS TRACKING - real-time feedback
- FALLBACK STRATEGY - hibás városok kihagyása

🔧 KRITIKUS JAVÍTÁSOK v2.8.2:
- ✅ ABSOLUTE DATABASE PATH FIX: Most már minden esetben megtalálja a data/ mappát!
- ✅ Path(__file__).parent.parent.parent használata a projekt root megkeresésére
- ✅ Working directory független működés
- ✅ Részletes path debugging minden inicializáláskor
- ✅ Fallback path logika ha a relatív utak nem működnek
- ✅ WINDSPEED METRIC JAVÍTVA: windgusts_10m_max → windspeed_10m_max (MEGBÍZHATÓBB!)
- ✅ windiest_today most windspeed_10m_max-ot használ windgusts_10m_max helyett
- ✅ RÉGIÓ SZŰRÉS IMPLEMENTÁLVA: get_cities_for_region() most már VALÓDI regionális szűrést csinál
- ✅ HUNGARIAN_REGIONAL_MAPPING: 7 statisztikai régió → megyék mapping
- ✅ "Észak-Magyarország" → Borsod-Abaúj-Zemplén, Heves, Nógrád megyék szűrése
- ✅ Database query optimalizálás: megye alapú WHERE feltétel
- ✅ RÉGIÓ MAPPING KIEGÉSZÍTVE: "Észak-Magyarország", "Dél-Magyarország", "Közép-Magyarország", stb.
- ✅ ERROR HANDLING JAVÍTVA: analyze_multi_city() mindig AnalyticsResult objektumot ad vissza dict helyett
- ✅ RESOLVE_REGION_NAME CATCH: Exception esetén fallback logic értelmezhetetlen régiókhoz
- ✅ MEGYÉK TÁMOGATÁSA: 19 magyar megye + Budapest mapping hozzáadva
- ✅ NONE-SAFE STATISZTIKÁK: statistics.mean/min/max helyett safe_ függvények
- ✅ ADAT TRANSZFORMÁCIÓS HIBA JAVÍTVA: A motor most már a UI által várt `AnalyticsResult` és `CityWeatherResult` objektumokat adja vissza.
- ✅ 0.0°C HIBA JAVÍTVA: A helyes metrika érték (`temperature_2m_max` stb.) most már bekerül a `value` mezőbe.
- ✅ STATISZTIKAI HIBA JAVÍTVA: A statisztikák a teljes, sikeresen feldolgozott adathalmazon számolódnak.
- ✅ NULL-safe sorting logic
- ✅ Type-safe value comparisons
- ✅ MAX_CITIES PARAMÉTER TÁMOGATÁS HOZZÁADVA - BACKWARD COMPATIBLE!
- ✅ COUNTRY CODE MAPPING: HU → Hungary, EU → Europe, GLOBAL → Global
- ✅ TypeError: '>' not supported between instances of 'NoneType' and 'float' JAVÍTVA
- 🔥 QUICKTYPE ENUM JAVÍTÁS: SINGLE_LOCATION/MULTI_CITY/COMPARISON → WEATHER_COMPARISON/TEMPERATURE_MAX
- 🔥 WINDSPEED METRIC JAVÍTÁS: windgusts_10m_max → windspeed_10m_max (ROBUSZTUSABB!)
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.application.use_cases.analyze_multi_city import AnalyzeMultiCityUseCase
from src.domain.analytics.models import CityWeatherData, MultiCityQuery
from src.domain.analytics.repositories import CityRepositoryProtocol
from src.domain.analytics.statistics import (
    safe_mean as _safe_mean,
    safe_median as _safe_median,
    safe_min_max as _safe_min_max,
    safe_stdev as _safe_stdev,
)
from src.infrastructure.repositories.city_repository import CityRepository
from src.domain.analytics.services import (
    AnalyticsTransformService,
    RegionResolverService,
    WeatherFetchService,
)
from ..data.enums import AnalyticsMetric, DataSource, QuestionType, RegionScope
from ..data.models import AnalyticsQuestion, AnalyticsResult, CityWeatherResult

Number = float | int
NumberOrNone = Number | None

# Logging beállítás
logger = logging.getLogger(__name__)


# 🔧 BACKWARD-COMPATIBILITY EXPORTS FOR LEGACY TESTS
def safe_mean(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_mean."""
    return _safe_mean(values)


def safe_statistics_mean(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_mean."""
    return safe_mean(values)


def safe_median(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_median."""
    return _safe_median(values)


def safe_statistics_median(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_median."""
    return safe_median(values)


def safe_stdev(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_stdev."""
    return _safe_stdev(values)


def safe_statistics_stdev(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_stdev."""
    return safe_stdev(values)


def safe_min_max(values: List[NumberOrNone]) -> Tuple[Optional[float], Optional[float]]:
    """Legacy wrapper → domain safe_min_max."""
    return _safe_min_max(values)


# 🔧 NONE-SAFE HELPER FÜGGVÉNYEK (MULTI-CITY ENGINE VERZIÓJA)
class MultiCityEngine:
    """
    Multi-city időjárás elemzés koordinátor (ABSOLUTE DATABASE PATH FIX v2.8.2 + DUAL-API CLEAN + NULL-SAFE + DATA TRANSFORM FIXED + RÉGIÓ/MEGYE MAPPING TELJES + RÉGIÓ SZŰRÉS JAVÍTVA + WINDSPEED METRIC JAVÍTVA!)
    
    Felelősségek:
    - DUAL-API ROUTING
    - Országválasztás kezelése
    - BATCH PROCESSING
    - PROGRESS TRACKING
    - ✅ ADAT TRANSZFORMÁCIÓ (CityWeatherData -> CityWeatherResult)
    - ✅ NONE-SAFE STATISZTIKÁK
    - ✅ RÉGIÓ/MEGYE MAPPING TELJES (19 megye + 7 régió)
    - ✅ ERROR HANDLING JAVÍTVA (mindig AnalyticsResult objektum)
    - 🔧 KRITIKUS JAVÍTÁS: VALÓDI REGIONÁLIS SZŰRÉS IMPLEMENTÁLVA!
    - 🔥 WINDSPEED METRIC JAVÍTÁS: windgusts_10m_max → windspeed_10m_max (MEGBÍZHATÓBB!)
    - 🔧 ABSOLUTE DATABASE PATH FIX: Working directory független működés!
    """
    
    # 🔧 KRITIKUS JAVÍTÁS: MAGYAR REGIONÁLIS SZŰRÉS MAPPING HOZZÁADVA!
    HUNGARIAN_REGIONAL_MAPPING = {
        # 7 STATISZTIKAI RÉGIÓ → MEGYÉK MAPPING (KSH HIVATALOS)
        "Észak-Magyarország": ["Borsod-Abaúj-Zemplén", "Heves", "Nógrád"],
        "Közép-Magyarország": ["Budapest", "Pest"],
        "Észak-Alföld": ["Hajdú-Bihar", "Jász-Nagykun-Szolnok", "Szabolcs-Szatmár-Bereg"],
        "Dél-Alföld": ["Bács-Kiskun", "Békés", "Csongrád-Csanád"],
        "Dél-Dunántúl": ["Baranya", "Somogy", "Tolna"],
        "Nyugat-Dunántúl": ["Győr-Moson-Sopron", "Vas", "Zala"],
        "Közép-Dunántúl": ["Fejér", "Komárom-Esztergom", "Veszprém"],
        
        # MEGYÉK EGYEDI KEZELÉSE (ha valaki konkrét megyét választ)
        "Budapest": ["Budapest"],
        "Pest": ["Pest"],
        "Borsod-Abaúj-Zemplén": ["Borsod-Abaúj-Zemplén"],
        "Heves": ["Heves"],
        "Nógrád": ["Nógrád"],
        "Hajdú-Bihar": ["Hajdú-Bihar"],
        "Jász-Nagykun-Szolnok": ["Jász-Nagykun-Szolnok"],
        "Szabolcs-Szatmár-Bereg": ["Szabolcs-Szatmár-Bereg"],
        "Bács-Kiskun": ["Bács-Kiskun"],
        "Békés": ["Békés"],
        "Csongrád-Csanád": ["Csongrád-Csanád"],
        "Baranya": ["Baranya"],
        "Somogy": ["Somogy"],
        "Tolna": ["Tolna"],
        "Győr-Moson-Sopron": ["Győr-Moson-Sopron"],
        "Vas": ["Vas"],
        "Zala": ["Zala"],
        "Fejér": ["Fejér"],
        "Komárom-Esztergom": ["Komárom-Esztergom"],
        "Veszprém": ["Veszprém"]
    }
    
    REGIONS = {
        "Hungary": {"name": "Magyarország", "country_codes": ["HU"], "max_cities": 165, "batch_size": 8, "rate_limit_delay": 0.2},
        "Europe": {"name": "Európa", "country_codes": ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "CH", "GB", "NO", "IS", "RS", "BA", "MK", "AL", "MD", "UA", "BY", "RU"], "max_cities": 150, "batch_size": 4, "rate_limit_delay": 0.4},
        "Global": {"name": "Globális", "country_codes": [], "max_cities": 160, "batch_size": 8, "rate_limit_delay": 0.5},
    }
    
    # 🔥 KRITIKUS JAVÍTÁS: WINDSPEED METRIC JAVÍTVA!
    # windgusts_10m_max → windspeed_10m_max (MEGBÍZHATÓBB!)
    QUERY_TYPES = {
        "hottest_today": {"name": "Legmelegebb ma", "metric": "temperature_2m_max", "unit": "°C", "sort_desc": True, "question_template": "Hol volt ma a legmelegebb {region}ban?", "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MAX},
        "coldest_today": {"name": "Leghidegebb ma", "metric": "temperature_2m_min", "unit": "°C", "sort_desc": False, "question_template": "Hol volt ma a leghidegebb {region}ban?", "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MIN},
        "temperature_mean": {"name": "Átlag hőmérséklet", "metric": "temperature_2m_mean", "unit": "°C", "sort_desc": True, "question_template": "Hol volt ma a legmagasabb átlaghőmérséklet {region}ban?", "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MEAN},
        "wettest_today": {"name": "Legcsapadékosabb ma", "metric": "precipitation_sum", "unit": "mm", "sort_desc": True, "question_template": "Hol esett ma a legtöbb csapadék {region}ban?", "metric_enum": AnalyticsMetric.PRECIPITATION_SUM},

        # 🔥 KRITIKUS JAVÍTÁS: windgusts_10m_max → windspeed_10m_max
        # A windspeed_10m_max sokkal megbízhatóbban elérhető az API-kban!
        "windiest_today": {"name": "Legszelesebb ma", "metric": "windspeed_10m_max", "unit": "km/h", "sort_desc": True, "question_template": "Hol fújt ma a legerősebb szél {region}ban?", "metric_enum": AnalyticsMetric.WINDSPEED_10M_MAX},
        "wind_gusts": {"name": "Legerősebb széllökés", "metric": "windgusts_10m_max", "unit": "km/h", "sort_desc": True, "question_template": "Hol fújt ma a legerősebb széllökés {region}ban?", "metric_enum": AnalyticsMetric.WINDGUSTS_10M_MAX},

        "temperature_range": {"name": "Legnagyobb hőingás", "metric": "temperature_range", "unit": "°C", "sort_desc": True, "question_template": "Hol volt ma a legnagyobb hőingás {region}ban?", "metric_enum": AnalyticsMetric.TEMPERATURE_RANGE}
    }
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        hungarian_db_path: Optional[str] = None,
        city_repository: Optional[CityRepositoryProtocol] = None,
    ):
        """
        MultiCityEngine inicializálása repository injekcióval.
        """
        project_root = Path(__file__).parent.parent.parent
        default_db = project_root / "data" / "cities.db"
        default_hu_db = project_root / "data" / "hungarian_settlements.db"

        self.db_path = Path(db_path) if db_path else default_db
        self.hungarian_db_path = (
            Path(hungarian_db_path) if hungarian_db_path else default_hu_db
        )

        self.city_repository: CityRepositoryProtocol = city_repository or CityRepository(
            self.db_path,
            self.hungarian_db_path,
        )
        self.city_repository.validate_paths()
        self.region_resolver = RegionResolverService()

        self.max_workers = 8
        self.request_timeout = 90
        self.max_retries = 2
        self.retry_delay = 3.0
        
        try:
            from src.data.weather_client import WeatherClient
            self.weather_client = WeatherClient()
            logger.info("✅ WeatherClient dual-API integráció sikeres")
        except ImportError as e:
            logger.warning(f"⚠ WeatherClient import hiba: {e}")
            self.weather_client = None

        self.weather_fetch_service = WeatherFetchService(
            weather_client=self.weather_client,
            max_workers=self.max_workers,
            request_timeout=self.request_timeout,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
        )
        self.analytics_transform_service = AnalyticsTransformService(self.QUERY_TYPES)
        self.use_case = AnalyzeMultiCityUseCase(
            region_resolver=self.region_resolver,
            city_repository=self.city_repository,
            weather_fetch_service=self.weather_fetch_service,
            analytics_transform_service=self.analytics_transform_service,
            query_types=self.QUERY_TYPES,
            regions=self.REGIONS,
            hungarian_mapping=self.HUNGARIAN_REGIONAL_MAPPING,
        )
        
        logger.info("🚀 Multi-city engine inicializálva (ABSOLUTE DATABASE PATH FIX v2.8.2)")

    def execute_analytics_query(
        self,
        query: MultiCityQuery,
        progress_callback: Optional[callable] = None,
    ) -> AnalyticsResult:
        return self.use_case.execute(query)

    def get_cities_for_region(self, region: str, limit: Optional[int] = None, max_cities: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        🔧 KRITIKUS JAVÍTÁS: VALÓDI REGIONÁLIS SZŰRÉS IMPLEMENTÁLVA!
        
        RÉGI VISELKEDÉS:
        - "Észak-Magyarország" → "Hungary" → ÖSSZES magyar város (165)
        
        ÚJ VISELKEDÉS:
        - "Észak-Magyarország" → "Hungary" + regionális szűrés → Csak Borsod-Abaúj-Zemplén, Heves, Nógrád megyék városai
        
        Args:
            region: Eredeti régió név (pl. "Észak-Magyarország")
            limit: Eredmények limitje
            max_cities: Maximum városok száma
            
        Returns:
            Szűrt városok listája (regionális vagy teljes)
        """
        original_region = region  # Eredeti régió név tárolása
        
        try:
            mapped_region = self.resolve_region_name(region)
        except ValueError as e:
            logger.error(f"⚠ Invalid region: {region} - {e}")
            return []
            
        region_config = self.REGIONS[mapped_region]
        country_codes = region_config["country_codes"]
        final_limit = max_cities or limit or region_config["max_cities"]
        
        logger.info(f"🔧 get_cities_for_region JAVÍTVA: original='{original_region}' → mapped='{mapped_region}', limit={final_limit}")
        
        try:
            cities = self.city_repository.get_cities_for_region(
                mapped_region=mapped_region,
                original_region=original_region,
                country_codes=country_codes,
                limit=final_limit,
                hungarian_mapping=self.HUNGARIAN_REGIONAL_MAPPING,
            )
            if original_region in self.HUNGARIAN_REGIONAL_MAPPING:
                logger.info(
                    "✅ REGIONÁLIS lekérdezés: %d város %s régióból (%s)",
                    len(cities),
                    original_region,
                    self.HUNGARIAN_REGIONAL_MAPPING[original_region],
                )
            else:
                logger.info(
                    "✅ ORSZÁGOS lekérdezés: %d város %s régióból",
                    len(cities),
                    mapped_region,
                )
            return cities

        except Exception as e:
            logger.error(f"⚠ Hiba városok lekérdezésénél: {e}", exc_info=True)
            return []

    def analyze_multi_city(
        self,
        query_type: str,
        region: str,
        date: str,
        limit: Optional[int] = None,
        question: Optional[AnalyticsQuestion] = None,
    ) -> AnalyticsResult:
        query = MultiCityQuery(
            query_type=query_type,
            region=region,
            date=date,
            limit=limit,
            question=question,
            max_cities=None,
        )
        return self.use_case.execute(query)

    def _transform_to_city_weather_result(self, city_data: CityWeatherData, query_type: str) -> CityWeatherResult:
        """BC wrapper: CityWeatherData → CityWeatherResult."""
        return self.analytics_transform_service.transform_to_city_weather_result(city_data, query_type)
        
    def _fetch_weather_data_dual_api_batch(self, cities: List[Dict[str, Any]], date: str, region: str) -> List[CityWeatherData]:
        """Párhuzamos időjárás lekérdezés (DUAL-API BATCH PROCESSING) delegálva a service-re."""
        region_config = self.REGIONS[region]
        return self.weather_fetch_service.fetch_weather_data_dual_api_batch(
            cities=cities,
            date=date,
            region_config=region_config,
        )

    def _process_dual_api_batch(self, batch: List[Dict[str, Any]], date: str, rate_limit_delay: float) -> List[CityWeatherData]:
        """BC wrapper a WeatherFetchService batch feldolgozására."""
        return self.weather_fetch_service.process_dual_api_batch(batch, date)

    def _fetch_single_city_weather_dual_api(self, city: Dict[str, Any], date: str) -> CityWeatherData:
        """BC wrapper egyetlen város lekérdezésére."""
        return self.weather_fetch_service.fetch_single_city_weather_dual_api(city, date)

    def _create_empty_city_data(self, city: Dict[str, Any], error_msg: str = "Ismeretlen hiba") -> CityWeatherData:
        """BC wrapper üres CityWeatherData létrehozására."""
        return self.weather_fetch_service.create_empty_city_data(city, error_msg)

    def _process_weather_results(self, weather_data: List[CityWeatherData], query_type: str) -> List[CityWeatherData]:
        """BC wrapper: rendezés és hőingás számítás."""
        return self.analytics_transform_service.process_weather_results(weather_data, query_type)

    def _calculate_statistics_for_results_none_safe(self, results: List[CityWeatherResult]) -> Dict[str, float]:
        """BC wrapper: none-safe statisztikák számítása."""
        return self.analytics_transform_service.calculate_statistics_for_results_none_safe(results)

    def _get_provider_stats(self, weather_data: List[CityWeatherData]) -> Dict[str, int]:
        """BC wrapper: provider statisztikák."""
        return self.analytics_transform_service.get_provider_stats(weather_data)

    def _create_empty_analytics_result(self, question: Optional[AnalyticsQuestion], error_msg: str = "Ismeretlen hiba") -> AnalyticsResult:
        """BC wrapper: üres AnalyticsResult létrehozása."""
        return self.analytics_transform_service.create_empty_analytics_result(question, error_msg)

    def _create_empty_analytics_result(self, question: Optional[AnalyticsQuestion], error_msg: str = "Ismeretlen hiba") -> AnalyticsResult:
        """
        🔧 KRITIKUS JAVÍTÁS: Üres AnalyticsResult létrehozása hibák esetén - JAVÍTOTT ERROR HANDLING.
        
        Ez a metódus biztosítja, hogy analyze_multi_city() MINDIG AnalyticsResult objektumot adjon vissza,
        még hiba esetén is (nem dict-et).
        
        Args:
            question: AnalyticsQuestion objektum (lehet None)
            error_msg: Hibaüzenet
            
        Returns:
            Üres AnalyticsResult objektum proper fallback question-nel
        """
        try:
            # Fallback question létrehozása ha nincs megadva
            fallback_question = question
            if not fallback_question:
                fallback_question = AnalyticsQuestion(
                    question_text=f"Multi-city elemzés hiba: {error_msg}",
                    question_type=QuestionType.WEATHER_COMPARISON,  # 🔥 FIX: SINGLE_LOCATION → WEATHER_COMPARISON
                    region_scope=RegionScope.GLOBAL,
                    metric=AnalyticsMetric.TEMPERATURE_2M_MAX
                )
            
            # Üres AnalyticsResult objektum létrehozása
            empty_result = AnalyticsResult(
                question=fallback_question,
                city_results=[],  # Üres lista
                execution_time=0.0,
                total_cities_found=0,
                data_sources_used=[],
                statistics={},
                provider_statistics={}
            )
            
            logger.info(f"✅ Empty AnalyticsResult created for error: {error_msg}")
            return empty_result
            
        except Exception as e:
            # Ultimate fallback - ha még ez sem működik
            logger.error(f"⚠ Critical error creating empty AnalyticsResult: {e}")
            
            # Manuális objektum létrehozás
            try:
                ultra_fallback_question = AnalyticsQuestion(
                    question_text="Critical error",
                    question_type=QuestionType.TEMPERATURE_MAX,  # 🔥 FIX: COMPARISON → TEMPERATURE_MAX
                    region_scope=RegionScope.GLOBAL,
                    metric=AnalyticsMetric.TEMPERATURE_2M_MAX
                )
                
                ultra_fallback_result = AnalyticsResult(
                    question=ultra_fallback_question,
                    city_results=[],
                    execution_time=0.0,
                    total_cities_found=0,
                    data_sources_used=[],
                    statistics={},
                    provider_statistics={}
                )
                
                return ultra_fallback_result
                
            except Exception as ultra_e:
                logger.error(f"⚠ ULTRA CRITICAL: Cannot create AnalyticsResult at all: {ultra_e}")
                # Ha még ez sem működik, akkor valami alapvető hiba van
                raise RuntimeError(f"Cannot create AnalyticsResult: {ultra_e}")

    def resolve_region_name(self, region_input: str) -> str:
        """
        🔧 KRITIKUS JAVÍTÁS: Régió név feloldása - TELJES MAGYAR RÉGIÓ/MEGYE TÁMOGATÁSSAL + ERROR HANDLING.
        
        BC wrapper: delegál a RegionResolverService-re.
        """
        return self.region_resolver.resolve_region_name(region_input)


# 🧪 TESTING & DEBUG (ABSOLUTE DATABASE PATH FIX + NONE-SAFE + RÉGIÓ MAPPING + RÉGIÓ SZŰRÉS + WINDSPEED METRIC JAVÍTÁS)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("\n🚀 ABSOLUTE DATABASE PATH FIX TESZTEK v2.8.2:")
    print(f"🔧 Script location: {Path(__file__).absolute()}")
    print(f"🔧 Working directory: {Path.cwd().absolute()}")
    
    try:
        engine = MultiCityEngine()
        today = datetime.now().strftime("%Y-%m-%d")
        
        print(f"\n🔧 Calculated paths:")
        print(f"   Global cities DB: {engine.db_path.absolute()}")
        print(f"   Hungarian settlements DB: {engine.hungarian_db_path.absolute()}")
        print(f"   Global DB exists: {engine.db_path.exists()}")
        print(f"   Hungarian DB exists: {engine.hungarian_db_path.exists()}")
        
        print("\n🚀 RÉGIÓ MAPPING TESZTEK:")
        test_regions = [
            "HU", "Észak-Magyarország", "Pest", "Budapest", 
            "észak-magyarország", "közép-magyarország", "EU", "GLOBAL"
        ]
        
        for region in test_regions:
            try:
                mapped = engine.resolve_region_name(region)
                print(f"✅ '{region}' → '{mapped}'")
            except ValueError as e:
                print(f"⚠ '{region}' → ERROR: {e}")
        
        print("\n🚀 WINDSPEED METRIC JAVÍTÁS TESZT: 'Észak-Magyarország' régióval (windiest):")
        try:
            result_wind = engine.analyze_multi_city("windiest_today", "Észak-Magyarország", today, limit=10)
            print(f"📊 Eredmények: {len(result_wind.city_results)} város")
            print(f"📊 NONE-SAFE Statisztikák: {result_wind.statistics}")
            
            # Első 3 város részletei
            print("🔥 TOP 3 LEGSZELESEBB VÁROSOK:")
            for i, city in enumerate(result_wind.city_results[:3]):
                print(f"  {i+1}. {city.city_name}: {city.value} km/h")
                
            # ELLENŐRIZZÜK: vannak-e nem-nulla értékek?
            non_zero_count = len([c for c in result_wind.city_results if c.value > 0])
            print(f"\n🔧 WINDSPEED METRIC JAVÍTÁS ELLENŐRZÉS:")
            print(f"   Nem-nulla szélsebesség értékek: {non_zero_count}/{len(result_wind.city_results)}")
            
            if non_zero_count > 0:
                print("✅ WINDSPEED METRIC JAVÍTÁS SIKERES!")
            else:
                print("⚠ WINDSPEED METRIC JAVÍTÁS SIKERTELEN!")
                
        except Exception as e:
            print(f"⚠ Teszt hiba: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n🔧 ABSOLUTE DATABASE PATH TESZT BEFEJEZVE v2.8.2")
        
    except Exception as e:
        print(f"❌ KRITIKUS HIBA az engine inicializáláskor: {e}")
        print(f"🔧 Debugging info:")
        print(f"   Current working dir: {Path.cwd().absolute()}")
        print(f"   Script location: {Path(__file__).absolute()}")
        
        # Projekt root keresés debug
        project_root = Path(__file__).parent.parent.parent
        print(f"   Calculated project root: {project_root.absolute()}")
        print(f"   Project root exists: {project_root.exists()}")
        
        data_dir = project_root / "data"
        print(f"   Data directory: {data_dir.absolute()}")
        print(f"   Data directory exists: {data_dir.exists()}")
        
        if data_dir.exists():
            files = list(data_dir.iterdir())
            print(f"   Files in data/: {[f.name for f in files]}")
        
        import traceback
        traceback.print_exc()
