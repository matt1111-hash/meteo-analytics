#!/usr/bin/env python3
"""
Weather Data Bridge - Multi-City Engine → Folium Map Integration
Global Weather Analyzer projekt

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

from ..data.models import AnalyticsResult, CityWeatherResult, AnalyticsQuestion
from ..data.enums import AnalyticsMetric

logger = logging.getLogger(__name__)


@dataclass
class WeatherOverlayData:
    """Weather overlay adat struktúra Folium térképhez"""
    overlay_type: str  # 'temperature', 'precipitation', 'wind_speed', 'wind_gusts'
    data: Dict[str, Dict[str, Any]]  # city_name -> {coordinates, value, additional_info}
    metadata: Dict[str, Any]  # min/max értékek, egységek, színskála info
    

class WeatherDataBridge:
    """
    Weather Data Bridge - Analytics Engine → Folium Map Integration
    
    Felelősségek:
    - AnalyticsResult → Folium overlay format konverzió
    - 4 weather típus támogatása (hőmérséklet, csapadék, szél, széllökés)
    - Koordináták + értékek kinyerése
    - Metrika alapú overlay típus automatikus felismerés
    - Min/max értékek számítása színskálákhoz
    """
    
    # Metrika → Overlay típus mapping
    METRIC_TO_OVERLAY = {
        AnalyticsMetric.TEMPERATURE_2M_MAX: 'temperature',
        AnalyticsMetric.TEMPERATURE_2M_MIN: 'temperature', 
        AnalyticsMetric.TEMPERATURE_2M_MEAN: 'temperature',
        AnalyticsMetric.PRECIPITATION_SUM: 'precipitation',
        AnalyticsMetric.WINDSPEED_10M_MAX: 'wind_speed',
        AnalyticsMetric.WINDGUSTS_10M_MAX: 'wind_gusts',
        AnalyticsMetric.TEMPERATURE_RANGE: 'temperature'
    }
    
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
        logger.info("🌉 Weather Data Bridge inicializálva")
    
    def convert_analytics_to_weather_overlay(self, analytics_result: AnalyticsResult) -> Optional[WeatherOverlayData]:
        """
        🔧 KRITIKUS METÓDUS: AnalyticsResult → WeatherOverlayData konverzió
        
        Ez a metódus átalakítja a multi_city_engine.py eredményeit
        Folium térkép által várt formátumba.
        
        Args:
            analytics_result: Multi-City Engine eredménye
            
        Returns:
            WeatherOverlayData vagy None hiba esetén
        """
        try:
            if not analytics_result or not analytics_result.city_results:
                logger.warning("⚠️ Üres analytics eredmény")
                return None
            
            # Metrika alapú overlay típus meghatározása
            metric = analytics_result.question.metric
            overlay_type = self.METRIC_TO_OVERLAY.get(metric)
            
            if not overlay_type:
                logger.error(f"❌ Ismeretlen metrika overlay konverzióhoz: {metric}")
                return None
            
            logger.info(f"🔄 Konverzió: {metric} → {overlay_type} ({len(analytics_result.city_results)} város)")
            
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
            
            logger.info(f"✅ Weather overlay konverzió sikeres: {len(weather_data)} város, tartomány: {metadata.get('value_min', 'N/A')}-{metadata.get('value_max', 'N/A')}")
            
            return overlay_data
            
        except Exception as e:
            logger.error(f"❌ Hiba az analytics→overlay konverzióban: {e}", exc_info=True)
            return None
    
    def _is_valid_city_result(self, city_result: CityWeatherResult) -> bool:
        """Ellenőrzi hogy a város eredmény érvényes-e overlay-hez"""
        return (city_result.latitude is not None and 
                city_result.longitude is not None and
                city_result.value is not None and
                isinstance(city_result.value, (int, float)) and
                not (city_result.value == 0 and city_result.city_name != ""))  # 0 érték csak akkor valid ha nem placeholder
    
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
            # Egyéb metrикáknál 0-tól induló skála
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
            'generated_at': datetime.now().isoformat()
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
            'question': metadata['analytics_question']
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
        
        # Egyszerű szín interpoláció (kék → piros)
        if normalized < 0.33:
            return '#0000FF'  # Kék
        elif normalized < 0.66:
            return '#FFFF00'  # Sárga
        else:
            return '#FF0000'  # Piros


# 🧪 TESTING & DEBUG
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("🌉 Weather Data Bridge - Teszt mód")
    bridge = WeatherDataBridge()
    
    # Mock AnalyticsResult létrehozása teszteléshez
    from ..data.models import AnalyticsQuestion
    from ..data.enums import QuestionType, RegionScope
    
    mock_question = AnalyticsQuestion(
        question_text="Hol volt ma a legmelegebb Magyarországban?",
        question_type=QuestionType.MULTI_CITY,
        region_scope=RegionScope.COUNTRY,
        metric=AnalyticsMetric.TEMPERATURE_2M_MAX
    )
    
    mock_cities = [
        CityWeatherResult(
            city_name="Budapest", country="Hungary", country_code="HU",
            latitude=47.4979, longitude=19.0402, value=25.3,
            metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
            date=datetime.now().date(), population=1750000, quality_score=0.9
        ),
        CityWeatherResult(
            city_name="Debrecen", country="Hungary", country_code="HU", 
            latitude=47.5316, longitude=21.6273, value=23.8,
            metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
            date=datetime.now().date(), population=200000, quality_score=0.8
        )
    ]
    
    mock_result = AnalyticsResult(
        question=mock_question, city_results=mock_cities,
        execution_time=2.5, total_cities_found=165,
        data_sources_used=[], statistics={'mean': 24.55, 'max': 25.3, 'min': 23.8},
        provider_statistics={}
    )
    
    # Konverzió teszt
    overlay_data = bridge.convert_analytics_to_weather_overlay(mock_result)
    if overlay_data:
        print(f"✅ Overlay konverzió sikeres: {overlay_data.overlay_type}")
        print(f"📊 Városok: {len(overlay_data.data)}")
        print(f"📊 Tartomány: {overlay_data.metadata['value_min']}-{overlay_data.metadata['value_max']} {overlay_data.metadata['unit']}")
        
        # HeatMap data teszt
        heatmap_data = bridge.get_folium_heatmap_data(overlay_data)
        print(f"🗺️ HeatMap pontok: {len(heatmap_data)}")
        
        # Marker data teszt
        marker_data = bridge.get_folium_marker_data(overlay_data)
        print(f"📍 Marker konfiguráció: {len(marker_data)}")
    else:
        print("❌ Overlay konverzió sikertelen")
