#!/usr/bin/env python3
"""Tests for LocationDTO and UniversalLocationDTO."""

from __future__ import annotations

from src.application.dto.location_dto import LocationDTO, UniversalLocationDTO
from src.domain.entities.location import Location
from src.domain.entities.location_types import LocationType
from src.domain.entities.universal_location import UniversalLocation


class TestLocationDTOFromDomain:
    """Tests for LocationDTO.from_domain."""

    def test_from_domain_creates_dto(self) -> None:
        location = Location(
            identifier="budapest",
            display_name="Budapest",
            latitude=47.4979,
            longitude=19.0402,
            country_code="HU",
            timezone="Europe/Budapest",
            metadata={"region": "Közép-Magyarország"},
        )
        dto = LocationDTO.from_domain(location)

        assert dto.identifier == "budapest"
        assert dto.display_name == "Budapest"
        assert dto.latitude == 47.4979
        assert dto.longitude == 19.0402
        assert dto.country_code == "HU"
        assert dto.timezone == "Europe/Budapest"
        assert dto.metadata == {"region": "Közép-Magyarország"}

    def test_from_domain_preserves_non_hungarian(self) -> None:
        location = Location(
            identifier="vienna",
            display_name="Vienna",
            latitude=48.21,
            longitude=16.37,
            country_code="AT",
            timezone="Europe/Vienna",
        )
        dto = LocationDTO.from_domain(location)

        assert dto.country_code == "AT"


class TestLocationDTOToDict:
    """Tests for LocationDTO.to_dict."""

    def test_to_dict_returns_complete_mapping(self) -> None:
        dto = LocationDTO(
            identifier="budapest",
            display_name="Budapest",
            latitude=47.4979,
            longitude=19.0402,
            country_code="HU",
            timezone="Europe/Budapest",
            metadata={"key": "value"},
        )
        result = dto.to_dict()

        assert result == {
            "identifier": "budapest",
            "display_name": "Budapest",
            "latitude": 47.4979,
            "longitude": 19.0402,
            "country_code": "HU",
            "timezone": "Europe/Budapest",
            "metadata": {"key": "value"},
        }


class TestLocationDTOGetCoordinates:
    """Tests for LocationDTO.get_coordinates."""

    def test_get_coordinates_returns_lat_lon_tuple(self) -> None:
        dto = LocationDTO(
            identifier="test",
            display_name="Test",
            latitude=12.5,
            longitude=34.7,
        )
        assert dto.get_coordinates() == (12.5, 34.7)


class TestLocationDTOIsHungarian:
    """Tests for LocationDTO.is_hungarian."""

    def test_hungarian_code_returns_true(self) -> None:
        dto = LocationDTO(
            identifier="bp",
            display_name="Bp",
            latitude=0.0,
            longitude=0.0,
            country_code="HU",
        )
        assert dto.is_hungarian() is True

    def test_lowercase_hu_returns_true(self) -> None:
        dto = LocationDTO(
            identifier="bp",
            display_name="Bp",
            latitude=0.0,
            longitude=0.0,
            country_code="hu",
        )
        assert dto.is_hungarian() is True

    def test_non_hungarian_code_returns_false(self) -> None:
        dto = LocationDTO(
            identifier="vienna",
            display_name="Vienna",
            latitude=0.0,
            longitude=0.0,
            country_code="AT",
        )
        assert dto.is_hungarian() is False


class TestUniversalLocationDTOFromDomain:
    """Tests for UniversalLocationDTO.from_domain."""

    def test_from_domain_with_coordinates(self) -> None:
        loc = UniversalLocation(
            type=LocationType.CITY,
            identifier="budapest",
            display_name="Budapest",
            coordinates=(47.4979, 19.0402),
            country_code="HU",
            timezone="Europe/Budapest",
            region_code="HU-BU",
            population=1750000,
            area_km2=525.0,
            climate_zone="Continental",
        )
        dto = UniversalLocationDTO.from_domain(loc)

        assert dto.identifier == "budapest"
        assert dto.display_name == "Budapest"
        assert dto.latitude == 47.4979
        assert dto.longitude == 19.0402
        assert dto.location_type == "city"
        assert dto.country_code == "HU"
        assert dto.timezone == "Europe/Budapest"
        assert dto.metadata["region_code"] == "HU-BU"
        assert dto.metadata["population"] == 1750000
        assert dto.metadata["area_km2"] == 525.0
        assert dto.metadata["climate_zone"] == "Continental"
        assert dto.metadata["child_locations_count"] == 0

    def test_from_domain_with_tuple_identifier_as_coordinates(self) -> None:
        loc = UniversalLocation(
            type=LocationType.COORDINATES,
            identifier=(47.0, 19.0),
            display_name="Point",
            country_code=None,
            timezone=None,
        )
        dto = UniversalLocationDTO.from_domain(loc)

        assert dto.latitude == 47.0
        assert dto.longitude == 19.0
        assert dto.identifier == "(47.0, 19.0)"
        assert dto.country_code == "HU"
        assert dto.timezone == "Europe/Budapest"

    def test_from_domain_with_child_locations(self) -> None:
        child = UniversalLocation(
            type=LocationType.CITY,
            identifier="child1",
            display_name="Child City",
            coordinates=(10.0, 20.0),
        )
        parent = UniversalLocation(
            type=LocationType.REGION,
            identifier="region1",
            display_name="Region",
            coordinates=None,
            child_locations=[child],
        )
        dto = UniversalLocationDTO.from_domain(parent)

        assert dto.latitude == 0.0
        assert dto.longitude == 0.0
        assert dto.metadata["child_locations_count"] == 1

    def test_from_domain_defaults_none_country(self) -> None:
        loc = UniversalLocation(
            type=LocationType.CITY,
            identifier="x",
            display_name="X",
            coordinates=(1.0, 2.0),
            country_code=None,
            timezone=None,
        )
        dto = UniversalLocationDTO.from_domain(loc)

        assert dto.country_code == "HU"
        assert dto.timezone == "Europe/Budapest"


class TestUniversalLocationDTOToDict:
    """Tests for UniversalLocationDTO.to_dict."""

    def test_to_dict_returns_complete_mapping(self) -> None:
        dto = UniversalLocationDTO(
            identifier="test",
            display_name="Test",
            latitude=1.0,
            longitude=2.0,
            location_type="city",
            country_code="HU",
            timezone="Europe/Budapest",
            metadata={"pop": 100},
        )
        result = dto.to_dict()

        assert result == {
            "identifier": "test",
            "display_name": "Test",
            "latitude": 1.0,
            "longitude": 2.0,
            "location_type": "city",
            "country_code": "HU",
            "timezone": "Europe/Budapest",
            "metadata": {"pop": 100},
        }


class TestUniversalLocationDTOGetCoordinates:
    """Tests for UniversalLocationDTO.get_coordinates."""

    def test_get_coordinates_returns_tuple(self) -> None:
        dto = UniversalLocationDTO(
            identifier="x",
            display_name="X",
            latitude=5.5,
            longitude=6.6,
            location_type="coordinates",
        )
        assert dto.get_coordinates() == (5.5, 6.6)
