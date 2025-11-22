"""FastAPI entrypoint for Global Weather Analyzer backend."""
from __future__ import annotations

import logging

from fastapi import FastAPI

from src.api.routes.weather import router as weather_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Global Weather Analyzer API")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health probe."""
    return {"status": "ok"}


app.include_router(weather_router)
