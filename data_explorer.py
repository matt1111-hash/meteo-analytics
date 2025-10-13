#!/usr/bin/env python3
"""
Adatbázis Elemző Script - Health Monitoring Project
Cél: Apple Health XML és Sleep Cycle CSV struktúrájának feltárása
"""

import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import json
import sys
from typing import Dict, List, Any


class HealthDataExplorer:
    """Egészségügyi adatbázisok struktúrájának elemzése"""
    
    def __init__(self):
        self.results = {
            'apple_health': {},
            'sleep_cycle': {},
            'summary': {}
        }
    
    def analyze_sleep_cycle_csv(self, csv_path: str) -> Dict[str, Any]:
        """Sleep Cycle CSV részletes elemzése"""
        print(f"\n{'='*60}")
        print("SLEEP CYCLE CSV ELEMZÉS")
        print(f"{'='*60}")
        
        try:
            # CSV beolvasás
            df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
            
            # Alapadatok
            basic_info = {
                'total_records': len(df),
                'columns_count': len(df.columns),
                'columns': list(df.columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            }
            
            print(f"📊 Rekordok száma: {basic_info['total_records']}")
            print(f"📊 Oszlopok száma: {basic_info['columns_count']}")
            print(f"💾 Memóriahasználat: {basic_info['memory_usage_mb']:.2f} MB")
            
            # Dátumtartomány elemzés
            date_info = self._analyze_sleep_dates(df)
            
            # Oszlopok minőségi elemzése
            columns_quality = self._analyze_sleep_columns(df)
            
            # Numerikus mezők statisztikái
            numeric_stats = self._analyze_sleep_numeric_fields(df)
            
            # Összesítés
            sleep_analysis = {
                'basic_info': basic_info,
                'date_range': date_info,
                'columns_quality': columns_quality,
                'numeric_statistics': numeric_stats
            }
            
            self.results['sleep_cycle'] = sleep_analysis
            return sleep_analysis
            
        except Exception as e:
            print(f"❌ HIBA a Sleep Cycle elemzésben: {e}")
            return {}
    
    def _analyze_sleep_dates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Dátumtartomány és időbélyegek elemzése"""
        print(f"\n📅 DÁTUM ELEMZÉS")
        print("-" * 30)
        
        try:
            # End oszlop feldolgozása (ébredés ideje)
            df['end_clean'] = df['End'].astype(str).str.strip()
            valid_dates = pd.to_datetime(df['end_clean'], errors='coerce')
            valid_dates = valid_dates.dropna()
            
            if len(valid_dates) > 0:
                first_date = valid_dates.min()
                last_date = valid_dates.max()
                days_span = (last_date - first_date).days
                
                date_info = {
                    'first_date': first_date.strftime('%Y-%m-%d'),
                    'last_date': last_date.strftime('%Y-%m-%d'),
                    'days_span': days_span,
                    'valid_dates_count': len(valid_dates),
                    'invalid_dates_count': len(df) - len(valid_dates)
                }
                
                print(f"   Első mérés: {date_info['first_date']}")
                print(f"   Utolsó mérés: {date_info['last_date']}")
                print(f"   Időtartam: {days_span} nap")
                print(f"   Érvényes dátumok: {len(valid_dates)}/{len(df)}")
                
                return date_info
            else:
                print("   ❌ Nincsenek érvényes dátumok")
                return {}
                
        except Exception as e:
            print(f"   ❌ Dátum elemzési hiba: {e}")
            return {}
    
    def _analyze_sleep_columns(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Oszlopok kitöltöttségének és minőségének elemzése"""
        print(f"\n📋 OSZLOPOK MINŐSÉGE")
        print("-" * 30)
        
        columns_analysis = {}
        
        for col in df.columns:
            # Alapstatisztikák
            total_count = len(df)
            non_null_count = df[col].notna().sum()
            non_empty_count = 0
            non_zero_count = 0
            
            # Nem üres értékek száma
            if df[col].dtype == 'object':
                non_empty_count = (df[col].astype(str).str.strip() != '').sum()
            else:
                non_empty_count = non_null_count
            
            # Nem nulla értékek száma (numerikus mezőknél)
            try:
                numeric_series = pd.to_numeric(df[col].astype(str).str.replace('%', ''), errors='coerce')
                non_zero_count = (numeric_series > 0).sum()
            except:
                non_zero_count = non_empty_count
            
            # Egyedi értékek
            unique_count = df[col].nunique()
            
            # Mintaértékek
            sample_values = df[col].dropna().astype(str).str.strip()
            sample_values = sample_values[sample_values != ''].head(3).tolist()
            
            columns_analysis[col] = {
                'fill_rate': non_empty_count / total_count * 100,
                'non_zero_rate': non_zero_count / total_count * 100,
                'unique_values': unique_count,
                'sample_values': sample_values
            }
            
            # Kiírás
            fill_rate = columns_analysis[col]['fill_rate']
            status = "✅" if fill_rate >= 90 else "⚠️" if fill_rate >= 50 else "❌"
            print(f"   {status} {col}: {fill_rate:.1f}% kitöltött")
            if sample_values:
                print(f"      Példák: {', '.join(sample_values[:2])}")
        
        return columns_analysis
    
    def _analyze_sleep_numeric_fields(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Numerikus mezők statisztikai elemzése"""
        print(f"\n📈 NUMERIKUS STATISZTIKÁK")
        print("-" * 30)
        
        numeric_fields = [
            'Sleep Quality', 'Light (seconds)', 'Air Pressure (Pa)', 
            'Ambient Noise (dB)', 'Time asleep (seconds)', 'Movements per hour'
        ]
        
        stats_results = {}
        
        for field in numeric_fields:
            if field in df.columns:
                try:
                    # Numerikus konverzió
                    series = df[field].astype(str).str.replace('%', '').str.strip()
                    numeric_series = pd.to_numeric(series, errors='coerce')
                    valid_values = numeric_series[numeric_series > 0]
                    
                    if len(valid_values) > 0:
                        stats = {
                            'count': len(valid_values),
                            'min': float(valid_values.min()),
                            'max': float(valid_values.max()),
                            'mean': float(valid_values.mean()),
                            'median': float(valid_values.median()),
                            'std': float(valid_values.std()) if len(valid_values) > 1 else 0
                        }
                        
                        stats_results[field] = stats
                        
                        print(f"   {field}:")
                        print(f"      Érvényes értékek: {stats['count']}")
                        print(f"      Min-Max: {stats['min']:.1f} - {stats['max']:.1f}")
                        print(f"      Átlag: {stats['mean']:.1f}")
                        
                        # Speciális konverziók
                        if 'seconds' in field:
                            hours = stats['mean'] / 3600
                            print(f"      Átlag órában: {hours:.1f} óra")
                
                except Exception as e:
                    print(f"   ❌ {field}: Nem elemezhető ({e})")
        
        return stats_results
    
    def analyze_apple_health_xml(self, xml_path: str) -> Dict[str, Any]:
        """Apple Health XML részletes elemzése"""
        print(f"\n{'='*60}")
        print("APPLE HEALTH XML ELEMZÉS")
        print(f"{'='*60}")
        
        try:
            # Fájl méret
            file_size_mb = Path(xml_path).stat().st_size / 1024 / 1024
            print(f"📁 Fájlméret: {file_size_mb:.1f} MB")
            
            # XML struktúra elemzése
            structure_info = self._analyze_xml_structure(xml_path)
            
            # Adattípusok elemzése
            datatypes_info = self._analyze_xml_datatypes(xml_path)
            
            # Dátumtartomány elemzése
            date_range_info = self._analyze_xml_dates(xml_path)
            
            apple_analysis = {
                'file_size_mb': file_size_mb,
                'structure': structure_info,
                'datatypes': datatypes_info,
                'date_range': date_range_info
            }
            
            self.results['apple_health'] = apple_analysis
            return apple_analysis
            
        except Exception as e:
            print(f"❌ HIBA az Apple Health elemzésben: {e}")
            return {}
    
    def _analyze_xml_structure(self, xml_path: str) -> Dict[str, Any]:
        """XML alapstruktúra elemzése"""
        print(f"\n🔍 XML STRUKTÚRA")
        print("-" * 30)
        
        try:
            # Nagy XML fájl esetén iteratív parsing
            observation_count = 0
            unique_tags = set()
            sample_observations = []
            
            for event, elem in ET.iterparse(xml_path, events=('start', 'end')):
                if event == 'start':
                    unique_tags.add(elem.tag)
                
                if event == 'end' and elem.tag == 'observation':
                    observation_count += 1
                    
                    # Első néhány observation mintája
                    if len(sample_observations) < 3:
                        code_elem = elem.find('.//code')
                        value_elem = elem.find('.//value[@xsi:type="PQ"]', 
                                             namespaces={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
                        time_elem = elem.find('.//effectiveTime/low')
                        
                        sample = {
                            'code': code_elem.get('displayName') if code_elem is not None else 'N/A',
                            'value': value_elem.get('value') if value_elem is not None else 'N/A',
                            'unit': value_elem.get('unit') if value_elem is not None else 'N/A',
                            'time': time_elem.get('value') if time_elem is not None else 'N/A'
                        }
                        sample_observations.append(sample)
                    
                    # Memória takarítás
                    elem.clear()
                    
                    # Mintavételezés nagy fájloknál
                    if observation_count >= 1000:  # Első 1000 observation
                        break
            
            structure_info = {
                'total_observations': observation_count,
                'unique_xml_tags': list(unique_tags),
                'sample_observations': sample_observations
            }
            
            print(f"   Observations száma: {observation_count}+")
            print(f"   XML tagek száma: {len(unique_tags)}")
            print(f"   Minta observations:")
            for i, sample in enumerate(sample_observations):
                print(f"      {i+1}. {sample['code']}: {sample['value']} {sample['unit']} ({sample['time']})")
            
            return structure_info
            
        except Exception as e:
            print(f"   ❌ XML struktúra elemzési hiba: {e}")
            return {}
    
    def _analyze_xml_datatypes(self, xml_path: str) -> Dict[str, Any]:
        """XML adattípusok elemzése"""
        print(f"\n📊 ADATTÍPUSOK ELEMZÉSE")
        print("-" * 30)
        
        try:
            datatypes = Counter()
            sources = Counter()
            units = Counter()
            
            for event, elem in ET.iterparse(xml_path, events=('end',)):
                if elem.tag == 'observation':
                    # Adattípus
                    code_elem = elem.find('.//code')
                    if code_elem is not None:
                        display_name = code_elem.get('displayName', 'Unknown')
                        datatypes[display_name] += 1
                    
                    # Forrás
                    source_elem = elem.find('.//sourceName')
                    if source_elem is not None and source_elem.text:
                        sources[source_elem.text] += 1
                    
                    # Mértékegység
                    value_elem = elem.find('.//value[@xsi:type="PQ"]', 
                                         namespaces={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
                    if value_elem is not None:
                        unit = value_elem.get('unit', 'N/A')
                        units[unit] += 1
                    
                    elem.clear()
                    
                    # Mintavételezés
                    if sum(datatypes.values()) >= 1000:
                        break
            
            datatypes_info = {
                'datatypes': dict(datatypes.most_common(10)),
                'sources': dict(sources.most_common(5)),
                'units': dict(units.most_common(10))
            }
            
            print("   Top adattípusok:")
            for dtype, count in list(datatypes.most_common(5)):
                print(f"      {dtype}: {count}")
            
            print("   Források:")
            for source, count in list(sources.most_common(3)):
                print(f"      {source}: {count}")
            
            return datatypes_info
            
        except Exception as e:
            print(f"   ❌ Adattípus elemzési hiba: {e}")
            return {}
    
    def _analyze_xml_dates(self, xml_path: str) -> Dict[str, Any]:
        """XML dátumtartomány elemzése"""
        print(f"\n📅 XML DÁTUMTARTOMÁNY")
        print("-" * 30)
        
        try:
            dates = []
            
            for event, elem in ET.iterparse(xml_path, events=('end',)):
                if elem.tag == 'observation':
                    time_elem = elem.find('.//effectiveTime/low')
                    if time_elem is not None:
                        time_str = time_elem.get('value')
                        if time_str:
                            try:
                                # Format: 20241211090108+0200
                                if len(time_str) >= 14:
                                    date_part = time_str[:8]  # YYYYMMDD
                                    dates.append(date_part)
                            except:
                                pass
                    
                    elem.clear()
                    
                    if len(dates) >= 100:  # Mintavételezés
                        break
            
            if dates:
                dates = sorted(set(dates))
                first_date = dates[0]
                last_date = dates[-1]
                
                # Formázás YYYY-MM-DD
                first_formatted = f"{first_date[:4]}-{first_date[4:6]}-{first_date[6:8]}"
                last_formatted = f"{last_date[:4]}-{last_date[4:6]}-{last_date[6:8]}"
                
                date_info = {
                    'first_date': first_formatted,
                    'last_date': last_formatted,
                    'unique_dates_sample': len(dates)
                }
                
                print(f"   Első mérés: {first_formatted}")
                print(f"   Utolsó mérés (minta): {last_formatted}")
                print(f"   Egyedi napok (minta): {len(dates)}")
                
                return date_info
            else:
                print("   ❌ Nem találhatók dátumok")
                return {}
                
        except Exception as e:
            print(f"   ❌ XML dátum elemzési hiba: {e}")
            return {}
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Összefoglaló jelentés generálása"""
        print(f"\n{'='*60}")
        print("ÖSSZEFOGLALÓ JELENTÉS")
        print(f"{'='*60}")
        
        summary = {
            'data_sources': {},
            'integration_opportunities': [],
            'data_quality_issues': [],
            'recommendations': []
        }
        
        # Adatforrások összesítése
        if self.results['sleep_cycle']:
            sc = self.results['sleep_cycle']
            summary['data_sources']['sleep_cycle'] = {
                'records': sc.get('basic_info', {}).get('total_records', 0),
                'date_range': f"{sc.get('date_range', {}).get('first_date', 'N/A')} - {sc.get('date_range', {}).get('last_date', 'N/A')}",
                'quality_score': self._calculate_sleep_quality_score(sc)
            }
        
        if self.results['apple_health']:
            ah = self.results['apple_health']
            summary['data_sources']['apple_health'] = {
                'size_mb': ah.get('file_size_mb', 0),
                'datatypes_count': len(ah.get('datatypes', {}).get('datatypes', {})),
                'date_range': f"{ah.get('date_range', {}).get('first_date', 'N/A')} - {ah.get('date_range', {}).get('last_date', 'N/A')}"
            }
        
        # Integráció lehetőségek
        summary['integration_opportunities'] = [
            "Sleep Quality (Sleep Cycle) ↔ Vérnyomás korreláció",
            "Air Pressure (Sleep Cycle) ↔ Weather API validáció",
            "Heart Rate (Apple Health) ↔ Vérnyomás időbélyeg matching",
            "Ambient Noise ↔ Időjárási szélsebesség összefüggés"
        ]
        
        # Adatminőségi problémák
        summary['data_quality_issues'] = [
            "Sleep Cycle: Deep sleep minden értéke 0.0",
            "Sleep Cycle: Heart rate minden értéke 0",
            "Sleep Cycle: Mood és Notes mezők üresek"
        ]
        
        # Javaslatok
        summary['recommendations'] = [
            "Sleep Cycle: Csak működő mezőket használni (Sleep Quality, Light sleep, Air Pressure, Ambient Noise)",
            "Apple Health: Heart Rate adatok kinyerése és aggregálása",
            "Időbélyeg szinkronizáció: ISO 8601 formátumra egységesítés",
            "Moduláris adatmodell: Típusonként külön DataFrame-ek"
        ]
        
        self.results['summary'] = summary
        
        # Kiírás
        print("\n📋 ADATFORRÁSOK:")
        for source, info in summary['data_sources'].items():
            print(f"   {source}: {info}")
        
        print("\n🔗 INTEGRÁCIÓ LEHETŐSÉGEK:")
        for opp in summary['integration_opportunities']:
            print(f"   • {opp}")
        
        print("\n⚠️ ADATMINŐSÉGI PROBLÉMÁK:")
        for issue in summary['data_quality_issues']:
            print(f"   • {issue}")
        
        print("\n💡 JAVASLATOK:")
        for rec in summary['recommendations']:
            print(f"   • {rec}")
        
        return summary
    
    def _calculate_sleep_quality_score(self, sleep_analysis: Dict) -> float:
        """Sleep Cycle adatminőségi pontszám (0-100)"""
        score = 0
        columns = sleep_analysis.get('columns_quality', {})
        
        # Kitöltöttség alapján pontozás
        for col, stats in columns.items():
            fill_rate = stats.get('fill_rate', 0)
            if fill_rate >= 90:
                score += 10
            elif fill_rate >= 50:
                score += 5
        
        return min(score, 100)
    
    def save_results(self, output_path: str = "data_analysis_results.json"):
        """Eredmények mentése JSON fájlba"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n💾 Eredmények mentve: {output_path}")
        except Exception as e:
            print(f"❌ Mentési hiba: {e}")


def main():
    """Főprogram"""
    print("🏥 HEALTH DATA EXPLORER")
    print("=" * 60)
    
    explorer = HealthDataExplorer()
    
    # Fájlútvonalak (módosítsd az aktuális útvonalakra)
    sleep_cycle_path = "sleepdata.csv"
    apple_health_path = "export_cda.xml"  # vagy "exportálás.xml"
    
    # Sleep Cycle elemzés
    if Path(sleep_cycle_path).exists():
        explorer.analyze_sleep_cycle_csv(sleep_cycle_path)
    else:
        print(f"⚠️ Sleep Cycle fájl nem található: {sleep_cycle_path}")
    
    # Apple Health elemzés
    if Path(apple_health_path).exists():
        explorer.analyze_apple_health_xml(apple_health_path)
    else:
        print(f"⚠️ Apple Health fájl nem található: {apple_health_path}")
    
    # Összefoglaló
    explorer.generate_summary_report()
    
    # Eredmények mentése
    explorer.save_results()
    
    print(f"\n✅ Elemzés befejezve!")


if __name__ == "__main__":
    main()
