#!/usr/bin/env python3
"""
CityInfo - Domain Value Object for City Information.

This is a domain-level value object that represents city information
without depending on data layer types. It contains only the essential
fields needed by the domain layer.

For full city data with all fields, use src.data.city_types.City.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class CityInfo:
    """
    Immutable value object representing basic city information.

    This is a Clean Architecture compliant domain value object.
    It contains only the essential city information needed by
    domain entities and use cases.

    Attributes:
        id: Unique city identifier
        city: City name
        lat: Geographic latitude
        lon: Geographic longitude
        country_code: ISO 3166-1 alpha-2 country code (e.g., "HU", "DE")
        country: Full country name
        display_name: Human-readable display name with region info
        population: City population (optional)
        timezone: Timezone identifier (optional)
        admin_name: Administrative region name (optional)
        is_hungarian: Whether this is a Hungarian settlement
    """

    id: int
    city: str
    lat: float
    lon: float
    country_code: str
    country: str = ""
    display_name: Optional[str] = None
    population: Optional[int] = None
    timezone: Optional[str] = None
    admin_name: Optional[str] = None
    is_hungarian: bool = False

    def __post_init__(self) -> None:
        """Compute derived fields after initialization."""
        # Use object.__setattr__ because frozen=True
        if self.display_name is None:
            parts = [self.city]
            if self.admin_name and self.admin_name != self.city:
                parts.append(self.admin_name)
            if not self.is_hungarian and self.country:
                parts.append(self.country)
            object.__setattr__(self, "display_name", ", ".join(parts))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "city": self.city,
            "lat": self.lat,
            "lon": self.lon,
            "country_code": self.country_code,
            "country": self.country,
            "display_name": self.display_name,
            "population": self.population,
            "timezone": self.timezone,
            "admin_name": self.admin_name,
            "is_hungarian": self.is_hungarian,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CityInfo":
        """
        Create CityInfo from dictionary.

        Args:
            data: Dictionary with city information

        Returns:
            CityInfo instance
        """
        return cls(
            id=data["id"],
            city=data["city"],
            lat=data["lat"],
            lon=data["lon"],
            country_code=data.get("country_code", ""),
            country=data.get("country", ""),
            display_name=data.get("display_name"),
            population=data.get("population"),
            timezone=data.get("timezone"),
            admin_name=data.get("admin_name"),
            is_hungarian=data.get("is_hungarian", False),
        )


__all__ = ["CityInfo"]
