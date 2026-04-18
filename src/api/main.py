# mypy: ignore-errors
"""FastAPI entrypoint for Global Weather Analyzer backend."""

from __future__ import annotations  # noqa: I001

import logging
import secrets
from typing import Callable  # noqa: UP035

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from src.api.routes.analytics import router as analytics_router
from src.api.routes.anomalies import router as anomalies_router
from src.api.routes.cities import router as cities_router
from src.api.routes.detailed_city import router as detailed_city_router
from src.api.routes.hungary import router as hungary_router
from src.api.routes.metadata import router as metadata_router
from src.api.routes.providers import router as providers_router
from src.api.routes.single_city import router as single_city_router
from src.api.routes.weather import router as weather_router
from src.api.routes.wind_rose import router as wind_rose_router
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.config.api_config import APIConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Global Weather Analyzer API")


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


@app.on_event("startup")
def _enforce_production_security() -> None:
    """Fail fast if production security prerequisites are not met."""
    if APIConfig.APP_ENV == "production":
        if not APIConfig.API_KEY_ENABLED:
            raise RuntimeError(
                "FATAL: APP_ENV=production but API_KEY is not set. "
                "Refusing to start without authentication."
            )
        if "*" in APIConfig.CORS_ORIGINS:
            raise RuntimeError(
                "FATAL: APP_ENV=production but CORS_ORIGINS contains '*'. "
                "Refusing to start with wildcard CORS in production."
            )
        logger.info("Production security checks passed")

    if not APIConfig.API_KEY_ENABLED:
        logger.warning(
            "API key authentication is DISABLED. Set API_KEY env var to enable authentication."
        )


# CORS middleware - origins configurable via CORS_ORIGINS env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=APIConfig.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting — production: strict; development: generous for tests
_rate_cfg = (
    {"max_requests": 60, "window_seconds": 60}
    if APIConfig.APP_ENV == "production"
    else {"max_requests": 10000, "window_seconds": 60}
)
app.add_middleware(RateLimitMiddleware, **_rate_cfg)

# API Key authentication setup
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    """Verify API key from X-API-Key header.

    Returns the API key if valid, raises HTTPException otherwise.
    """
    if not APIConfig.API_KEY_ENABLED:
        # API key authentication not configured, allow all requests
        return "disabled"

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header.",
        )

    # Use constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(api_key, APIConfig.API_KEY):
        logger.warning("Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return api_key


# Public endpoints (no authentication required) — env-dependent
_BASE_PUBLIC_PATHS: set[str] = {"/health"}
_DOCS_PATHS: set[str] = {"/docs", "/openapi.json", "/redoc"}
if APIConfig.APP_ENV == "production":
    PUBLIC_PATHS: set[str] = _BASE_PUBLIC_PATHS
else:
    PUBLIC_PATHS = _BASE_PUBLIC_PATHS | _DOCS_PATHS


@app.middleware("http")
async def auth_middleware(request: Request, call_next: Callable):
    """Middleware to check API key for non-public endpoints."""
    # Allow public paths without authentication
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    # Allow OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return await call_next(request)

    # If API key auth is not enabled, allow all requests
    if not APIConfig.API_KEY_ENABLED:
        return await call_next(request)

    # Check for API key in header
    api_key = request.headers.get("X-API-Key")

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header.",
        )

    if not secrets.compare_digest(api_key, APIConfig.API_KEY):
        logger.warning(
            "Invalid API key attempt from %s",
            request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return await call_next(request)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health probe (public endpoint)."""
    return {"status": "ok"}


@app.get("/auth/status")
async def auth_status(api_key: str = Depends(verify_api_key)) -> dict[str, str | bool]:  # noqa: ARG001
    """Check authentication status (requires valid API key if enabled)."""
    return {
        "authenticated": True,
        "api_key_enabled": APIConfig.API_KEY_ENABLED,
    }


app.include_router(weather_router)
app.include_router(single_city_router)
app.include_router(detailed_city_router)
app.include_router(wind_rose_router)
app.include_router(analytics_router)
app.include_router(metadata_router)
app.include_router(anomalies_router)
app.include_router(cities_router)
app.include_router(hungary_router)
app.include_router(providers_router)
