"""Weather Data Bridge - Multi-City Engine → Folium Map Integration."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.data.enums import AnalyticsMetric
from src.data.models import AnalyticsQuestion, AnalyticsResult, CityWeatherResult

from src.presentation.gui.weather_data_bridge.constants import (
    DISPLAY_PARAMETER_MAP,
    METRIC_MAP,
    OVERLAY_CONFIGS,
)
from src.presentation.gui.weather_data_bridge.data import WeatherOverlayData

logger = logging.getLogger(__name__)


class WeatherDataBridge:
    """
    Weather Data Bridge - Analytics Engine → Folium Map Integration.

    Responsibilities:
    - AnalyticsResult → Folium overlay format conversion
    - 4 weather types supported (temperature, precipitation, wind, wind_gusts)
    - Coordinates + values extraction
    - Metric-based overlay type auto-detection
    - Min/max values calculation for color scales
    """

    METRIC_MAP = METRIC_MAP
    METRIC_TO_OVERLAY = METRIC_MAP
    OVERLAY_CONFIGS = OVERLAY_CONFIGS

    def __init__(self) -> None:
        logger.info("Weather Data Bridge initialized with METRIC_MAP")

    def convert_analytics_result(
        self, analytics_result: AnalyticsResult, display_parameter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert analytics result based on display_parameter."""
        try:
            if not analytics_result or not analytics_result.city_results:
                logger.warning("Empty analytics result")
                return {}

            metric = analytics_result.question.metric

            if display_parameter:
                detected_parameter = self._normalize_display_parameter(display_parameter)
            else:
                detected_parameter = self.METRIC_MAP.get(metric)
                if not detected_parameter:
                    logger.error(f"Unknown metric: {metric}")
                    return {}

            result_data = {detected_parameter: {}}

            for city_result in analytics_result.city_results:
                if self._is_valid_city_result(city_result):
                    city_data = {
                        'coordinates': [city_result.latitude, city_result.longitude],
                        'value': float(city_result.value)
                    }
                    if detected_parameter in ['wind_speed', 'wind_gusts']:
                        city_data['speed'] = float(city_result.value)
                        city_data['direction'] = 0
                    result_data[detected_parameter][city_result.city_name] = city_data

            if not result_data[detected_parameter]:
                return {}

            return result_data

        except Exception as e:
            logger.error(f"Error in analytics result conversion: {e}", exc_info=True)
            return {}

    def _normalize_display_parameter(self, display_parameter: str) -> str:
        """Display parameter normalizálása belső formátumra"""
        normalized = DISPLAY_PARAMETER_MAP.get(display_parameter, display_parameter.lower())
        return normalized

    def convert_analytics_to_weather_overlay(
        self, analytics_result: AnalyticsResult
    ) -> Optional[WeatherOverlayData]:
        """AnalyticsResult → WeatherOverlayData conversion."""
        try:
            if not analytics_result or not analytics_result.city_results:
                return None

            metric = analytics_result.question.metric
            overlay_type = self.METRIC_MAP.get(metric)

            if not overlay_type:
                return None

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
                    if overlay_type in ['wind_speed', 'wind_gusts']:
                        city_data['speed'] = float(city_result.value)
                        city_data['direction'] = 0
                    weather_data[city_result.city_name] = city_data
                    values.append(float(city_result.value))

            if not weather_data:
                return None

            metadata = self._create_overlay_metadata(overlay_type, values, analytics_result)

            return WeatherOverlayData(
                overlay_type=overlay_type,
                data=weather_data,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error in overlay conversion: {e}", exc_info=True)
            return None

    def get_display_parameter_for_metric(self, metric: AnalyticsMetric) -> Optional[str]:
        """Metrika alapján display parameter lekérdezése"""
        return self.METRIC_MAP.get(metric)

    def get_supported_metrics(self) -> List[AnalyticsMetric]:
        """Támogatott metrikák listája"""
        return list(self.METRIC_MAP.keys())

    def is_metric_supported(self, metric: AnalyticsMetric) -> bool:
        """Metrika támogatottság ellenőrzése"""
        return metric in self.METRIC_MAP

    def _is_valid_city_result(self, city_result: CityWeatherResult) -> bool:
        """Ellenőrzi hogy a város eredmény érvényes-e overlay-hez"""
        is_valid = (
            city_result.latitude is not None and
            city_result.longitude is not None and
            city_result.value is not None and
            isinstance(city_result.value, (int, float)) and
            not (city_result.value == 0 and city_result.city_name == "")
        )
        return is_valid

    def _create_overlay_metadata(
        self, overlay_type: str, values: List[float], analytics_result: AnalyticsResult
    ) -> Dict[str, Any]:
        """Overlay metadata létrehozása."""
        config = self.OVERLAY_CONFIGS[overlay_type]

        value_min = min(values) if values else 0
        value_max = max(values) if values else 1

        if overlay_type == 'temperature':
            abs_max = max(abs(value_min), abs(value_max))
            scale_min = -abs_max if value_min < 0 else min(value_min, 0)
            scale_max = abs_max if value_max > 0 else max(value_max, 0)
        else:
            scale_min = 0
            scale_max = value_max * 1.1

        return {
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
            'metric': analytics_result.question.metric.value
        }

    def get_overlay_legend_data(self, overlay_data: WeatherOverlayData) -> Dict[str, Any]:
        """Legend adatok generálása a Folium térképhez"""
        metadata = overlay_data.metadata

        return {
            'title': f"{metadata['icon']} {metadata['name']}",
            'unit': metadata['unit'],
            'min_value': metadata['scale_min'],
            'max_value': metadata['scale_max'],
            'color_scale': metadata['color_scale'],
            'total_cities': metadata['total_cities'],
            'value_range': f"{metadata['value_min']:.1f} - {metadata['value_max']:.1f}",
            'question': metadata['analytics_question'],
            'metric': metadata.get('metric', 'unknown')
        }

    def create_multiple_overlays_from_analytics(
        self, analytics_results: List[AnalyticsResult]
    ) -> Dict[str, WeatherOverlayData]:
        """Több analytics eredményből több overlay létrehozása"""
        overlays = {}

        for result in analytics_results:
            overlay_data = self.convert_analytics_to_weather_overlay(result)
            if overlay_data:
                overlays[overlay_data.overlay_type] = overlay_data

        return overlays

    def get_folium_heatmap_data(self, overlay_data: WeatherOverlayData) -> List[List[float]]:
        """Folium HeatMap plugin formátumra konvertálás"""
        heatmap_data = []

        for city_name, city_data in overlay_data.data.items():
            lat, lon = city_data['coordinates']
            value = city_data['value']
            heatmap_data.append([lat, lon, value])

        return heatmap_data

    def get_folium_marker_data(self, overlay_data: WeatherOverlayData) -> List[Dict[str, Any]]:
        """Folium CircleMarker formátumra konvertálás"""
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

            if overlay_data.overlay_type in ['wind_speed', 'wind_gusts']:
                marker_config['speed'] = city_data.get('speed', city_data['value'])
                marker_config['direction'] = city_data.get('direction', 0)

            marker_data.append(marker_config)

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
        """Marker szín számítása érték alapján"""
        value_range = metadata['scale_max'] - metadata['scale_min']
        if value_range == 0:
            return '#FF0000'

        normalized = (value - metadata['scale_min']) / value_range
        overlay_type = metadata['overlay_type']

        if overlay_type == 'temperature':
            if normalized < 0.33:
                return '#0000FF'
            elif normalized < 0.66:
                return '#FFFF00'
            else:
                return '#FF0000'
        elif overlay_type == 'precipitation':
            if normalized < 0.5:
                return '#87CEEB'
            else:
                return '#0000CD'
        elif overlay_type in ['wind_speed', 'wind_gusts']:
            if normalized < 0.33:
                return '#00FF00'
            elif normalized < 0.66:
                return '#FFFF00'
            else:
                return '#FF0000'
        else:
            if normalized < 0.33:
                return '#0000FF'
            elif normalized < 0.66:
                return '#FFFF00'
            else:
                return '#FF0000'

    def debug_metric_mapping(self) -> Dict[str, Any]:
        """DEBUG: Metrika mapping információk"""
        return {
            'total_supported_metrics': len(self.METRIC_MAP),
            'metric_mappings': {str(m): dp for m, dp in self.METRIC_MAP.items()},
            'overlay_types': list(self.OVERLAY_CONFIGS.keys()),
            'windspeed_supported': AnalyticsMetric.WINDSPEED_10M_MAX in self.METRIC_MAP,
            'windspeed_maps_to': self.METRIC_MAP.get(AnalyticsMetric.WINDSPEED_10M_MAX),
            'bridge_version': '2.0_METRIC_MAP_FIXED'
        }
