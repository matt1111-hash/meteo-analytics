/**
 * MapView - Interactive Leaflet map showing cities with weather metric markers
 */
import React, { useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { CityWeatherResult } from '../types/weather';
import './MapView.css';

interface MapViewProps {
  data: CityWeatherResult[];
  metric: string;
  unit: string;
}

/**
 * Calculate color based on value position in min-max range
 * Blue (cold/low) → Green (mid) → Red (hot/high)
 */
const getMarkerColor = (value: number, min: number, max: number): string => {
  if (max === min) return '#3388ff';

  const normalized = (value - min) / (max - min);

  // Color scale: blue → cyan → green → yellow → red
  if (normalized < 0.25) {
    return '#2166ac'; // Blue
  } else if (normalized < 0.5) {
    return '#67a9cf'; // Cyan
  } else if (normalized < 0.75) {
    return '#fdae61'; // Orange
  }
  return '#d73027'; // Red
};

/**
 * Calculate marker radius based on value (larger = more extreme)
 */
const getMarkerRadius = (value: number, min: number, max: number): number => {
  if (max === min) return 10;
  const normalized = (value - min) / (max - min);
  return 8 + normalized * 12; // Range: 8-20px
};

/**
 * Format metric name for display
 */
const formatMetricName = (metric: string): string => {
  return metric
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
};

/**
 * Format value with unit
 */
const formatValue = (value: number | null | undefined, unit: string): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }
  return `${value.toFixed(1)}${unit}`;
};

const MapView: React.FC<MapViewProps> = ({ data, metric, unit }) => {
  // Filter valid data points with coordinates
  const validData = useMemo(() => {
    return data.filter(d =>
      d.latitude !== null &&
      d.latitude !== undefined &&
      d.longitude !== null &&
      d.longitude !== undefined &&
      !isNaN(d.latitude) &&
      !isNaN(d.longitude)
    );
  }, [data]);

  // Calculate min/max for color scale
  const { minValue, maxValue, center } = useMemo(() => {
    if (validData.length === 0) {
      return { minValue: 0, maxValue: 100, center: { lat: 47.5, lng: 19.0 } };
    }

    const values = validData.map(d => d.value).filter(v => v !== null && !isNaN(v));
    const min = Math.min(...values);
    const max = Math.max(...values);

    // Calculate center from all markers
    const avgLat = validData.reduce((sum, d) => sum + d.latitude, 0) / validData.length;
    const avgLng = validData.reduce((sum, d) => sum + d.longitude, 0) / validData.length;

    return {
      minValue: min,
      maxValue: max,
      center: { lat: avgLat, lng: avgLng }
    };
  }, [validData]);

  // Empty state
  if (validData.length === 0) {
    return (
      <div className="mapview-empty">
        <p>No cities with valid coordinates available for map display.</p>
      </div>
    );
  }

  return (
    <div className="mapview-container">
      <div className="mapview-header">
        <h3>Weather Map: {formatMetricName(metric)}</h3>
        <div className="mapview-legend">
          <span className="legend-label">Low</span>
          <div className="legend-gradient"></div>
          <span className="legend-label">High</span>
          <span className="legend-values">
            ({formatValue(minValue, unit)} - {formatValue(maxValue, unit)})
          </span>
        </div>
      </div>

      <MapContainer
        center={[center.lat, center.lng]}
        zoom={4}
        className="mapview-map"
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {validData.map((city, index) => {
          const color = getMarkerColor(city.value, minValue, maxValue);
          const radius = getMarkerRadius(city.value, minValue, maxValue);

          return (
            <CircleMarker
              key={`${city.city_name}-${city.date}-${index}`}
              center={[city.latitude, city.longitude]}
              radius={radius}
              fillColor={color}
              color="#fff"
              weight={2}
              opacity={1}
              fillOpacity={0.8}
            >
              <Tooltip direction="top" offset={[0, -10]} permanent={false}>
                <strong>{city.city_name}</strong>
                <br />
                {formatValue(city.value, unit)}
              </Tooltip>
              <Popup>
                <div className="marker-popup">
                  <h4>{city.city_name}</h4>
                  <p className="popup-country">{city.country}</p>
                  <p className="popup-value">
                    <strong>{formatMetricName(metric)}:</strong> {formatValue(city.value, unit)}
                  </p>
                  <p className="popup-date">
                    <strong>Date:</strong> {city.date}
                  </p>
                  {city.rank && (
                    <p className="popup-rank">
                      <strong>Rank:</strong> #{city.rank}
                    </p>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      <div className="mapview-stats">
        <div className="stat-item">
          <span className="stat-label">Cities:</span>
          <span className="stat-value">{validData.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Min:</span>
          <span className="stat-value">{formatValue(minValue, unit)}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Max:</span>
          <span className="stat-value">{formatValue(maxValue, unit)}</span>
        </div>
      </div>
    </div>
  );
};

export default MapView;
