"""Repository interfaces for multi-city analytics."""

from __future__ import annotations

from typing import Dict, List, Protocol


class CityRepositoryProtocol(Protocol):
    """Port for city data access and validation."""

    def validate_paths(self) -> None:
        """Validate configured database paths or raise RuntimeError."""

    def get_cities_by_names(self, city_names: List[str]) -> List[Dict[str, object]]:
        """Return city dictionaries by explicit city names."""

    def get_cities_for_region(
        self,
        mapped_region: str,
        original_region: str,
        country_codes: List[str],
        limit: int,
        hungarian_mapping: Dict[str, List[str]],
    ) -> List[Dict[str, object]]:
        """Return city dictionaries with optional Hungarian filtering."""
