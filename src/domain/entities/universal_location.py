"""Universal location domain entity."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from src.domain.entities.location import Location
from src.domain.entities.location_types import LocationType


@dataclass
class UniversalLocation:
    """
    Universal location model - complete user freedom.

    Can represent any location type:
    - Climate regions (Mediterranean, Continental)
    - Countries (Hungary, Germany)
    - Hungarian micro-regions (Alföld, Nyugat-Dunántúl)
    - Cities (Budapest, Berlin)
    - Coordinates (47.4979, 19.0402)
    - Multiple locations combination
    """

    type: LocationType
    identifier: Union[str, Tuple[float, float], List[str]]
    display_name: str

    # Geo information (if available)
    coordinates: Optional[Tuple[float, float]] = None
    country_code: Optional[str] = None
    region_code: Optional[str] = None

    # Hierarchical information
    parent_location: Optional["UniversalLocation"] = None
    child_locations: List["UniversalLocation"] = field(default_factory=list)

    # Metadata
    population: Optional[int] = None
    area_km2: Optional[float] = None
    timezone: Optional[str] = None
    climate_zone: Optional[str] = None

    def __str__(self) -> str:
        """String representation."""
        return f"{self.display_name} ({self.type.value})"

    def is_geographical_point(self) -> bool:
        """Check if point location (city or coordinate)."""
        return self.type in [LocationType.CITY, LocationType.COORDINATES]

    def is_area_location(self) -> bool:
        """Check if area location (region, country)."""
        return self.type in [
            LocationType.REGION,
            LocationType.COUNTRY,
            LocationType.MICRO_REGION,
        ]

    def get_coordinates_list(self) -> List[Tuple[float, float]]:
        """
        Get list of coordinates for the location.

        Returns:
            List of coordinates - 1 element for point, multiple for area
        """
        if self.type == LocationType.COORDINATES:
            if isinstance(self.identifier, tuple) and len(self.identifier) == 2:
                return [self.identifier]
        elif self.coordinates:
            return [self.coordinates]
        elif self.child_locations:
            coords = []
            for child in self.child_locations:
                coords.extend(child.get_coordinates_list())
            return coords

        return []

    def contains_location(self, other: "UniversalLocation") -> bool:
        """Check if contains the other location (hierarchical)."""
        if self.type == LocationType.MULTIPLE:
            return other in self.child_locations

        # Hierarchical check
        current = other.parent_location
        while current:
            if current == self:
                return True
            current = current.parent_location

        return False

    def to_simple_location(self) -> Location:
        """
        Convert to simple Location object.

        Returns:
            Location object
        """
        coords = self.coordinates or (0.0, 0.0)
        if isinstance(self.identifier, tuple) and len(self.identifier) == 2:
            coords = self.identifier

        return Location(
            identifier=str(self.identifier),
            display_name=self.display_name,
            latitude=coords[0],
            longitude=coords[1],
            country_code=self.country_code or "HU",
            timezone=self.timezone or "Europe/Budapest",
            metadata={
                "location_type": self.type.value,
                "climate_zone": self.climate_zone,
                "population": self.population,
                "area_km2": self.area_km2,
                "region_code": self.region_code,
                "source": "universal_location",
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "identifier": self.identifier,
            "display_name": self.display_name,
            "coordinates": self.coordinates,
            "country_code": self.country_code,
            "region_code": self.region_code,
            "population": self.population,
            "area_km2": self.area_km2,
            "timezone": self.timezone,
            "climate_zone": self.climate_zone,
            "child_locations_count": len(self.child_locations),
        }


__all__ = ["UniversalLocation"]
