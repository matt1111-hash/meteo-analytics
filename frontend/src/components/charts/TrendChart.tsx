/**
 * TrendChart - Linear regression trend visualization
 * Displays trend lines with confidence intervals for multiple time periods
 */
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
import { TrendPeriodResult, METRIC_UNITS } from '../../services/trendService';

interface TrendChartProps {
  location: string;
  metric: string;
  periods: TrendPeriodResult[];
  selectedPeriod: number;
  onPeriodChange: (period: number) => void;
  loading?: boolean;
  error?: string | null;
}

interface ChartDataPoint {
  year: number;
  value: number;
  trend: number;
}

// KPI Card component for displaying statistics
const KPICard: React.FC<{
  label: string;
  value: string | number;
  unit?: string;
  color?: string;
}> = ({ label, value, unit = '', color = '#C43939' }) => (
  <div className="kpi-card" style={{ borderLeft: `4px solid ${color}` }}>
    <div className="kpi-label">{label}</div>
    <div className="kpi-value">
      {typeof value === 'number' ? value.toFixed(3) : value}
      {unit && <span className="kpi-unit"> {unit}</span>}
    </div>
  </div>
);

const TrendChart: React.FC<TrendChartProps> = ({
  location,
  metric,
  periods,
  selectedPeriod,
  onPeriodChange,
  loading = false,
  error = null,
}) => {
  // Get selected period data
  const selectedPeriodData = periods.find(p => p.time_period === selectedPeriod);

  // Prepare chart data
  const chartData: ChartDataPoint[] = React.useMemo(() => {
    if (!selectedPeriodData) return [];

    return selectedPeriodData.years.map((year, index) => ({
      year,
      value: selectedPeriodData.yearly_means[index] || 0,
      trend: selectedPeriodData.intercept +
             (selectedPeriodData.slope * index * 12), // Convert to monthly trend
    }));
  }, [selectedPeriodData]);

  // Determine trend direction color
  const getTrendColor = (): string => {
    if (!selectedPeriodData) return '#C43939';
    if (selectedPeriodData.trend_direction === 'increasing') return '#ef4444';
    if (selectedPeriodData.trend_direction === 'decreasing') return '#3b82f6';
    return '#9ca3af';
  };

  const trendColor = getTrendColor();

  // Get metric unit
  const getUnit = (): string => {
    const metricKey = metric as keyof typeof METRIC_UNITS;
    return METRIC_UNITS[metricKey] || '';
  };

  // Loading state
  if (loading) {
    return (
      <div className="trend-chart-container">
        <div className="chart-loading">
          <div className="spinner"></div>
          <p>Betöltés...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="trend-chart-container">
        <div className="chart-error">
          <p>❌ {error}</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (!periods || periods.length === 0 || !selectedPeriodData) {
    return (
      <div className="trend-chart-container">
        <div className="chart-empty">
          <p>📈 Trend Elemzés</p>
          <p className="text-sm text-gray-500">
            Válassz helyszínt és mutatót az analízis indításához
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="trend-chart-container">
      {/* Header with location and metric */}
      <div className="trend-chart-header">
        <h3>
          📈 {location} - {selectedPeriodData.time_period} éves trend
        </h3>
      </div>

      {/* KPI Dashboard */}
      <div className="trend-kpi-dashboard">
        <KPICard
          label="Trend/évtized"
          value={selectedPeriodData.slope_per_decade}
          unit={getUnit()}
          color={trendColor}
        />
        <KPICard
          label="R² (illesztés)"
          value={selectedPeriodData.r_squared}
          color="#10b981"
        />
        <KPICard
          label="p-érték"
          value={selectedPeriodData.p_value}
          color="#f59e0b"
        />
        <KPICard
          label="Irány"
          value={
            selectedPeriodData.trend_direction === 'increasing' ? '↗ Növekvő' :
            selectedPeriodData.trend_direction === 'decreasing' ? '↘ Csökkenő' :
            '→ Stabil'
          }
          color={trendColor}
        />
        <KPICard
          label="Szignifikancia"
          value={
            selectedPeriodData.significance === 'highly_significant' ? 'Nagyon szignifikáns' :
            selectedPeriodData.significance === 'significant' ? 'Szignifikáns' :
            selectedPeriodData.significance === 'moderately_significant' ? 'Mérsékelten' :
            'Nem szignifikáns'
          }
          color={
            selectedPeriodData.significance === 'not_significant' ? '#9ca3af' : '#8b5cf6'
          }
        />
      </div>

      {/* Period Selector */}
      <div className="trend-period-selector">
        {periods.map((period) => (
          <button
            key={period.time_period}
            className={`period-button ${period.time_period === selectedPeriod ? 'active' : ''}`}
            onClick={() => onPeriodChange(period.time_period)}
          >
            {period.time_period} év
          </button>
        ))}
      </div>

      {/* Chart */}
      <div className="trend-chart">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="year"
              stroke="#6b7280"
              label={{ value: 'Év', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              stroke="#6b7280"
              label={{ value: `${metric} (${getUnit()})`, angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
              }}
              formatter={(value: number, name: string) => [
                `${value.toFixed(2)} ${getUnit()}`,
                name === 'value' ? 'Mért érték' : 'Trendvonal',
              ]}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#6b7280"
              strokeWidth={2}
              dot={{ r: 4 }}
              name="Mért érték"
            />
            <Line
              type="monotone"
              dataKey="trend"
              stroke={trendColor}
              strokeWidth={3}
              dot={false}
              strokeDasharray="5 5"
              name="Trend"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Confidence Interval */}
      {selectedPeriodData.confidence_interval && (
        <div className="trend-confidence-interval">
          <small className="text-gray-500">
            95%-os konfidencia intervallum: ({selectedPeriodData.confidence_interval[0].toFixed(3)}, {selectedPeriodData.confidence_interval[1].toFixed(3)}) {getUnit()}
          </small>
        </div>
      )}
    </div>
  );
};

export default TrendChart;
