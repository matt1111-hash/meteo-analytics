"""Multi-year batch weather endpoint — single HTTP request for N years."""

from __future__ import annotations  # noqa: I001

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from src.api.adapters.weather_adapter import to_multi_city_query
from src.api.dependencies import ServiceRegistry, get_services
from src.api.dto.multi_year_request import MultiYearBatchRequest
from src.api.dto.weather_request import WeatherAnalysisRequest
from src.application.use_cases.analyze_multi_city import AnalyzeMultiCityUseCase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weather", tags=["weather"])


def _metric_to_query_type(metric: str) -> str:
    """Map metric name to query_type."""
    mapping = {
        "temperature_2m_max": "hottest_today",
        "temperature_2m_min": "coldest_today",
        "temperature_2m_mean": "temperature_mean",
        "precipitation_sum": "wettest_today",
        "windspeed_10m_max": "windiest_today",
        "windgusts_10m_max": "wind_gusts",
        "temperature_range": "temperature_range",
    }
    return mapping.get(metric, "hottest_today")


def _fetch_year_data(
    use_case: AnalyzeMultiCityUseCase,
    city: str,
    year: int,
    query_type: str,
) -> dict:
    """Fetch single-year data synchronously (runs in thread pool)."""
    request = WeatherAnalysisRequest(
        cities=[city],
        date_range={"start": f"{year}-01-01", "end": f"{year}-12-31"},
    )
    query = to_multi_city_query(request)
    query = replace(query, query_type=query_type)
    uc_result = use_case.execute(query, aggregate=False)

    if uc_result is not None and uc_result.is_success and uc_result.data is not None:
        return {"year": year, "data": uc_result.data.to_dict().get("city_results", [])}
    return {"year": year, "data": []}


@router.post("/multi-year-batch")
async def multi_year_batch(
    request: MultiYearBatchRequest,
    services: ServiceRegistry = Depends(get_services),
) -> dict:
    """Fetch weather data for multiple years in a single request.

    Returns per-year city_results for monthly comparison charts.
    """
    try:
        use_case = services.analyze_multi_city_use_case
        query_type = _metric_to_query_type(request.metric)

        def _fetch_all() -> list[dict]:
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = [
                    pool.submit(_fetch_year_data, use_case, request.city, year, query_type)
                    for year in request.years
                ]
                return [f.result() for f in futures]

        results = await run_in_threadpool(_fetch_all)

        return {
            "city": request.city,
            "metric": request.metric,
            "years": {str(r["year"]): r["data"] for r in results},
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error in multi-year-batch: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


__all__ = ["router"]
