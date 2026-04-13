import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import './PrecipitationChart.css';

interface PrecipitationDataPoint {
  date: string;
  precipitation: number | null;
}

interface PrecipitationChartProps {
  data: PrecipitationDataPoint[];
  city: string;
}

const PrecipitationChart: React.FC<PrecipitationChartProps> = ({ data, city }) => {
  if (!data || data.length === 0) {
    return (
      <div className="precipitation-chart-empty">
        <p>No precipitation data available for visualization</p>
      </div>
    );
  }

  // Filter out null values and sort by date
  const chartData = data
    .map((point) => ({
      ...point,
      precipitation: point.precipitation || 0,
    }))
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  // Calculate statistics
  const totalPrecipitation = chartData.reduce((sum, d) => sum + d.precipitation, 0);
  const rainyDays = chartData.filter((d) => d.precipitation > 0.1).length;
  const maxPrecipitation = Math.max(...chartData.map((d) => d.precipitation));
  const avgPrecipitation = totalPrecipitation / chartData.length;


  return (
    <div className="precipitation-chart">
      <div className="chart-header">
        <h3>🌧️ Precipitation Analysis</h3>
        <p className="chart-subtitle">
          Daily precipitation for {city} • {chartData.length} days
        </p>
        <div className="chart-stats">
          <div className="stat-item">
            <span className="stat-label">Total:</span>
            <span className="stat-value stat-total">{totalPrecipitation.toFixed(1)} mm</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Rainy Days:</span>
            <span className="stat-value stat-rainy">{rainyDays} days</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Max Daily:</span>
            <span className="stat-value stat-max">{maxPrecipitation.toFixed(1)} mm</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Daily Avg:</span>
            <span className="stat-value stat-avg">{avgPrecipitation.toFixed(1)} mm</span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={450}>
        <BarChart
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
              value: 'Precipitation (mm)',
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
            formatter={(value: number) => [`${value.toFixed(1)} mm`, 'Precipitation']}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Legend wrapperStyle={{ paddingTop: '20px' }} />
          <ReferenceLine
            y={avgPrecipitation}
            stroke="#f59e0b"
            strokeDasharray="5 5"
            strokeWidth={2}
            label={{
              value: 'Average',
              position: 'right',
              fill: '#f59e0b',
              fontSize: 12,
              fontWeight: 600,
            }}
          />
          <Bar
            dataKey="precipitation"
            fill="#3b82f6"
            radius={[4, 4, 0, 0]}
            name="Daily Precipitation"
          />
        </BarChart>
      </ResponsiveContainer>

      <div className="precipitation-scale">
        <h4>Precipitation Scale</h4>
        <div className="scale-items">
          <div className="scale-item">
            <span className="scale-marker" style={{ background: '#e5e7eb' }}></span>
            <span className="scale-text">None (0 mm)</span>
          </div>
          <div className="scale-item">
            <span className="scale-marker" style={{ background: '#93c5fd' }}></span>
            <span className="scale-text">Light (&lt; 5 mm)</span>
          </div>
          <div className="scale-item">
            <span className="scale-marker" style={{ background: '#3b82f6' }}></span>
            <span className="scale-text">Moderate (5-15 mm)</span>
          </div>
          <div className="scale-item">
            <span className="scale-marker" style={{ background: '#1d4ed8' }}></span>
            <span className="scale-text">Heavy (15-30 mm)</span>
          </div>
          <div className="scale-item">
            <span className="scale-marker" style={{ background: '#1e3a8a' }}></span>
            <span className="scale-text">Very Heavy (&gt; 30 mm)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrecipitationChart;
