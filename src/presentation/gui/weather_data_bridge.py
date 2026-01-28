#!/usr/bin/env python3
"""
Weather Data Bridge - Multi-City Engine → Folium Map Integration
Global Weather Analyzer projekt

🔧 KRITIKUS JAVÍTÁS v2.0 - METRIC_MAP IMPLEMENTÁCIÓ:
✅ METRIC_MAP dictionary hozzáadva minden AnalyticsMetric-hez
✅ convert_analytics_result paraméter bővítése display_parameter-rel
✅ Intelligens metrika felismerés a question.metric alapján
✅ Windspeed, precipitation, temperature helyes kezelése
✅ "Buta Tolmács" probléma MEGOLDVA

Fájl: src/gui/weather_data_bridge.py
Cél: Multi-City Engine eredmények átalakítása Folium térkép formátumra
- AnalyticsResult → Folium Weather Overlay Data
- Koordináták + értékek kinyerése
- 4 weather overlay típus támogatás
- Performance optimalizáció nagyobb adathalmazokhoz

🔧 KRITIKUS BREAKTHROUGH:
A multi_city_engine.py már tartalmaz MINDEN szükséges adatot:
- CityWeatherResult objektumok koordinátákkal
- Valós weather értékek (temperature, precipitation, wind)
- NONE-safe adatkezelés
- Teljes statisztikák

Ez a bridge összköti az Analytics Engine-t a Folium térképpel!
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
from dataclasses import dataclass

from src.data.models import AnalyticsResult, CityWeatherResult, AnalyticsQuestion
from src.data.enums import AnalyticsMetric

logger = logging.getLogger(__name__)


@dataclass
class WeatherOverlayData:
    """Weather overlay adat struktúra Folium térképhez"""
    overlay_type: str  # 'temperature', 'precipitation', 'wind_speed', 'wind_gusts'
    data: Dict[str, Dict[str, Any]]  # city_name -> {coordinates, value, additional_info}
    metadata: Dict[str, Any]  # min/max értékek, egységek, színskála info
    

class WeatherDataBridge:
    """
    🔧 JAVÍTOTT Weather Data Bridge - Analytics Engine → Folium Map Integration
    
    🚀 ÚJ FUNKCIÓK v2.0:
    - METRIC_MAP: Minden AnalyticsMetric → display_parameter mapping
    - Intelligens convert_analytics_result paraméter kezelés
    - Windspeed, precipitation, temperature helyes felismerés
    - "Buta Tolmács" probléma teljes kijavítása
    
    Felelősségek:
    - AnalyticsResult → Folium overlay format konverzió
    - 4 weather típus támogatása (hőmérséklet, csapadék, szél, széllökés)
    - Koordináták + értékek kinyerése
    - Metrika alapú overlay típus automatikus felismerés
    - Min/max értékek számítása színskálákhoz
    """
    
    # 🔧 KRITIKUS ÚJ: METRIC_MAP - AnalyticsMetric → Display Parameter Mapping
    METRIC_MAP = {
        # Hőmérséklet metrikák
        AnalyticsMetric.TEMPERATURE_2M_MAX: 'temperature',
        AnalyticsMetric.TEMPERATURE_2M_MIN: 'temperature', 
        AnalyticsMetric.TEMPERATURE_2M_MEAN: 'temperature',
        AnalyticsMetric.TEMPERATURE_RANGE: 'temperature',
        
        # Csapadék metrikák
        AnalyticsMetric.PRECIPITATION_SUM: 'precipitation',
        
        # Szél metrikák - KRITIKUS JAVÍTÁS
        AnalyticsMetric.WINDSPEED_10M_MAX: 'wind_speed',      # ← EZ HIÁNYZOTT!
        AnalyticsMetric.WINDGUSTS_10M_MAX: 'wind_gusts',
        
        # További potenciális metrikák
        # AnalyticsMetric.HUMIDITY: 'humidity',
        # AnalyticsMetric.PRESSURE: 'pressure',
    }
    
    # Metrika → Overlay típus mapping (kompatibilitás)
    METRIC_TO_OVERLAY = METRIC_MAP  # Alias az előző verzióhoz
    
    # Overlay konfigurációk
    OVERLAY_CONFIGS = {
        'temperature': {
            'name': 'Hőmérséklet',
            'unit': '°C',
            'color_scale': 'RdYlBu_r',  # Kék (hideg) → Piros (meleg)
            'default_range': (-20, 40),
            'icon': '🌡️'
        },
        'precipitation': {
            'name': 'Csapadék', 
            'unit': 'mm',
            'color_scale': 'Blues',  # Világoskék → Sötétkék
            'default_range': (0, 50),
            'icon': '🌧️'
        },
        'wind_speed': {
            'name': 'Szélsebesség',
            'unit': 'km/h', 
            'color_scale': 'Greens',  # Világoszöld → Sötétzöld
            'default_range': (0, 60),
            'icon': '💨'
        },
        'wind_gusts': {
            'name': 'Széllökések',
            'unit': 'km/h',
            'color_scale': 'Oranges',  # Világos → Sötét narancs
            'default_range': (0, 100), 
            'icon': '🌪️'
        }
    }
    
    def __init__(self):
        logger.info("🌉 Weather Data Bridge v2.0 inicializálva - METRIC_MAP javítással")
        logger.info(f"🔧 Támogatott metrikák: {list(self.METRIC_MAP.keys())}")
    
    def convert_analytics_result(self, analytics_result: AnalyticsResult, display_parameter: Optional[str] = None) -> Dict[str, Any]:
        """
        🔧 KRITIKUS ÚJ METÓDUS: Analytics eredmény konvertálása display_parameter alapján
        
        Ez a metódus helyettesíti a régi "csak temperature" logikát.
        Most már intelligensen felismeri a metrika típusát és megfelelően konvertál.
        
        Args:
            analytics_result: Multi-City Engine eredménye
            display_parameter: Explicit display parameter ("Hőmérséklet", "Szél", "Csapadék")
                              Ha None, akkor auto-detect a metric alapján
            
        Returns:
            HungarianMapVisualizer kompatibilis dictionary
        """
        try:
            if not analytics_result or not analytics_result.city_results:
                logger.warning("⚠️ Üres analytics eredmény")
                return {}
            
            # 🔧 INTELLIGENS METRIKA FELISMERÉS
            metric = analytics_result.question.metric
            
            # Display parameter meghatározása
            if display_parameter:
                # Explicit parameter használata
                detected_parameter = self._normalize_display_parameter(display_parameter)
                logger.info(f"🎯 Explicit display parameter: {display_parameter} → {detected_parameter}")
            else:
                # Auto-detect metric alapján
                detected_parameter = self.METRIC_MAP.get(metric)
                if not detected_parameter:
                    logger.error(f"❌ Ismeretlen metrika: {metric}")
                    return {}
                logger.info(f"🔄 Auto-detect: {metric} → {detected_parameter}")
            
            logger.info(f"🔄 Konverzió: {metric} → {detected_parameter} ({len(analytics_result.city_results)} város)")
            
            # HungarianMapVisualizer kompatibilis formátum létrehozása
            result_data = {
                detected_parameter: {}
            }
            
            # Város adatok konvertálása
            for city_result in analytics_result.city_results:
                if self._is_valid_city_result(city_result):
                    city_data = {
                        'coordinates': [city_result.latitude, city_result.longitude],
                        'value': float(city_result.value)
                    }
                    
                    # Szél esetén extra adatok
                    if detected_parameter in ['wind_speed', 'wind_gusts']:
                        city_data['speed'] = float(city_result.value)
                        city_data['direction'] = 0  # Default irány - később bővíthető
                    
                    result_data[detected_parameter][city_result.city_name] = city_data
            
            if not result_data[detected_parameter]:
                logger.error("❌ Nincs érvényes város adat a konverzióhoz")
                return {}
            
            logger.info(f"✅ Convert analytics result sikeres: {detected_parameter}, {len(result_data[detected_parameter])} város")
            
            return result_data
            
        except Exception as e:
            logger.error(f"❌ Hiba az analytics result konverzióban: {e}", exc_info=True)
            return {}
    
    def _normalize_display_parameter(self, display_parameter: str) -> str:
        """Display parameter normalizálása belső formátumra"""
        normalization_map = {
            "Hőmérséklet": "temperature",
            "Szél": "wind_speed", 
            "Széllökés": "wind_gusts",
            "Csapadék": "precipitation",
            "Páratartalom": "humidity",
            "Légnyomás": "pressure"
        }
        
        normalized = normalization_map.get(display_parameter, display_parameter.lower())
        logger.debug(f"🔄 Display parameter normalizálás: {display_parameter} → {normalized}")
        return normalized
    
    def convert_analytics_to_weather_overlay(self, analytics_result: AnalyticsResult) -> Optional[WeatherOverlayData]:
        """
        🔧 JAVÍTOTT: AnalyticsResult → WeatherOverlayData konverzió METRIC_MAP alapján
        
        Ez a metódus átalakítja a multi_city_engine.py eredményeit
        Folium térkép által várt formátumba a METRIC_MAP használatával.
        
        Args:
            analytics_result: Multi-City Engine eredménye
            
        Returns:
            WeatherOverlayData vagy None hiba esetén
        """
        try:
            if not analytics_result or not analytics_result.city_results:
                logger.warning("⚠️ Üres analytics eredmény")
                return None
            
            # 🔧 JAVÍTOTT: METRIC_MAP alapú overlay típus meghatározása
            metric = analytics_result.question.metric
            overlay_type = self.METRIC_MAP.get(metric)
            
            if not overlay_type:
                logger.error(f"❌ Ismeretlen metrika overlay konverzióhoz: {metric}")
                logger.error(f"🔧 Támogatott metrikák: {list(self.METRIC_MAP.keys())}")
                return None
            
            logger.info(f"🔄 Overlay konverzió: {metric} → {overlay_type} ({len(analytics_result.city_results)} város)")
            
            # Weather data Dictionary létrehozása
            weather_data = {}
            values = []
            
            for city_result in analytics_result.city_results:
                if self._is_valid_city_result(city_result):
                    city_data = {
                        'coordinates': [city_result.latitude, city_result.longitude],
                        'value': float(city_result.value),
                        'city_name': city_result.city_name,
                        'country': city_result.country,
                        'country_code': city_result.country_code,
                        'population': city_result.population,
                        'rank': getattr(city_result, 'rank', 0),
                        'quality_score': city_result.quality_score
                    }
                    
                    # Szél esetén extra adatok
                    if overlay_type in ['wind_speed', 'wind_gusts']:
                        city_data['speed'] = float(city_result.value)
                        city_data['direction'] = 0  # Default - később kibővíthető wind direction-nel
                    
                    weather_data[city_result.city_name] = city_data
                    values.append(float(city_result.value))
            
            if not weather_data:
                logger.error("❌ Nincs érvényes város adat a konverzióhoz")
                return None
            
            # Metadata létrehozása (min/max, színskála info)
            metadata = self._create_overlay_metadata(overlay_type, values, analytics_result)
            
            overlay_data = WeatherOverlayData(
                overlay_type=overlay_type,
                data=weather_data,
                metadata=metadata
            )
            
            logger.info(f"✅ Weather overlay konverzió sikeres: {overlay_type}, {len(weather_data)} város, tartomány: {metadata.get('value_min', 'N/A')}-{metadata.get('value_max', 'N/A')}")
            
            return overlay_data
            
        except Exception as e:
            logger.error(f"❌ Hiba az analytics→overlay konverzióban: {e}", exc_info=True)
            return None
    
    def get_display_parameter_for_metric(self, metric: AnalyticsMetric) -> Optional[str]:
        """
        🔧 ÚJ METÓDUS: Metrika alapján display parameter lekérdezése
        
        Args:
            metric: AnalyticsMetric enum érték
            
        Returns:
            Display parameter string vagy None
        """
        display_parameter = self.METRIC_MAP.get(metric)
        logger.debug(f"🔍 Metrika → Display parameter: {metric} → {display_parameter}")
        return display_parameter
    
    def get_supported_metrics(self) -> List[AnalyticsMetric]:
        """
        📋 Támogatott metrikák listája
        
        Returns:
            AnalyticsMetric lista
        """
        return list(self.METRIC_MAP.keys())
    
    def is_metric_supported(self, metric: AnalyticsMetric) -> bool:
        """
        ✅ Metrika támogatottság ellenőrzése
        
        Args:
            metric: AnalyticsMetric enum érték
            
        Returns:
            Támogatott-e a metrika
        """
        supported = metric in self.METRIC_MAP
        logger.debug(f"🔍 Metrika támogatottság: {metric} → {supported}")
        return supported
    
    def _is_valid_city_result(self, city_result: CityWeatherResult) -> bool:
        """Ellenőrzi hogy a város eredmény érvényes-e overlay-hez"""
        is_valid = (city_result.latitude is not None and 
                   city_result.longitude is not None and
                   city_result.value is not None and
                   isinstance(city_result.value, (int, float)) and
                   not (city_result.value == 0 and city_result.city_name == ""))  # 0 érték csak akkor valid ha nem placeholder
        
        if not is_valid:
            logger.debug(f"⚠️ Invalid city result: {city_result.city_name} - lat: {city_result.latitude}, lon: {city_result.longitude}, value: {city_result.value}")
        
        return is_valid
    
    def _create_overlay_metadata(self, overlay_type: str, values: List[float], analytics_result: AnalyticsResult) -> Dict[str, Any]:
        """Overlay metadata létrehozása (színskála, tartomány, stb.)"""
        config = self.OVERLAY_CONFIGS[overlay_type]
        
        # Min/max értékek
        value_min = min(values) if values else 0
        value_max = max(values) if values else 1
        
        # Színskála tartomány optimalizálás
        if overlay_type == 'temperature':
            # Hőmérsékletnél szimmetrikus skála a 0°C körül
            abs_max = max(abs(value_min), abs(value_max))
            scale_min = -abs_max if value_min < 0 else min(value_min, 0)
            scale_max = abs_max if value_max > 0 else max(value_max, 0)
        else:
            # Egyéb metrikáknál 0-tól induló skála
            scale_min = 0
            scale_max = value_max * 1.1  # 10% padding felfelé
        
        metadata = {
            'overlay_type': overlay_type,
            'name': config['name'],
            'unit': config['unit'],
            'icon': config['icon'],
            'color_scale': config['color_scale'],
            'value_min': value_min,
            'value_max': value_max,
            'scale_min': scale_min,
            'scale_max': scale_max,
            'total_cities': len(values),
            'analytics_question': analytics_result.question.question_text,
            'execution_time': analytics_result.execution_time,
            'data_sources': [source.value for source in analytics_result.data_sources_used],
            'statistics': analytics_result.statistics,
            'generated_at': datetime.now().isoformat(),
            'metric': analytics_result.question.metric.value  # 🔧 ÚJ: Eredeti metrika megőrzése
        }
        
        return metadata
    
    def get_overlay_legend_data(self, overlay_data: WeatherOverlayData) -> Dict[str, Any]:
        """
        Legend adatok generálása a Folium térképhez
        
        Returns:
            Legend konfigurációs dictionary
        """
        metadata = overlay_data.metadata
        
        legend_data = {
            'title': f"{metadata['icon']} {metadata['name']}",
            'unit': metadata['unit'],
            'min_value': metadata['scale_min'],
            'max_value': metadata['scale_max'],
            'color_scale': metadata['color_scale'],
            'total_cities': metadata['total_cities'],
            'value_range': f"{metadata['value_min']:.1f} - {metadata['value_max']:.1f}",
            'question': metadata['analytics_question'],
            'metric': metadata.get('metric', 'unknown')  # 🔧 ÚJ: Metrika info
        }
        
        return legend_data
    
    def create_multiple_overlays_from_analytics(self, analytics_results: List[AnalyticsResult]) -> Dict[str, WeatherOverlayData]:
        """
        Több analytics eredményből több overlay létrehozása
        
        Használat: Ha egyszerre több metrika eredménye van (pl. hőmérséklet + csapadék)
        """
        overlays = {}
        
        for result in analytics_results:
            overlay_data = self.convert_analytics_to_weather_overlay(result)
            if overlay_data:
                overlays[overlay_data.overlay_type] = overlay_data
        
        logger.info(f"✅ Múltiplex overlay konverzió: {len(overlays)} overlay típus")
        return overlays
    
    def get_folium_heatmap_data(self, overlay_data: WeatherOverlayData) -> List[List[float]]:
        """
        Folium HeatMap plugin formátumra konvertálás
        
        Returns:
            [[lat, lon, value], [lat, lon, value], ...] formátum
        """
        heatmap_data = []
        
        for city_name, city_data in overlay_data.data.items():
            lat, lon = city_data['coordinates']
            value = city_data['value']
            heatmap_data.append([lat, lon, value])
        
        logger.debug(f"🗺️ HeatMap data generálva: {len(heatmap_data)} pont")
        return heatmap_data
    
    def get_folium_marker_data(self, overlay_data: WeatherOverlayData) -> List[Dict[str, Any]]:
        """
        Folium CircleMarker vagy egyéb marker formátumra konvertálás
        
        Returns:
            Marker konfigurációs lista
        """
        marker_data = []
        metadata = overlay_data.metadata
        
        for city_name, city_data in overlay_data.data.items():
            marker_config = {
                'latitude': city_data['coordinates'][0],
                'longitude': city_data['coordinates'][1], 
                'value': city_data['value'],
                'city_name': city_name,
                'country': city_data['country'],
                'popup_text': f"{city_name}, {city_data['country']}<br>{city_data['value']:.1f} {metadata['unit']}",
                'tooltip_text': f"{city_name}: {city_data['value']:.1f} {metadata['unit']}",
                'marker_size': self._calculate_marker_size(city_data['value'], metadata),
                'marker_color': self._calculate_marker_color(city_data['value'], metadata),
                'rank': city_data.get('rank', 0)
            }
            
            # Szél esetén extra adatok
            if overlay_data.overlay_type in ['wind_speed', 'wind_gusts']:
                marker_config['speed'] = city_data.get('speed', city_data['value'])
                marker_config['direction'] = city_data.get('direction', 0)
            
            marker_data.append(marker_config)
        
        logger.debug(f"📍 Marker data generálva: {len(marker_data)} marker")
        return marker_data
    
    def _calculate_marker_size(self, value: float, metadata: Dict[str, Any]) -> int:
        """Marker méret számítása érték alapján"""
        value_range = metadata['scale_max'] - metadata['scale_min']
        if value_range == 0:
            return 8
        
        normalized = (value - metadata['scale_min']) / value_range
        min_size, max_size = 4, 20
        return int(min_size + normalized * (max_size - min_size))
    
    def _calculate_marker_color(self, value: float, metadata: Dict[str, Any]) -> str:
        """Marker szín számítása érték alapján (egyszerű megoldás)"""
        value_range = metadata['scale_max'] - metadata['scale_min']
        if value_range == 0:
            return '#FF0000'
        
        normalized = (value - metadata['scale_min']) / value_range
        
        # 🎨 Overlay típus alapú színválasztás
        overlay_type = metadata['overlay_type']
        
        if overlay_type == 'temperature':
            # Hőmérséklet: Kék → Sárga → Piros
            if normalized < 0.33:
                return '#0000FF'  # Kék
            elif normalized < 0.66:
                return '#FFFF00'  # Sárga
            else:
                return '#FF0000'  # Piros
        elif overlay_type == 'precipitation':
            # Csapadék: Világoskék → Sötétkék
            if normalized < 0.5:
                return '#87CEEB'  # Világoskék
            else:
                return '#0000CD'  # Sötétkék
        elif overlay_type in ['wind_speed', 'wind_gusts']:
            # Szél: Zöld → Sárga → Piros
            if normalized < 0.33:
                return '#00FF00'  # Zöld
            elif normalized < 0.66:
                return '#FFFF00'  # Sárga
            else:
                return '#FF0000'  # Piros
        else:
            # Fallback
            if normalized < 0.33:
                return '#0000FF'
            elif normalized < 0.66:
                return '#FFFF00'
            else:
                return '#FF0000'
    
    def debug_metric_mapping(self) -> Dict[str, Any]:
        """
        🔍 DEBUG: Metrika mapping információk
        
        Returns:
            Debug információk dictionary
        """
        debug_info = {
            'total_supported_metrics': len(self.METRIC_MAP),
            'metric_mappings': {str(metric): display_param for metric, display_param in self.METRIC_MAP.items()},
            'overlay_types': list(self.OVERLAY_CONFIGS.keys()),
            'windspeed_supported': AnalyticsMetric.WINDSPEED_10M_MAX in self.METRIC_MAP,
            'windspeed_maps_to': self.METRIC_MAP.get(AnalyticsMetric.WINDSPEED_10M_MAX, 'NOT_FOUND'),
            'bridge_version': '2.0_METRIC_MAP_FIXED'
        }
        
        logger.info(f"🔍 DEBUG Metric Mapping Info: {debug_info}")
        return debug_info


# 🧪 TESTING & DEBUG
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("🌉 Weather Data Bridge v2.0 - METRIC_MAP JAVÍTÁS Teszt mód")
    bridge = WeatherDataBridge()
    
    # Debug info
    debug_info = bridge.debug_metric_mapping()
    print("🔍 Debug információk:")
    for key, value in debug_info.items():
        print(f"   {key}: {value}")
    
    # Mock AnalyticsResult létrehozása teszteléshez
    from src.data.models import AnalyticsQuestion
    from src.data.enums import QuestionType, RegionScope
    
    # WINDSPEED teszt
    print("\n💨 WINDSPEED METRIC TESZT:")
    windspeed_question = AnalyticsQuestion(
        question_text="Hol volt ma a legszelesebb Magyarországban?",
        question_type=QuestionType.MULTI_CITY,
        region_scope=RegionScope.COUNTRY,
        metric=AnalyticsMetric.WINDSPEED_10M_MAX
    )
    
    windspeed_cities = [
        CityWeatherResult(
            city_name="Győr", country="Hungary", country_code="HU",
            latitude=47.6874, longitude=17.6504, value=28.5,
            metric=AnalyticsMetric.WINDSPEED_10M_MAX,
            date=datetime.now().date(), population=130000, quality_score=0.8
        ),
        CityWeatherResult(
            city_name="Pécs", country="Hungary", country_code="HU", 
            latitude=46.0727, longitude=18.2329, value=22.1,
            metric=AnalyticsMetric.WINDSPEED_10M_MAX,
            date=datetime.now().date(), population=140000, quality_score=0.7
        )
    ]
    
    windspeed_result = AnalyticsResult(
        question=windspeed_question, city_results=windspeed_cities,
        execution_time=1.8, total_cities_found=120,
        data_sources_used=[], statistics={'mean': 25.3, 'max': 28.5, 'min': 22.1},
        provider_statistics={}
    )
    
    # WINDSPEED konverzió teszt
    print("🔄 Windspeed konverzió teszt:")
    windspeed_overlay = bridge.convert_analytics_to_weather_overlay(windspeed_result)
    if windspeed_overlay:
        print(f"✅ Windspeed overlay konverzió sikeres: {windspeed_overlay.overlay_type}")
        print(f"📊 Városok: {len(windspeed_overlay.data)}")
        print(f"📊 Tartomány: {windspeed_overlay.metadata['value_min']}-{windspeed_overlay.metadata['value_max']} {windspeed_overlay.metadata['unit']}")
        print(f"🎨 Színskála: {windspeed_overlay.metadata['color_scale']}")
        print(f"🏷️ Icon: {windspeed_overlay.metadata['icon']}")
    else:
        print("❌ Windspeed overlay konverzió sikertelen")
    
    # convert_analytics_result teszt
    print("\n🔄 convert_analytics_result teszt (HungarianMapVisualizer format):")
    folium_format = bridge.convert_analytics_result(windspeed_result, "Szél")
    if folium_format:
        print(f"✅ Folium format konverzió sikeres: {list(folium_format.keys())}")
        for key, data in folium_format.items():
            print(f"   {key}: {len(data)} város")
            if data:
                sample_city = list(data.keys())[0]
                sample_data = data[sample_city]
                print(f"   Sample: {sample_city} → {sample_data}")
    else:
        print("❌ Folium format konverzió sikertelen")
    
    print("\n✅ Weather Data Bridge v2.0 METRIC_MAP javítás teszt befejezve!")
    print("🎯 KRITIKUS JAVÍTÁSOK:")
    print("   ✅ METRIC_MAP minden metrikával")
    print("   ✅ convert_analytics_result display_parameter támogatás")
    print("   ✅ WINDSPEED_10M_MAX → wind_speed mapping")
    print("   ✅ Intelligens metrika felismerés")
    print("   ✅ 'Buta Tolmács' probléma MEGOLDVA")
