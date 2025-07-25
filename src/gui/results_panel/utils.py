#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Results Panel Utility Classes
Közös utility osztályok a results panel moduljai számára.
🌪️ WIND GUSTS TÁMOGATÁS: Élethű széllökés kategorizálás és értékelés
🚀 PROFESSIONAL CODING: DRY, KISS, SOLID principles
🔧 MODULÁRIS DESIGN: Újrafelhasználható komponensek

🏗️ UTILITY OSZTÁLYOK:
✅ WindGustsConstants - Széllökés konstansok és küszöbök
✅ DataFrameExtractor - DataFrame konvertálás és validálás  
✅ WindGustsAnalyzer - Széllökés elemzés és kategorizálás

🎯 HASZNÁLAT:
from .utils import WindGustsConstants, DataFrameExtractor, WindGustsAnalyzer
"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd

# Logging konfigurálása
logger = logging.getLogger(__name__)


class WindGustsConstants:
    """
    🌪️ Széllökés kategorizálási és küszöb konstansok.
    METEOROLÓGIAI STANDARDOKRA KALIBRÁLT értékek.
    """
    
    # Széllökés kategóriák km/h-ban - ÉLETHŰ ÉRTÉKEK
    MODERATE_THRESHOLD = 50.0    # Mérsékelt széllökés (Beaufort 6-7)
    STRONG_THRESHOLD = 70.0      # Erős széllökés (Beaufort 8)
    EXTREME_THRESHOLD = 100.0    # Extrém széllökés (Beaufort 10)
    HURRICANE_THRESHOLD = 120.0  # Hurrikán erősségű (Beaufort 12)
    
    # Windy days küszöbök (data source alapján)
    WINDY_THRESHOLD_GUSTS = 70.0      # wind_gusts_max esetén
    WINDY_THRESHOLD_WINDSPEED = 20.0  # windspeed_10m_max esetén
    
    # Kategória címkék - MAGYAR LOKALIZÁCIÓ
    CATEGORIES = {
        'moderate': 'MÉRSÉKELT',
        'strong': 'ERŐS', 
        'extreme': 'EXTRÉM',
        'hurricane': 'HURRIKÁN ERŐSSÉGŰ'
    }
    
    # Kategória színek (ThemeManager kompatibilis)
    CATEGORY_COLORS = {
        'moderate': 'success',     # Zöld - biztonságos
        'strong': 'warning',       # Sárga - figyelem
        'extreme': 'error',        # Piros - veszélyes  
        'hurricane': 'error'       # Piros - kritikus
    }
    
    # Emoji ikonok kategóriánként
    CATEGORY_EMOJIS = {
        'moderate': '💨',
        'strong': '🌪️', 
        'extreme': '⚠️',
        'hurricane': '🚨'
    }


class DataFrameExtractor:
    """
    Adatok DataFrame-be konvertálásáért felelős utility osztály.
    🚀 SOLID: Single Responsibility Principle
    🌪️ WIND GUSTS TÁMOGATÁS: wind_gusts_max prioritással, windspeed_10m_max fallback-kel
    """
    
    @staticmethod
    def extract_safely(data: Dict[str, Any]) -> pd.DataFrame:
        """
        Adatok DataFrame-be konvertálása - robusztus implementáció.
        🌪️ WIND GUSTS PRIORITÁS: wind_gusts_max → windspeed_10m_max fallback
        
        Args:
            data: OpenMeteo API válasz
            
        Returns:
            pandas.DataFrame: Feldolgozott időjárási adatok
            
        Raises:
            ValueError: Ha az adatok nem megfelelő formátumúak
        """
        try:
            logger.debug("DataFrameExtractor.extract_safely() - START")
            
            daily_data = data.get("daily", {})
            if not daily_data:
                logger.warning("Nincs 'daily' adat a válaszban")
                return pd.DataFrame()
            
            dates = daily_data.get("time", [])
            if not dates:
                logger.warning("Nincs 'time' adat a daily adatokban")
                return pd.DataFrame()
            
            logger.debug(f"Extracting {len(dates)} napok adatai...")
            
            # === HŐMÉRSÉKLET ADATOK ===
            temp_max = daily_data.get("temperature_2m_max", [])
            temp_min = daily_data.get("temperature_2m_min", [])
            temp_mean = daily_data.get("temperature_2m_mean", [])
            
            # === CSAPADÉK ADATOK ===
            precip = daily_data.get("precipitation_sum", [])
            
            # === 🌪️ KRITIKUS: WIND GUSTS PRIORITÁS ===
            wind_gusts_max = daily_data.get("wind_gusts_max", [])
            windspeed_10m_max = daily_data.get("windspeed_10m_max", [])
            
            # Hiányzó temp_mean számítása ha nincs
            if not temp_mean and temp_max and temp_min:
                logger.debug("Temp_mean számítása temp_max és temp_min alapján...")
                temp_mean = [
                    round((t_max + t_min) / 2, 1) if t_max is not None and t_min is not None else None
                    for t_max, t_min in zip(temp_max, temp_min)
                ]
            
            max_length = len(dates)
            
            # === DATAFRAME ÖSSZEÁLLÍTÁSA ===
            df_data = {
                'date': dates,
                'temp_max': DataFrameExtractor._ensure_length(temp_max, max_length),
                'temp_min': DataFrameExtractor._ensure_length(temp_min, max_length),
                'precipitation': DataFrameExtractor._ensure_length(precip, max_length)
            }
            
            # Temp_mean hozzáadása ha van
            if temp_mean:
                df_data['temp_mean'] = DataFrameExtractor._ensure_length(temp_mean, max_length)
            
            # === 🌪️ KRITIKUS: WIND DATA SOURCE DETECTION ===
            if wind_gusts_max:
                # ELSŐDLEGES: wind_gusts_max (élethű széllökések)
                df_data['windspeed'] = DataFrameExtractor._ensure_length(wind_gusts_max, max_length)
                df_data['wind_data_source'] = ['wind_gusts_max'] * max_length
                logger.info(f"✅ Wind data source: wind_gusts_max ({len(wind_gusts_max)} values)")
                
            elif windspeed_10m_max:
                # FALLBACK: windspeed_10m_max (szélsebesség átlag)
                df_data['windspeed'] = DataFrameExtractor._ensure_length(windspeed_10m_max, max_length)
                df_data['wind_data_source'] = ['windspeed_10m_max'] * max_length
                logger.warning(f"⚠️ Fallback to windspeed_10m_max ({len(windspeed_10m_max)} values)")
                
            else:
                # NINCS SZÉL ADAT
                logger.error("❌ Nincs szél adat sem wind_gusts_max, sem windspeed_10m_max")
                df_data['windspeed'] = [None] * max_length
                df_data['wind_data_source'] = ['no_data'] * max_length
            
            # DataFrame létrehozása
            df = pd.DataFrame(df_data)
            
            logger.info(f"✅ DataFrame extracted successfully: {df.shape} (rows, cols)")
            logger.debug(f"Columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ DataFrame extract hiba: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def _ensure_length(lst: List, target: int) -> List:
        """
        Lista hosszának biztosítása célérték szerint.
        
        Args:
            lst: Input lista
            target: Célhossz
            
        Returns:
            List: Megfelelő hosszúságú lista
        """
        if not lst:
            return [None] * target
            
        current_len = len(lst)
        
        if current_len == target:
            return lst
        elif current_len < target:
            # Kiegészítés None értékekkel
            return lst + [None] * (target - current_len)
        else:
            # Levágas célhosszra
            return lst[:target]
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        DataFrame validálása és minőség ellenőrzése.
        
        Args:
            df: Validálandó DataFrame
            
        Returns:
            Validációs eredmények dictionary
        """
        try:
            if df.empty:
                return {
                    "valid": False,
                    "error": "DataFrame üres",
                    "rows": 0,
                    "columns": 0
                }
            
            # Alapvető statisztikák
            stats = {
                "valid": True,
                "rows": len(df),
                "columns": len(df.columns),
                "date_range": None,
                "missing_data": {},
                "wind_source": "unknown"
            }
            
            # Dátum tartomány
            if 'date' in df.columns and not df['date'].empty:
                stats["date_range"] = f"{df['date'].iloc[0]} - {df['date'].iloc[-1]}"
            
            # Hiányzó adatok számlálása
            for col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    stats["missing_data"][col] = missing_count
            
            # Szél adatforrás detektálása
            if 'wind_data_source' in df.columns and not df['wind_data_source'].empty:
                stats["wind_source"] = df['wind_data_source'].iloc[0]
            
            logger.debug(f"DataFrame validation: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"DataFrame validation hiba: {e}")
            return {
                "valid": False,
                "error": str(e),
                "rows": 0,
                "columns": 0
            }


class WindGustsAnalyzer:
    """
    🌪️ Széllökés elemzésért felelős utility osztály.
    🚀 SOLID: Single Responsibility Principle
    🌪️ METEOROLÓGIAI STANDARDOK: Beaufort skála alapú kategorizálás
    """
    
    @staticmethod
    def categorize_wind_gust(wind_speed: float, data_source: str = 'wind_gusts_max') -> str:
        """
        Széllökés kategorizálása élethű értékek alapján.
        🌪️ METEOROLÓGIAI KALIBRÁLÁS: Beaufort skála szerinti kategóriák
        
        Args:
            wind_speed: Szélsebesség km/h-ban
            data_source: Adatforrás típusa ('wind_gusts_max' vagy 'windspeed_10m_max')
            
        Returns:
            str: Kategória neve ('moderate', 'strong', 'extreme', 'hurricane')
        """
        if wind_speed is None or wind_speed < 0:
            return 'moderate'  # Default safe category
        
        try:
            if data_source == 'wind_gusts_max':
                # ÉLETHŰ SZÉLLÖKÉS KÜSZÖBÖK (wind_gusts_max)
                if wind_speed >= WindGustsConstants.HURRICANE_THRESHOLD:
                    return 'hurricane'    # ≥120 km/h - Hurrikán (Beaufort 12)
                elif wind_speed >= WindGustsConstants.EXTREME_THRESHOLD:
                    return 'extreme'      # ≥100 km/h - Extrém vihar (Beaufort 10-11)
                elif wind_speed >= WindGustsConstants.STRONG_THRESHOLD:
                    return 'strong'       # ≥70 km/h - Erős vihar (Beaufort 8-9)
                elif wind_speed >= WindGustsConstants.MODERATE_THRESHOLD:
                    return 'strong'       # ≥50 km/h - Erős szél (Beaufort 7-8)
                else:
                    return 'moderate'     # <50 km/h - Mérsékelt (Beaufort 1-6)
            
            else:
                # WINDSPEED_10M_MAX KÜSZÖBÖK (alacsonyabbak)
                # Import from parent utils for backward compatibility
                from ..utils import AnomalyConstants
                
                if wind_speed >= AnomalyConstants.WIND_HIGH_THRESHOLD:  # ≥70 km/h
                    return 'strong'
                else:
                    return 'moderate'
            
        except Exception as e:
            logger.error(f"Wind gust categorization hiba: {e}")
            return 'moderate'  # Safe fallback
    
    @staticmethod
    def get_windy_days_threshold(data_source: str) -> float:
        """
        Szeles napok küszöbének meghatározása adatforrás alapján.
        
        Args:
            data_source: Adatforrás típusa
            
        Returns:
            float: Küszöbérték km/h-ban
        """
        if data_source == 'wind_gusts_max':
            return WindGustsConstants.WINDY_THRESHOLD_GUSTS  # 70.0 km/h
        else:
            return WindGustsConstants.WINDY_THRESHOLD_WINDSPEED  # 20.0 km/h
    
    @staticmethod
    def generate_wind_description(wind_speed: float, category: str, data_source: str) -> str:
        """
        Széllökés leírásának generálása.
        
        Args:
            wind_speed: Szélsebesség km/h-ban
            category: Kategória ('moderate', 'strong', 'extreme', 'hurricane')
            data_source: Adatforrás típusa
            
        Returns:
            str: Leírás szöveg emoji-val és értékkel
        """
        if wind_speed is None:
            return "❓ Nincs adat"
        
        try:
            # Kategória címke és emoji lekérdezése
            category_label = WindGustsConstants.CATEGORIES.get(category, 'ISMERETLEN')
            category_emoji = WindGustsConstants.CATEGORY_EMOJIS.get(category, '💨')
            
            if data_source == 'wind_gusts_max':
                # Részletes széllökés leírás
                return f"{category_emoji} {category_label} ({wind_speed:.1f} km/h)"
            else:
                # Egyszerű szélsebesség leírás
                return f"💨 Szél: {wind_speed:.1f} km/h"
        
        except Exception as e:
            logger.error(f"Wind description generation hiba: {e}")
            return f"💨 {wind_speed:.1f} km/h"
    
    @staticmethod
    def get_wind_risk_level(wind_speed: float, data_source: str = 'wind_gusts_max') -> Dict[str, Any]:
        """
        Széllökés kockázati szint meghatározása.
        
        Args:
            wind_speed: Szélsebesség km/h-ban
            data_source: Adatforrás típusa
            
        Returns:
            Dict: Kockázati információk (level, color, warning, actions)
        """
        if wind_speed is None:
            return {
                "level": "unknown",
                "color": "#9ca3af",
                "warning": "Nincs adat",
                "actions": []
            }
        
        try:
            category = WindGustsAnalyzer.categorize_wind_gust(wind_speed, data_source)
            
            risk_levels = {
                'moderate': {
                    "level": "low",
                    "color": "#10b981",  # Zöld
                    "warning": "Alacsony kockázat",
                    "actions": ["Szabadtéri tevékenységek biztonságosak"]
                },
                'strong': {
                    "level": "medium", 
                    "color": "#f59e0b",  # Sárga
                    "warning": "Közepes kockázat",
                    "actions": [
                        "Óvatosság szabadban",
                        "Vezetésnél figyeljen a széllökésekre"
                    ]
                },
                'extreme': {
                    "level": "high",
                    "color": "#dc2626",  # Piros
                    "warning": "Magas kockázat",
                    "actions": [
                        "Kerülje a szabadtéri tevékenységeket",
                        "Biztosítsa a laza tárgyakat", 
                        "Vezetést kerülje"
                    ]
                },
                'hurricane': {
                    "level": "critical",
                    "color": "#7c2d12",  # Sötét piros
                    "warning": "KRITIKUS KOCKÁZAT",
                    "actions": [
                        "MARADJON BENT!",
                        "Kerülje az ablakokat",
                        "Készüljön áramkimaradásra",
                        "Kövesse a hivatalos figyelmeztetéseket"
                    ]
                }
            }
            
            return risk_levels.get(category, risk_levels['moderate'])
        
        except Exception as e:
            logger.error(f"Wind risk level calculation hiba: {e}")
            return {
                "level": "unknown",
                "color": "#9ca3af", 
                "warning": "Hiba a számítás során",
                "actions": []
            }
    
    @staticmethod
    def analyze_wind_series(wind_data: List[float], data_source: str = 'wind_gusts_max') -> Dict[str, Any]:
        """
        Széllökés idősor elemzése.
        
        Args:
            wind_data: Széllökés értékek listája
            data_source: Adatforrás típusa
            
        Returns:
            Dict: Részletes elemzési eredmények
        """
        if not wind_data:
            return {"error": "Nincs szél adat"}
        
        try:
            # Tiszta adatok (None és negatív értékek eltávolítása)
            clean_data = [x for x in wind_data if x is not None and x >= 0]
            
            if not clean_data:
                return {"error": "Nincs érvényes szél adat"}
            
            # Alapstatisztikák
            import statistics
            
            analysis = {
                "data_source": data_source,
                "total_days": len(wind_data),
                "valid_days": len(clean_data),
                "missing_days": len(wind_data) - len(clean_data),
                
                # Statisztikák
                "min_speed": min(clean_data),
                "max_speed": max(clean_data),
                "avg_speed": statistics.mean(clean_data),
                "median_speed": statistics.median(clean_data),
                "std_dev": statistics.stdev(clean_data) if len(clean_data) > 1 else 0,
                
                # Kategória elemzés
                "categories": {},
                "windy_days": 0,
                "risk_days": 0
            }
            
            # Kategóriánkénti eloszlás
            for category in ['moderate', 'strong', 'extreme', 'hurricane']:
                count = len([
                    speed for speed in clean_data 
                    if WindGustsAnalyzer.categorize_wind_gust(speed, data_source) == category
                ])
                analysis["categories"][category] = count
            
            # Szeles napok száma
            threshold = WindGustsAnalyzer.get_windy_days_threshold(data_source)
            analysis["windy_days"] = len([x for x in clean_data if x > threshold])
            
            # Magas kockázatú napok (strong+)
            analysis["risk_days"] = len([
                speed for speed in clean_data 
                if WindGustsAnalyzer.categorize_wind_gust(speed, data_source) in ['strong', 'extreme', 'hurricane']
            ])
            
            # Maximum széllökés részletes adatai
            max_speed = max(clean_data)
            max_category = WindGustsAnalyzer.categorize_wind_gust(max_speed, data_source)
            max_risk = WindGustsAnalyzer.get_wind_risk_level(max_speed, data_source)
            
            analysis["max_wind_details"] = {
                "speed": max_speed,
                "category": max_category,
                "risk_level": max_risk["level"],
                "description": WindGustsAnalyzer.generate_wind_description(max_speed, max_category, data_source)
            }
            
            logger.debug(f"Wind series analysis completed: {len(clean_data)} days analyzed")
            return analysis
            
        except Exception as e:
            logger.error(f"Wind series analysis hiba: {e}")
            return {"error": f"Elemzési hiba: {str(e)}"}


# === MODUL EXPORT INFORMÁCIÓK ===

__all__ = [
    "WindGustsConstants",
    "DataFrameExtractor", 
    "WindGustsAnalyzer"
]

logger.info("✅ Results panel utils loaded: WindGustsConstants, DataFrameExtractor, WindGustsAnalyzer")
