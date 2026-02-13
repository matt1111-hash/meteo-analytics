#!/usr/bin/env python3
"""
Application Layer DTOs (Data Transfer Objects).

These DTOs provide a stable contract for the presentation layer.
Following Clean Architecture, presentation should depend on application
layer interfaces, not directly on domain entities.

This allows domain entities to change without breaking presentation.
"""

from .analytics_dto import AnalyticsResultDTO, CityWeatherResultDTO
from .location_dto import LocationDTO, UniversalLocationDTO

__all__ = [
    "AnalyticsResultDTO",
    "CityWeatherResultDTO",
    "LocationDTO",
    "UniversalLocationDTO",
]
