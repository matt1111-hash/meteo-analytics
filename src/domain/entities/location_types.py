"""Location type enum for domain entities."""

from enum import Enum


class LocationType(Enum):
    """
    Universal location types.
    """

    REGION = "region"  # Climate regions (Mediterranean, Continental)
    COUNTRY = "country"  # Countries (Hungary, Germany)
    MICRO_REGION = "micro_region"  # Hungarian micro-regions (Alföld, Nyugat-Dunántúl)
    CITY = "city"  # Cities (Budapest, Berlin)
    COORDINATES = "coordinates"  # Coordinates (47.4979, 19.0402)
    MULTIPLE = "multiple"  # Multiple locations combination
    CUSTOM = "custom"  # User-defined location


__all__ = ["LocationType"]
