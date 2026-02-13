"""City repository database query methods."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List


class CityRepositoryQueries:
    """Database query operations for city repository."""

    def __init__(self, db_path: Path, hungarian_db_path: Path):
        """Initialize with database paths."""
        self.db_path = db_path
        self.hungarian_db_path = hungarian_db_path

    def get_cities_by_names(self, city_names: List[str]) -> List[Dict[str, object]]:
        """Fetch cities by explicit city names (case-insensitive).

        For each city name, returns the match with highest population.
        """
        if not city_names:
            return []

        # Safe: in_clause contains only '?' placeholders, params passed separately
        in_clause = ",".join(["?"] * len(city_names))
        query = (
            "SELECT city, country, country_code, lat, lon, population, "
            "meteostat_station_id, data_quality_score FROM cities "
            f"WHERE LOWER(city) IN ({in_clause}) "  # nosec B608
            "AND population = ("
            "  SELECT MAX(population) FROM cities c2 "
            "  WHERE LOWER(c2.city) = LOWER(cities.city)"
            ") "
            "ORDER BY population DESC"
        )
        params = [name.lower() for name in city_names]

        if self.db_path.exists():
            results = self._execute(self.db_path, query, params)
            if results:
                return results

        # Fallback to Hungarian database
        if self.hungarian_db_path.exists():
            hun_query = (
                'SELECT name as city, "Magyarország" as country, '
                '"HU" as country_code, latitude as lat, longitude as lon, '
                "population, NULL as meteostat_station_id, "
                "region_priority as data_quality_score "
                "FROM hungarian_settlements "
                f"WHERE LOWER(name) IN ({in_clause}) "  # nosec B608
                "ORDER BY population DESC"
            )
            return self._execute_hungarian(self.hungarian_db_path, hun_query, params)

        return []

    def get_cities_for_region(
        self,
        mapped_region: str,
        original_region: str,
        country_codes: List[str],
        limit: int,
        hungarian_mapping: Dict[str, List[str]],
    ) -> List[Dict[str, object]]:
        """Fetch cities for a region with optional Hungarian filtering."""
        if mapped_region == "Global":
            return self.query_global(limit)
        if mapped_region == "Hungary":
            if original_region in hungarian_mapping:
                return self.query_hungarian_region(
                    original_region, hungarian_mapping, limit
                )
            return self.query_hungarian_all(limit)
        return self.query_countries(country_codes, limit)

    def query_global(self, limit: int) -> List[Dict[str, object]]:
        """Query global cities database."""
        base_select = (
            "SELECT city, country, country_code, lat, lon, population, "
            "meteostat_station_id, data_quality_score FROM cities "
            "WHERE population IS NOT NULL AND population > 100000 "
            "ORDER BY population DESC LIMIT ?"
        )
        return self._execute(self.db_path, base_select, [limit])

    def query_hungarian_all(self, limit: int) -> List[Dict[str, object]]:
        """Query all Hungarian settlements."""
        base_select = (
            "SELECT city, country, country_code, lat, lon, population, "
            "meteostat_station_id, data_quality_score FROM cities "
            'WHERE country_code = "HU" '
            "ORDER BY CASE WHEN population IS NOT NULL "
            "THEN population ELSE 0 END DESC "
            "LIMIT ?"
        )
        return self._execute(self.db_path, base_select, [limit])

    def query_hungarian_region(
        self,
        original_region: str,
        hungarian_mapping: Dict[str, List[str]],
        limit: int,
    ) -> List[Dict[str, object]]:
        """Query Hungarian settlements by region (megye)."""
        target_counties = hungarian_mapping.get(original_region, [])
        if not target_counties:
            return []

        # Safe: in_clause contains only '?' placeholders, params passed separately
        in_clause = ",".join(["?"] * len(target_counties))
        base_select = (
            'SELECT name as city, "Magyarország" as country, '
            '"HU" as country_code, latitude as lat, longitude as lon, '
            "population, NULL as meteostat_station_id, "
            "region_priority as data_quality_score "
            "FROM hungarian_settlements "
            f"WHERE megye IN ({in_clause}) "  # nosec B608
            "ORDER BY CASE WHEN population IS NOT NULL "
            "THEN population ELSE 0 END DESC "
            "LIMIT ?"
        )
        params: List[object] = list(target_counties) + [limit]
        return self._execute_hungarian(self.hungarian_db_path, base_select, params)

    def query_countries(
        self,
        country_codes: List[str],
        limit: int,
    ) -> List[Dict[str, object]]:
        """Query cities by country codes."""
        # Safe: in_clause contains only '?' placeholders, params passed separately
        in_clause = ",".join(["?"] * len(country_codes))
        base_select = (
            "SELECT city, country, country_code, lat, lon, population, "
            "meteostat_station_id, data_quality_score FROM cities "
            f"WHERE country_code IN ({in_clause}) "  # nosec B608
            "AND population IS NOT NULL AND population > 50000 "
            "ORDER BY CASE WHEN population IS NOT NULL "
            "THEN population ELSE 0 END DESC "
            "LIMIT ?"
        )
        params: List[object] = list(country_codes) + [limit]
        return self._execute(self.db_path, base_select, params)

    def autocomplete_city_name(
        self, query: str, limit: int = 20
    ) -> List[Dict[str, object]]:
        """Autocomplete city names by partial match."""
        if not query or len(query.strip()) < 2:
            return []

        query_str = query.strip().lower()

        # Search in global cities database first
        base_select = (
            "SELECT city, country, country_code, lat, lon, population, "
            "meteostat_station_id, data_quality_score FROM cities "
            "WHERE LOWER(city) LIKE ? "
            "ORDER BY population DESC, city ASC "
            "LIMIT ?"
        )
        params = [f"%{query_str}%", limit]

        results = []
        if self.db_path.exists():
            global_results = self._execute(self.db_path, base_select, params)
            results.extend(global_results)

        # If we have enough results from global database, return them
        if len(results) >= limit:
            return results[:limit]

        # Otherwise, search in Hungarian database for additional results
        remaining_limit = limit - len(results)
        hun_query = (
            "SELECT name, 'Hungary' as country, 'HU' as country_code, "
            "latitude as lat, longitude as lon, population, "
            "NULL as meteostat_station_id, NULL as data_quality_score "
            "FROM hungarian_settlements "
            "WHERE LOWER(name) LIKE ? "
            "ORDER BY population DESC, name ASC "
            "LIMIT ?"
        )

        if self.hungarian_db_path.exists():
            hun_results = self._execute_hungarian(
                self.hungarian_db_path, hun_query, [f"%{query_str}%", remaining_limit]
            )
            results.extend(hun_results)

        return results[:limit]

    def _execute(
        self,
        database_path: Path,
        query: str,
        params: List[object],
    ) -> List[Dict[str, object]]:
        """Execute query on global database."""
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
        return [
            {
                "city": row[0],
                "country": row[1],
                "country_code": row[2],
                "lat": row[3],
                "lon": row[4],
                "population": row[5],
                "meteostat_station_id": row[6],
                "data_quality_score": row[7],
            }
            for row in rows
        ]

    def _execute_hungarian(
        self,
        database_path: Path,
        query: str,
        params: List[object],
    ) -> List[Dict[str, object]]:
        """Execute query on Hungarian database with proper column mapping."""
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
        return [
            {
                "city": row[0],  # name -> city
                "country": row[1],
                "country_code": row[2],
                "lat": row[3],  # latitude -> lat
                "lon": row[4],  # longitude -> lon
                "population": row[5],
                "meteostat_station_id": row[6],
                "data_quality_score": row[7],
            }
            for row in rows
        ]


__all__ = ["CityRepositoryQueries"]
