#!/usr/bin/env python3

"""
City Manager - Statistics and Context Manager
Global Weather Analyzer project

Part of the city_manager refactoring - split into focused modules.
"""

import logging
from typing import Any

from .city_manager_search import CityManagerSearch
from .city_types import City

logger = logging.getLogger(__name__)


class CityManagerStats(CityManagerSearch):
    """
    Statistics and context manager support for CityManager.

    Provides database statistics, legacy methods, and context manager functionality.
    """

    # ========================================================================
    # STATISTICS
    # ========================================================================

    def get_database_statistics(self) -> dict[str, Any]:
        """Extended database statistics with dual database support."""
        stats: dict[str, Any] = {
            "query_count": self.query_count,
            "hungarian_query_count": self.hungarian_query_count,
            "last_query": self.last_query_time.isoformat() if self.last_query_time else None,
        }

        if self.connection:
            stats["global_cities"] = self._get_total_city_count()
            stats["continents"] = self._get_available_continents()
            stats["countries"] = self._get_available_countries()
        else:
            stats["global_cities"] = 0
            stats["continents"] = []
            stats["countries"] = []

        if self.hungarian_connection:
            stats["hungarian_settlements"] = self._get_total_hungarian_settlements_count()
            stats["hungarian_counties"] = self.get_hungarian_counties()
            stats["settlement_types"] = self.get_hungarian_settlement_types()
        else:
            stats["hungarian_settlements"] = 0
            stats["hungarian_counties"] = []
            stats["settlement_types"] = []

        stats["total_searchable_locations"] = (
            stats["global_cities"] + stats["hungarian_settlements"]
        )

        return stats

    def get_hungarian_statistics(self) -> dict[str, Any]:
        """Hungarian settlements detailed statistics."""
        if not self.hungarian_connection:
            return {"error": "Hungarian database not available"}

        cursor = self.hungarian_connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM hungarian_settlements")
        total_settlements = cursor.fetchone()[0]

        cursor.execute("""
            SELECT settlement_type, COUNT(*) as count
            FROM hungarian_settlements
            WHERE settlement_type IS NOT NULL
            GROUP BY settlement_type
            ORDER BY count DESC
        """)
        by_type = dict(cursor.fetchall())

        cursor.execute("""
            SELECT megye, COUNT(*) as count
            FROM hungarian_settlements
            WHERE megye IS NOT NULL
            GROUP BY megye
            ORDER BY count DESC
            LIMIT 10
        """)
        by_county = dict(cursor.fetchall())

        cursor.execute("""
            SELECT
                COUNT(CASE WHEN population >= 100000 THEN 1 END) as large_cities,
                COUNT(CASE WHEN population >= 10000 THEN 1 END) as medium_towns,
                COUNT(CASE WHEN population < 10000 AND population > 0 THEN 1 END) as small_towns,
                AVG(CASE WHEN population > 0 THEN population END) as avg_population,
                MAX(population) as max_population
            FROM hungarian_settlements
        """)
        row = cursor.fetchone()

        return {
            "total_settlements": total_settlements,
            "by_settlement_type": by_type,
            "top_counties": by_county,
            "population_stats": {
                "large_cities_100k_plus": row[0],
                "medium_towns_10k_plus": row[1],
                "small_towns_under_10k": row[2],
                "average_population": int(row[3]) if row[3] else 0,
                "largest_settlement_population": row[4],
            },
        }

    # ========================================================================
    # LEGACY METHODS (COMPATIBILITY)
    # ========================================================================

    def get_cities_by_continent(
        self, continent: str, limit: int = 50, min_population: int | None = None
    ) -> list[City]:
        """Continent-based city query (original)."""
        if not self.connection:
            return []

        sql_parts = ["SELECT * FROM cities WHERE continent = ?"]
        params: list[str | int] = [continent]

        if min_population:
            sql_parts.append("AND population >= ?")
            params.append(min_population)

        sql_parts.append("ORDER BY population DESC NULLS LAST")
        sql_parts.append(f"LIMIT {limit}")

        sql = " ".join(sql_parts)
        rows = self._execute_query(sql, tuple(params))

        return [City.from_db_row(tuple(row)) for row in rows]

    def _get_available_continents(self) -> list[str]:
        """Get available continents list."""
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT DISTINCT continent FROM cities WHERE continent IS NOT NULL ORDER BY continent"
        )
        return [row[0] for row in cursor.fetchall()]

    def _get_available_countries(self) -> list[dict[str, Any]]:
        """Get available countries list."""
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT country_code, country, COUNT(*) as city_count
            FROM cities
            WHERE country_code IS NOT NULL
            GROUP BY country_code, country
            ORDER BY city_count DESC
        """)

        return [
            {"country_code": row[0], "country_name": row[1], "city_count": row[2]}
            for row in cursor.fetchall()
        ]

    # ========================================================================
    # CONTEXT MANAGER
    # ========================================================================

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        """Context manager support."""
        self.close()

    # ========================================================================
    # PORT IMPLEMENTATION (CityManagerPort)
    # ========================================================================

    def get_cities_for_hungarian_county(self, county: str) -> list[dict[str, Any]]:
        """Get Hungarian settlements by county (Port implementation).

        Args:
            county: County name (e.g., "Pest", "Bács-Kiskun")

        Returns:
            List of dictionaries with city data
        """
        cities = self.get_hungarian_settlements_by_county(county)
        return [city.to_dict() for city in cities]

    def get_settlements_bulk(self, limit: int = 200) -> list[dict[str, Any]]:
        """Get Hungarian settlements in a single query (no N+1).

        Args:
            limit: Maximum number of settlements to return

        Returns:
            List of dictionaries with settlement data
        """
        if not self.hungarian_connection:
            return []

        cursor = self.hungarian_connection.cursor()
        cursor.execute(
            """
            SELECT id, name, megye, latitude, longitude,
                   population, region_priority, settlement_type
            FROM hungarian_settlements
            ORDER BY region_priority DESC, population DESC
            LIMIT ?
            """,
            (limit,),
        )
        columns = [
            "id",
            "city",
            "megye",
            "lat",
            "lon",
            "population",
            "region_priority",
            "settlement_type",
        ]
        return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


__all__ = ["CityManagerStats"]
