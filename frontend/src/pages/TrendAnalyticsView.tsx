/**
 * TrendAnalyticsView - Climate trend analysis with KPI dashboard
 *
 * Features:
 * - Location selector with autocomplete
 * - Time period selector (5/10/25/55 years)
 * - Metric selector dropdown
 * - Trend chart with linear regression
 * - Export functionality (Excel, JSON, PNG)
 */
import React, { useState } from 'react';
import CityAutocomplete from '../components/common/CityAutocomplete';
import TrendChart from '../components/charts/TrendChart';
import { useTrendAnalytics } from '../hooks/useTrendAnalytics';
import { TIME_PERIODS, METRIC_LABELS, METRIC_UNITS, TrendMetric } from '../services/trendService';
import './TrendAnalyticsView.css';

const TrendAnalyticsView: React.FC = () => {
  // State
  const [city, setCity] = useState<string>('Budapest');
  const [metric, setMetric] = useState<TrendMetric>('temperature_2m_max');
  const [selectedPeriod, setSelectedPeriod] = useState<number>(10);

  // Hook
  const { data, loading, error, fetchTrendData, resetData } = useTrendAnalytics();

  // Handle analysis trigger
  const handleAnalyze = () => {
    fetchTrendData({
      location: city,
      metric,
      time_periods: [...TIME_PERIODS],
    });
  };

  // Handle city change
  const handleCityChange = (newCity: string) => {
    setCity(newCity);
    resetData();
  };

  // Handle metric change
  const handleMetricChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setMetric(e.target.value as TrendMetric);
    resetData();
  };

  // Export functions
  const handleExportJSON = () => {
    if (!data) return;

    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trend_${city}_${metric}_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    if (!data || !data.periods.length) return;

    const selectedPeriodData = data.periods.find((p) => p.time_period === selectedPeriod);
    if (!selectedPeriodData) return;

    // CSV header
    let csv = 'Year,Value,Trend\n';

    // CSV rows
    selectedPeriodData.years.forEach((year, index) => {
      const value = selectedPeriodData.yearly_means[index] || 0;
      const trend = selectedPeriodData.intercept + selectedPeriodData.slope * index * 12;
      csv += `${year},${value.toFixed(3)},${trend.toFixed(3)}\n`;
    });

    // Statistics
    csv += `\nMetric,${data.metric}\n`;
    csv += `Location,${data.location_name}\n`;
    csv += `Period,${selectedPeriodData.time_period} years\n`;
    csv += `Slope per decade,${selectedPeriodData.slope_per_decade}\n`;
    csv += `R²,${selectedPeriodData.r_squared}\n`;
    csv += `p-value,${selectedPeriodData.p_value}\n`;
    csv += `Trend direction,${selectedPeriodData.trend_direction}\n`;
    csv += `Significance,${selectedPeriodData.significance}\n`;

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trend_${city}_${metric}_${selectedPeriod}y_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportPNG = () => {
    const chartElement = document.querySelector('.trend-chart-container');
    if (!chartElement) return;

    // Simple HTML-to-image approach using canvas would go here
    // For now, show a message
    alert('PNG export feature: Chart image export implementation pending');
  };

  return (
    <div className="trend-analytics-view">
      {/* Header */}
      <div className="trend-header">
        <h1>📈 Trend Analytics</h1>
        <p>Linear regression trend analysis with statistical significance testing</p>
      </div>

      {/* Controls */}
      <div className="trend-controls">
        <div className="control-group">
          <label htmlFor="city-select">Helyszín:</label>
          <CityAutocomplete value={city} onChange={handleCityChange} placeholder="Város neve..." />
        </div>

        <div className="control-group">
          <label htmlFor="metric-select">Mutató:</label>
          <select
            id="metric-select"
            value={metric}
            onChange={handleMetricChange}
            className="metric-select"
          >
            {(Object.keys(METRIC_LABELS) as TrendMetric[]).map((key) => (
              <option key={key} value={key}>
                {METRIC_LABELS[key]}
              </option>
            ))}
          </select>
        </div>

        <button onClick={handleAnalyze} className="analyze-button" disabled={loading || !city}>
          {loading ? 'Betöltés...' : '📊 Elemzés indítása'}
        </button>

        {data && (
          <div className="export-buttons">
            <button onClick={handleExportCSV} className="export-button csv">
              📄 CSV
            </button>
            <button onClick={handleExportJSON} className="export-button json">
              📋 JSON
            </button>
            <button onClick={handleExportPNG} className="export-button png">
              🖼️ PNG
            </button>
          </div>
        )}
      </div>

      {/* Chart */}
      <TrendChart
        location={city}
        metric={metric}
        periods={data?.periods || []}
        selectedPeriod={selectedPeriod}
        onPeriodChange={setSelectedPeriod}
        loading={loading}
        error={error}
      />

      {/* Statistics Table */}
      {data && data.periods.length > 0 && (
        <div className="trend-statistics-table">
          <h3>📊 Összesítő statisztika</h3>
          <table>
            <thead>
              <tr>
                <th>Időszak</th>
                <th>Trend/évtized</th>
                <th>R²</th>
                <th>p-érték</th>
                <th>Irány</th>
                <th>Szignifikancia</th>
              </tr>
            </thead>
            <tbody>
              {data.periods.map((period) => (
                <tr
                  key={period.time_period}
                  className={period.time_period === selectedPeriod ? 'active-row' : ''}
                  onClick={() => setSelectedPeriod(period.time_period)}
                >
                  <td>{period.time_period} év</td>
                  <td>
                    {period.slope_per_decade.toFixed(3)} {METRIC_UNITS[metric]}
                  </td>
                  <td>{period.r_squared.toFixed(4)}</td>
                  <td>{period.p_value.toFixed(6)}</td>
                  <td>
                    {period.trend_direction === 'increasing'
                      ? '↗ Növekvő'
                      : period.trend_direction === 'decreasing'
                        ? '↘ Csökkenő'
                        : '→ Stabil'}
                  </td>
                  <td>
                    {period.significance === 'highly_significant'
                      ? 'Nagyon szignifikáns'
                      : period.significance === 'significant'
                        ? 'Szignifikáns'
                        : period.significance === 'moderately_significant'
                          ? 'Mérsékelten'
                          : 'Nem szignifikáns'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TrendAnalyticsView;
