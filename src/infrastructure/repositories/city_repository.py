# mypy: ignore-errors
"""SQLite-backed city repository with regional filtering and validation."""

from __future__ import annotations

from pathlib import Path

from src.domain.analytics.repositories import CityRepositoryProtocol

from .city_repository_paths import CityRepositoryPaths
from .city_repository_queries import CityRepositoryQueries


class CityRepository(CityRepositoryProtocol):
    """Provides city lookups with Hungarian regional filtering support."""

    def __init__(
        self,
        db_path: Path | None = None,
        hungarian_db_path: Path | None = None,
    ):
        """Initialize city repository with optional custom paths."""
        self._paths = CityRepositoryPaths(db_path, hungarian_db_path)
        self._queries: CityRepositoryQueries | None = None

    @property
    def db_path(self) -> Path:
        """Get global cities database path."""
        return self._paths.db_path

    @db_path.setter
    def db_path(self, value: Path) -> None:
        """Set global cities database path and update queries."""
        self._paths.db_path = value
        self._update_queries()

    @property
    def hungarian_db_path(self) -> Path:
        """Get Hungarian settlements database path."""
        return self._paths.hungarian_db_path

    @hungarian_db_path.setter
    def hungarian_db_path(self, value: Path) -> None:
        """Set Hungarian settlements database path and update queries."""
        self._paths.hungarian_db_path = value
        self._update_queries()

    def _update_queries(self) -> None:
        """Update queries object with current paths."""
        self._queries = CityRepositoryQueries(self._paths.db_path, self._paths.hungarian_db_path)

    def validate_paths(self) -> None:
        """Validate that at least one database is available."""
        self._paths.validate_paths()

    def get_cities_by_names(self, city_names: list[str]) -> list[dict[str, object]]:
        """Fetch cities by explicit city names (case-insensitive)."""
        if self._queries is None:
            self._update_queries()
        return self._queries.get_cities_by_names(city_names)

    def get_cities_for_region(
        self,
        mapped_region: str,
        original_region: str,
        country_codes: list[str],
        limit: int,
        hungarian_mapping: dict[str, list[str]],
    ) -> list[dict[str, object]]:
        """Fetch cities for a region with optional Hungarian filtering."""
        if self._queries is None:
            self._update_queries()
        return self._queries.get_cities_for_region(
            mapped_region, original_region, country_codes, limit, hungarian_mapping
        )

    def autocomplete_city_name(self, query: str, limit: int = 20) -> list[dict[str, object]]:
        """Autocomplete city names by partial match."""
        if self._queries is None:
            self._update_queries()
        return self._queries.autocomplete_city_name(query, limit)


__all__ = ["CityRepository"]
