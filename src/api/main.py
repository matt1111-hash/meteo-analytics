"""FastAPI entrypoint for Global Weather Analyzer backend."""

from __future__ import annotations  # noqa: I001

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Callable  # noqa: UP035

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.analytics import router as analytics_router
from src.api.routes.anomalies import router as anomalies_router
from src.api.routes.cities import router as cities_router
from src.api.routes.detailed_city import router as detailed_city_router
from src.api.routes.hungary import router as hungary_router
from src.api.routes.metadata import router as metadata_router
from src.api.routes.multi_year import router as multi_year_router
from src.api.routes.providers import router as providers_router
from src.api.routes.single_city import router as single_city_router
from src.api.routes.weather import router as weather_router
from src.api.routes.wind_rose import router as wind_rose_router
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.config.api_config import APIConfig

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle."""
    if APIConfig.APP_ENV == "production":
        if "*" in APIConfig.CORS_ORIGINS:
            raise RuntimeError(
                "FATAL: APP_ENV=production but CORS_ORIGINS contains '*'. "
                "Refusing to start with wildcard CORS in production."
            )
        logger.info("Production security checks passed")

    from src.api.dependencies import build_service_registry  # noqa: PLC0415

    app.state.services = build_service_registry()
    logger.info("Service registry initialized")

    yield

    del app.state.services
    logger.info("Application shutting down")


app = FastAPI(title="Global Weather Analyzer API", lifespan=lifespan)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next: Callable):
    """Add security headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if APIConfig.APP_ENV == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


# CORS middleware — restricted methods and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=APIConfig.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Rate limiting — production: strict; development: generous for tests
_rate_cfg = (
    {"max_requests": 60, "window_seconds": 60}
    if APIConfig.APP_ENV == "production"
    else {"max_requests": 10000, "window_seconds": 60}
)
app.add_middleware(RateLimitMiddleware, **_rate_cfg)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health probe (public endpoint)."""
    return {"status": "ok"}


app.include_router(weather_router)
app.include_router(single_city_router)
app.include_router(detailed_city_router)
app.include_router(wind_rose_router)
app.include_router(analytics_router)
app.include_router(metadata_router)
app.include_router(anomalies_router)
app.include_router(cities_router)
app.include_router(hungary_router)
app.include_router(multi_year_router)
app.include_router(providers_router)
