#!/usr/bin/env python3
"""
Multi-City Analytics Engine - Demo
Demo and test code for multi-city analytics
"""

import logging
from datetime import datetime
from pathlib import Path

from .multi_city_engine_core import MultiCityEngine


def _print_path_debug(engine: MultiCityEngine) -> None:
    """Print resolved database path diagnostics."""
    print("\n🔧 Calculated paths:")
    print(f"   Global cities DB: {engine.db_path.absolute()}")
    print(f"   Hungarian settlements DB: {engine.hungarian_db_path.absolute()}")
    print(f"   Global DB exists: {engine.db_path.exists()}")
    print(f"   Hungarian DB exists: {engine.hungarian_db_path.exists()}")


def _print_region_mapping(engine: MultiCityEngine, test_regions: list[str]) -> None:
    """Print region mapping diagnostics."""
    print("\n🚀 REGION MAPPING TESTS:")
    for region in test_regions:
        try:
            mapped = engine.resolve_region_name(region)
            print(f"✅ '{region}' → '{mapped}'")
        except ValueError as error:
            print(f"⚠ '{region}' → ERROR: {error}")


def _print_wind_results(engine: MultiCityEngine, today: str) -> None:
    """Print analytics demo results for windiest cities."""
    print("\n🚀 ANALYTICS TEST: 'Észak-Magyarország' region (windiest):")
    result_wind = engine.analyze_multi_city(
        "windiest_today", "Észak-Magyarország", today, limit=10
    )
    print(f"📊 Results: {len(result_wind.city_results)} cities")
    print(f"📊 Statistics: {result_wind.statistics}")
    print("🔥 TOP 3 WINDIEST CITIES:")
    for index, city in enumerate(result_wind.city_results[:3], start=1):
        print(f"  {index}. {city.city_name}: {city.value} km/h")

    non_zero_count = len([city for city in result_wind.city_results if city.value > 0])
    print("\n🔧 WINDSPEED CHECK:")
    print(
        f"   Non-zero wind speed values: {non_zero_count}/{len(result_wind.city_results)}"
    )
    print(
        "✅ WINDSPEED METRIC SUCCESS!"
        if non_zero_count > 0
        else "⚠ WINDSPEED METRIC FAILED!"
    )


def _print_initialization_debug() -> None:
    """Print path diagnostics after critical initialization failure."""
    print("🔧 Debugging info:")
    print(f"   Current working dir: {Path.cwd().absolute()}")
    print(f"   Script location: {Path(__file__).absolute()}")

    project_root = Path(__file__).parent.parent.parent
    print(f"   Calculated project root: {project_root.absolute()}")
    print(f"   Project root exists: {project_root.exists()}")

    data_dir = project_root / "data"
    print(f"   Data directory: {data_dir.absolute()}")
    print(f"   Data directory exists: {data_dir.exists()}")
    if data_dir.exists():
        files = list(data_dir.iterdir())
        print(f"   Files in data/: {[file.name for file in files]}")


def demo_multi_city_engine() -> None:
    """Demo: Multi-city analytics engine testing."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("\n🚀 MULTI-CITY ENGINE DEMO:")
    print(f"🔧 Script location: {Path(__file__).absolute()}")
    print(f"🔧 Working directory: {Path.cwd().absolute()}")

    try:
        engine = MultiCityEngine()
        today = datetime.now().strftime("%Y-%m-%d")
        _print_path_debug(engine)
        _print_region_mapping(
            engine,
            [
                "HU",
                "Észak-Magyarország",
                "Pest",
                "Budapest",
                "észak-magyarország",
                "közép-magyarország",
                "EU",
                "GLOBAL",
            ],
        )

        try:
            _print_wind_results(engine, today)
        except Exception as error:
            print(f"⚠ Test error: {error}")

        print("\n🔧 DEMO COMPLETE")

    except Exception as error:
        print(f"❌ CRITICAL ERROR during engine initialization: {error}")
        _print_initialization_debug()


__all__ = ["demo_multi_city_engine"]


if __name__ == "__main__":
    demo_multi_city_engine()
