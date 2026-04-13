/**
 * HungaryMap - Interactive map of Hungarian counties with Leaflet
 *
 * Displays Hungary's 20 counties (Budapest + 19 megye) with:
 * - County boundaries (GeoJSON)
 * - Interactive selection
 * - Weather station markers
 * - Region-based coloring
 */
import React, { useMemo, useState } from 'react';
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  CircleMarker,
  Popup,
  Tooltip,
  useMap
} from 'react-leaflet';
import { LatLng, LatLngBounds } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './HungaryMap.css';
import {
  HUNGARY_COUNTIES_GEOJSON,
  HUNGARY_CENTER,
  DEFAULT_ZOOM,
  COUNTY_ZOOM,
  getCountyCenter
} from './hungaryCounties.geojson';
import { HungarianWeatherStation } from '../../services/hungaryService';

// =============================================================================
// TYPES
// =============================================================================

export interface CountyData {
  county: string;
  value?: number;
  label?: string;
  color?: string;
}

export interface WeatherStationData extends HungarianWeatherStation {
  metric?: number;
  metricUnit?: string;
  metricLabel?: string;
}

export interface HungaryMapProps {
  /** Weather stations to display on the map */
  stations?: WeatherStationData[];
  /** County-level data for coloring/labeling */
  countyData?: CountyData[];
  /** Selected county name */
  selectedCounty?: string | null;
  /** Callback when a county is clicked */
  onCountySelect?: (county: string) => void;
  /** Callback when a station is clicked */
  onStationSelect?: (station: HungarianWeatherStation) => void;
  /** Whether to show weather stations */
  showStations?: boolean;
  /** Map height in pixels */
  height?: number;
  /** Additional CSS class name */
  className?: string;
}

// =============================================================================
// COLOR HELPERS
// =============================================================================

/**
 * Region colors for county highlighting
 */
const REGION_COLORS: Record<string, string> = {
  'Közép-Magyarország': '#3b82f6',    // blue
  'Észak-Magyarország': '#8b5cf6',    // purple
  'Észak-Alföld': '#06b6d4',          // cyan
  'Dél-Alföld': '#10b981',            // green
  'Dél-Dunántúl': '#f59e0b',          // amber
  'Nyugat-Dunántúl': '#f97316',       // orange
  'Közép-Dunántúl': '#ef4444',        // red
};

/**
 * Get color for a county based on region
 */
function getCountyColor(region: string): string {
  return REGION_COLORS[region] || '#6b7280';
}

/**
 * Calculate color based on value (heatmap style)
 */
function getValueColor(value: number, min: number, max: number): string {
  if (max === min) return '#3b82f6';
  const normalized = (value - min) / (max - min);

  if (normalized < 0.25) return '#2166ac';
  if (normalized < 0.5) return '#67a9cf';
  if (normalized < 0.75) return '#fdae61';
  return '#d73027';
}

// =============================================================================
// MAP VIEW CONTROLLER
// =============================================================================

interface MapViewControllerProps {
  center: LatLng;
  zoom: number;
  bounds?: LatLngBounds;
}

/**
 * Component to programmatically control map view
 */
const MapViewController: React.FC<MapViewControllerProps> = ({ center, zoom, bounds }) => {
  const map = useMap();

  React.useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [20, 20] });
    } else {
      map.setView(center, zoom);
    }
  }, [map, center, zoom, bounds]);

  return null;
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

const HungaryMap: React.FC<HungaryMapProps> = ({
  stations = [],
  countyData = [],
  selectedCounty,
  onCountySelect,
  onStationSelect,
  showStations = true,
  height = 500,
  className = ''
}) => {
  const [hoveredCounty, setHoveredCounty] = useState<string | null>(null);

  // Calculate value range for heatmap coloring
  const { minValue, maxValue } = useMemo(() => {
    const values = countyData
      .map(d => d.value)
      .filter((v): v is number => v !== undefined && v !== null && !isNaN(v));
    if (values.length === 0) return { minValue: 0, maxValue: 100 };
    return {
      minValue: Math.min(...values),
      maxValue: Math.max(...values)
    };
  }, [countyData]);

  // Create county data map for quick lookup
  const countyDataMap = useMemo(() => {
    const map = new Map<string, CountyData>();
    countyData.forEach(d => map.set(d.county, d));
    return map;
  }, [countyData]);

  // Map center and zoom based on selection
  const { mapCenter, mapZoom } = useMemo(() => {
    if (selectedCounty) {
      const center = getCountyCenter(selectedCounty);
      if (center) {
        return { mapCenter: new LatLng(center[0], center[1]), mapZoom: COUNTY_ZOOM };
      }
    }
    return { mapCenter: new LatLng(HUNGARY_CENTER[0], HUNGARY_CENTER[1]), mapZoom: DEFAULT_ZOOM };
  }, [selectedCounty]);

  // Style for each county feature
  const getCountyStyle = (feature?: GeoJSON.Feature<GeoJSON.Geometry, any>) => {
    const countyName = feature?.properties?.name as string | undefined;
    if (!countyName) {
      return {
        fillColor: '#6b7280',
        weight: 2,
        opacity: 1,
        color: '#ffffff',
        fillOpacity: 0.4
      };
    }

    const isSelected = selectedCounty === countyName;
    const isHovered = hoveredCounty === countyName;
    const data = countyDataMap.get(countyName);
    const region = feature?.properties?.region as string | undefined;

    let fillColor = region ? getCountyColor(region) : '#6b7280';

    // Use heatmap color if value is provided
    if (data?.value !== undefined) {
      fillColor = getValueColor(data.value, minValue, maxValue);
    }

    return {
      fillColor,
      weight: isSelected || isHovered ? 3 : 2,
      opacity: 1,
      color: isSelected ? '#1f2937' : isHovered ? '#4b5563' : '#ffffff',
      dashArray: isSelected ? '' : '3',
      fillOpacity: isSelected ? 0.7 : isHovered ? 0.6 : 0.4
    };
  };

  // County feature handlers
  const onEachCounty = (
    feature: GeoJSON.Feature<GeoJSON.Geometry, any>,
    layer: any
  ) => {
    const countyName = feature.properties?.name as string;
    if (!countyName) return;

    layer.on({
      mouseover: () => setHoveredCounty(countyName),
      mouseout: () => setHoveredCounty(null),
      click: () => onCountySelect?.(countyName)
    });

    // Build popup content
    const props = feature.properties;
    const data = countyDataMap.get(countyName);
    const popupContent = `
      <div class="county-popup">
        <h3>${props?.nameHu || countyName}</h3>
        <p><strong>Régió:</strong> ${props?.region || 'N/A'}</p>
        ${props?.population ? `<p><strong>Népesség:</strong> ${props.population.toLocaleString('hu-HU')}</p>` : ''}
        ${props?.areaKm2 ? `<p><strong>Terület:</strong> ${props.areaKm2} km²</p>` : ''}
        ${data?.value !== undefined ? `<p><strong>Érték:</strong> ${data.value.toFixed(1)}${data.label ? ` (${data.label})` : ''}</p>` : ''}
      </div>
    `;

    layer.bindPopup(popupContent);

    // Tooltip on hover
    layer.bindTooltip(feature.properties?.nameHu || countyName, {
      sticky: true,
      direction: 'top'
    });
  };

  // Filter valid stations
  const validStations = useMemo(() => {
    return stations.filter(
      s => s.coordinates?.lat !== undefined && s.coordinates?.lon !== undefined
    );
  }, [stations]);

  return (
    <div className={`hungary-map-container ${className}`} style={{ height: `${height}px` }}>
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <MapViewController center={mapCenter} zoom={mapZoom} />

        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* County boundaries */}
        <GeoJSON
          data={HUNGARY_COUNTIES_GEOJSON}
          style={getCountyStyle}
          onEachFeature={onEachCounty}
        />

        {/* Weather station markers */}
        {showStations && validStations.map((station, index) => (
          <CircleMarker
            key={`${station.id}-${index}`}
            center={[station.coordinates!.lat, station.coordinates!.lon]}
            radius={8}
            fillColor="#dc2626"
            color="#ffffff"
            weight={2}
            opacity={1}
            fillOpacity={0.8}
            eventHandlers={{
              click: () => onStationSelect?.(station)
            }}
          >
            <Tooltip direction="top" offset={[0, -10]} sticky>
              <strong>{station.name}</strong>
              {station.metric !== undefined && (
                <>{station.metric.toFixed(1)} {station.metricUnit || ''}</>
              )}
            </Tooltip>
            <Popup>
              <div className="station-popup">
                <h4>{station.name}</h4>
                <p><strong>Megye:</strong> {station.county || 'N/A'}</p>
                {station.data_quality_score !== undefined && (
                  <p><strong>Adatminőség:</strong> {station.data_quality_score}%</p>
                )}
                {station.metric !== undefined && (
                  <p><strong>{station.metricLabel || 'Érték'}:</strong> {station.metric.toFixed(1)} {station.metricUnit || ''}</p>
                )}
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      {/* Legend */}
      {countyData.length > 0 && (
        <div className="hungary-map-legend">
          <span className="legend-label">Alacsony</span>
          <div className="legend-gradient"></div>
          <span className="legend-label">Magas</span>
          <span className="legend-values">
            ({minValue.toFixed(1)} - {maxValue.toFixed(1)})
          </span>
        </div>
      )}

      {/* Stats bar */}
      <div className="hungary-map-stats">
        {selectedCounty && (
          <span className="stat-selected">Kiválasztva: {selectedCounty}</span>
        )}
        {validStations.length > 0 && (
          <span className="stat-stations">Állomások: {validStations.length}</span>
        )}
      </div>
    </div>
  );
};

export default HungaryMap;
