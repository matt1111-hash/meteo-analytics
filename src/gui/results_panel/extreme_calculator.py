#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Extreme Weather Calculator
📊 MINI REFAKTORING: Rekordok számítása kiemelése ExtremeEventsTab-ból
🎯 SINGLE RESPONSIBILITY: Csak extrém értékek számítása és rekordok keresése
🛠️ FACADE PATTERN: ExtremeEventsTab delegál ide

🚀 PROFESSZIONÁLIS KÓDOLÁSI ELVEK:
✅ SOLID: Single Responsibility Principle
✅ DRY: WindGustsAnalyzer utility használata
✅ Type hints: Explicit típusok
✅ Pure functions: Testelhető, side-effect mentes
✅ Error handling: Robusztus kivételkezelés
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

from .utils import WindGustsConstants, WindGustsAnalyzer

# Logging konfigurálása
logger = logging.getLogger(__name__)


@dataclass
class ExtremeRecord:
    """
    🏆 Extrém időjárási rekord adatstruktúra
    """
    category: str      # 'temperature', 'precipitation', 'wind'
    record_type: str   # 'Legmelegebb nap', 'Legnagyobb széllökés', stb.
    value: str         # Formázott érték (pl. "35.2°C", "91.4km/h")
    date: str          # Dátum string
    raw_value: Optional[float] = None  # Nyers érték számításokhoz


@dataclass
class RecordsTextSummary:
    """
    📋 Rekordok szöveges összefoglalója
    """
    temperature_text: str
    precipitation_text: str
    wind_text: str
    
    def get_full_text(self) -> str:
        """Teljes szöveges összefoglaló generálása."""
        return f"""📊 IDŐJÁRÁSI REKORDOK ÉS SZÉLSŐÉRTÉKEK
{"=" * 50}

{self.temperature_text}
{self.precipitation_text}
{self.wind_text}"""


class ExtremeCalculator:
    """
    📊 EXTRÉM IDŐJÁRÁSI ÉRTÉKEK SZÁMÍTÓJA
    
    🎯 FELELŐSSÉG: Csak rekordok számítása és szélsőértékek keresése
    ✅ SOLID: Single Responsibility Principle
    ✅ Testelhető: Pure functions, determinisztikus eredmények
    ✅ Reusable: Különböző időszakokra használható
    """
    
    def __init__(self):
        """Extrém értékek számítójának inicializálása."""
        logger.info("ExtremeCalculator inicializálva")
    
    def calculate_records_by_period(
        self, 
        daily_data: Dict[str, List], 
        dates: List[str], 
        period_type: str = "daily"
    ) -> List[ExtremeRecord]:
        """
        🏆 Rekordok számítása időszak típus szerint.
        
        Args:
            daily_data: OpenMeteo API daily adatok Dict[List] formátumban
            dates: Dátumok listája
            period_type: "daily", "monthly", vagy "yearly"
            
        Returns:
            List[ExtremeRecord]: Rekordok listája
        """
        try:
            logger.info(f"Rekordok számítása - Időszak: {period_type}, Napok: {len(dates)}")
            
            if period_type == "daily":
                return self._calculate_daily_records(daily_data, dates)
            elif period_type == "monthly":
                return self._calculate_monthly_records(daily_data, dates)
            elif period_type == "yearly":
                return self._calculate_yearly_records(daily_data, dates)
            else:
                logger.warning(f"Ismeretlen period_type: {period_type}, fallback daily-re")
                return self._calculate_daily_records(daily_data, dates)
                
        except Exception as e:
            logger.error(f"Rekordok számítási hiba: {e}")
            return []
    
    def generate_text_summary(
        self, 
        daily_data: Dict[str, List], 
        dates: List[str]
    ) -> RecordsTextSummary:
        """
        📋 Szöveges rekord összefoglaló generálása.
        
        Args:
            daily_data: Daily adatok Dict[List] formátumban
            dates: Dátumok listája
            
        Returns:
            RecordsTextSummary: Strukturált szöveges összefoglaló
        """
        try:
            temp_text = self._generate_temperature_text(daily_data, dates)
            precip_text = self._generate_precipitation_text(daily_data, dates)
            wind_text = self._generate_wind_text(daily_data, dates)
            
            return RecordsTextSummary(
                temperature_text=temp_text,
                precipitation_text=precip_text,
                wind_text=wind_text
            )
            
        except Exception as e:
            logger.error(f"Szöveges összefoglaló hiba: {e}")
            return RecordsTextSummary(
                temperature_text="🌡️ HŐMÉRSÉKLET REKORDOK: Hiba a számítás során\n",
                precipitation_text="🌧️ CSAPADÉK REKORDOK: Hiba a számítás során\n",
                wind_text="🌪️ SZÉLLÖKÉS REKORDOK: Hiba a számítás során\n"
            )
    
    def _calculate_daily_records(self, daily_data: Dict[str, List], dates: List[str]) -> List[ExtremeRecord]:
        """
        📊 Napi rekordok számítása.
        
        Args:
            daily_data: Daily adatok
            dates: Dátumok listája
            
        Returns:
            List[ExtremeRecord]: Napi rekordok
        """
        records = []
        
        try:
            # === HŐMÉRSÉKLET REKORDOK ===
            records.extend(self._calculate_temperature_records(daily_data, dates))
            
            # === CSAPADÉK REKORDOK ===
            records.extend(self._calculate_precipitation_records(daily_data, dates))
            
            # === SZÉLLÖKÉS REKORDOK ===
            records.extend(self._calculate_wind_records(daily_data, dates))
            
            logger.info(f"Napi rekordok számítva: {len(records)} rekord")
            return records
            
        except Exception as e:
            logger.error(f"Napi rekordok számítási hiba: {e}")
            return []
    
    def _calculate_monthly_records(self, daily_data: Dict[str, List], dates: List[str]) -> List[ExtremeRecord]:
        """
        📅 Havi rekordok számítása pandas aggregációval.
        
        Args:
            daily_data: Daily adatok
            dates: Dátumok listája
            
        Returns:
            List[ExtremeRecord]: Havi rekordok
        """
        try:
            import pandas as pd
            
            # DataFrame létrehozása
            df_data = {'date': dates}
            for key, values in daily_data.items():
                if key != 'time' and values:
                    df_data[key] = values[:len(dates)]
            
            df = pd.DataFrame(df_data)
            df['date'] = pd.to_datetime(df['date'])
            df['year_month'] = df['date'].dt.to_period('M')
            
            records = []
            
            # Hőmérséklet aggregációk
            if 'temperature_2m_max' in df.columns:
                monthly_temp_max = df.groupby('year_month')['temperature_2m_max'].max()
                if not monthly_temp_max.empty:
                    hottest_month = monthly_temp_max.idxmax()
                    hottest_temp = monthly_temp_max.max()
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🔥 Legmelegebb hónap",
                        value=f"{hottest_temp:.1f}°C",
                        date=str(hottest_month),
                        raw_value=hottest_temp
                    ))
            
            if 'temperature_2m_min' in df.columns:
                monthly_temp_min = df.groupby('year_month')['temperature_2m_min'].min()
                if not monthly_temp_min.empty:
                    coldest_month = monthly_temp_min.idxmin()
                    coldest_temp = monthly_temp_min.min()
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🧊 Leghidegebb hónap",
                        value=f"{coldest_temp:.1f}°C",
                        date=str(coldest_month),
                        raw_value=coldest_temp
                    ))
            
            # Csapadék aggregációk
            if 'precipitation_sum' in df.columns:
                monthly_precip = df.groupby('year_month')['precipitation_sum'].sum()
                if not monthly_precip.empty:
                    wettest_month = monthly_precip.idxmax()
                    wettest_precip = monthly_precip.max()
                    records.append(ExtremeRecord(
                        category="🌧️ Csapadék",
                        record_type="💧 Legcsapadékosabb hónap",
                        value=f"{wettest_precip:.1f}mm",
                        date=str(wettest_month),
                        raw_value=wettest_precip
                    ))
                    
                    driest_month = monthly_precip.idxmin()
                    driest_precip = monthly_precip.min()
                    records.append(ExtremeRecord(
                        category="🌧️ Csapadék",
                        record_type="🏜️ Legszárazabb hónap",
                        value=f"{driest_precip:.1f}mm",
                        date=str(driest_month),
                        raw_value=driest_precip
                    ))
            
            # Széllökés aggregációk
            wind_col = self._get_wind_column(df.columns)
            if wind_col:
                monthly_wind = df.groupby('year_month')[wind_col].max()
                if not monthly_wind.empty:
                    windiest_month = monthly_wind.idxmax()
                    windiest_speed = monthly_wind.max()
                    
                    if wind_col == 'wind_gusts_max':
                        category = WindGustsAnalyzer.categorize_wind_gust(windiest_speed, wind_col)
                        category_info = WindGustsConstants.CATEGORIES.get(category, 'ISMERETLEN')
                        records.append(ExtremeRecord(
                            category="🌪️ Széllökés",
                            record_type=f"🚨 Legszelesebb hónap ({category_info})",
                            value=f"{windiest_speed:.1f}km/h",
                            date=str(windiest_month),
                            raw_value=windiest_speed
                        ))
                    else:
                        records.append(ExtremeRecord(
                            category="💨 Szél",
                            record_type="🌪️ Legszelesebb hónap",
                            value=f"{windiest_speed:.1f}km/h",
                            date=str(windiest_month),
                            raw_value=windiest_speed
                        ))
            
            logger.info(f"Havi rekordok számítva: {len(records)} rekord")
            return records
            
        except Exception as e:
            logger.error(f"Havi rekordok számítási hiba: {e}")
            # Fallback: napi számítás
            return self._calculate_daily_records(daily_data, dates)
    
    def _calculate_yearly_records(self, daily_data: Dict[str, List], dates: List[str]) -> List[ExtremeRecord]:
        """
        🗓️ Éves rekordok számítása hosszú időszakokra optimalizálva.
        
        Args:
            daily_data: Daily adatok
            dates: Dátumok listája
            
        Returns:
            List[ExtremeRecord]: Éves rekordok
        """
        try:
            import pandas as pd
            
            # DataFrame létrehozása
            df_data = {'date': dates}
            for key, values in daily_data.items():
                if key != 'time' and values:
                    df_data[key] = values[:len(dates)]
            
            df = pd.DataFrame(df_data)
            df['date'] = pd.to_datetime(df['date'])
            df['year'] = df['date'].dt.year
            
            records = []
            years = sorted(df['year'].unique())
            
            logger.info(f"Éves rekordok számítása: {len(years)} év ({years[0]}-{years[-1]})")
            
            # Hőmérséklet éves rekordok
            if 'temperature_2m_max' in df.columns:
                yearly_temp_max = df.groupby('year')['temperature_2m_max'].max()
                if not yearly_temp_max.empty:
                    hottest_year = yearly_temp_max.idxmax()
                    hottest_temp = yearly_temp_max.max()
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🔥 Legmelegebb év",
                        value=f"{hottest_temp:.1f}°C",
                        date=str(hottest_year),
                        raw_value=hottest_temp
                    ))
                    
                    # Átlag hőmérséklet trend
                    yearly_temp_avg = df.groupby('year')['temperature_2m_max'].mean()
                    warmest_avg_year = yearly_temp_avg.idxmax()
                    warmest_avg_temp = yearly_temp_avg.max()
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="📈 Legmelegebb átlag év",
                        value=f"{warmest_avg_temp:.1f}°C",
                        date=str(warmest_avg_year),
                        raw_value=warmest_avg_temp
                    ))
            
            if 'temperature_2m_min' in df.columns:
                yearly_temp_min = df.groupby('year')['temperature_2m_min'].min()
                if not yearly_temp_min.empty:
                    coldest_year = yearly_temp_min.idxmin()
                    coldest_temp = yearly_temp_min.min()
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🧊 Leghidegebb év",
                        value=f"{coldest_temp:.1f}°C",
                        date=str(coldest_year),
                        raw_value=coldest_temp
                    ))
            
            # Csapadék éves rekordok
            if 'precipitation_sum' in df.columns:
                yearly_precip = df.groupby('year')['precipitation_sum'].sum()
                if not yearly_precip.empty:
                    wettest_year = yearly_precip.idxmax()
                    wettest_precip = yearly_precip.max()
                    records.append(ExtremeRecord(
                        category="🌧️ Csapadék",
                        record_type="💧 Legcsapadékosabb év",
                        value=f"{wettest_precip:.0f}mm",
                        date=str(wettest_year),
                        raw_value=wettest_precip
                    ))
                    
                    driest_year = yearly_precip.idxmin()
                    driest_precip = yearly_precip.min()
                    records.append(ExtremeRecord(
                        category="🌧️ Csapadék",
                        record_type="🏜️ Legszárazabb év",
                        value=f"{driest_precip:.0f}mm",
                        date=str(driest_year),
                        raw_value=driest_precip
                    ))
            
            # Széllökés éves rekordok
            wind_col = self._get_wind_column(df.columns)
            if wind_col:
                yearly_wind_max = df.groupby('year')[wind_col].max()
                if not yearly_wind_max.empty:
                    windiest_year = yearly_wind_max.idxmax()
                    windiest_speed = yearly_wind_max.max()
                    
                    if wind_col == 'wind_gusts_max':
                        category = WindGustsAnalyzer.categorize_wind_gust(windiest_speed, wind_col)
                        category_info = WindGustsConstants.CATEGORIES.get(category, 'ISMERETLEN')
                        records.append(ExtremeRecord(
                            category="🌪️ Széllökés",
                            record_type=f"🚨 Legszelesebb év ({category_info})",
                            value=f"{windiest_speed:.1f}km/h",
                            date=str(windiest_year),
                            raw_value=windiest_speed
                        ))
                    else:
                        records.append(ExtremeRecord(
                            category="💨 Szél",
                            record_type="🌪️ Legszelesebb év",
                            value=f"{windiest_speed:.1f}km/h",
                            date=str(windiest_year),
                            raw_value=windiest_speed
                        ))
            
            # Klímaváltozási trendek (10+ év esetén)
            if len(years) >= 10:
                records.extend(self._calculate_climate_trends(df, years))
            
            logger.info(f"Éves rekordok számítva: {len(records)} rekord {len(years)} évhez")
            return records
            
        except Exception as e:
            logger.error(f"Éves rekordok számítási hiba: {e}")
            # Fallback: havi számítás
            return self._calculate_monthly_records(daily_data, dates)
    
    def _calculate_temperature_records(self, daily_data: Dict[str, List], dates: List[str]) -> List[ExtremeRecord]:
        """Hőmérséklet rekordok számítása."""
        records = []
        
        try:
            temp_max_list = daily_data.get('temperature_2m_max', [])
            temp_min_list = daily_data.get('temperature_2m_min', [])
            
            if temp_max_list and len(temp_max_list) == len(dates):
                clean_max = [(i, t) for i, t in enumerate(temp_max_list) if t is not None]
                if clean_max:
                    max_idx, max_temp = max(clean_max, key=lambda x: x[1])
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🔥 Legmelegebb nap",
                        value=f"{max_temp:.1f}°C",
                        date=dates[max_idx],
                        raw_value=max_temp
                    ))
            
            if temp_min_list and len(temp_min_list) == len(dates):
                clean_min = [(i, t) for i, t in enumerate(temp_min_list) if t is not None]
                if clean_min:
                    min_idx, min_temp = min(clean_min, key=lambda x: x[1])
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="🧊 Leghidegebb nap",
                        value=f"{min_temp:.1f}°C",
                        date=dates[min_idx],
                        raw_value=min_temp
                    ))
            
            # Legnagyobb napi hőingás
            if temp_max_list and temp_min_list:
                daily_ranges = []
                for i in range(min(len(temp_max_list), len(temp_min_list))):
                    if temp_max_list[i] is not None and temp_min_list[i] is not None:
                        daily_range = temp_max_list[i] - temp_min_list[i]
                        daily_ranges.append((i, daily_range))
                
                if daily_ranges:
                    max_range_idx, max_range = max(daily_ranges, key=lambda x: x[1])
                    records.append(ExtremeRecord(
                        category="🌡️ Hőmérséklet",
                        record_type="📊 Legnagyobb napi hőingás",
                        value=f"{max_range:.1f}°C",
                        date=dates[max_range_idx],
                        raw_value=max_range
                    ))
            
        except Exception as e:
            logger.error(f"Hőmérséklet rekordok hiba: {e}")
        
        return records
    
    def _calculate_precipitation_records(self, daily_data: Dict[str, List], dates: List[str]) -> List[ExtremeRecord]:
        """Csapadék rekordok számítása."""
        records = []
        
        try:
            precip_list = daily_data.get('precipitation_sum', [])
            if precip_list and len(precip_list) == len(dates):
                clean_precip = [(i, p) for i, p in enumerate(precip_list) if p is not None]
                if clean_precip:
                    max_precip_idx, max_precip = max(clean_precip, key=lambda x: x[1])
                    records.append(ExtremeRecord(
                        category="🌧️ Csapadék",
                        record_type="💧 Legcsapadékosabb nap",
                        value=f"{max_precip:.1f}mm",
                        date=dates[max_precip_idx],
                        raw_value=max_precip
                    ))
        
        except Exception as e:
            logger.error(f"Csapadék rekordok hiba: {e}")
        
        return records
    
    def _calculate_wind_records(self, daily_data: Dict[str, List], dates: List[str]) -> List[ExtremeRecord]:
        """Széllökés rekordok számítása."""
        records = []
        
        try:
            wind_data, wind_source = self._get_wind_data(daily_data)
            
            if wind_data and len(wind_data) == len(dates):
                clean_wind = [(i, w) for i, w in enumerate(wind_data) if w is not None]
                if clean_wind:
                    max_wind_idx, max_wind = max(clean_wind, key=lambda x: x[1])
                    
                    if wind_source == 'wind_gusts_max':
                        category = WindGustsAnalyzer.categorize_wind_gust(max_wind, wind_source)
                        category_info = WindGustsConstants.CATEGORIES.get(category, 'ISMERETLEN')
                        records.append(ExtremeRecord(
                            category="🌪️ Széllökés",
                            record_type=f"🚨 Legerősebb ({category_info})",
                            value=f"{max_wind:.1f}km/h",
                            date=dates[max_wind_idx],
                            raw_value=max_wind
                        ))
                    else:
                        records.append(ExtremeRecord(
                            category="💨 Szél",
                            record_type="🌪️ Legszelesebb nap",
                            value=f"{max_wind:.1f}km/h",
                            date=dates[max_wind_idx],
                            raw_value=max_wind
                        ))
        
        except Exception as e:
            logger.error(f"Széllökés rekordok hiba: {e}")
        
        return records
    
    def _get_wind_data(self, daily_data: Dict[str, List]) -> Tuple[Optional[List], str]:
        """Széladatok prioritás alapú kiválasztása."""
        wind_gusts_max = daily_data.get('wind_gusts_max', [])
        windspeed_10m_max = daily_data.get('windspeed_10m_max', [])
        windspeed = daily_data.get('windspeed', [])
        
        if wind_gusts_max:
            return wind_gusts_max, "wind_gusts_max"
        elif windspeed_10m_max:
            return windspeed_10m_max, "windspeed_10m_max"
        elif windspeed:
            return windspeed, "windspeed"
        else:
            return None, "no_data"
    
    def _get_wind_column(self, columns) -> Optional[str]:
        """Széllökés oszlop kiválasztása DataFrame-hez."""
        if 'wind_gusts_max' in columns:
            return 'wind_gusts_max'
        elif 'windspeed_10m_max' in columns:
            return 'windspeed_10m_max'
        elif 'windspeed' in columns:
            return 'windspeed'
        return None
    
    def _calculate_climate_trends(self, df, years: List[int]) -> List[ExtremeRecord]:
        """Klímaváltozási trendek számítása 10+ évre."""
        records = []
        
        try:
            # Egyszerű trend számítás (első 5 év vs utolsó 5 év)
            early_years = years[:5]
            late_years = years[-5:]
            
            if 'temperature_2m_mean' in df.columns or ('temperature_2m_max' in df.columns and 'temperature_2m_min' in df.columns):
                if 'temperature_2m_mean' in df.columns:
                    temp_col = 'temperature_2m_mean'
                else:
                    df['temp_calculated_mean'] = (df['temperature_2m_max'] + df['temperature_2m_min']) / 2
                    temp_col = 'temp_calculated_mean'
                
                early_avg = df[df['year'].isin(early_years)][temp_col].mean()
                late_avg = df[df['year'].isin(late_years)][temp_col].mean()
                temp_trend = late_avg - early_avg
                
                if temp_trend > 0.5:
                    records.append(ExtremeRecord(
                        category="🌡️ Trend",
                        record_type="🔥 Felmelegedés trend",
                        value=f"+{temp_trend:.1f}°C",
                        date=f"{years[0]}-{years[-1]}",
                        raw_value=temp_trend
                    ))
                elif temp_trend < -0.5:
                    records.append(ExtremeRecord(
                        category="🌡️ Trend",
                        record_type="🧊 Lehűlés trend",
                        value=f"{temp_trend:.1f}°C",
                        date=f"{years[0]}-{years[-1]}",
                        raw_value=temp_trend
                    ))
                else:
                    records.append(ExtremeRecord(
                        category="🌡️ Trend",
                        record_type="📊 Stabil hőmérséklet",
                        value=f"{temp_trend:+.1f}°C",
                        date=f"{years[0]}-{years[-1]}",
                        raw_value=temp_trend
                    ))
        
        except Exception as e:
            logger.error(f"Klíma trend számítási hiba: {e}")
        
        return records
    
    def _generate_temperature_text(self, daily_data: Dict[str, List], dates: List[str]) -> str:
        """Hőmérséklet szöveges összefoglaló."""
        try:
            temp_max_list = daily_data.get('temperature_2m_max', [])
            temp_min_list = daily_data.get('temperature_2m_min', [])
            
            if temp_max_list and temp_min_list and len(temp_max_list) == len(dates) and len(temp_min_list) == len(dates):
                clean_max = [(i, t) for i, t in enumerate(temp_max_list) if t is not None]
                clean_min = [(i, t) for i, t in enumerate(temp_min_list) if t is not None]
                
                if clean_max and clean_min:
                    max_temp_idx, max_temp = max(clean_max, key=lambda x: x[1])
                    min_temp_idx, min_temp = min(clean_min, key=lambda x: x[1])
                    
                    return f"""🌡️ HŐMÉRSÉKLET REKORDOK:
   🔥 Legmelegebb nap: {max_temp:.1f}°C ({dates[max_temp_idx]})
   🧊 Leghidegebb nap: {min_temp:.1f}°C ({dates[min_temp_idx]})
   📈 Hőingás: {max_temp - min_temp:.1f}°C

"""
            return "🌡️ HŐMÉRSÉKLET REKORDOK: Nincs megfelelő adat\n\n"
        except Exception as e:
            logger.error(f"Hőmérséklet szöveg hiba: {e}")
            return "🌡️ HŐMÉRSÉKLET REKORDOK: Hiba a számítás során\n\n"
    
    def _generate_precipitation_text(self, daily_data: Dict[str, List], dates: List[str]) -> str:
        """Csapadék szöveges összefoglaló."""
        try:
            precip_list = daily_data.get('precipitation_sum', [])
            
            if precip_list and len(precip_list) == len(dates):
                clean_precip = [(i, p) for i, p in enumerate(precip_list) if p is not None]
                
                if clean_precip:
                    max_precip_idx, max_precip = max(clean_precip, key=lambda x: x[1])
                    dry_days = len([p for p in precip_list if p is not None and p <= 0.1])
                    total_precip = sum([p for p in precip_list if p is not None])
                    
                    return f"""🌧️ CSAPADÉK REKORDOK:
   💧 Legtöbb csapadék: {max_precip:.1f}mm ({dates[max_precip_idx]})
   🏜️ Száraz napok: {dry_days} nap
   📊 Összes csapadék: {total_precip:.1f}mm

"""
            return "🌧️ CSAPADÉK REKORDOK: Nincs csapadék adat\n\n"
        except Exception as e:
            logger.error(f"Csapadék szöveg hiba: {e}")
            return "🌧️ CSAPADÉK REKORDOK: Hiba a számítás során\n\n"
    
    def _generate_wind_text(self, daily_data: Dict[str, List], dates: List[str]) -> str:
        """Széllökés szöveges összefoglaló."""
        try:
            wind_data, wind_source = self._get_wind_data(daily_data)
            
            if wind_data and len(wind_data) == len(dates):
                clean_wind = [(i, w) for i, w in enumerate(wind_data) if w is not None]
                
                if clean_wind:
                    max_wind_idx, max_wind_value = max(clean_wind, key=lambda x: x[1])
                    avg_wind = sum([w for w in wind_data if w is not None]) / len([w for w in wind_data if w is not None])
                    
                    if wind_source == 'wind_gusts_max':
                        category = WindGustsAnalyzer.categorize_wind_gust(max_wind_value, wind_source)
                        
                        text = f"""🌪️ SZÉLLÖKÉS REKORDOK:
   🚨 Legerősebb széllökés: {max_wind_value:.1f}km/h ({dates[max_wind_idx]})
"""
                        
                        if category == 'hurricane':
                            text += f"   ⚠️ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]} (>{WindGustsConstants.HURRICANE_THRESHOLD:.0f} km/h)\n"
                        elif category == 'extreme':
                            text += f"   ⚠️ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]} (>{WindGustsConstants.EXTREME_THRESHOLD:.0f} km/h)\n"
                        elif category == 'strong':
                            text += f"   ⚠️ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]} (>{WindGustsConstants.STRONG_THRESHOLD:.0f} km/h)\n"
                        else:
                            text += f"   ✅ KATEGÓRIA: {WindGustsConstants.CATEGORIES[category]}\n"
                    else:
                        text = f"""💨 SZÉL REKORDOK:
   🌪️ Legerősebb szél: {max_wind_value:.1f}km/h ({dates[max_wind_idx]})
"""
                    
                    text += f"   📊 Átlagos szélsebesség: {avg_wind:.1f}km/h\n"
                    text += f"   📈 Adatforrás: {wind_source}\n\n"
                    
                    return text
            
            return "🌪️ SZÉLLÖKÉS REKORDOK: Nincs szél adat\n\n"
        except Exception as e:
            logger.error(f"Széllökés szöveg hiba: {e}")
            return "🌪️ SZÉLLÖKÉS REKORDOK: Hiba a számítás során\n\n"
