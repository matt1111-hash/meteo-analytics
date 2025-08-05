#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ GeoJSON Fájlok Tesztelő és Validáló Szkript
Magyar Klímaanalitika MVP - Térkép Komponens Előkészítés

Fájl helye: test_geojson.py (projekt root)
Futtatás: python test_geojson.py
"""

import os
import json
import sys
from pathlib import Path

def test_geojson_files():
    """
    GeoJSON fájlok tesztelése és validálása.
    """
    print("🗺️ GEOJSON FÁJLOK TESZTELÉSE ÉS VALIDÁLÁSA")
    print("=" * 50)
    
    # Projekt root könyvtár
    project_root = Path(__file__).parent
    geojson_dir = project_root / "data" / "geojson"
    
    print(f"📁 GeoJSON könyvtár: {geojson_dir}")
    print(f"📁 Könyvtár létezik: {geojson_dir.exists()}")
    
    if not geojson_dir.exists():
        print("❌ GeoJSON könyvtár nem található!")
        return False
    
    # Fájlok ellenőrzése
    counties_file = geojson_dir / "counties.geojson"
    postal_codes_file = geojson_dir / "postal_codes.geojson"
    
    print("\n📋 FÁJL INFORMÁCIÓK:")
    print("-" * 30)
    
    # Counties.geojson tesztelése
    if counties_file.exists():
        file_size = counties_file.stat().st_size
        print(f"✅ counties.geojson - {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        try:
            # JSON validálás
            with open(counties_file, 'r', encoding='utf-8') as f:
                counties_data = json.load(f)
            
            print(f"   📊 GeoJSON típus: {counties_data.get('type', 'Ismeretlen')}")
            
            if 'features' in counties_data:
                feature_count = len(counties_data['features'])
                print(f"   🗺️ Features száma: {feature_count}")
                
                # Első feature elemzése
                if feature_count > 0:
                    first_feature = counties_data['features'][0]
                    properties = first_feature.get('properties', {})
                    geometry_type = first_feature.get('geometry', {}).get('type', 'Ismeretlen')
                    
                    print(f"   📐 Geometria típus: {geometry_type}")
                    print(f"   🏷️ Tulajdonságok: {list(properties.keys())}")
                    
                    # Magyar megye nevek keresése
                    if properties:
                        print(f"   📍 Első feature példa: {dict(list(properties.items())[:3])}")
                
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing hiba: {e}")
        except Exception as e:
            print(f"   ❌ Általános hiba: {e}")
    else:
        print("❌ counties.geojson nem található!")
    
    # Postal codes.geojson tesztelése
    if postal_codes_file.exists():
        file_size = postal_codes_file.stat().st_size
        print(f"✅ postal_codes.geojson - {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        try:
            # JSON validálás (csak header, mert nagy fájl)
            with open(postal_codes_file, 'r', encoding='utf-8') as f:
                # Első néhány sor beolvasása a nagy fájl miatt
                first_chunk = f.read(10000)  # Első 10KB
                
            print("   📊 Fájl kezdete sikeresen olvasható")
            
            # Teljes fájl betöltése (opciós, ha nem túl nagy)
            if file_size < 50 * 1024 * 1024:  # 50MB alatt
                with open(postal_codes_file, 'r', encoding='utf-8') as f:
                    postal_data = json.load(f)
                
                print(f"   📊 GeoJSON típus: {postal_data.get('type', 'Ismeretlen')}")
                
                if 'features' in postal_data:
                    feature_count = len(postal_data['features'])
                    print(f"   🗺️ Features száma: {feature_count}")
                    
                    # Első feature elemzése
                    if feature_count > 0:
                        first_feature = postal_data['features'][0]
                        properties = first_feature.get('properties', {})
                        geometry_type = first_feature.get('geometry', {}).get('type', 'Ismeretlen')
                        
                        print(f"   📐 Geometria típus: {geometry_type}")
                        print(f"   🏷️ Tulajdonságok: {list(properties.keys())}")
                        
                        if properties:
                            print(f"   📍 Első feature példa: {dict(list(properties.items())[:3])}")
            else:
                print("   ⚠️ Fájl túl nagy a teljes betöltéshez (>50MB)")
                
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing hiba: {e}")
        except Exception as e:
            print(f"   ❌ Általános hiba: {e}")
    else:
        print("❌ postal_codes.geojson nem található!")
    
    return True

def check_geopandas_installation():
    """
    GeoPandas telepítés ellenőrzése.
    """
    print("\n🐍 GEOPANDAS TELEPÍTÉS ELLENŐRZÉSE")
    print("=" * 40)
    
    try:
        import geopandas as gpd
        print(f"✅ GeoPandas telepítve - verzió: {gpd.__version__}")
        
        # További függőségek ellenőrzése
        try:
            import fiona
            print(f"✅ Fiona telepítve - verzió: {fiona.__version__}")
        except ImportError:
            print("⚠️ Fiona nem telepítve (GeoPandas függőség)")
        
        try:
            import shapely
            print(f"✅ Shapely telepítve - verzió: {shapely.__version__}")
        except ImportError:
            print("⚠️ Shapely nem telepítve (GeoPandas függőség)")
            
        return True
        
    except ImportError:
        print("❌ GeoPandas nincs telepítve!")
        print("📦 Telepítési parancs: pip install geopandas")
        return False

def test_geopandas_with_geojson():
    """
    GeoPandas tesztelése a GeoJSON fájlokkal.
    """
    print("\n🗺️ GEOPANDAS + GEOJSON INTEGRÁCIÓ TESZT")
    print("=" * 45)
    
    try:
        import geopandas as gpd
        
        # Projekt root könyvtár
        project_root = Path(__file__).parent
        counties_file = project_root / "data" / "geojson" / "counties.geojson"
        
        if not counties_file.exists():
            print("❌ counties.geojson nem található a teszthez!")
            return False
        
        print("📖 Counties.geojson betöltése GeoPandas-szal...")
        
        # GeoDataFrame betöltése
        gdf_counties = gpd.read_file(counties_file)
        
        print(f"✅ Sikeresen betöltve!")
        print(f"📊 Sorok száma: {len(gdf_counties)}")
        print(f"📊 Oszlopok száma: {len(gdf_counties.columns)}")
        print(f"📊 Oszlopok: {list(gdf_counties.columns)}")
        
        # CRS (koordináta rendszer) információ
        print(f"🌍 Koordináta rendszer (CRS): {gdf_counties.crs}")
        
        # Első néhány sor mintája
        print("\n📋 Első 3 sor adatmintája:")
        print(gdf_counties.head(3))
        
        # Geometria típusok ellenőrzése
        geom_types = gdf_counties.geometry.geom_type.value_counts()
        print(f"\n📐 Geometria típusok eloszlása:")
        for geom_type, count in geom_types.items():
            print(f"   {geom_type}: {count} db")
        
        # Bounding box információ
        bounds = gdf_counties.total_bounds
        print(f"\n🗺️ Térkép határoló téglalap:")
        print(f"   Min X (nyugat): {bounds[0]:.6f}")
        print(f"   Min Y (dél): {bounds[1]:.6f}")
        print(f"   Max X (kelet): {bounds[2]:.6f}")
        print(f"   Max Y (észak): {bounds[3]:.6f}")
        
        return True
        
    except ImportError:
        print("❌ GeoPandas nincs telepítve!")
        return False
    except Exception as e:
        print(f"❌ Hiba a GeoPandas tesztnél: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Fő teszt függvény.
    """
    print("🚀 MAGYAR TÉRKÉPES KOMPONENS - GEOJSON VALIDÁCIÓ")
    print("=" * 55)
    
    # 1. GeoJSON fájlok tesztelése
    geojson_ok = test_geojson_files()
    
    # 2. GeoPandas telepítés ellenőrzése
    geopandas_ok = check_geopandas_installation()
    
    # 3. GeoPandas + GeoJSON integráció tesztelése
    if geojson_ok and geopandas_ok:
        integration_ok = test_geopandas_with_geojson()
    else:
        integration_ok = False
        print("\n⚠️ GeoPandas integráció teszt kihagyva (hiányzó függőségek)")
    
    # Összefoglaló
    print("\n" + "=" * 55)
    print("📋 TESZT EREDMÉNYEK ÖSSZEFOGLALÓJA:")
    print(f"   🗺️ GeoJSON fájlok: {'✅ OK' if geojson_ok else '❌ HIBA'}")
    print(f"   🐍 GeoPandas: {'✅ OK' if geopandas_ok else '❌ HIÁNYZIK'}")
    print(f"   🔗 Integráció: {'✅ OK' if integration_ok else '❌ HIBA'}")
    
    if geojson_ok and geopandas_ok and integration_ok:
        print("\n🎉 MINDEN TESZT SIKERES! A térképes komponens fejlesztés indulhat!")
    else:
        print("\n⚠️ Néhány teszt sikertelen. Javítás szükséges a folytatás előtt.")
    
    print("\n📋 KÖVETKEZŐ LÉPÉSEK:")
    if not geopandas_ok:
        print("   1. GeoPandas telepítése: pip install geopandas")
    if geojson_ok and geopandas_ok and integration_ok:
        print("   1. Hierarchikus lokáció választó készítése")
        print("   2. Folium térkép komponens fejlesztése")
        print("   3. QWebEngineView integráció")

if __name__ == "__main__":
    main()
