#!/usr/bin/env python3
"""
Koordináta-Pótló Szkript a Magyar Települések Adatbázisához
Cél: A 'hungarian_settlements.db' adatbázis feltöltése valós GPS koordinátákkal
     az OpenStreetMap Nominatim API segítségével.
"""

import sqlite3
import requests
import time
import logging
from pathlib import Path
from typing import Optional

# Logger beállítása
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- KONFIGURÁCIÓ ---
# 🔧 KRITIKUS JAVÍTÁS: Az adatbázis a projekt gyökerében lévő `data` mappában van.
DB_PATH = Path("data/hungarian_settlements.db")
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "GlobalWeatherAnalyzer/1.0 (https://github.com/yourproject)"}
REQUEST_DELAY_SECONDS = 1.1 
DEFAULT_LAT = 47.4979
DEFAULT_LON = 19.0402

def get_settlements_to_update(conn: sqlite3.Connection) -> list:
    """Lekérdezi az adatbázisból azokat a településeket, amik még nincsenek geokódolva."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, megye FROM hungarian_settlements WHERE latitude = ? AND longitude = ?",
        (DEFAULT_LAT, DEFAULT_LON)
    )
    return cursor.fetchall()

def get_coordinates_from_osm(session: requests.Session, settlement_name: str, megye: str) -> Optional[tuple[float, float]]:
    """Lekérdezi egy település koordinátáit a Nominatim API-tól."""
    if megye:
        query = f"{settlement_name}, {megye}, Magyarország"
    else:
        query = f"{settlement_name}, Magyarország"
        
    params = {'q': query, 'format': 'json', 'limit': 1}
    
    try:
        response = session.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            if 45.5 < lat < 49.0 and 16.0 < lon < 23.0:
                return lat, lon
            else:
                logger.warning(f"OSM érvénytelen koordinátát adott vissza '{query}'-re: [{lat}, {lon}]")
                return None
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API hiba a '{query}' lekérdezésénél: {e}")
        return None
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Válasz feldolgozási hiba a '{query}' lekérdezésénél: {e}")
        return None

def update_settlement_coordinates(conn: sqlite3.Connection, settlement_id: int, lat: float, lon: float):
    """Frissíti egy település koordinátáit az adatbázisban."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE hungarian_settlements SET latitude = ?, longitude = ? WHERE id = ?",
        (lat, lon, settlement_id)
    )

def main():
    """A fő geokódolási folyamat."""
    if not DB_PATH.exists():
        logger.error(f"Adatbázis nem található itt: {DB_PATH}. Kérlek, ellenőrizd a fájl helyét.")
        return

    conn = sqlite3.connect(DB_PATH)
    session = requests.Session()
    
    logger.info("📍 Koordináta-pótló szkript elindítva...")
    
    settlements_to_update = get_settlements_to_update(conn)
    total_count = len(settlements_to_update)
    
    if total_count == 0:
        logger.info("✅ Nincs frissítendő település. Az adatbázis naprakész.")
        conn.close()
        return

    logger.info(f"Frissítendő települések száma: {total_count}")
    
    success_count = 0
    fail_count = 0

    try:
        for i, (settlement_id, name, megye) in enumerate(settlements_to_update):
            print(f"\rFeldolgozás... {i + 1}/{total_count} ({name})", end="", flush=True)
            
            coords = get_coordinates_from_osm(session, name, megye)
            
            if coords:
                update_settlement_coordinates(conn, settlement_id, coords[0], coords[1])
                success_count += 1
            else:
                logger.warning(f"\nNem sikerült koordinátát találni: {name}, {megye}")
                fail_count += 1
            
            if (i + 1) % 50 == 0:
                conn.commit()
                logger.info(f"\nAdatok mentve az adatbázisba ({i+1}/{total_count})...")

            time.sleep(REQUEST_DELAY_SECONDS)
    
    except KeyboardInterrupt:
        logger.warning("\nFolyamat megszakítva a felhasználó által.")
    
    finally:
        conn.commit()
        conn.close()

        print("\n" + "="*50)
        logger.info("🎉 Geokódolás befejezve!")
        logger.info(f"Sikeres frissítések: {success_count}")
        logger.info(f"Sikertelen lekérdezések: {fail_count}")
        logger.info(f"Az adatbázis ({DB_PATH}) most már valós koordinátákat tartalmaz.")
        print("="*50)

if __name__ == "__main__":
    main()