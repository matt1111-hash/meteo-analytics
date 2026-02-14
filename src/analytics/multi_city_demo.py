#!/usr/bin/env python3
"""
Multi-City Analytics Engine - Demo
Demo and test code for multi-city analytics
"""

import logging
from datetime import datetime
from pathlib import Path

from .multi_city_engine_core import MultiCityEngine


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

        print("\n🔧 Calculated paths:")
        print(f"   Global cities DB: {engine.db_path.absolute()}")
        print(f"   Hungarian settlements DB: {engine.hungarian_db_path.absolute()}")
        print(f"   Global DB exists: {engine.db_path.exists()}")
        print(f"   Hungarian DB exists: {engine.hungarian_db_path.exists()}")

        print("\n🚀 REGION MAPPING TESTS:")
        test_regions = [
            "HU",
            "Észak-Magyarország",
            "Pest",
            "Budapest",
            "észak-magyarország",
            "közép-magyarország",
            "EU",
            "GLOBAL",
        ]

        for region in test_regions:
            try:
                mapped = engine.resolve_region_name(region)
                print(f"✅ '{region}' → '{mapped}'")
            except ValueError as e:
                print(f"⚠ '{region}' → ERROR: {e}")

        print("\n🚀 ANALYTICS TEST: 'Észak-Magyarország' region (windiest):")
        try:
            result_wind = engine.analyze_multi_city(
                "windiest_today", "Észak-Magyarország", today, limit=10
            )
            print(f"📊 Results: {len(result_wind.city_results)} cities")
            print(f"📊 Statistics: {result_wind.statistics}")

            print("🔥 TOP 3 WINDIEST CITIES:")
            for i, city in enumerate(result_wind.city_results[:3]):
                print(f"  {i + 1}. {city.city_name}: {city.value} km/h")

            non_zero_count = len([c for c in result_wind.city_results if c.value > 0])
            print("\n🔧 WINDSPEED CHECK:")
            print(
                f"   Non-zero wind speed values: {non_zero_count}/{len(result_wind.city_results)}"
            )

            if non_zero_count > 0:
                print("✅ WINDSPEED METRIC SUCCESS!")
            else:
                print("⚠ WINDSPEED METRIC FAILED!")

        except Exception as e:
            print(f"⚠ Test error: {e}")
            import traceback

            traceback.print_exc()

        print("\n🔧 DEMO COMPLETE")

    except Exception as e:
        print(f"❌ CRITICAL ERROR during engine initialization: {e}")
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
            print(f"   Files in data/: {[f.name for f in files]}")

        import traceback

        traceback.print_exc()


__all__ = ["demo_multi_city_engine"]


if __name__ == "__main__":
    demo_multi_city_engine()
