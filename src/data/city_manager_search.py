#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
City Manager - Global and Unified Search
Global Weather Analyzer project

Part of the city_manager refactoring - split into focused modules.
"""

import logging
from typing import List, Optional, Tuple

from .city_manager_hungarian import CityManagerHungarian
from .city_types import City


logger = logging.getLogger(__name__)


class CityManagerSearch(CityManagerHungarian):
    """Global cities and unified search methods."""

    def find_city_by_name(self, city_name: str) -> Optional[Tuple[float, float]]:
        """
        Find single city coordinates for TrendDataProcessor support.

        LOGIC:
        1. Hungarian priority - If Hungarian settlement exists, use it
        2. Global fallback - If no Hungarian result, use global cities
        3. Largest population - Return coordinates of the largest city
        4. Exact match priority - Exact name match takes precedence
        """
        try:
            logger.info(f"find_city_by_name: '{city_name}'")

            # 1. HUNGARIAN SEARCH PRIORITY
            if self.hungarian_connection:
                hungarian_results = self.search_hungarian_settlements(city_name, limit=3)

                if hungarian_results:
                    exact_match = next((city for city in hungarian_results
                                       if city.city.lower() == city_name.lower()), None)

                    if exact_match:
                        logger.info(f"Hungarian exact match: {exact_match.display_name}")
                        return (exact_match.lat, exact_match.lon)

                    best_hungarian = max(hungarian_results,
                                        key=lambda c: (c.region_priority or 0, c.population or 0))
                    logger.info(f"Hungarian best match: {best_hungarian.display_name}")
                    return (best_hungarian.lat, best_hungarian.lon)

            # 2. GLOBAL SEARCH (if no Hungarian result)
            if self.connection:
                global_results = self.search_cities(city_name, limit=3)

                if global_results:
                    exact_match = next((city for city in global_results
                                       if city.city.lower() == city_name.lower()), None)

                    if exact_match:
                        logger.info(f"Global exact match: {exact_match.display_name}")
                        return (exact_match.lat, exact_match.lon)

                    best_global = max(global_results, key=lambda c: c.population or 0)
                    logger.info(f"Global best match: {best_global.display_name}")
                    return (best_global.lat, best_global.lon)

            # 3. NO RESULTS
            logger.warning(f"No match found: '{city_name}'")
            return None

        except Exception as e:
            logger.error(f"find_city_by_name error '{city_name}': {e}")
            logger.exception("find_city_by_name stacktrace:")
            return None

    def search_unified(self, search_term: str, limit: int = 20,
                      hungarian_priority: bool = True,
                      global_limit_ratio: float = 0.3) -> List[City]:
        """
        COMBINED SEARCH - Hungarian Settlements + Global Cities.

        This is the CORE function that searches ALL Hungarian settlements
        and global cities.
        """
        results = []

        if hungarian_priority:
            hungarian_limit = int(limit * 0.7)
            global_limit = limit - hungarian_limit
        else:
            hungarian_limit = int(limit * 0.5)
            global_limit = limit - hungarian_limit

        hungarian_results = self.search_hungarian_settlements(search_term, limit=hungarian_limit)
        results.extend(hungarian_results)

        global_results = self.search_cities(search_term, limit=global_limit)

        # Filter duplicates (Hungarian Budapest vs global Budapest)
        hungarian_names = {city.city.lower() for city in hungarian_results}
        filtered_global = [
            city for city in global_results
            if city.city.lower() not in hungarian_names or city.country_code != "HU"
        ]

        results.extend(filtered_global)

        logger.info(f"Combined search '{search_term}': {len(hungarian_results)} Hungarian + {len(filtered_global)} global = {len(results)} total")

        return results[:limit]

    # ========================================================================
    # ORIGINAL GLOBAL SEARCH
    # ========================================================================

    def search_cities(self, search_term: str, limit: int = 20,
                     country_filter: Optional[str] = None) -> List[City]:
        """Global city search by name (ORIGINAL FUNCTION)."""
        if not self.connection:
            logger.warning("Global cities database not available")
            return []

        sql_parts = ["SELECT * FROM cities"]
        where_conditions = ["city LIKE ?"]
        params = [f"%{search_term}%"]

        if country_filter:
            where_conditions.append("country_code = ?")
            params.append(country_filter.upper())

        sql_parts.append("WHERE " + " AND ".join(where_conditions))
        sql_parts.append("ORDER BY population DESC NULLS LAST")
        sql_parts.append(f"LIMIT {limit}")

        sql = " ".join(sql_parts)
        rows = self._execute_query(sql, tuple(params))

        cities = [City.from_db_row(tuple(row)) for row in rows]

        logger.info(f"Global city search '{search_term}': {len(cities)} results")
        return cities

    def get_cities_by_country(self, country_code: str, limit: int = 20,
                             min_population: Optional[int] = None) -> List[City]:
        """Country-based city query (original)."""
        if country_code.upper() == "HU":
            return self._get_hungarian_cities_combined(limit, min_population)

        if not self.connection:
            return []

        sql_parts = ["SELECT * FROM cities WHERE country_code = ?"]
        params = [country_code.upper()]

        if min_population:
            sql_parts.append("AND population >= ?")
            params.append(min_population)

        sql_parts.append("ORDER BY population DESC NULLS LAST")
        sql_parts.append(f"LIMIT {limit}")

        sql = " ".join(sql_parts)
        rows = self._execute_query(sql, tuple(params))

        return [City.from_db_row(tuple(row)) for row in rows]

    def _get_hungarian_cities_combined(self, limit: int, min_population: Optional[int] = None) -> List[City]:
        """Hungarian cities combined query (settlements + global)."""
        results = []

        hungarian_limit = int(limit * 0.75)
        if self.hungarian_connection:
            sql_parts = ["SELECT * FROM hungarian_settlements"]
            params = []

            if min_population:
                sql_parts.append("WHERE population >= ?")
                params.append(min_population)

            sql_parts.append("ORDER BY region_priority DESC, population DESC NULLS LAST")
            sql_parts.append(f"LIMIT {hungarian_limit}")

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
            sql_parts.append(f"LIMIT {global_limit}")

            sql = " ".join(sql_parts)
            rows = self._execute_query(sql, tuple(params))

            hungarian_names = {city.city.lower() for city in results}
            for row in rows:
                city = City.from_db_row(tuple(row))
                if city.city.lower() not in hungarian_names:
                    results.append(city)

        return results[:limit]


__all__ = ['CityManagerSearch']
