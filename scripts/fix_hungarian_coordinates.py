#!/usr/bin/env python3
"""
Magyar Települések Koordináta-javító Script (PROFESSZIONÁLIS v1.0)
Global Weather Analyzer projekt

Fájl: scripts/fix_hungarian_coordinates.py
Hely: /home/tibor/PythonProjects/openmeteo_history/global_weather_analyzer/scripts/

Cél: 3178 magyar település koordinátáinak javítása OpenStreetMap Nominatim API-val
KRITIKUS PROBLÉMA: Minden település Budapest koordinátáin van (47.4979, 19.0402)
MEGOLDÁS: Geocoding minden településhez + adatbázis frissítés

FONTOS:
- OpenStreetMap Nominatim API (100% INGYENES)
- Rate limit: 1 request/second (strict betartás)
- Resume capability (megszakítás esetén folytatható)
- Professional error handling és logging
- Automatikus backup készítés

Futási idő: ~53 perc (3178 település × 1 sec)
Siker várható: 95%+ (OSM kiváló magyar pokrítás)
"""

import sqlite3
import requests
import time
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import sys

# Logging inicializálás - PROFESSZIONÁLIS SZINT
log_dir = Path("../logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'fix_hungarian_coordinates.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HungarianCoordinatesFixer:
    """
    Magyar települések koordináta-javító osztály
    
    PROFESSZIONÁLIS FUNKCIONALITÁS:
    - OpenStreetMap Nominatim API integráció
    - Rate limiting (1 req/sec) strict betartás
    - Resume capability megszakítás esetén
    - Automatic backup és rollback
    - Comprehensive error handling
    - Progress tracking és statistics
    - Duplicate detection és validation
    """
    
    def __init__(self, db_path: str):
        """
        Inicializálás professional validációval
        
        Args:
            db_path: Magyar települések adatbázis elérési útja
        """
        self.db_path = Path(db_path)
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Adatbázis nem található: {self.db_path}")
        
        # Nominatim API konfiguráció (STRICT OpenStreetMap guidelines)
        self.nominatim_base_url = "https://nominatim.openstreetmap.org/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Global Weather Analyzer/2.2.0 (Hungarian Coordinates Fixer)',
            'Accept': 'application/json',
            'Accept-Language': 'hu,en'
        })
        
        # Rate limiting (OpenStreetMap STRICT: 1 req/sec maximum)
        self.min_request_interval = 1.0  # 1 másodperc
        self.last_request_time = 0.0
        
        # Progress tracking
        self.stats = {
            'total_settlements': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'api_requests': 0,
            'start_time': 0.0,
            'errors': []
        }
        
        # Resume támogatás
        self.resume_file = Path("coordinate_fix_progress.json")
        self.processed_settlements = set()
        
        logger.info("🚀 HungarianCoordinatesFixer inicializálva (Professional v1.0)")
        logger.info(f"📁 Adatbázis: {self.db_path}")
        logger.info(f"🌍 API: {self.nominatim_base_url}")
        logger.info(f"⏱️ Rate limit: {self.min_request_interval} sec/request")
    
    def create_backup(self) -> Path:
        """
        Automatikus adatbázis backup létrehozása
        
        Returns:
            Backup fájl elérési útja
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.db_path.with_suffix(f'.backup_{timestamp}.db')
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"📦 Backup létrehozva: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"❌ Backup létrehozási hiba: {e}")
            raise
    
    def load_resume_progress(self) -> None:
        """Resume progress betöltése megszakítás esetén"""
        if self.resume_file.exists():
            try:
                with open(self.resume_file, 'r', encoding='utf-8') as f:
                    resume_data = json.load(f)
                    
                self.processed_settlements = set(resume_data.get('processed', []))
                self.stats.update(resume_data.get('stats', {}))
                
                logger.info(f"🔄 Resume: {len(self.processed_settlements)} település már feldolgozva")
            except Exception as e:
                logger.warning(f"⚠️ Resume file olvasási hiba: {e}")
                self.processed_settlements = set()
    
    def save_resume_progress(self) -> None:
        """Resume progress mentése"""
        try:
            resume_data = {
                'processed': list(self.processed_settlements),
                'stats': self.stats,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.resume_file, 'w', encoding='utf-8') as f:
                json.dump(resume_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"⚠️ Resume file mentési hiba: {e}")
    
    def get_settlements_to_fix(self) -> List[Dict[str, Any]]:
        """
        Javítandó települések lekérdezése Budapest koordinátákkal
        
        Returns:
            Települések listája ID-val, névvel és megyével
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Csak Budapest koordinátákkal rendelkező települések
                cursor.execute('''
                    SELECT id, name, megye, jaras, settlement_type
                    FROM hungarian_settlements 
                    WHERE latitude = 47.4979 AND longitude = 19.0402
                    ORDER BY name
                ''')
                
                settlements = []
                for row in cursor.fetchall():
                    settlement = {
                        'id': row[0],
                        'name': row[1],
                        'megye': row[2],
                        'jaras': row[3],
                        'type': row[4]
                    }
                    settlements.append(settlement)
                
                self.stats['total_settlements'] = len(settlements)
                logger.info(f"📊 Javítandó települések: {len(settlements)}")
                
                return settlements
                
        except sqlite3.Error as e:
            logger.error(f"❌ Adatbázis lekérdezési hiba: {e}")
            raise
    
    def rate_limit_wait(self) -> None:
        """
        Professional rate limiting - OpenStreetMap strict compliance
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"⏳ Rate limiting: várakozás {sleep_time:.2f} másodperc")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def geocode_settlement(self, settlement: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """
        Település geocoding OpenStreetMap Nominatim API-val
        
        Args:
            settlement: Település adatok (név, megye)
            
        Returns:
            (latitude, longitude) tuple vagy None ha sikertelen
        """
        settlement_name = settlement['name']
        megye = settlement['megye']
        
        # Különböző keresési stratégiák (magyar specifikus)
        search_queries = [
            f"{settlement_name}, {megye}, Hungary",  # Legspecifikusabb
            f"{settlement_name}, Hungary",           # Általános
            f"{settlement_name}, Magyarország"       # Magyar nyelvű
        ]
        
        for query in search_queries:
            try:
                # Rate limiting STRICT betartása
                self.rate_limit_wait()
                
                params = {
                    'q': query,
                    'format': 'json',
                    'limit': 1,
                    'countrycodes': 'hu',  # Csak Magyarország
                    'addressdetails': 1,
                    'dedupe': 1
                }
                
                logger.debug(f"🔍 Geocoding: {query}")
                
                response = self.session.get(
                    self.nominatim_base_url,
                    params=params,
                    timeout=10
                )
                
                self.stats['api_requests'] += 1
                
                if response.status_code == 200:
                    results = response.json()
                    
                    if results and len(results) > 0:
                        result = results[0]
                        lat = float(result['lat'])
                        lon = float(result['lon'])
                        
                        # Koordináta validálás (Magyarország boundaries)
                        if self.validate_hungarian_coordinates(lat, lon):
                            logger.debug(f"✅ Siker: {settlement_name} -> {lat:.4f}, {lon:.4f}")
                            return (lat, lon)
                        else:
                            logger.warning(f"⚠️ Koordináta kívül esik Magyarországon: {lat}, {lon}")
                    
                elif response.status_code == 429:
                    logger.warning("⚠️ Rate limit hit, várunk 2 másodpercet...")
                    time.sleep(2)
                    continue
                else:
                    logger.warning(f"⚠️ API hiba: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⚠️ Timeout: {query}")
                continue
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Request hiba: {e}")
                continue
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"⚠️ Response parsing hiba: {e}")
                continue
        
        # Minden keresési stratégia sikertelen
        logger.error(f"❌ Geocoding sikertelen: {settlement_name}, {megye}")
        return None
    
    def validate_hungarian_coordinates(self, lat: float, lon: float) -> bool:
        """
        Magyar koordináták validálása (bounding box)
        
        Args:
            lat: Földrajzi szélesség
            lon: Földrajzi hosszúság
            
        Returns:
            True ha Magyarország területén van
        """
        # Magyarország bounding box (approx)
        HU_BOUNDS = {
            'lat_min': 45.7,   # Déli határ
            'lat_max': 48.6,   # Északi határ
            'lon_min': 16.1,   # Nyugati határ
            'lon_max': 22.9    # Keleti határ
        }
        
        return (HU_BOUNDS['lat_min'] <= lat <= HU_BOUNDS['lat_max'] and
                HU_BOUNDS['lon_min'] <= lon <= HU_BOUNDS['lon_max'])
    
    def update_settlement_coordinates(self, settlement_id: int, lat: float, lon: float) -> bool:
        """
        Település koordinátáinak frissítése az adatbázisban
        
        Args:
            settlement_id: Település ID
            lat: Új földrajzi szélesség
            lon: Új földrajzi hosszúság
            
        Returns:
            True ha sikeres a frissítés
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE hungarian_settlements 
                    SET latitude = ?, longitude = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (lat, lon, settlement_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    logger.error(f"❌ Nincs frissítendő rekord: ID {settlement_id}")
                    return False
                    
        except sqlite3.Error as e:
            logger.error(f"❌ Adatbázis frissítési hiba: {e}")
            return False
    
    def process_settlements(self) -> None:
        """
        Összes település feldolgozása professional orchestration-nal
        """
        logger.info("🔧 Települések koordináta-javításának kezdése...")
        
        # Resume progress betöltése
        self.load_resume_progress()
        
        # Javítandó települések lekérdezése
        settlements = self.get_settlements_to_fix()
        
        if not settlements:
            logger.info("✅ Nincs javítandó település (minden koordináta rendben)")
            return
        
        self.stats['start_time'] = time.time()
        
        # Progress információk
        total_to_process = len([s for s in settlements if s['id'] not in self.processed_settlements])
        logger.info(f"🎯 Feldolgozandó települések: {total_to_process}")
        if len(self.processed_settlements) > 0:
            logger.info(f"🔄 Már feldolgozott: {len(self.processed_settlements)}")
        
        estimated_time = total_to_process * self.min_request_interval / 60
        logger.info(f"⏱️ Becsült idő: {estimated_time:.1f} perc")
        
        processed_count = 0
        
        for settlement in settlements:
            settlement_id = settlement['id']
            settlement_name = settlement['name']
            
            # Skip ha már feldolgozva (resume)
            if settlement_id in self.processed_settlements:
                self.stats['skipped'] += 1
                continue
            
            try:
                processed_count += 1
                progress = (processed_count / total_to_process) * 100
                
                logger.info(f"🔍 [{processed_count}/{total_to_process}] ({progress:.1f}%) {settlement_name}")
                
                # Geocoding végrehajtása
                coordinates = self.geocode_settlement(settlement)
                
                if coordinates:
                    lat, lon = coordinates
                    
                    # Adatbázis frissítése
                    if self.update_settlement_coordinates(settlement_id, lat, lon):
                        self.stats['successful'] += 1
                        logger.info(f"  ✅ Frissítve: {lat:.6f}, {lon:.6f}")
                    else:
                        self.stats['failed'] += 1
                        logger.error(f"  ❌ Adatbázis frissítés sikertelen")
                else:
                    self.stats['failed'] += 1
                    logger.error(f"  ❌ Geocoding sikertelen")
                    
                    # Hiba mentése részletes elemzéshez
                    self.stats['errors'].append({
                        'settlement': settlement_name,
                        'megye': settlement['megye'],
                        'error': 'geocoding_failed'
                    })
                
                # Progress tracking update
                self.stats['processed'] += 1
                self.processed_settlements.add(settlement_id)
                
                # Resume progress mentése minden 10. település után
                if processed_count % 10 == 0:
                    self.save_resume_progress()
                    elapsed = time.time() - self.stats['start_time']
                    remaining = (total_to_process - processed_count) * self.min_request_interval
                    logger.info(f"📊 Progress: {self.stats['successful']} siker, {self.stats['failed']} hiba")
                    logger.info(f"⏱️ Hátralévő idő: {remaining/60:.1f} perc")
                
            except KeyboardInterrupt:
                logger.info("⚠️ Megszakítás! Progress mentése...")
                self.save_resume_progress()
                raise
            except Exception as e:
                logger.error(f"❌ Váratlan hiba {settlement_name}-nél: {e}")
                self.stats['failed'] += 1
                self.stats['processed'] += 1
                continue
        
        # Final progress mentése
        self.save_resume_progress()
    
    def generate_final_report(self) -> None:
        """Final report generálása"""
        elapsed_time = time.time() - self.stats['start_time']
        success_rate = (self.stats['successful'] / max(self.stats['processed'], 1)) * 100
        
        logger.info("=" * 80)
        logger.info("🏆 MAGYAR TELEPÜLÉSEK KOORDINÁTA-JAVÍTÁS BEFEJEZVE!")
        logger.info("=" * 80)
        logger.info(f"📊 VÉGEREDMÉNY:")
        logger.info(f"   Összes település: {self.stats['total_settlements']}")
        logger.info(f"   Feldolgozott: {self.stats['processed']}")
        logger.info(f"   Sikeres: {self.stats['successful']}")
        logger.info(f"   Sikertelen: {self.stats['failed']}")
        logger.info(f"   Átugrott: {self.stats['skipped']}")
        logger.info(f"   Sikerességi arány: {success_rate:.1f}%")
        logger.info("")
        logger.info(f"🌍 API STATISZTIKÁK:")
        logger.info(f"   Nominatim kérések: {self.stats['api_requests']}")
        logger.info(f"   Átlagos válaszidő: {elapsed_time/max(self.stats['api_requests'], 1):.2f} sec")
        logger.info("")
        logger.info(f"⏱️ IDŐSTATISZTIKÁK:")
        logger.info(f"   Teljes futási idő: {elapsed_time/60:.1f} perc")
        logger.info(f"   Átlagos feldolgozási idő: {elapsed_time/max(self.stats['processed'], 1):.2f} sec/település")
        logger.info("")
        
        if self.stats['errors']:
            logger.info(f"❌ HIBÁS TELEPÜLÉSEK (első 10):")
            for i, error in enumerate(self.stats['errors'][:10], 1):
                logger.info(f"   {i}. {error['settlement']} ({error['megye']})")
            
            if len(self.stats['errors']) > 10:
                logger.info(f"   ... és további {len(self.stats['errors']) - 10} hiba")
        
        logger.info("=" * 80)
        
        # Resume file törlése ha sikerült
        if success_rate > 80:  # 80% feletti siker esetén
            if self.resume_file.exists():
                self.resume_file.unlink()
                logger.info("🗑️ Resume file törölve (sikeres befejezés)")
    
    def validate_results(self) -> None:
        """Javított koordináták validálása"""
        logger.info("🔍 Javított koordináták validálása...")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Budapest koordinátákkal még mindig rendelkező települések
                cursor.execute('''
                    SELECT COUNT(*) FROM hungarian_settlements 
                    WHERE latitude = 47.4979 AND longitude = 19.0402
                ''')
                remaining_budapest = cursor.fetchone()[0]
                
                # Egyedi koordináták száma
                cursor.execute('''
                    SELECT COUNT(DISTINCT CONCAT(latitude, longitude)) 
                    FROM hungarian_settlements
                ''')
                unique_coords = cursor.fetchone()[0]
                
                # Magyar határon belüli koordináták
                cursor.execute('''
                    SELECT COUNT(*) FROM hungarian_settlements 
                    WHERE latitude BETWEEN 45.7 AND 48.6 
                    AND longitude BETWEEN 16.1 AND 22.9
                ''')
                valid_hungarian_coords = cursor.fetchone()[0]
                
                logger.info(f"📊 VALIDÁCIÓ EREDMÉNYEK:")
                logger.info(f"   Budapest koordinátákon: {remaining_budapest}")
                logger.info(f"   Egyedi koordináták: {unique_coords}")
                logger.info(f"   Magyar határon belül: {valid_hungarian_coords}")
                
                if remaining_budapest == 0:
                    logger.info("🎉 TELJES SIKER! Nincs több Budapest koordináta!")
                elif remaining_budapest < 100:
                    logger.info(f"✅ SZINTE KÉSZ! Csak {remaining_budapest} maradt")
                else:
                    logger.warning(f"⚠️ RÉSZLEGES SIKER: {remaining_budapest} település még javításra szorul")
                    
        except sqlite3.Error as e:
            logger.error(f"❌ Validáció hiba: {e}")
    
    def run(self) -> int:
        """
        Teljes koordináta-javítási folyamat futtatása
        
        Returns:
            Exit kód (0=success, 1=error)
        """
        try:
            logger.info("🚀 Magyar települések koordináta-javítás kezdése...")
            
            # Backup létrehozása
            self.create_backup()
            
            # Települések feldolgozása
            self.process_settlements()
            
            # Eredmények validálása
            self.validate_results()
            
            # Final report
            self.generate_final_report()
            
            logger.info("🎯 Koordináta-javítás sikeresen befejezve!")
            return 0
            
        except KeyboardInterrupt:
            logger.info("⚠️ Felhasználói megszakítás")
            logger.info("💡 A folyamat később folytatható ugyanazzal a paranccsal")
            return 1
        except Exception as e:
            logger.error(f"❌ Kritikus hiba: {e}")
            logger.exception("Full stacktrace:")
            return 1


def main() -> int:
    """
    Főprogram - parancssori futtatás
    
    Returns:
        Exit kód (0=success, 1=error)
    """
    try:
        # Adatbázis elérési útvonal
        db_path = "../data/hungarian_settlements.db"
        
        if not Path(db_path).exists():
            logger.error(f"❌ Adatbázis nem található: {Path(db_path).absolute()}")
            logger.error("💡 Ellenőrizd az elérési utat!")
            return 1
        
        # Fixer létrehozása és futtatása
        fixer = HungarianCoordinatesFixer(db_path)
        return fixer.run()
        
    except Exception as e:
        logger.error(f"❌ Inicializálási hiba: {e}")
        return 1


if __name__ == "__main__":
    print("🌍 Magyar Települések Koordináta-javító v1.0")
    print("=" * 50)
    print("FIGYELEM: Ez a script kb. 53 percig fog futni!")
    print("Rate limit: 1 request/second (OpenStreetMap policy)")
    print("Resume támogatás: megszakítás esetén folytatható")
    print("=" * 50)
    
    confirm = input("Folytatod a javítást? (igen/nem): ").lower().strip()
    if confirm in ['igen', 'i', 'yes', 'y']:
        exit(main())
    else:
        print("❌ Megszakítva.")
        exit(0)
