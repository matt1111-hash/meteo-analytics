"""FastAPI entrypoint for Global Weather Analyzer backend."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.analytics import router as analytics_router
from src.api.routes.anomalies import router as anomalies_router
from src.api.routes.cities import router as cities_router
from src.api.routes.detailed_city import router as detailed_city_router
from src.api.routes.hungary import router as hungary_router
from src.api.routes.metadata import router as metadata_router
from src.api.routes.single_city import router as single_city_router
from src.api.routes.weather import router as weather_router
from src.api.routes.wind_rose import router as wind_rose_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Global Weather Analyzer API")

# CORS middleware - allow frontend on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health probe."""
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
