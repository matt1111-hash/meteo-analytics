#!/usr/bin/env python3
"""
Magyar Települések Adatbázis Integrátor - JSON alapú feltöltő
Forrás: magyar_telepulesek_2024_min.json
Cél: Teljes magyar települési adatbázis létrehozása a projekt számára.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Logger beállítása
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HungarianSettlementsJSONImporter:
    """
    3178 magyar település adatainak beolvasása JSON-ból és betöltése SQLite adatbázisba.
    """
    
    def __init__(self, json_path: str = "magyar_telepulesek_2024_min.json", db_path: str = "src/data/hungarian_settlements.db"):
        self.json_path = Path(json_path)
        self.db_path = Path(db_path)
        # Biztosítjuk, hogy a /src/data könyvtár létezzen
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def load_from_json(self) -> List[Dict]:
        """Adatok beolvasása a megadott JSON fájlból."""
        if not self.json_path.exists():
            logger.error(f"❌ A forrásfájl nem található: {self.json_path}")
            raise FileNotFoundError(f"A forrásfájl nem található: {self.json_path}")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"✅ Sikeresen beolvasva {len(data)} település a JSON fájlból.")
            return data

    def create_database_schema(self):
        """Adatbázis séma létrehozása a magyar települések adatai számára."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS hungarian_settlements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            settlement_type TEXT,
            megye TEXT,
            jaras TEXT,
            terulet_hektar REAL,
            population INTEGER,
            lakasok_szama INTEGER,
            latitude REAL,
            longitude REAL,
            climate_zone TEXT,
            data_source TEXT DEFAULT 'JSON_2024',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Indexek a gyorsabb kereséshez
        CREATE INDEX IF NOT EXISTS idx_name ON hungarian_settlements (name);
        CREATE INDEX IF NOT EXISTS idx_megye ON hungarian_settlements (megye);
        CREATE INDEX IF NOT EXISTS idx_jaras ON hungarian_settlements (jaras);
        CREATE INDEX IF NOT EXISTS idx_population ON hungarian_settlements (population DESC);
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(create_table_sql)
            logger.info(f"✅ Adatbázis séma létrehozva/ellenőrizve itt: {self.db_path}")

    def process_and_insert_data(self, settlements_data: List[Dict]):
        """JSON adatok feldolgozása és betöltése az adatbázisba."""
        processed_settlements = []
        for settlement in settlements_data:
            # Kihagyjuk az "Összesen" sort, ha van ilyen
            if settlement.get("telepules") == "Összesen":
                continue

            processed = {
                'name': settlement.get("telepules"),
                'settlement_type': settlement.get("jogallas"),
                'megye': settlement.get("megye"),
                'jaras': settlement.get("jaras_nev"),
                'terulet_hektar': settlement.get("terulet_ha"),
                'population': settlement.get("nepesseg"),
                'lakasok_szama': settlement.get("lakasok_szama"),
                # Koordináták helyőrzővel, ahogy a régi szkriptben is volt
                'latitude': 47.4979,
                'longitude': 19.0402,
                'climate_zone': self._determine_climate_zone(47.4979, 19.0402) # Egyelőre ez is placeholder
            }
            processed_settlements.append(processed)

        self._batch_insert_settlements(processed_settlements)
        logger.info(f"✅ {len(processed_settlements)} település sikeresen betöltve az adatbázisba.")

    def _batch_insert_settlements(self, settlements: List[Dict]):
        """Adatok kötegelt beszúrása az adatbázisba."""
        insert_sql = """
        INSERT INTO hungarian_settlements 
        (name, settlement_type, megye, jaras, terulet_hektar, population, lakasok_szama, latitude, longitude, climate_zone)
        VALUES (:name, :settlement_type, :megye, :jaras, :terulet_hektar, :population, :lakasok_szama, :latitude, :longitude, :climate_zone)
        """
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Meglévő adatok törlése a tiszta import érdekében
            cursor.execute("DELETE FROM hungarian_settlements;")
            logger.info("Régi adatok törölve az adatbázisból az új import előtt.")
            
            cursor.executemany(insert_sql, settlements)
            conn.commit()

    def _determine_climate_zone(self, lat: float, lon: float) -> str:
        """Egyszerűsített klíma-zóna besorolás (később fejleszthető)."""
        if lat > 47.5:
            return "Északi-középhegység"
        elif lon < 18.5 and lat > 46.5:
            return "Dunántúl"  
        elif lon > 19.5 and lat < 47.0:
            return "Alföld"
        else:
            return "Átmeneti"

    def run_import(self):
        """A teljes importálási folyamat futtatása."""
        logger.info("🇭🇺 Magyar Települések Adatbázis Generátor Indítása (JSON forrásból)...")
        # 1. JSON beolvasása
        settlements = self.load_from_json()
        # 2. Adatbázis séma létrehozása
        self.create_database_schema()
        # 3. Adatok feldolgozása és betöltése
        self.process_and_insert_data(settlements)
        logger.info("🎉 Az importálási folyamat sikeresen lezajlott.")

def main():
    """A szkript fő belépési pontja."""
    importer = HungarianSettlementsJSONImporter()
    importer.run_import()

if __name__ == "__main__":
    main()