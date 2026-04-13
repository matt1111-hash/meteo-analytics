#!/usr/bin/env python3

"""
City Entity - Domain Layer

This module defines the core City entity for the domain layer.
It contains only domain logic - no database-specific code.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RegionType(Enum):
    """Region type enumeration."""

    GLOBAL = "global"
    CONTINENT = "continent"
    COUNTRY = "country"
    REGION = "region"
    CUSTOM = "custom"
    HUNGARIAN_SETTLEMENT = "hungarian_settlement"


class CitySort(Enum):
    """City sorting options."""

    POPULATION_DESC = "population_desc"
    POPULATION_ASC = "population_asc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    DISTANCE_ASC = "distance_asc"
    HUNGARIAN_PRIORITY = "hungarian_priority"


@dataclass
class City:
    """City data structure with Hungarian settlements support.

    This is the domain entity - pure Python, no framework dependencies.
    Database-specific factory methods are in src.data.city_types.
    """

    id: int
    city: str
    lat: float
    lon: float
    country: str
    country_code: str
    population: int | None = None
    continent: str | None = None
    admin_name: str | None = None
    capital: str | None = None
    timezone: str | None = None

    settlement_type: str | None = None
    megye: str | None = None
    jaras: str | None = None
    climate_zone: str | None = None
    region_priority: int | None = None
    is_hungarian: bool = False
    terulet_hektar: int | None = None
    lakasok_szama: int | None = None

    distance_km: float | None = field(default=None, init=False)
    display_name: str | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Auto-compute calculated fields."""
        parts = [self.city]

        if self.is_hungarian and self.megye:
            parts.append(f"{self.megye} megye")
        elif self.admin_name and self.admin_name != self.city:
            parts.append(self.admin_name)

        if not self.is_hungarian:
            parts.append(self.country)

        self.display_name = ", ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert City object to dictionary."""
        return {
            "id": self.id,
            "city": self.city,
            "lat": self.lat,
            "lon": self.lon,
            "country": self.country,
            "country_code": self.country_code,
            "population": self.population,
            "continent": self.continent,
            "admin_name": self.admin_name,
            "capital": self.capital,
            "timezone": self.timezone,
            "settlement_type": self.settlement_type,
            "megye": self.megye,
            "jaras": self.jaras,
            "climate_zone": self.climate_zone,
            "region_priority": self.region_priority,
            "is_hungarian": self.is_hungarian,
            "terulet_hektar": self.terulet_hektar,
            "lakasok_szama": self.lakasok_szama,
            "distance_km": self.distance_km,
            "display_name": self.display_name,
        }


__all__ = ["City", "CitySort", "RegionType"]
