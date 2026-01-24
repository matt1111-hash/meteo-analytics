"""Factory functions for location entities."""
from typing import Optional, Tuple, Union

from src.domain.entities.location_types import LocationType
from src.domain.entities.location import Location
from src.domain.entities.universal_location import UniversalLocation
from src.domain.entities.city_info import CityInfo


def create_universal_location(
    location_type: Union[LocationType, str],
    identifier: Union[str, Tuple[float, float], list[str]],
    display_name: str,
    **kwargs
) -> UniversalLocation:
    """
    UniversalLocation factory - user-friendly.
    """
    if isinstance(location_type, str):
        location_type = LocationType(location_type.lower())

    return UniversalLocation(
        type=location_type,
        identifier=identifier,
        display_name=display_name,
        **kwargs
    )


def create_location(
    identifier: str,
    display_name: str,
    latitude: float,
    longitude: float,
    **kwargs
) -> Location:
    """
    Location factory function - HungarianLocationSelector compatible.
    """
    return Location(
        identifier=identifier,
        display_name=display_name,
        latitude=latitude,
        longitude=longitude,
        **kwargs
    )


def create_location_from_coordinates(
    latitude: float,
    longitude: float,
    display_name: Optional[str] = None,
    **kwargs
) -> Location:
    """
    Create Location from coordinates - for map components.
    """
    return Location.from_coordinates(latitude, longitude, display_name, **kwargs)


__all__ = [
    'create_universal_location',
    'create_location',
    'create_location_from_coordinates'
]
