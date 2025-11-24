import React from 'react';
import { CityWeatherResult } from '../types/weather';
import './HeatmapChart.css';

interface HeatmapChartProps {
  data: CityWeatherResult[];
  metric: string;
  unit: string;
}

interface HeatmapCell {
  value: number | null;
  date: string;
}

interface CityRow {
  cityName: string;
  cells: HeatmapCell[];
}

const HeatmapChart: React.FC<HeatmapChartProps> = ({ data, metric, unit }) => {
  // Extract unique dates and sort them
  const uniqueDates = Array.from(new Set(data.map(d => d.date))).sort();

  // Extract unique cities
  const uniqueCities = Array.from(new Set(data.map(d => d.city_name)));

  // Build matrix: cities × dates
  const matrix: CityRow[] = uniqueCities.map(cityName => {
    const cells: HeatmapCell[] = uniqueDates.map(date => {
      const result = data.find(d => d.city_name === cityName && d.date === date);
      return {
        value: result ? result.value : null,
        date: date
      };
    });
    return { cityName, cells };
  });

  // Calculate min/max for color scale
  const values = data.map(d => d.value).filter(v => v !== null && !isNaN(v));
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);

  // Color scale function: min (blue) → max (red)
  const getColor = (value: number | null): string => {
    if (value === null || isNaN(value)) return '#f0f0f0'; // Gray for missing data

    const normalized = (value - minValue) / (maxValue - minValue);

    // 5-tier color scale: blue → cyan → green → yellow → orange → red
    if (normalized < 0.2) return `rgba(33, 102, 172, ${0.5 + normalized * 2.5})`; // Blue
    if (normalized < 0.4) return `rgba(103, 169, 207, ${0.5 + (normalized - 0.2) * 2.5})`; // Cyan
    if (normalized < 0.6) return `rgba(209, 229, 240, ${0.5 + (normalized - 0.4) * 2.5})`; // Light blue
    if (normalized < 0.8) return `rgba(253, 219, 199, ${0.5 + (normalized - 0.6) * 2.5})`; // Light orange
    return `rgba(239, 101, 72, ${0.5 + (normalized - 0.8) * 2.5})`; // Red
  };

  // Format date for display (Nov 1, Nov 2, etc.)
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Format value with unit
  const formatValue = (value: number | null): string => {
    if (value === null || isNaN(value)) return 'N/A';
    return `${value.toFixed(1)}${unit}`;
  };

  if (data.length === 0) {
    return <div className="heatmap-empty">No data available for heatmap</div>;
  }

  return (
    <div className="heatmap-container">
      <div className="heatmap-header">
        <h3>Weather Heatmap: {metric.replace(/_/g, ' ')}</h3>
        <div className="heatmap-legend">
          <span className="legend-label">Low</span>
          <div className="legend-gradient"></div>
          <span className="legend-label">High</span>
          <span className="legend-values">({minValue.toFixed(1)} - {maxValue.toFixed(1)}{unit})</span>
        </div>
      </div>

      <div className="heatmap-scroll">
        <table className="heatmap-table">
          <thead>
            <tr>
              <th className="city-header">City</th>
              {uniqueDates.map(date => (
                <th key={date} className="date-header">{formatDate(date)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrix.map((row, rowIdx) => (
              <tr key={rowIdx}>
                <td className="city-cell">{row.cityName}</td>
                {row.cells.map((cell, cellIdx) => (
                  <td
                    key={cellIdx}
                    className="value-cell"
                    style={{ backgroundColor: getColor(cell.value) }}
                    title={`${row.cityName} - ${formatDate(cell.date)}: ${formatValue(cell.value)}`}
                  >
                    {formatValue(cell.value)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="heatmap-stats">
        <div className="stat-item">
          <span className="stat-label">Cities:</span>
          <span className="stat-value">{uniqueCities.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Days:</span>
          <span className="stat-value">{uniqueDates.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Data Points:</span>
          <span className="stat-value">{data.length}</span>
        </div>
      </div>
    </div>
  );
};

export default HeatmapChart;
