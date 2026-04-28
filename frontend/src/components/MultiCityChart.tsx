import React, { useState, useCallback } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { CityWeatherResult } from '../types/weather';
import './MultiCityChart.css';

interface MultiCityChartProps {
  data: CityWeatherResult[];
  aggregate: boolean;
  metricName: string;
  metricUnit: string;
}

const CITY_COLORS = [
  '#3b82f6', // blue
  '#ef4444', // red
  '#10b981', // green
  '#f59e0b', // amber
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#84cc16', // lime
];

const MultiCityChart: React.FC<MultiCityChartProps> = ({
  data,
  aggregate,
  metricName,
  metricUnit,
}) => {
  // Track which cities are visible (all visible by default)
  const [hiddenCities, setHiddenCities] = useState<Set<string>>(new Set());

  // Toggle city visibility
  const handleLegendClick = useCallback((cityName: string) => {
    setHiddenCities((prev) => {
      const next = new Set(prev);
      if (next.has(cityName)) {
        next.delete(cityName);
      } else {
        next.add(cityName);
      }
      return next;
    });
  }, []);

  if (!data || data.length === 0) {
    return (
      <div className="chart-empty">
        <p>No data available for chart visualization</p>
      </div>
    );
  }

  // Aggregate mode: Bar chart with cities on X-axis
  if (aggregate) {
    const chartData = data.map((result) => ({
      city: result.city_name,
      value: result.value,
      country: result.country_code,
    }));

    return (
      <div className="multi-city-chart">
        <div className="chart-header">
          <h3>📊 City Comparison</h3>
          <p className="chart-subtitle">
            {metricName} across {data.length} {data.length === 1 ? 'city' : 'cities'}
          </p>
        </div>

        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="city"
              angle={-45}
              textAnchor="end"
              height={80}
              tick={{ fill: '#374151', fontSize: 12 }}
            />
            <YAxis
              label={{
                value: metricUnit,
                angle: -90,
                position: 'insideLeft',
                style: { fill: '#374151' },
              }}
              tick={{ fill: '#374151', fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '12px',
              }}
              formatter={(value) => [`${Number(value).toFixed(1)} ${metricUnit}`, metricName]}
            />
            <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // Non-aggregate mode: Line chart with dates on X-axis, multiple lines for cities
  const cities = Array.from(new Set(data.map((r) => r.city_name)));
  const dates = Array.from(new Set(data.map((r) => r.date))).sort();

  // Transform data for multi-line chart
  const chartData = dates.map((date) => {
    const dataPoint: { date: string; [key: string]: string | number | null } = { date };
    cities.forEach((city) => {
      const result = data.find((r) => r.city_name === city && r.date === date);
      dataPoint[city] = result ? result.value : null;
    });
    return dataPoint;
  });

  // Custom legend renderer with click handlers
  const renderLegend = () => (
    <div className="custom-legend">
      {cities.map((city, index) => {
        const isHidden = hiddenCities.has(city);
        const color = CITY_COLORS[index % CITY_COLORS.length];
        return (
          <button
            key={city}
            type="button"
            className={`legend-item ${isHidden ? 'legend-item--hidden' : ''}`}
            onClick={() => handleLegendClick(city)}
            style={
              {
                '--legend-color': color,
              } as React.CSSProperties
            }
          >
            <span
              className="legend-color"
              style={{ backgroundColor: isHidden ? '#d1d5db' : color }}
            />
            <span className={`legend-label ${isHidden ? 'legend-label--hidden' : ''}`}>{city}</span>
          </button>
        );
      })}
    </div>
  );

  return (
    <div className="multi-city-chart">
      <div className="chart-header">
        <h3>📈 Time Series Comparison</h3>
        <p className="chart-subtitle">
          {metricName} over {dates.length} days • {cities.length}{' '}
          {cities.length === 1 ? 'city' : 'cities'}
        </p>
        <p className="chart-hint">Kattints a város nevére a vonal elrejtéséhez/megjelenítéséhez</p>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#374151', fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            label={{
              value: metricUnit,
              angle: -90,
              position: 'insideLeft',
              style: { fill: '#374151' },
            }}
            tick={{ fill: '#374151', fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '12px',
            }}
          />
          <Legend content={renderLegend} />
          {cities.map((city, index) => (
            <Line
              key={city}
              type="monotone"
              dataKey={city}
              stroke={CITY_COLORS[index % CITY_COLORS.length]}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name={city}
              hide={hiddenCities.has(city)}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MultiCityChart;
