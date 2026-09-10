"""Weather fetch service handling dual-API batch retrieval with retries."""

from __future__ import annotations

import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from concurrent.futures import TimeoutError as FuturesTimeoutError
from typing import Any

from src.domain.analytics.models import CityWeatherData
from src.domain.analytics.services.weather_fetch_service_support import (
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
        logger.debug(
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
        logger.debug(
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

        logger.debug("Dual-API batch processing befejezve: %d város", len(weather_data))
        return weather_data

    def process_dual_api_batch(
        self, batch: list[dict[str, Any]], start_date: str, end_date: str
    ) -> list[CityWeatherData]:
        """Process a batch in parallel and collect results.

        `request_timeout` is a wall-clock budget for the whole batch: once it is
        exhausted no further city is started, the still-queued cities are
        cancelled and reported as failed, while already running fetches are
        still harvested (each HTTP call is capped by `APIConfig.REQUEST_TIMEOUT`,
        so they drain quickly). Previously the per-future timeout below was a
        no-op, because `as_completed` only yields futures that are already done.

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

            collected: set[Future] = set()
            try:
                for future in as_completed(futures, timeout=self.request_timeout):
                    collected.add(future)
                    self._collect_batch_result(future, futures[future], batch_results)
            except FuturesTimeoutError:
                skipped = [future for future in futures if future.cancel()]
                logger.error(
                    "⚠ Batch időkeret (%.0fs) lejárt: %d város kihagyva, %d fut tovább",
                    self.request_timeout,
                    len(skipped),
                    len(futures) - len(skipped),
                )
                batch_results.extend(
                    self.create_empty_city_data(futures[future], "batch deadline exceeded")
                    for future in skipped
                )
                for future, city in futures.items():
                    if future not in skipped and future not in collected:
                        self._collect_batch_result(future, city, batch_results)

        return batch_results

    def _collect_batch_result(
        self, future: Future, city: dict[str, Any], batch_results: list[CityWeatherData]
    ) -> None:
        """Append one city's fetched rows, or its failure placeholder."""
        try:
            city_data_list = future.result()
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
        return [self.create_empty_city_data(city, last_error or "Ismeretlen hiba")]

    def create_empty_city_data(
        self, city: dict[str, Any], error_msg: str = "Ismeretlen hiba"
    ) -> CityWeatherData:
        """Return empty CityWeatherData for failure cases."""
        return create_empty_city_data(city, error_msg)
