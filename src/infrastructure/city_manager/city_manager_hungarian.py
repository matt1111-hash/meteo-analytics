#!/usr/bin/env python3

"""
City Manager - Hungarian Settlements Search
Global Weather Analyzer project

Part of the city_manager refactoring - split into focused modules.
"""

import logging

from src.infrastructure.db.like_utils import escape_like

from .city_manager_db import CityManagerDB
from .city_types import City

logger = logging.getLogger(__name__)


class CityManagerHungarian(CityManagerDB):
    """
    Hungarian settlements search methods.

    Handles search operations for 3200+ Hungarian settlements
    from hungarian_settlements.db database.
    """

    def search_hungarian_settlements(
        self,
        search_term: str,
        limit: int = 20,
        county_filter: str | None = None,
        settlement_type_filter: str | None = None,
    ) -> list[City]:
        """
        Search Hungarian settlements by name - ALL villages, municipalities, cities.

        Args:
            search_term: Search expression (e.g., "Kiskunhalas", "Buda")
            limit: Maximum result count
            county_filter: County filter (e.g., "Bács-Kiskun")
            settlement_type_filter: Settlement type ("város", "nagyközség", "község")

        Returns:
            List of Hungarian settlements sorted by priority
        """
        if not self.hungarian_connection:
            logger.warning("Hungarian settlements database not available")
            return []

        sql_parts = ["SELECT * FROM hungarian_settlements"]
        where_conditions = ["name LIKE ? ESCAPE '\\'"]
        params = [f"%{escape_like(search_term)}%"]

        if county_filter:
            where_conditions.append("megye = ?")
            params.append(county_filter)

        if settlement_type_filter:
            where_conditions.append("settlement_type = ?")
            params.append(settlement_type_filter)

        sql_parts.append("WHERE " + " AND ".join(where_conditions))
        sql_parts.append("ORDER BY region_priority DESC, population DESC NULLS LAST, name ASC")
        sql_parts.append(f"LIMIT {limit}")

        sql = " ".join(sql_parts)
        rows = self._execute_query(sql, tuple(params), use_hungarian=True)

        cities = [City.from_hungarian_settlement(row) for row in rows]

        logger.info(f"Hungarian settlements search '{search_term}': {len(cities)} results")
        return cities

    def get_hungarian_counties(self) -> list[str]:
        """Get list of Hungarian counties (cached)."""
        if (
            hasattr(self, "_hungarian_counties_cache")
            and self._hungarian_counties_cache is not None
        ):
            return self._hungarian_counties_cache

        if not self.hungarian_connection:
            return []

        sql = "SELECT DISTINCT megye FROM hungarian_settlements WHERE megye IS NOT NULL ORDER BY megye"
        rows = self._execute_query(sql, use_hungarian=True)

        self._hungarian_counties_cache = [row[0] for row in rows]
        return self._hungarian_counties_cache

    def get_hungarian_settlement_types(self) -> list[str]:
        """Get list of Hungarian settlement types."""
        if not self.hungarian_connection:
            return []

        sql = "SELECT DISTINCT settlement_type FROM hungarian_settlements WHERE settlement_type IS NOT NULL ORDER BY settlement_type"
        rows = self._execute_query(sql, use_hungarian=True)

        return [row[0] for row in rows]

    def get_hungarian_settlements_by_county(self, county: str, limit: int = 50) -> list[City]:
        """Get Hungarian settlements by county."""
        if not self.hungarian_connection:
            return []

        sql = """
            SELECT * FROM hungarian_settlements
            WHERE megye = ?
            ORDER BY region_priority DESC, population DESC NULLS LAST, name ASC
            LIMIT ?
        """

        rows = self._execute_query(sql, (county, limit), use_hungarian=True)
        cities = [City.from_hungarian_settlement(row) for row in rows]

        logger.info(f"Hungarian settlements ({county}): {len(cities)} results")
        return cities


__all__ = ["CityManagerHungarian"]
