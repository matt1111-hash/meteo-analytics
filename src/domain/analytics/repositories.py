"""Repository interfaces for multi-city analytics."""

from __future__ import annotations

from typing import Protocol


class CityRepositoryProtocol(Protocol):
    """Port for city data access and validation."""

    def validate_paths(self) -> None:
        """Validate configured database paths or raise RuntimeError."""

    def get_cities_by_names(self, city_names: list[str]) -> list[dict[str, object]]:
        """Return city dictionaries by explicit city names."""

    def get_cities_for_region(
        self,
        mapped_region: str,
        original_region: str,
        country_codes: list[str],
        limit: int,
        hungarian_mapping: dict[str, list[str]],
    ) -> list[dict[str, object]]:
        """Return city dictionaries with optional Hungarian filtering."""
