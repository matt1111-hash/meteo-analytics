#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
City Manager - Demo and Test Functions
Global Weather Analyzer project

Part of the city_manager refactoring - split into focused modules.
"""

from .city_manager_stats import CityManagerStats
from .city_types import CityDatabaseError


def _print_statistics(stats: dict) -> None:
    """Print top-level database statistics."""
    print("DUAL DATABASE STATISTICS:")
    print(f"   Global cities: {stats['global_cities']:,}")
    print(f"   Hungarian settlements: {stats['hungarian_settlements']:,}")
    print(f"   Total searchable locations: {stats['total_searchable_locations']:,}")
    print()


def _print_find_city_tests(manager: CityManagerStats) -> None:
    """Print coordinate lookup demo results."""
    print("NEW FUNCTION TEST: find_city_by_name() - TrendDataProcessor support")
    print("-" * 70)
    test_cities = ["Budapest", "Kiskunhalas", "Broxbourne", "London", "New York"]
    for city_name in test_cities:
        print(f"Coordinate search: '{city_name}'")
        coords = manager.find_city_by_name(city_name)
        if coords:
            lat, lon = coords
            print(f"   Coordinates: {lat:.4f}, {lon:.4f}")
        else:
            print("   Not found")
        print()


def _print_hungarian_stats(manager: CityManagerStats, stats: dict) -> None:
    """Print Hungarian settlement statistics when available."""
    if stats["hungarian_settlements"] <= 0:
        return
    hu_stats = manager.get_hungarian_statistics()
    print("HUNGARIAN SETTLEMENTS DETAILS:")
    print(f"   Types: {hu_stats['by_settlement_type']}")
    print(f"   Top counties: {dict(list(hu_stats['top_counties'].items())[:3])}")
    print(
        f"   100k+ population: {hu_stats['population_stats']['large_cities_100k_plus']}"
    )
    print()


def _print_unified_search_demo(manager: CityManagerStats) -> None:
    """Print unified search sample output."""
    print("UNIFIED SEARCH TEST - Hungarian small settlement:")
    print("   Search: 'Kiskunhalas'")
    kiskunhalas_results = manager.search_unified("Kiskunhalas", limit=3)
    for index, city in enumerate(kiskunhalas_results, 1):
        flag = "HU" if city.is_hungarian else "Global"
        pop = f"{city.population:,}" if city.population else "N/A"
        settlement_info = f" ({city.settlement_type})" if city.settlement_type else ""
        print(
            f"   {index}. {flag} {city.display_name}: {pop} population{settlement_info}"
        )
    print()


def _print_query_statistics(manager: CityManagerStats) -> None:
    """Print query counters."""
    print("QUERY STATISTICS:")
    print(f"   Global queries: {manager.query_count}")
    print(f"   Hungarian queries: {manager.hungarian_query_count}")
    print(f"   Total queries: {manager.query_count + manager.hungarian_query_count}")


def demo_dual_database_city_manager():
    """Dual Database City Manager demo and testing."""
    print("Dual Database City Manager Demo v4.2")
    print("=" * 60)

    try:
        with CityManagerStats() as manager:
            stats = manager.get_database_statistics()
            _print_statistics(stats)
            _print_find_city_tests(manager)
            _print_hungarian_stats(manager, stats)
            _print_unified_search_demo(manager)
            _print_query_statistics(manager)

    except CityDatabaseError as e:
        print(f"Database error: {e}")
        print("To fix:")
        print("   1. Run: python scripts/populate_cities_db.py")
        print("   2. Run: python scripts/hungarian_settlements_importer.py")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    demo_dual_database_city_manager()


__all__ = ["demo_dual_database_city_manager"]
