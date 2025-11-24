import React from 'react';
import {
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
import './TimeSeriesChart.css';

interface TimeSeriesChartProps {
  data: CityWeatherResult[];
  metric: string;
  metricName?: string;
  metricUnit?: string;
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({
  data,
  metric,
  metricName = metric,
  metricUnit = '',
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="time-series-chart">
        <div className="chart-empty-state">
          <p>📊 No data available for chart</p>
        </div>
      </div>
    );
  }

  // Transform data for Recharts format
  const chartData = data.map((item) => ({
    date: item.date,
    value: item.value,
    city: item.city_name,
  }));

  // Sort by date to ensure proper time series order
  chartData.sort((a, b) => a.date.localeCompare(b.date));

  return (
    <div className="time-series-chart">
      <div className="chart-header">
        <h3 className="chart-title">
          📈 {metricName} Time Series
        </h3>
        {data[0]?.city_name && (
          <p className="chart-subtitle">
            {data[0].city_name}, {data[0].country}
          </p>
        )}
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => {
              // Format date to MM/DD
              const date = new Date(value);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            label={{
              value: metricUnit,
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 14 },
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #e0e7ff',
              borderRadius: '8px',
              padding: '12px',
            }}
            labelFormatter={(value) => {
              // Format date to readable format
              const date = new Date(value);
              return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              });
            }}
            formatter={(value: number) => [
              `${value.toFixed(1)} ${metricUnit}`,
              metricName,
            ]}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#6366f1"
            strokeWidth={2}
            dot={{ fill: '#6366f1', r: 4 }}
            activeDot={{ r: 6 }}
            name={metricName}
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="chart-stats">
        <div className="stat-item">
          <span className="stat-label">Data Points:</span>
          <span className="stat-value">{chartData.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Min:</span>
          <span className="stat-value">
            {Math.min(...chartData.map((d) => d.value)).toFixed(1)} {metricUnit}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Max:</span>
          <span className="stat-value">
            {Math.max(...chartData.map((d) => d.value)).toFixed(1)} {metricUnit}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Average:</span>
          <span className="stat-value">
            {(
              chartData.reduce((sum, d) => sum + d.value, 0) / chartData.length
            ).toFixed(1)}{' '}
            {metricUnit}
          </span>
        </div>
      </div>
    </div>
  );
};

export default TimeSeriesChart;
