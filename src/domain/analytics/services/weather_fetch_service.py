"""Weather fetch service handling dual-API batch retrieval with retries."""
from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from src.domain.analytics.models import CityWeatherData

logger = logging.getLogger(__name__)


class WeatherFetchService:
    """Fetch weather data for multiple cities using a retry-capable client."""

    def __init__(
        self,
        weather_client: Any,
        max_workers: int,
        request_timeout: float,
        max_retries: int,
        retry_delay: float,
    ) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        if max_retries < 1:
            raise ValueError("max_retries must be >= 1")
        self.weather_client = weather_client
        self.max_workers = max_workers
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def fetch_weather_data_dual_api_batch(
        self,
        cities: List[Dict[str, Any]],
        date: str,
        region_config: Dict[str, Any],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[CityWeatherData]:
        """Parallel dual-API fetching with throttling by region config.

        Args:
            date: Primary date (for backward compatibility)
            start_date: Optional range start (overrides date if provided)
            end_date: Optional range end (overrides date if provided)
        """
        if not self.weather_client:
            logger.error("⚠ WeatherClient nem elérhető")
            return [self.create_empty_city_data(city) for city in cities]

        # Use date range if provided, otherwise use single date
        effective_start = start_date if start_date else date
        effective_end = end_date if end_date else date

        batch_size = region_config["batch_size"]
        rate_limit_delay = region_config["rate_limit_delay"]

        batches = [cities[i : i + batch_size] for i in range(0, len(cities), batch_size)]
        logger.info("Dual-API batch processing: %d batch, %d város/batch", len(batches), batch_size)

        weather_data: List[CityWeatherData] = []
        for batch_idx, batch in enumerate(batches):
            batch_start_time = time.time()
            batch_results = self.process_dual_api_batch(batch, effective_start, effective_end)
            weather_data.extend(batch_results)

            batch_time = time.time() - batch_start_time
            successful_in_batch = len([r for r in batch_results if r.fetch_success])
            logger.info(
                "Batch %d/%d: %d/%d siker, idő: %.1fs",
                batch_idx + 1,
                len(batches),
                successful_in_batch,
                len(batch),
                batch_time,
            )

            if batch_idx < len(batches) - 1:
                time.sleep(rate_limit_delay)

        logger.info("Dual-API batch processing befejezve: %d város", len(weather_data))
        return weather_data

    def process_dual_api_batch(
        self, batch: List[Dict[str, Any]], start_date: str, end_date: str
    ) -> List[CityWeatherData]:
        """Process a batch in parallel and collect results.

        Returns:
            Flattened list of CityWeatherData (multiple days per city).
        """
        batch_results: List[CityWeatherData] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.fetch_single_city_weather_dual_api, city, start_date, end_date): city
                for city in batch
            }

            for future in as_completed(futures):
                city = futures[future]
                try:
                    city_data_list = future.result(timeout=self.request_timeout)
                    # Flatten the list - each city returns multiple days
                    batch_results.extend(city_data_list)
                except Exception as exc:
                    logger.error("⚠ Hiba a város feldolgozásánál (%s): %s", city.get("city"), exc, exc_info=True)
                    batch_results.append(self.create_empty_city_data(city, str(exc)))
        return batch_results

    def fetch_single_city_weather_dual_api(
        self, city: Dict[str, Any], start_date: str, end_date: Optional[str] = None
    ) -> List[CityWeatherData]:
        """Fetch one city's weather with retry logic and safe transforms.

        Returns:
            List of CityWeatherData, one per day in the date range.
        """
        # Handle optional end_date by defaulting to start_date (single day query)
        effective_end = end_date if end_date else start_date

        last_error: Optional[str] = None
        for attempt in range(self.max_retries):
            try:
                weather_result = self.weather_client.get_weather_data(
                    city["lat"], city["lon"], start_date, effective_end
                )
                if isinstance(weather_result, tuple) and len(weather_result) == 2:
                    weather_data, source = weather_result
                else:
                    weather_data = weather_result
                    source = "auto"

                if weather_data and len(weather_data) > 0:
                    # Create CityWeatherData for EACH day in the range
                    results: List[CityWeatherData] = []
                    for daily_data in weather_data:
                        temp_max = daily_data.get("temperature_2m_max")
                        temp_min = daily_data.get("temperature_2m_min")

                        temp_range = None
                        if temp_max is not None and temp_min is not None:
                            try:
                                temp_range = temp_max - temp_min
                            except (TypeError, ValueError):
                                temp_range = None

                        windspeed = daily_data.get("windspeed_10m_max")
                        windgusts = daily_data.get("wind_gusts_10m_max")  # Fixed: match weather_client output

                        results.append(
                            CityWeatherData(
                                city=city["city"],
                                country=city["country"],
                                country_code=city["country_code"],
                                lat=city["lat"],
                                lon=city["lon"],
                                population=city.get("population"),
                                date=daily_data.get("date") or start_date,
                                temperature_2m_max=temp_max,
                                temperature_2m_min=temp_min,
                                temperature_2m_mean=daily_data.get("temperature_2m_mean"),
                                precipitation_sum=daily_data.get("precipitation_sum"),
                                windspeed_10m_max=windspeed,
                                windgusts_10m_max=windgusts,
                                meteostat_station_id=city.get("meteostat_station_id"),
                                data_quality_score=city.get("data_quality_score"),
                                data_source=source,
                                fetch_timestamp=datetime.now().isoformat(),
                                fetch_success=True,
                                retry_count=attempt,
                                temperature_range=temp_range,
                            )
                        )
                    logger.debug("Fetched %d days for %s", len(results), city["city"])
                    return results
                last_error = f"Nincs időjárási adat {city['city']}-hoz"
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "⚠️ Hiba a(z) %s lekérdezésekor (próba: %d): %s", city.get("city"), attempt + 1, exc
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        logger.error("⚠ Végső hiba a(z) %s lekérdezésénél: %s", city.get("city"), last_error)
        return [self.create_empty_city_data(city, last_error)]

    def create_empty_city_data(self, city: Dict[str, Any], error_msg: str = "Ismeretlen hiba") -> CityWeatherData:
        """Return empty CityWeatherData for failure cases."""
        return CityWeatherData(
            city=city.get("city", "Ismeretlen"),
            country=city.get("country", "Ismeretlen"),
            country_code=city.get("country_code", "XX"),
            lat=city.get("lat", 0.0),
            lon=city.get("lon", 0.0),
            population=city.get("population"),
            data_source="error",
            fetch_success=False,
            error_message=error_msg,
        )
