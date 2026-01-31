import React from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import './WindChart.css';

interface WindDataPoint {
  date: string;
  windspeed: number | null;
  windgusts: number | null;
}

interface WindChartProps {
  data: WindDataPoint[];
  city: string;
}

const WindChart: React.FC<WindChartProps> = ({ data, city }) => {
  console.log('🔍 DEBUG WindChart: received data', data);
  
  if (!data || data.length === 0) {
    return (
      <div className="wind-chart-empty">
        <p>No wind data available for visualization</p>
      </div>
    );
  }

  // Filter out invalid data points and sort by date
  const chartData = data
    .filter((point) => point.windspeed !== null || point.windgusts !== null)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  console.log('🔍 DEBUG WindChart: filtered chartData', chartData);
  
  if (chartData.length === 0) {
    return (
      <div className="wind-chart-empty">
        <p>No valid wind data available</p>
      </div>
    );
  }

  // Calculate statistics
  const avgSpeed = chartData
    .filter((d) => d.windspeed !== null)
    .reduce((sum, d) => sum + (d.windspeed || 0), 0) / chartData.length;

  const maxGust = Math.max(...chartData.map((d) => d.windgusts || 0));

  return (
    <div className="wind-chart">
      <div className="chart-header">
        <h3>💨 Wind Analysis</h3>
        <p className="chart-subtitle">
          Wind speed and gusts for {city} • {chartData.length} days
        </p>
        <div className="chart-stats">
          <div className="stat-item">
            <span className="stat-label">Avg Speed:</span>
            <span className="stat-value">{avgSpeed.toFixed(1)} km/h</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Max Gust:</span>
            <span className="stat-value">{maxGust.toFixed(1)} km/h</span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={450}>
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fill: '#374151', fontSize: 11 }}
          />
          <YAxis
            label={{
              value: 'Wind Speed (km/h)',
              angle: -90,
              position: 'insideLeft',
              style: { fill: '#374151', fontWeight: 600 },
            }}
            tick={{ fill: '#374151', fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '2px solid #3b82f6',
              borderRadius: '8px',
              padding: '12px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            }}
            formatter={(value: number, name: string) => {
              const label = name === 'windspeed' ? 'Avg Speed' : 'Max Gust';
              return [`${value.toFixed(1)} km/h`, label];
            }}
          />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          <Bar
            dataKey="windgusts"
            fill="#93c5fd"
            fillOpacity={0.6}
            radius={[4, 4, 0, 0]}
            name="Wind Gusts"
          />
          <Line
            type="monotone"
            dataKey="windspeed"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ r: 4, fill: '#3b82f6' }}
            activeDot={{ r: 6, fill: '#2563eb' }}
            name="Wind Speed"
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="chart-legend-info">
        <div className="legend-item">
          <span className="legend-marker legend-line"></span>
          <span className="legend-text">Wind Speed (sustained average)</span>
        </div>
        <div className="legend-item">
          <span className="legend-marker legend-bar"></span>
          <span className="legend-text">Wind Gusts (peak speeds)</span>
        </div>
      </div>
    </div>
  );
};

export default WindChart;
