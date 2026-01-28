#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
City Manager - Type Definitions
Global Weather Analyzer project

Part of the city_manager refactoring - split into focused modules.
"""

import sqlite3
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


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
    """City data structure with Hungarian settlements support."""
    id: int
    city: str
    lat: float
    lon: float
    country: str
    country_code: str
    population: Optional[int] = None
    continent: Optional[str] = None
    admin_name: Optional[str] = None
    capital: Optional[str] = None
    timezone: Optional[str] = None

    settlement_type: Optional[str] = None
    megye: Optional[str] = None
    jaras: Optional[str] = None
    climate_zone: Optional[str] = None
    region_priority: Optional[int] = None
    is_hungarian: bool = False
    terulet_hektar: Optional[int] = None
    lakasok_szama: Optional[int] = None

    distance_km: Optional[float] = field(default=None, init=False)
    display_name: Optional[str] = field(default=None, init=False)

    def __post_init__(self):
        """Auto-compute calculated fields."""
        parts = [self.city]

        if self.is_hungarian and self.megye:
            parts.append(f"{self.megye} megye")
        elif self.admin_name and self.admin_name != self.city:
            parts.append(self.admin_name)

        if not self.is_hungarian:
            parts.append(self.country)

        self.display_name = ", ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
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
            "display_name": self.display_name
        }

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'City':
        """Create City object from database row (original format)."""
        return cls(
            id=row[0],
            city=row[1],
            lat=row[2],
            lon=row[3],
            country=row[4],
            country_code=row[5],
            population=row[6],
            continent=row[7],
            admin_name=row[8],
            capital=row[9],
            timezone=row[10]
        )

    @classmethod
    def from_hungarian_settlement(cls, row: sqlite3.Row) -> 'City':
        """Create City object from Hungarian settlement row."""
        return cls(
            id=row['id'],
            city=row['name'],
            lat=row['latitude'],
            lon=row['longitude'],
            country="Magyarország",
            country_code="HU",
            population=row['population'],
            continent="Europe",
            admin_name=row['megye'],
            settlement_type=row['settlement_type'],
            megye=row['megye'],
            jaras=row['jaras'] if row['jaras'] else None,
            climate_zone=row['climate_zone'],
            region_priority=row['region_priority'],
            is_hungarian=True,
            terulet_hektar=row['terulet_hektar'],
            lakasok_szama=row['lakasok_szama']
        )


@dataclass
class CityQuery:
    """City query parameters with Hungarian support."""
    region_type: RegionType
    region_value: Optional[str] = None
    limit: int = 50
    min_population: Optional[int] = None
    max_population: Optional[int] = None
    sort_by: CitySort = CitySort.POPULATION_DESC
    include_capitals_only: bool = False
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    max_distance_km: Optional[float] = None
    exclude_countries: List[str] = field(default_factory=list)
    include_countries: List[str] = field(default_factory=list)

    include_hungarian: bool = True
    hungarian_priority: bool = True
    settlement_types: List[str] = field(default_factory=list)
    hungarian_counties: List[str] = field(default_factory=list)


class CityDatabaseError(Exception):
    """City database specific errors."""
    pass


__all__ = [
    'RegionType',
    'CitySort',
    'City',
    'CityQuery',
    'CityDatabaseError'
]
