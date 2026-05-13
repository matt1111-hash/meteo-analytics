# ruff: noqa: F401, F403,noqa: I001
"""Compatibility wrapper for wind_rose.py."""

from __future__ import annotations

from fastapi import Depends
from src.api.dependencies import ServiceRegistry, get_services

from . import wind_rose_part3 as wind_rose_impl
from .wind_rose_part1 import DirectionData, WindRoseRequest, WindRoseResponse
from .wind_rose_part2 import _process_wind_rose_data
from .wind_rose_support import *


async def get_wind_rose(
    request: WindRoseRequest,
    services: ServiceRegistry = Depends(get_services),
) -> WindRoseResponse:
    """Delegate to the split implementation with lifespan-managed services."""
    return await wind_rose_impl.get_wind_rose(request, services=services)
