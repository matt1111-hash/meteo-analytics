"""Tests for RegionResolverService."""

from __future__ import annotations

import pytest
from src.domain.analytics.services.region_resolver import RegionResolverService


def test_exact_region_code_maps_to_canonical() -> None:
    resolver = RegionResolverService()
    assert resolver.resolve_region_name("HU") == "Hungary"
    assert resolver.resolve_region_name("EU") == "Europe"


def test_case_insensitive_mapping_is_supported() -> None:
    resolver = RegionResolverService()
    assert resolver.resolve_region_name("global") == "Global"
    assert resolver.resolve_region_name("magyarország") == "Hungary"


def test_partial_hungarian_region_names_map_to_hungary() -> None:
    resolver = RegionResolverService()
    assert resolver.resolve_region_name("Észak-Magyarország") == "Hungary"
    assert resolver.resolve_region_name("dél-alföld") == "Hungary"


def test_county_names_map_to_hungary() -> None:
    resolver = RegionResolverService()
    assert resolver.resolve_region_name("Pest") == "Hungary"
    assert resolver.resolve_region_name("borsod-abaúj-zemplén") == "Hungary"


def test_empty_input_raises_value_error() -> None:
    resolver = RegionResolverService()
    with pytest.raises(ValueError, match="Üres régió név"):
        resolver.resolve_region_name("")


def test_unknown_region_raises_value_error() -> None:
    resolver = RegionResolverService()
    with pytest.raises(ValueError):
        resolver.resolve_region_name("Atlantis")
