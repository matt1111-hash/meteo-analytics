# mypy: ignore-errors
"""Weather fetch service handling dual-API batch retrieval with retries."""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from src.domain.analytics.models import CityWeatherData

from .weather_fetch_service_support import (
    create_city_results,
    create_empty_city_data,
    normalize_weather_result,
    resolve_effective_dates,
    split_batches,
)

logger = logging.getLogger(__name__)


class WeatherFetchService:
    """Fetch weather data for multiple cities using a retry-capable client."""

    def __init__(  # noqa: D107
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

    def _log_batch_result(
        self,
        batch_idx: int,
        batch_count: int,
        batch: list[dict[str, Any]],
        batch_results: list[CityWeatherData],
        batch_start_time: float,
    ) -> None:
        """Log batch processing summary."""
        batch_time = time.time() - batch_start_time
        successful_in_batch = len([result for result in batch_results if result.fetch_success])
        logger.info(
            "Batch %d/%d: %d/%d siker, idő: %.1fs",
            batch_idx + 1,
            batch_count,
            successful_in_batch,
            len(batch),
            batch_time,
        )

    def fetch_weather_data_dual_api_batch(
        self,
        cities: list[dict[str, Any]],
        date: str,
        region_config: dict[str, Any],
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[CityWeatherData]:
        """Parallel dual-API fetching with throttling by region config.

        Args:
            date: Primary date (for backward compatibility)
            start_date: Optional range start (overrides date if provided)
            end_date: Optional range end (overrides date if provided)
        """
        if not self.weather_client:
            logger.error("⚠ WeatherClient nem elérhető")
            return [self.create_empty_city_data(city) for city in cities]

        effective_start, effective_end = resolve_effective_dates(date, start_date, end_date)
        batch_size = region_config["batch_size"]
        rate_limit_delay = region_config["rate_limit_delay"]
        batches = split_batches(cities, batch_size)
        logger.info(
            "Dual-API batch processing: %d batch, %d város/batch",
            len(batches),
            batch_size,
        )

        weather_data: list[CityWeatherData] = []
        for batch_idx, batch in enumerate(batches):
            batch_start_time = time.time()
            batch_results = self.process_dual_api_batch(batch, effective_start, effective_end)
            weather_data.extend(batch_results)
            self._log_batch_result(batch_idx, len(batches), batch, batch_results, batch_start_time)

            if batch_idx < len(batches) - 1:
                time.sleep(rate_limit_delay)

        logger.info("Dual-API batch processing befejezve: %d város", len(weather_data))
        return weather_data

    def process_dual_api_batch(
        self, batch: list[dict[str, Any]], start_date: str, end_date: str
    ) -> list[CityWeatherData]:
        """Process a batch in parallel and collect results.

        Returns:
            Flattened list of CityWeatherData (multiple days per city).
        """
        batch_results: list[CityWeatherData] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self.fetch_single_city_weather_dual_api, city, start_date, end_date
                ): city
                for city in batch
            }

            for future in as_completed(futures):
                city = futures[future]
                try:
                    city_data_list = future.result(timeout=self.request_timeout)
                    # Flatten the list - each city returns multiple days
                    batch_results.extend(city_data_list)
                except Exception as exc:
                    logger.error(
                        "⚠ Hiba a város feldolgozásánál (%s): %s",
                        city.get("city"),
                        exc,
                        exc_info=True,
                    )
                    batch_results.append(self.create_empty_city_data(city, str(exc)))
        return batch_results

    def fetch_single_city_weather_dual_api(
        self, city: dict[str, Any], start_date: str, end_date: str | None = None
    ) -> list[CityWeatherData]:
        """Fetch one city's weather with retry logic and safe transforms.

        Returns:
            List of CityWeatherData, one per day in the date range.
        """
        effective_end = end_date or start_date

        last_error: str | None = None
        for attempt in range(self.max_retries):
            try:
                weather_result = self.weather_client.get_weather_data(
                    city["lat"], city["lon"], start_date, effective_end
                )
                weather_data, source = normalize_weather_result(weather_result)

                if weather_data and len(weather_data) > 0:
                    results = create_city_results(
                        city=city,
                        weather_data=weather_data,
                        start_date=start_date,
                        source=source,
                        attempt=attempt,
                    )
                    logger.debug("Fetched %d days for %s", len(results), city["city"])
                    return results
                last_error = f"Nincs időjárási adat {city['city']}-hoz"
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "⚠️ Hiba a(z) %s lekérdezésekor (próba: %d): %s",
                    city.get("city"),
                    attempt + 1,
                    exc,
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        logger.error("⚠ Végső hiba a(z) %s lekérdezésénél: %s", city.get("city"), last_error)
        return [self.create_empty_city_data(city, last_error)]

    def create_empty_city_data(
        self, city: dict[str, Any], error_msg: str = "Ismeretlen hiba"
    ) -> CityWeatherData:
        """Return empty CityWeatherData for failure cases."""
        return create_empty_city_data(city, error_msg)
