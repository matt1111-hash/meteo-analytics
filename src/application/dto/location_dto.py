#!/usr/bin/env python3
"""
Location DTOs - Data Transfer Objects for Location Information.

These DTOs provide a stable interface for the presentation layer
to work with location data without depending on domain entities.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

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
    metadata: Dict[str, Any] = field(default_factory=dict)

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

    def to_dict(self) -> Dict[str, Any]:
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

    def get_coordinates(self) -> Tuple[float, float]:
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
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_domain(cls, location: UniversalLocation) -> "UniversalLocationDTO":
        """Create DTO from domain entity."""
        return cls(
            identifier=location.identifier,
            display_name=location.display_name,
            latitude=location.latitude,
            longitude=location.longitude,
            location_type=location.location_type.value,
            country_code=location.country_code,
            timezone=location.timezone,
            metadata=location.metadata,
        )

    def to_dict(self) -> Dict[str, Any]:
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

    def get_coordinates(self) -> Tuple[float, float]:
        """Get coordinates as tuple."""
        return (self.latitude, self.longitude)


__all__ = ["LocationDTO", "UniversalLocationDTO"]
