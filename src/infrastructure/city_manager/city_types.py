#!/usr/bin/env python3

"""
City Manager - Type Definitions
Global Weather Analyzer project

Part of the city_manager refactoring - split into focused modules.

Note: City dataclass inherits from domain City and adds database-specific
factory methods. This maintains compatibility with existing code while
allowing infrastructure layer to type-check against domain City.
"""

import sqlite3
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Import domain enums
# Import domain City base class
from src.domain.entities.city import City as DomainCity
from src.domain.entities.city import CitySort, RegionType


@dataclass
class City(DomainCity):
    """City entity with database factory methods.

    Inherits from domain City and adds data-layer specific class methods.
    """

    @classmethod
    def from_db_row(cls, row: tuple) -> "City":
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
            timezone=row[10],
        )

    @classmethod
    def from_hungarian_settlement(cls, row: sqlite3.Row) -> "City":
        """Create City object from Hungarian settlement row."""
        return cls(
            id=row["id"],
            city=row["name"],
            lat=row["latitude"],
            lon=row["longitude"],
            country="Magyarország",
            country_code="HU",
            population=row["population"],
            continent="Europe",
            admin_name=row["megye"],
            settlement_type=row["settlement_type"],
            megye=row["megye"],
            jaras=row["jaras"] if row["jaras"] else None,
            climate_zone=row["climate_zone"],
            region_priority=row["region_priority"],
            is_hungarian=True,
            terulet_hektar=row["terulet_hektar"],
            lakasok_szama=row["lakasok_szama"],
        )


@dataclass
class CityQuery:
    """City query parameters with Hungarian support."""

    region_type: RegionType
    region_value: str | None = None
    limit: int = 50
    min_population: int | None = None
    max_population: int | None = None
    sort_by: CitySort = CitySort.POPULATION_DESC
    include_capitals_only: bool = False
    center_lat: float | None = None
    center_lon: float | None = None
    max_distance_km: float | None = None
    exclude_countries: list[str] = field(default_factory=list)
    include_countries: list[str] = field(default_factory=list)

    include_hungarian: bool = True
    hungarian_priority: bool = True
    settlement_types: list[str] = field(default_factory=list)
    hungarian_counties: list[str] = field(default_factory=list)


class CityDatabaseError(Exception):
    """City database specific errors."""

    pass


__all__ = ["City", "CityDatabaseError", "CityQuery", "CitySort", "RegionType"]
