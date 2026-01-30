#!/usr/bin/env python3
"""
Multi-City Analytics Engine - Core Engine
Main MultiCityEngine class for multi-city weather analytics
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.application.use_cases.analyze_multi_city import AnalyzeMultiCityUseCase
from src.domain.analytics.models import CityWeatherData, MultiCityQuery
from src.domain.analytics.repositories import CityRepositoryProtocol
from src.domain.analytics.services import (
    AnalyticsTransformService,
    RegionResolverService,
    WeatherFetchService,
)
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.entities.weather import CityWeatherResult
from src.domain.ports import CityRepositoryPort, get_city_repository_port, get_weather_client_port
from src.domain.value_objects.enums import AnalyticsMetric, QuestionType, RegionScope

from .multi_city_types import HUNGARIAN_REGIONAL_MAPPING, REGIONS

logger = logging.getLogger(__name__)


class MultiCityEngine:
    """
    Multi-city időjárás elemzés koordinátor.

    Felelősségek:
    - DUAL-API ROUTING
    - Országválasztás kezelése
    - BATCH PROCESSING
    - PROGRESS TRACKING
    - ADAT TRANSZFORMÁCIÓ (CityWeatherData -> CityWeatherResult)
    - NONE-SAFE STATISZTIKÁK
    - RÉGIÓ/MEGYE MAPPING TELJES
    - ERROR HANDLING
    - VALÓDI REGIONÁLIS SZŰRÉS
    """

    # Query types configuration
    QUERY_TYPES = {
        "hottest_today": {"name": "Legmelegebb ma", "metric": "temperature_2m_max", "unit": "°C", "sort_desc": True, "question_template": "Hol volt ma a legmelegebb {region}ban?", "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MAX},
        "coldest_today": {"name": "Leghidegebb ma", "metric": "temperature_2m_min", "unit": "°C", "sort_desc": False, "question_template": "Hol volt ma a leghidegebb {region}ban?", "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MIN},
        "temperature_mean": {"name": "Átlag hőmérséklet", "metric": "temperature_2m_mean", "unit": "°C", "sort_desc": True, "question_template": "Hol volt ma a legmagasabb átlaghőmérséklet {region}ban?", "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MEAN},
        "wettest_today": {"name": "Legcsapadékosabb ma", "metric": "precipitation_sum", "unit": "mm", "sort_desc": True, "question_template": "Hol esett ma a legtöbb csapadék {region}ban?", "metric_enum": AnalyticsMetric.PRECIPITATION_SUM},
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
        """MultiCityEngine inicializálása repository injekcióval (CA compliant - uses ports)."""
        project_root = Path(__file__).parent.parent.parent
        default_db = project_root / "data" / "cities.db"
        default_hu_db = project_root / "data" / "hungarian_settlements.db"

        self.db_path = Path(db_path) if db_path else default_db
        self.hungarian_db_path = (
            Path(hungarian_db_path) if hungarian_db_path else default_hu_db
        )

        # Use port for city repository (CA compliant)
        self.city_repository: CityRepositoryProtocol = city_repository or get_city_repository_port()
        self.city_repository.validate_paths()
        self.region_resolver = RegionResolverService()

        self.max_workers = 8
        self.request_timeout = 90
        self.max_retries = 2
        self.retry_delay = 3.0

        # Use port for weather client (CA compliant)
        try:
            self.weather_client = get_weather_client_port()
            logger.info("✅ WeatherClient dual-api integráció sikeres (port-based)")
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
            regions=REGIONS,
            hungarian_mapping=HUNGARIAN_REGIONAL_MAPPING,
        )

        logger.info("🚀 Multi-city engine inicializálva")

    def execute_analytics_query(
        self,
        query: MultiCityQuery,
        progress_callback: Optional[callable] = None,
    ) -> AnalyticsResult:
        """Execute analytics query with optional progress callback."""
        return self.use_case.execute(query)

    def get_cities_for_region(self, region: str, limit: Optional[int] = None, max_cities: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get cities for a given region with proper regional filtering.

        Args:
            region: Region name (e.g. "Észak-Magyarország")
            limit: Result limit
            max_cities: Maximum number of cities

        Returns:
            List of cities (filtered by region if applicable)
        """
        original_region = region

        try:
            mapped_region = self.resolve_region_name(region)
        except ValueError as e:
            logger.error(f"⚠ Invalid region: {region} - {e}")
            return []

        region_config = REGIONS[mapped_region]
        country_codes = region_config["country_codes"]
        final_limit = max_cities or limit or region_config["max_cities"]

        logger.info(f"🔧 get_cities_for_region: original='{original_region}' → mapped='{mapped_region}', limit={final_limit}")

        try:
            cities = self.city_repository.get_cities_for_region(
                mapped_region=mapped_region,
                original_region=original_region,
                country_codes=country_codes,
                limit=final_limit,
                hungarian_mapping=HUNGARIAN_REGIONAL_MAPPING,
            )
            if original_region in HUNGARIAN_REGIONAL_MAPPING:
                logger.info(
                    "✅ REGIONÁLIS lekérdezés: %d város %s régióból (%s)",
                    len(cities),
                    original_region,
                    HUNGARIAN_REGIONAL_MAPPING[original_region],
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
        """Analyze multi-city weather data."""
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
        """Transform CityWeatherData to CityWeatherResult."""
        return self.analytics_transform_service.transform_to_city_weather_result(city_data, query_type)

    def _fetch_weather_data_dual_api_batch(self, cities: List[Dict[str, Any]], date: str, region: str) -> List[CityWeatherData]:
        """Fetch weather data for multiple cities in parallel."""
        region_config = REGIONS[region]
        return self.weather_fetch_service.fetch_weather_data_dual_api_batch(
            cities=cities,
            date=date,
            region_config=region_config,
        )

    def _process_dual_api_batch(self, batch: List[Dict[str, Any]], date: str, rate_limit_delay: float) -> List[CityWeatherData]:
        """Process a batch of cities."""
        return self.weather_fetch_service.process_dual_api_batch(batch, date)

    def _fetch_single_city_weather_dual_api(self, city: Dict[str, Any], date: str) -> CityWeatherData:
        """Fetch weather data for a single city."""
        return self.weather_fetch_service.fetch_single_city_weather_dual_api(city, date)

    def _create_empty_city_data(self, city: Dict[str, Any], error_msg: str = "Ismeretlen hiba") -> CityWeatherData:
        """Create empty CityWeatherData for error cases."""
        return self.weather_fetch_service.create_empty_city_data(city, error_msg)

    def _process_weather_results(self, weather_data: List[CityWeatherData], query_type: str) -> List[CityWeatherData]:
        """Process and sort weather results."""
        return self.analytics_transform_service.process_weather_results(weather_data, query_type)

    def _calculate_statistics_for_results_none_safe(self, results: List[CityWeatherResult]) -> Dict[str, float]:
        """Calculate statistics for results."""
        return self.analytics_transform_service.calculate_statistics_for_results_none_safe(results)

    def _get_provider_stats(self, weather_data: List[CityWeatherData]) -> Dict[str, int]:
        """Get provider statistics."""
        return self.analytics_transform_service.get_provider_stats(weather_data)

    def _create_empty_analytics_result(self, question: Optional[AnalyticsQuestion], error_msg: str = "Ismeretlen hiba") -> AnalyticsResult:
        """Create empty AnalyticsResult for error cases."""
        try:
            fallback_question = question
            if not fallback_question:
                fallback_question = AnalyticsQuestion(
                    question_text=f"Multi-city elemzés hiba: {error_msg}",
                    question_type=QuestionType.WEATHER_COMPARISON,
                    region_scope=RegionScope.GLOBAL,
                    metric=AnalyticsMetric.TEMPERATURE_2M_MAX
                )

            empty_result = AnalyticsResult(
                question=fallback_question,
                city_results=[],
                execution_time=0.0,
                total_cities_found=0,
                data_sources_used=[],
                statistics={},
                provider_statistics={}
            )

            logger.info(f"✅ Empty AnalyticsResult created for error: {error_msg}")
            return empty_result

        except Exception as e:
            logger.error(f"⚠ Critical error creating empty AnalyticsResult: {e}")

            try:
                ultra_fallback_question = AnalyticsQuestion(
                    question_text="Critical error",
                    question_type=QuestionType.TEMPERATURE_MAX,
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
                raise RuntimeError(f"Cannot create AnalyticsResult: {ultra_e}")

    def resolve_region_name(self, region_input: str) -> str:
        """Resolve region name to canonical form."""
        return self.region_resolver.resolve_region_name(region_input)


__all__ = ['MultiCityEngine']
