#!/usr/bin/env python3
"""
City Adapter - Convert data layer City to domain CityInfo.

This adapter transforms data layer city types to domain value objects,
following Clean Architecture's dependency direction (outer → inner).
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.data.city_types import City
    from src.domain.value_objects.city_info import CityInfo


def city_to_city_info(city: "City") -> "CityInfo":
    """
    Convert data.City to domain.CityInfo.

    This adapter function transforms the data layer's City entity
    into a domain-level CityInfo value object.

    Args:
        city: City instance from data.city_types

    Returns:
        CityInfo value object for domain layer use
    """
    from src.domain.value_objects.city_info import CityInfo

    return CityInfo(
        id=city.id,
        city=city.city,
        lat=city.lat,
        lon=city.lon,
        country_code=city.country_code,
        country=city.country,
        display_name=city.display_name,
        population=city.population,
        timezone=city.timezone,
        admin_name=city.admin_name,
        is_hungarian=city.is_hungarian,
    )


def city_dict_to_city_info(data: dict) -> "CityInfo":
    """
    Convert city dictionary to domain.CityInfo.

    Args:
        data: Dictionary with city data

    Returns:
        CityInfo value object
    """
    from src.domain.value_objects.city_info import CityInfo

    return CityInfo(
        id=data.get("id", 0),
        city=data.get("city", ""),
        lat=data.get("lat", 0.0),
        lon=data.get("lon", 0.0),
        country_code=data.get("country_code", ""),
        country=data.get("country", ""),
        display_name=data.get("display_name"),
        population=data.get("population"),
        timezone=data.get("timezone"),
        admin_name=data.get("admin_name"),
        is_hungarian=data.get("is_hungarian", False),
    )


__all__ = ["city_to_city_info", "city_dict_to_city_info"]
