"""Location domain entity."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from src.domain.entities.location_types import LocationType


@dataclass
class Location:
    """
    Simple location model - HungarianLocationSelector compatible.

    This is a backward compatibility class for Hungarian map components.
    The HungarianLocationSelector expects this format.

    Attributes:
        identifier: Location identifier (city name, region code, etc.)
        display_name: Display name (user-friendly)
        latitude: Geographic latitude
        longitude: Geographic longitude
        country_code: Country code (ISO alpha-2, e.g. "HU")
        timezone: Timezone (e.g. "Europe/Budapest")
        metadata: Additional information in dictionary
    """
    identifier: str
    display_name: str
    latitude: float
    longitude: float
    country_code: str = "HU"
    timezone: str = "Europe/Budapest"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.display_name} ({self.latitude:.4f}, {self.longitude:.4f})"

    def get_coordinates(self) -> Tuple[float, float]:
        """Get coordinates as tuple."""
        return (self.latitude, self.longitude)

    def get_region(self) -> Optional[str]:
        """Get region name from metadata."""
        return self.metadata.get('region')

    def get_county(self) -> Optional[str]:
        """Get county name from metadata."""
        return self.metadata.get('county')

    def get_climate_zone(self) -> Optional[str]:
        """Get climate zone from metadata."""
        return self.metadata.get('climate_zone')

    def get_source(self) -> Optional[str]:
        """Get data source from metadata."""
        return self.metadata.get('source')

    def get_bounds(self) -> Optional[Tuple[float, float, float, float]]:
        """Get area bounds from metadata (minx, miny, maxx, maxy)."""
        return self.metadata.get('bounds')

    def is_hungarian_location(self) -> bool:
        """Check if Hungarian location."""
        return self.country_code.upper() == "HU"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'identifier': self.identifier,
            'display_name': self.display_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'country_code': self.country_code,
            'timezone': self.timezone,
            'metadata': self.metadata,
            'coordinates': self.get_coordinates(),
            'region': self.get_region(),
            'county': self.get_county(),
            'climate_zone': self.get_climate_zone(),
            'source': self.get_source(),
            'bounds': self.get_bounds(),
            'is_hungarian': self.is_hungarian_location()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """
        Create Location from dictionary.

        Args:
            data: Dictionary data

        Returns:
            Location object
        """
        identifier = data['identifier']
        display_name = data['display_name']
        latitude = data['latitude']
        longitude = data['longitude']

        country_code = data.get('country_code', 'HU')
        timezone = data.get('timezone', 'Europe/Budapest')
        metadata = data.get('metadata', {})

        # Old format compatibility
        if not metadata:
            extra_fields = ['region', 'county', 'climate_zone', 'source', 'bounds']
            for field_name in extra_fields:
                if field_name in data and data[field_name] is not None:
                    metadata[field_name] = data[field_name]

        return cls(
            identifier=identifier,
            display_name=display_name,
            latitude=latitude,
            longitude=longitude,
            country_code=country_code,
            timezone=timezone,
            metadata=metadata
        )

    @classmethod
    def from_coordinates(
        cls,
        latitude: float,
        longitude: float,
        display_name: Optional[str] = None,
        **kwargs
    ) -> 'Location':
        """
        Create Location from coordinates.

        Args:
            latitude: Geographic latitude
            longitude: Geographic longitude
            display_name: Display name (optional)
            **kwargs: Additional parameters

        Returns:
            Location object
        """
        if not display_name:
            display_name = f"Koordináta ({latitude:.4f}, {longitude:.4f})"

        identifier = f"coord_{latitude:.4f}_{longitude:.4f}"

        return cls(
            identifier=identifier,
            display_name=display_name,
            latitude=latitude,
            longitude=longitude,
            **kwargs
        )

    @classmethod
    def from_city_info(cls, city_info: 'CityInfo') -> 'Location':
        """
        Create Location from CityInfo.

        Args:
            city_info: CityInfo object

        Returns:
            Location object
        """
        from src.domain.entities.city_info import CityInfo

        return cls(
            identifier=city_info.city,
            display_name=city_info.get_display_name(),
            latitude=city_info.latitude,
            longitude=city_info.longitude,
            country_code=city_info.country_code,
            timezone=city_info.timezone or "Europe/Budapest",
            metadata={
                'city_id': city_info.id,
                'population': city_info.population,
                'continent': city_info.continent,
                'admin_name': city_info.admin_name,
                'capital': city_info.capital,
                'source': 'city_manager'
            }
        )


__all__ = ['Location']
