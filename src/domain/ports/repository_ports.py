"""Repository and profile-related domain ports."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class CityRepositoryPort(Protocol):
    """Port for city data repository operations."""

    @property
    def db_path(self) -> Path: ...  # noqa: D102

    @property
    def hungarian_db_path(self) -> Path: ...  # noqa: D102

    def validate_paths(self) -> bool: ...  # noqa: D102
    def get_cities_for_region(  # noqa: D102
        self,
        mapped_region: str,
        original_region: str,
        country_codes: list[str],
        limit: int,
        hungarian_mapping: dict[str, str],
    ) -> list[dict[str, Any]]: ...
    def search_cities(self, query: str, limit: int = 20) -> list[dict[str, Any]]: ...  # noqa: D102
    def autocomplete_city_name(  # noqa: D102
        self, query: str, limit: int = 20
    ) -> list[dict[str, Any]]: ...
    def get_city_by_id(self, city_id: int) -> dict[str, Any] | None: ...  # noqa: D102
    def get_city_by_coordinates(  # noqa: D102
        self,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any] | None: ...
    def close(self) -> None: ...  # noqa: D102


class AnomalyProfilePort(Protocol):
    """Port for anomaly profile management operations."""

    def get_active_profile(self) -> dict[str, Any]: ...  # noqa: D102
    def get_profile(self, profile_name: str) -> dict[str, Any] | None: ...  # noqa: D102
    def get_all_profiles(self) -> list[dict[str, Any]]: ...  # noqa: D102
    def create_profile(self, name: str, data: dict[str, Any]) -> bool: ...  # noqa: D102
    def update_profile(self, name: str, data: dict[str, Any]) -> bool: ...  # noqa: D102
    def delete_profile(self, name: str) -> bool: ...  # noqa: D102
