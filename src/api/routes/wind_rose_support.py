# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
"""Wind Rose API route - wind direction and speed distribution analysis."""

from __future__ import annotations  # noqa: I001

import logging
from typing import Any, Dict, List  # noqa: UP035

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.infrastructure.weather.weather_client_core import WeatherClient
from src.infrastructure.container import get_city_manager_port

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weather", tags=["weather", "wind"])


# Pydantic models for request/response
