#!/usr/bin/env python3
"""
Location DTOs - Data Transfer Objects for Location Information.

These DTOs provide a stable interface for the presentation layer
to work with location data without depending on domain entities.
"""

from dataclasses import dataclass, field
from typing import Any

from src.domain.entities.location import Location
from src.domain.entities.universal_location import UniversalLocation


@dataclass
class LocationDTO:
    """
    DTO for basic location information.

    Provides a stable interface for presentation layer.
    """

    identifier: str
    display_name: str
    latitude: float
    longitude: float
    country_code: str = "HU"
    timezone: str = "Europe/Budapest"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_domain(cls, location: Location) -> "LocationDTO":
        """Create DTO from domain entity."""
        return cls(
            identifier=location.identifier,
            display_name=location.display_name,
            latitude=location.latitude,
            longitude=location.longitude,
            country_code=location.country_code,
            timezone=location.timezone,
            metadata=location.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "identifier": self.identifier,
            "display_name": self.display_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "country_code": self.country_code,
            "timezone": self.timezone,
            "metadata": self.metadata,
        }

    def get_coordinates(self) -> tuple[float, float]:
        """Get coordinates as tuple."""
        return (self.latitude, self.longitude)

    def is_hungarian(self) -> bool:
        """Check if Hungarian location."""
        return self.country_code.upper() == "HU"


@dataclass
class UniversalLocationDTO:
    """
    DTO for universal location information.

    Provides a stable interface for presentation layer.
    """

    identifier: str
    display_name: str
    latitude: float
    longitude: float
    location_type: str  # Location type as string
    country_code: str = "HU"
    timezone: str = "Europe/Budapest"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_domain(cls, location: UniversalLocation) -> "UniversalLocationDTO":
        """Create DTO from domain entity."""
        latitude = 0.0
        longitude = 0.0
        if location.coordinates:
            latitude, longitude = location.coordinates
        elif isinstance(location.identifier, tuple) and len(location.identifier) == 2:  # noqa: PLR2004
            latitude, longitude = location.identifier

        return cls(
            identifier=str(location.identifier),
            display_name=location.display_name,
            latitude=latitude,
            longitude=longitude,
            location_type=location.type.value,
            country_code=location.country_code or "HU",
            timezone=location.timezone or "Europe/Budapest",
            metadata={
                "region_code": location.region_code,
                "population": location.population,
                "area_km2": location.area_km2,
                "climate_zone": location.climate_zone,
                "child_locations_count": len(location.child_locations),
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "identifier": self.identifier,
            "display_name": self.display_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_type": self.location_type,
            "country_code": self.country_code,
            "timezone": self.timezone,
            "metadata": self.metadata,
        }

    def get_coordinates(self) -> tuple[float, float]:
        """Get coordinates as tuple."""
        return (self.latitude, self.longitude)


__all__ = ["LocationDTO", "UniversalLocationDTO"]
