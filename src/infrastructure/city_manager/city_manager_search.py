#!/usr/bin/env python3
# mypy: ignore-errors

"""
City Manager - Global and Unified Search
Global Weather Analyzer project

Part of the city_manager refactoring - split into focused modules.
"""

import logging
from typing import Any

from .city_manager_hungarian import CityManagerHungarian
from .city_types import City

logger = logging.getLogger(__name__)


class CityManagerSearch(CityManagerHungarian):
    """Global cities and unified search methods."""

    MAX_SEARCH_LIMIT = 500

    @staticmethod
    def _safe_limit(limit: int) -> int:
        """Coerce and cap limit to safe integer range."""
        return max(1, min(int(limit), CityManagerSearch.MAX_SEARCH_LIMIT))

    @staticmethod
    def _find_exact_match(city_name: str, candidates: list[City]) -> tuple[float, float] | None:
        """Return coordinates for an exact case-insensitive city match."""
        exact_match = next(
            (city for city in candidates if city.city.lower() == city_name.lower()),
            None,
        )
        if not exact_match:
            return None
        return (exact_match.lat, exact_match.lon)

    @staticmethod
    def _find_best_match(candidates: list[City], key_func) -> tuple[float, float] | None:
        """Return coordinates for the best ranked candidate."""
        if not candidates:
            return None
        best_match = max(candidates, key=key_func)
        return (best_match.lat, best_match.lon)

    def _resolve_hungarian_match(self, city_name: str) -> tuple[float, float] | None:
        """Resolve a city from the Hungarian database when available."""
        if not self.hungarian_connection:
            return None

        hungarian_results = self.search_hungarian_settlements(city_name, limit=3)
        exact_match = self._find_exact_match(city_name, hungarian_results)
        if exact_match:
            return exact_match

        return self._find_best_match(
            hungarian_results,
            key_func=lambda city: (city.region_priority or 0, city.population or 0),
        )

    def _resolve_global_match(self, city_name: str) -> tuple[float, float] | None:
        """Resolve a city from the global database when available."""
        if not self.connection:
            return None

        global_results = self.search_cities(city_name, limit=3)
        exact_match = self._find_exact_match(city_name, global_results)
        if exact_match:
            return exact_match

        return self._find_best_match(global_results, key_func=lambda city: city.population or 0)

    def find_city_by_name(self, city_name: str) -> tuple[float, float] | None:
        """
        Find single city coordinates for TrendDataProcessor support.

        LOGIC:
        1. Hungarian priority - If Hungarian settlement exists, use it
        2. Global fallback - If no Hungarian result, use global cities
        3. Largest population - Return coordinates of the largest city
        4. Exact match priority - Exact name match takes precedence
        """
        try:
            logger.debug(f"find_city_by_name: '{city_name}'")
            match = self._resolve_hungarian_match(city_name)
            if match:
                return match

            match = self._resolve_global_match(city_name)
            if match:
                return match

            logger.warning(f"No match found: '{city_name}'")
            return None

        except Exception as exc:
            logger.error(f"find_city_by_name error '{city_name}': {exc}")
            logger.exception("find_city_by_name stacktrace:")
            return None

    def search_unified(
        self,
        search_term: str,
        limit: int = 20,
        hungarian_priority: bool = True,
        global_limit_ratio: float = 0.3,
    ) -> list[City]:
        """
        COMBINED SEARCH - Hungarian Settlements + Global Cities.

        This is the CORE function that searches ALL Hungarian settlements
        and global cities.
        """
        results = []

        normalized_ratio = min(max(global_limit_ratio, 0.0), 1.0)
        if hungarian_priority:
            global_limit = int(limit * normalized_ratio)
            hungarian_limit = limit - global_limit
        else:
            global_limit = int(limit * max(normalized_ratio, 0.5))
            hungarian_limit = limit - global_limit

        hungarian_results = self.search_hungarian_settlements(search_term, limit=hungarian_limit)
        results.extend(hungarian_results)

        global_results = self.search_cities(search_term, limit=global_limit)
        hungarian_names = {city.city.lower() for city in hungarian_results}
        filtered_global = [
            city
            for city in global_results
            if city.city.lower() not in hungarian_names or city.country_code != "HU"
        ]

        results.extend(filtered_global)

        logger.info(
            f"Combined search '{search_term}': {len(hungarian_results)} Hungarian + {len(filtered_global)} global = {len(results)} total"
        )

        return results[:limit]

    def search_cities(
        self, search_term: str, limit: int = 20, country_filter: str | None = None
    ) -> list[City]:
        """Global city search by name (ORIGINAL FUNCTION)."""
        if not self.connection:
            logger.warning("Global cities database not available")
            return []

        safe_limit = self._safe_limit(limit)
        sql_parts = ["SELECT * FROM cities"]
        where_conditions = ["city LIKE ?"]
        params: list[Any] = [f"%{search_term}%"]

        if country_filter:
            where_conditions.append("country_code = ?")
            params.append(country_filter.upper())

        sql_parts.append("WHERE " + " AND ".join(where_conditions))
        sql_parts.append("ORDER BY population DESC NULLS LAST")
        sql_parts.append(f"LIMIT {safe_limit}")

        sql = " ".join(sql_parts)
        rows = self._execute_query(sql, tuple(params))

        cities = [City.from_db_row(tuple(row)) for row in rows]

        logger.info(f"Global city search '{search_term}': {len(cities)} results")
        return cities

    def get_cities_by_country(
        self, country_code: str, limit: int = 20, min_population: int | None = None
    ) -> list[City]:
        """Country-based city query (original)."""
        if country_code.upper() == "HU":
            return self._get_hungarian_cities_combined(limit, min_population)

        if not self.connection:
            return []

        safe_limit = self._safe_limit(limit)
        sql_parts = ["SELECT * FROM cities WHERE country_code = ?"]
        params: list[Any] = [country_code.upper()]

        if min_population:
            sql_parts.append("AND population >= ?")
            params.append(min_population)

        sql_parts.append("ORDER BY population DESC NULLS LAST")
        sql_parts.append(f"LIMIT {safe_limit}")

        sql = " ".join(sql_parts)
        rows = self._execute_query(sql, tuple(params))

        return [City.from_db_row(tuple(row)) for row in rows]

    def _get_hungarian_cities_combined(
        self, limit: int, min_population: int | None = None
    ) -> list[City]:
        """Hungarian cities combined query (settlements + global)."""
        results = []

        safe_limit = self._safe_limit(limit)
        hungarian_limit = min(int(safe_limit * 0.75), safe_limit)
        if self.hungarian_connection:
            sql_parts = ["SELECT * FROM hungarian_settlements"]
            params: list[Any] = []

            if min_population:
                sql_parts.append("WHERE population >= ?")
                params.append(min_population)

            sql_parts.append("ORDER BY region_priority DESC, population DESC NULLS LAST")
            sql_parts.append(f"LIMIT {self._safe_limit(hungarian_limit)}")

            sql = " ".join(sql_parts)
            rows = self._execute_query(sql, tuple(params), use_hungarian=True)
            results.extend([City.from_hungarian_settlement(row) for row in rows])

        global_limit = limit - len(results)
        if global_limit > 0 and self.connection:
            sql_parts = ["SELECT * FROM cities WHERE country_code = 'HU'"]
            params = []

            if min_population:
                sql_parts.append("AND population >= ?")
                params.append(min_population)

            sql_parts.append("ORDER BY population DESC NULLS LAST")
            sql_parts.append(f"LIMIT {self._safe_limit(global_limit)}")

            sql = " ".join(sql_parts)
            rows = self._execute_query(sql, tuple(params))

            hungarian_names = {city.city.lower() for city in results}
            for row in rows:
                city = City.from_db_row(tuple(row))
                if city.city.lower() not in hungarian_names:
                    results.append(city)

        return results[:limit]


__all__ = ["CityManagerSearch"]
