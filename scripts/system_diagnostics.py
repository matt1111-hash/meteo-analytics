#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 Weather System Diagnostics - Rendszerdiagnosztika
Global Weather Analyzer projekt

Fájl: scripts/system_diagnostics.py
Cél: Teljes rendszer ellenőrzése és hibaelhárítás
- Adatbázisok ellenőrzése
- GeoJSON fájlok validálása
- Weather API kapcsolat tesztelése
- Multi-City Engine működés ellenőrzése

🚀 FUNKCIÓK:
✅ Cities.db tartalom ellenőrzése
✅ GeoJSON fájlok validálása
✅ Weather API konfiguráció tesztelése
✅ Multi-City Engine teszt futtatása
✅ Hibák diagnosztizálása és javítási javaslatok
"""

import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Projekt gyökér meghatározása
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WeatherSystemDiagnostics:
    """
    🔍 Weather System teljes diagnosztikai osztály.
    """

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_dir = self.project_root / "data"
        self.results = {
            "database_checks": {},
            "geojson_checks": {},
            "weather_api_check": {},
            "multi_city_engine_check": {},
            "recommendations": []
        }

    def run_full_diagnostics(self):
        """
        🔍 Teljes rendszer diagnosztika futtatása.
        """
        print("🔍 Weather System Diagnostics indítása...")
        print(f"📁 Projekt gyökér: {self.project_root}")
        print(f"📁 Data könyvtár: {self.data_dir}")
        print("=" * 80)

        # 1. Adatbázisok ellenőrzése
        print("1️⃣ Adatbázisok ellenőrzése...")
        self._check_databases()

        # 2. GeoJSON fájlok ellenőrzése
        print("\n2️⃣ GeoJSON fájlok ellenőrzése...")
        self._check_geojson_files()

        # 3. Weather API ellenőrzése
        print("\n3️⃣ Weather API kapcsolat ellenőrzése...")
        self._check_weather_api()

        # 4. Multi-City Engine teszt
        print("\n4️⃣ Multi-City Engine teszt...")
        self._check_multi_city_engine()

        # 5. Összegzés és javaslatok
        print("\n5️⃣ Összegzés és javaslatok...")
        self._generate_recommendations()

        # 6. Eredmények kiírása
        self._print_results()

    def _check_databases(self):
        """
        📊 Adatbázisok tartalmának ellenőrzése.
        """
        databases = [
            ("cities.db", "cities"),
            ("hungarian_settlements.db", "settlements"),
            ("meteo_data.db", "weather_data")
        ]

        for db_file, db_type in databases:
            db_path = self.data_dir / db_file
            result = {
                "exists": db_path.exists(),
                "size": 0,
                "tables": [],
                "row_counts": {},
                "sample_data": {}
            }

            if result["exists"]:
                try:
                    result["size"] = db_path.stat().st_size

                    with sqlite3.connect(db_path) as conn:
                        cursor = conn.cursor()

                        # Táblák listája
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                        result["tables"] = [row[0] for row in cursor.fetchall()]

                        # Sorok száma táblánként
                        for table in result["tables"]:
                            try:
                                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                                result["row_counts"][table] = cursor.fetchone()[0]

                                # Minta adatok (első 3 sor)
                                cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
                                result["sample_data"][table] = cursor.fetchall()

                            except Exception as e:
                                result["row_counts"][table] = f"ERROR: {e}"

                    print(f"✅ {db_file}: {result['size']:,} bytes, {len(result['tables'])} tábla")
                    for table, count in result["row_counts"].items():
                        print(f"   📊 {table}: {count} sor")

                except Exception as e:
                    result["error"] = str(e)
                    print(f"❌ {db_file}: Hiba - {e}")
            else:
                print(f"❌ {db_file}: Nem található")

            self.results["database_checks"][db_file] = result

    def _check_geojson_files(self):
        """
        🗺️ GeoJSON fájlok validálása.
        """
        geojson_files = [
            "counties.geojson",
            "postal_codes.geojson"
        ]

        geojson_dir = self.data_dir / "geojson"

        for geojson_file in geojson_files:
            file_path = geojson_dir / geojson_file
            result = {
                "exists": file_path.exists(),
                "size": 0,
                "valid_json": False,
                "feature_count": 0,
                "sample_properties": {}
            }

            if result["exists"]:
                try:
                    result["size"] = file_path.stat().st_size

                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        result["valid_json"] = True

                        if "features" in data:
                            result["feature_count"] = len(data["features"])

                            # Első feature tulajdonságai minta
                            if data["features"]:
                                result["sample_properties"] = data["features"][0].get("properties", {})

                    print(f"✅ {geojson_file}: {result['size']:,} bytes, {result['feature_count']} feature")
                    if result["sample_properties"]:
                        properties_sample = list(result["sample_properties"].keys())[:5]
                        print(f"   🏷️ Tulajdonságok: {', '.join(properties_sample)}")

                except Exception as e:
                    result["error"] = str(e)
                    print(f"❌ {geojson_file}: Hiba - {e}")
            else:
                print(f"❌ {geojson_file}: Nem található")

            self.results["geojson_checks"][geojson_file] = result

    def _check_weather_api(self):
        """
        🌤️ Weather API kapcsolat és konfiguráció ellenőrzése.
        """
        result = {
            "weather_client_available": False,
            "config_loaded": False,
            "api_test_success": False,
            "api_response": None,
            "error": None
        }

        try:
            # WeatherClient import
            from src.data.weather_client import WeatherClient
            result["weather_client_available"] = True
            print("✅ WeatherClient modul importálva")

            # WeatherClient instance létrehozása
            weather_client = WeatherClient()
            result["config_loaded"] = True
            print("✅ WeatherClient példány létrehozva")

            # Teszt API hívás Budapest koordinátákkal
            budapest_lat, budapest_lon = 47.4979, 19.0402
            today = datetime.now().strftime("%Y-%m-%d")

            print(f"🧪 Teszt API hívás: Budapest ({budapest_lat}, {budapest_lon}), {today}")

            api_response = weather_client.get_weather_data(
                latitude=budapest_lat,
                longitude=budapest_lon,
                start_date=today,
                end_date=today
            )

            if api_response:
                result["api_test_success"] = True
                result["api_response"] = str(api_response)[:200] + "..." if len(str(api_response)) > 200 else str(api_response)
                print("✅ Weather API teszt sikeres")
                print(f"   📊 Válasz típus: {type(api_response)}")

                if isinstance(api_response, tuple) and len(api_response) == 2:
                    weather_data, source = api_response
                    print(f"   🌤️ Adatforrás: {source}")
                    if weather_data and len(weather_data) > 0:
                        print(f"   📈 Adatpontok: {len(weather_data)}")
                        sample_data = weather_data[0]
                        print(f"   🔍 Minta adat kulcsok: {list(sample_data.keys()) if isinstance(sample_data, dict) else 'N/A'}")
            else:
                result["error"] = "API válasz üres"
                print("⚠️ Weather API válasz üres")

        except ImportError as e:
            result["error"] = f"WeatherClient import hiba: {e}"
            print(f"❌ WeatherClient import hiba: {e}")
        except Exception as e:
            result["error"] = f"Weather API teszt hiba: {e}"
            print(f"❌ Weather API teszt hiba: {e}")

        self.results["weather_api_check"] = result

    def _check_multi_city_engine(self):
        """
        🏙️ Multi-City Engine működés ellenőrzése.
        """
        result = {
            "engine_available": False,
            "engine_initialized": False,
            "test_query_success": False,
            "test_result": None,
            "error": None
        }

        try:
            # Multi-City Engine import
            from src.analytics.multi_city_engine import MultiCityEngine
            result["engine_available"] = True
            print("✅ MultiCityEngine modul importálva")

            # Engine példány létrehozása
            engine = MultiCityEngine()
            result["engine_initialized"] = True
            print("✅ MultiCityEngine példány létrehozva")

            # Teszt lekérdezés
            print("🧪 Teszt lekérdezés: hottest_today, HU, limit=5")
            today = datetime.now().strftime("%Y-%m-%d")

            test_result = engine.analyze_multi_city(
                query_type="hottest_today",
                region="HU",
                date=today,
                limit=5
            )

            if test_result and test_result.city_results:
                result["test_query_success"] = True
                result["test_result"] = {
                    "city_count": len(test_result.city_results),
                    "execution_time": test_result.execution_time,
                    "total_cities_found": test_result.total_cities_found,
                    "sample_cities": [
                        {
                            "city": city.city_name,
                            "value": city.value,
                            "coords": [city.latitude, city.longitude]
                        }
                        for city in test_result.city_results[:3]
                    ]
                }

                print("✅ Multi-City Engine teszt sikeres")
                print(f"   🏙️ Városok száma: {len(test_result.city_results)}")
                print(f"   ⏱️ Végrehajtási idő: {test_result.execution_time:.2f}s")
                print(f"   📊 Összes talált város: {test_result.total_cities_found}")

                for i, city in enumerate(test_result.city_results[:3]):
                    print(f"   {i+1}. {city.city_name}: {city.value}°C ({city.latitude:.2f}, {city.longitude:.2f})")
            else:
                result["error"] = "Multi-City Engine válasz üres vagy hibás"
                print("⚠️ Multi-City Engine válasz üres vagy hibás")

        except ImportError as e:
            result["error"] = f"MultiCityEngine import hiba: {e}"
            print(f"❌ MultiCityEngine import hiba: {e}")
        except Exception as e:
            result["error"] = f"Multi-City Engine teszt hiba: {e}"
            print(f"❌ Multi-City Engine teszt hiba: {e}")

        self.results["multi_city_engine_check"] = result

    def _generate_recommendations(self):
        """
        💡 Javítási javaslatok generálása.
        """
        recommendations = []

        # Adatbázis problémák
        for db_file, db_result in self.results["database_checks"].items():
            if not db_result["exists"]:
                recommendations.append(f"❌ {db_file} nem található - futtatd a populate_cities_db.py scriptet")
            elif not db_result.get("tables"):
                recommendations.append(f"⚠️ {db_file} üres - ellenőrizd az adatbázis struktúrát")
            elif all(count == 0 for count in db_result["row_counts"].values() if isinstance(count, int)):
                recommendations.append(f"⚠️ {db_file} táblái üresek - töltsd fel adatokkal")

        # GeoJSON problémák
        for geojson_file, geojson_result in self.results["geojson_checks"].items():
            if not geojson_result["exists"]:
                recommendations.append(f"❌ {geojson_file} nem található - töltsd le a GeoJSON fájlokat")
            elif not geojson_result["valid_json"]:
                recommendations.append(f"❌ {geojson_file} hibás JSON formátum")
            elif geojson_result["feature_count"] == 0:
                recommendations.append(f"⚠️ {geojson_file} nem tartalmaz feature-öket")

        # Weather API problémák
        weather_check = self.results["weather_api_check"]
        if not weather_check["weather_client_available"]:
            recommendations.append("❌ WeatherClient modul nem elérhető - ellenőrizd az import útvonalakat")
        elif not weather_check["config_loaded"]:
            recommendations.append("❌ WeatherClient konfiguráció hiba - ellenőrizd a konfigurációs fájlokat")
        elif not weather_check["api_test_success"]:
            recommendations.append("❌ Weather API teszt sikertelen - ellenőrizd az internet kapcsolatot és API kulcsokat")

        # Multi-City Engine problémák
        engine_check = self.results["multi_city_engine_check"]
        if not engine_check["engine_available"]:
            recommendations.append("❌ MultiCityEngine modul nem elérhető - ellenőrizd az import útvonalakat")
        elif not engine_check["engine_initialized"]:
            recommendations.append("❌ MultiCityEngine inicializálás sikertelen - ellenőrizd a függőségeket")
        elif not engine_check["test_query_success"]:
            recommendations.append("❌ MultiCityEngine teszt lekérdezés sikertelen - ellenőrizd az adatbázis kapcsolatot és weather API-t")

        # Ha minden OK
        if not recommendations:
            recommendations.append("✅ Minden komponens működik! A rendszer használatra kész.")

        self.results["recommendations"] = recommendations

    def _print_results(self):
        """
        📋 Diagnosztikai eredmények kiírása.
        """
        print("\n" + "=" * 80)
        print("📋 DIAGNOSZTIKAI ÖSSZEGZÉS")
        print("=" * 80)

        # Komponens státuszok
        print("\n🔍 KOMPONENS STÁTUSZOK:")

        # Adatbázisok
        db_ok = all(result["exists"] and result.get("tables") for result in self.results["database_checks"].values())
        print(f"   📊 Adatbázisok: {'✅ OK' if db_ok else '❌ PROBLÉMA'}")

        # GeoJSON
        geojson_ok = all(result["exists"] and result["valid_json"] for result in self.results["geojson_checks"].values())
        print(f"   🗺️ GeoJSON fájlok: {'✅ OK' if geojson_ok else '❌ PROBLÉMA'}")

        # Weather API
        weather_ok = self.results["weather_api_check"]["api_test_success"]
        print(f"   🌤️ Weather API: {'✅ OK' if weather_ok else '❌ PROBLÉMA'}")

        # Multi-City Engine
        engine_ok = self.results["multi_city_engine_check"]["test_query_success"]
        print(f"   🏙️ Multi-City Engine: {'✅ OK' if engine_ok else '❌ PROBLÉMA'}")

        # Összesített státusz
        overall_ok = db_ok and geojson_ok and weather_ok and engine_ok
        print(f"\n🎯 ÖSSZESÍTETT STÁTUSZ: {'✅ MINDEN OK - RENDSZER KÉSZ!' if overall_ok else '❌ JAVÍTÁSOK SZÜKSÉGESEK'}")

        # Javaslatok
        print("\n💡 JAVASLATOK:")
        for recommendation in self.results["recommendations"]:
            print(f"   {recommendation}")

        # JSON export
        results_file = self.project_root / "diagnostics_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n💾 Részletes eredmények mentve: {results_file}")


def main():
    """
    🔍 Főprogram - diagnosztika futtatása.
    """
    print("🔍 Global Weather Analyzer - System Diagnostics")
    print("=" * 80)

    diagnostics = WeatherSystemDiagnostics()
    diagnostics.run_full_diagnostics()


if __name__ == "__main__":
    main()
