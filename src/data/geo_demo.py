#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Geo Utils Demo
🌍 Demo and testing functions for geographic utilities.

Part of the geo_utils refactoring - split into focused modules.
"""

from .distance_calculator import DistanceCalculator
from .geo_utils_analytics import GeoUtilsAnalytics


def demo_geo_utils():
    """GeoUtils demo and testing."""
    print("🌍 Geographic Utils Demo")
    print("=" * 50)

    # Distance Calculator test
    print("📏 Distance Calculator:")
    calculator = DistanceCalculator()

    budapest = (47.4979, 19.0402)
    berlin = (52.5200, 13.4050)

    haversine_dist = calculator.haversine_distance(
        budapest[0], budapest[1], berlin[0], berlin[1]
    )
    vincenty_dist = calculator.vincenty_distance(
        budapest[0], budapest[1], berlin[0], berlin[1]
    )

    print(f"Budapest-Berlin distance:")
    print(f"  Haversine: {haversine_dist:.2f} km")
    print(f"  Vincenty:  {vincenty_dist:.2f} km")
    print(f"  Difference: {abs(haversine_dist - vincenty_dist):.3f} km")
    print()

    # GeoUtils test
    print("🗺️ Geographic Utils:")
    geo_utils = GeoUtilsAnalytics(calculator)

    test_cities = [
        {"lat": 47.4979, "lon": 19.0402, "population": 1750000, "name": "Budapest"},
        {"lat": 47.6835, "lon": 17.6383, "population": 130000, "name": "Győr"},
        {"lat": 47.5316, "lon": 21.6273, "population": 200000, "name": "Debrecen"},
        {"lat": 46.2530, "lon": 20.1414, "population": 160000, "name": "Szeged"},
        {"lat": 46.0727, "lon": 18.2324, "population": 145000, "name": "Pécs"}
    ]

    coordinates = [(city["lat"], city["lon"]) for city in test_cities]
    bbox = geo_utils.calculate_bounding_box(coordinates, padding_degrees=0.1)

    print(f"Hungarian cities bounding box:")
    print(f"  Lat: {bbox.min_latitude:.4f} - {bbox.max_latitude:.4f}")
    print(f"  Lon: {bbox.min_longitude:.4f} - {bbox.max_longitude:.4f}")

    center = geo_utils.calculate_geographic_center(coordinates)
    print(f"  Center: {center.latitude:.4f}, {center.longitude:.4f}")
    print()

    # Region calculation
    region = geo_utils.calculate_region_from_cities(test_cities, "Magyarország")
    print(f"Hungary region:")
    print(f"  Area: {region.area_km2:.0f} km²")
    print(f"  Population: {region.population:,}")
    print(f"  Cities: {region.cities_count}")
    print()

    # Proximity grouping
    print("📍 Proximity grouping (100 km):")
    groups = geo_utils.group_cities_by_proximity(test_cities, max_distance_km=100)
    for i, group in enumerate(groups, 1):
        cities_names = [city["name"] for city in group]
        print(f"  Group {i}: {', '.join(cities_names)}")
    print()

    # Multi-city analytics optimization
    print("🏙️ Multi-city analytics optimization:")
    optimized = geo_utils.optimize_cities_for_weather_analytics(
        test_cities, "temperature", max_cities=3
    )
    optimized_names = [city["name"] for city in optimized]
    print(f"  Optimized cities (temperature): {', '.join(optimized_names)}")

    coverage = geo_utils.calculate_multi_city_coverage_area(test_cities)
    print(f"  Coverage area: {coverage['area_km2']:.0f} km²")
    print(f"  Max distance from center: {coverage['distances']['max_distance_from_center']:.1f} km")
    print()

    # Map projection
    print("🗺️ Map projection:")
    web_mercator = geo_utils.convert_to_web_mercator(budapest[0], budapest[1])
    print(f"Budapest Web Mercator: {web_mercator[0]:.0f}, {web_mercator[1]:.0f}")

    zoom_level = geo_utils.suggest_map_zoom_level(bbox)
    print(f"Suggested zoom level: {zoom_level}")
    print()

    # Statistics
    stats = calculator.get_calculation_statistics()
    print(f"📊 Statistics: {stats['total_calculations']} distance calculations")


if __name__ == "__main__":
    demo_geo_utils()
