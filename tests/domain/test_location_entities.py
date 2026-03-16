"""Tests for location entities and factories."""

from src.domain.entities.location import Location
from src.domain.entities.location_factories import (
    create_location,
    create_location_from_coordinates,
    create_universal_location,
)
from src.domain.entities.location_types import LocationType
from src.domain.entities.universal_location import UniversalLocation


def test_location_to_dict_and_metadata_helpers() -> None:
    """Location exposes compatibility helpers and derived dictionary data."""
    location = Location(
        identifier="budapest",
        display_name="Budapest",
        latitude=47.4979,
        longitude=19.0402,
        metadata={
            "region": "Közép-Magyarország",
            "county": "Pest",
            "climate_zone": "continental",
            "source": "manual",
            "bounds": (1.0, 2.0, 3.0, 4.0),
        },
    )

    assert str(location) == "Budapest (47.4979, 19.0402)"
    assert location.get_coordinates() == (47.4979, 19.0402)
    assert location.get_region() == "Közép-Magyarország"
    assert location.get_county() == "Pest"
    assert location.get_climate_zone() == "continental"
    assert location.get_source() == "manual"
    assert location.get_bounds() == (1.0, 2.0, 3.0, 4.0)
    assert location.is_hungarian_location() is True
    assert location.to_dict()["coordinates"] == (47.4979, 19.0402)


def test_location_from_dict_supports_legacy_fields() -> None:
    """Legacy dict payloads are converted into metadata."""
    location = Location.from_dict(
        {
            "identifier": "berlin",
            "display_name": "Berlin",
            "latitude": 52.52,
            "longitude": 13.405,
            "country_code": "DE",
            "timezone": "Europe/Berlin",
            "region": "Berlin",
            "county": "Berlin",
            "climate_zone": "temperate",
            "source": "legacy",
            "bounds": (0.0, 1.0, 2.0, 3.0),
        }
    )

    assert location.country_code == "DE"
    assert location.timezone == "Europe/Berlin"
    assert location.metadata["source"] == "legacy"
    assert location.metadata["bounds"] == (0.0, 1.0, 2.0, 3.0)
    assert location.is_hungarian_location() is False


def test_location_factory_methods_cover_coordinate_and_city_info_paths() -> None:
    """Location factories produce expected specialized location objects."""
    generated = Location.from_coordinates(47.0, 19.0)
    assert generated.identifier == "coord_47.0000_19.0000"
    assert "Koordináta" in generated.display_name

    custom = create_location("id-1", "Custom", 1.5, 2.5, country_code="RO")
    assert custom.country_code == "RO"

    from_factory = create_location_from_coordinates(10.0, 20.0, display_name="Pinned")
    assert from_factory.display_name == "Pinned"

    class CityInfoStub:
        """Minimal object matching the attributes used by Location.from_city_info."""

        id = 7
        city = "Szeged"
        lat = 46.253
        lon = 20.141
        country_code = "HU"
        display_name = "Szeged, HU"
        population = 160000
        timezone = None
        continent = "Europe"
        admin_name = "Csongrád-Csanád"
        capital = None

    city_info = CityInfoStub()
    from_city = Location.from_city_info(city_info)

    assert from_city.display_name == "Szeged, HU"
    assert from_city.metadata["city_id"] == 7
    assert from_city.metadata["source"] == "city_manager"
    assert from_city.timezone == "Europe/Budapest"


def test_universal_location_handles_points_areas_and_hierarchy() -> None:
    """UniversalLocation returns coordinates and containment consistently."""
    coordinate_location = UniversalLocation(
        type=LocationType.COORDINATES,
        identifier=(47.5, 19.0),
        display_name="Point",
    )
    city_child = UniversalLocation(
        type=LocationType.CITY,
        identifier="bp",
        display_name="Budapest",
        coordinates=(47.4979, 19.0402),
    )
    area = UniversalLocation(
        type=LocationType.REGION,
        identifier="central",
        display_name="Central",
        child_locations=[city_child],
    )
    city_child.parent_location = area
    multiple = UniversalLocation(
        type=LocationType.MULTIPLE,
        identifier=["bp", "point"],
        display_name="Multiple",
        child_locations=[city_child, coordinate_location],
    )

    assert str(coordinate_location) == "Point (coordinates)"
    assert coordinate_location.is_geographical_point() is True
    assert area.is_area_location() is True
    assert coordinate_location.get_coordinates_list() == [(47.5, 19.0)]
    assert area.get_coordinates_list() == [(47.4979, 19.0402)]
    assert area.contains_location(city_child) is True
    assert multiple.contains_location(city_child) is True
    assert coordinate_location.contains_location(city_child) is False


def test_universal_location_to_simple_location_and_factories() -> None:
    """UniversalLocation factory and conversion preserve key metadata."""
    location = create_universal_location(
        "city",
        "debrecen",
        "Debrecen",
        coordinates=(47.5316, 21.6273),
        country_code="HU",
        climate_zone="continental",
        population=200000,
        area_km2=461.0,
        region_code="hajdu-bihar",
        timezone="Europe/Budapest",
    )

    assert location.type is LocationType.CITY
    simple = location.to_simple_location()
    serialized = location.to_dict()

    assert simple.display_name == "Debrecen"
    assert simple.metadata["location_type"] == "city"
    assert simple.metadata["population"] == 200000
    assert serialized["child_locations_count"] == 0
    assert serialized["coordinates"] == (47.5316, 21.6273)
