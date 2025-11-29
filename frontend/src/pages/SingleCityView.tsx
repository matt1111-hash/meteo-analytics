import React, { useState, useMemo } from 'react';
import axios from 'axios';
import MetricSelector from '../components/MetricSelector';
import CitySelector from '../components/CitySelector';
import TimeSeriesChart from '../components/TimeSeriesChart';
import WindChart from '../components/WindChart';
import PrecipitationChart from '../components/PrecipitationChart';
import MapView from '../components/MapView';
import { CityWeatherResult } from '../types/weather';
import './SingleCityView.css';

type ViewTab = 'chart' | 'map';

const API_BASE_URL = 'http://localhost:8001';

interface SingleCityFormData {
  city: string;
  startDate: string;
  endDate: string;
  metric: string;
}

const SingleCityView: React.FC = () => {
  const [formData, setFormData] = useState<SingleCityFormData>({
    city: '',
    startDate: '',
    endDate: '',
    metric: 'temperature_2m_max',
  });

  const [results, setResults] = useState<CityWeatherResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [metricInfo, setMetricInfo] = useState<{ name: string; unit: string }>({
    name: 'Temperature',
    unit: '°C',
  });
  const [viewMode, setViewMode] = useState<'simple' | 'detailed'>('simple');
  const [detailedData, setDetailedData] = useState<{
    wind: Array<{ date: string; windspeed: number | null; windgusts: number | null }>;
    precipitation: Array<{ date: string; precipitation: number | null }>;
  } | null>(null);
  const [activeTab, setActiveTab] = useState<ViewTab>('chart');

  // CSV Export handler
  const handleExportCSV = (): void => {
    if (results.length === 0) return;

    // Build CSV content
    const headers = ['date', 'metric', 'value', 'city'];
    const rows = results.map((r) => [
      r.date,
      formData.metric,
      r.value?.toString() ?? '',
      r.city_name,
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    // Filename: {city}_{metric}_{startDate}_{endDate}.csv
    const sanitizedCity = formData.city.replace(/[^a-zA-Z0-9]/g, '_');
    const filename = `${sanitizedCity}_${formData.metric}_${formData.startDate}_${formData.endDate}.csv`;

    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Aggregate time series data to single point for map view
  const mapData = useMemo((): CityWeatherResult[] => {
    if (results.length === 0) return [];
    const first = results[0];
    const validValues = results.map(r => r.value).filter(v => v !== null && !isNaN(v));
    const avgValue = validValues.length > 0
      ? validValues.reduce((sum, v) => sum + v, 0) / validValues.length
      : 0;
    return [{
      ...first,
      value: avgValue,
      date: `${formData.startDate} - ${formData.endDate}`,
    }];
  }, [results, formData.startDate, formData.endDate]);

  const handleChange = (field: keyof SingleCityFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleMetricChange = (metric: string) => {
    handleChange('metric', metric);

    // Update metric info for chart (simplified mapping)
    const metricMap: Record<string, { name: string; unit: string }> = {
      temperature_2m_max: { name: 'Maximum Temperature', unit: '°C' },
      temperature_2m_min: { name: 'Minimum Temperature', unit: '°C' },
      temperature_2m_mean: { name: 'Mean Temperature', unit: '°C' },
      precipitation_sum: { name: 'Precipitation', unit: 'mm' },
      windspeed_10m_max: { name: 'Wind Speed', unit: 'km/h' },
      windgusts_10m_max: { name: 'Wind Gusts', unit: 'km/h' },
      temperature_range: { name: 'Temperature Range', unit: '°C' },
    };

    setMetricInfo(metricMap[metric] || { name: metric, unit: '' });
  };

  const validateForm = (): string | null => {
    if (!formData.city.trim()) {
      return 'Please enter a city name';
    }
    if (!formData.startDate) {
      return 'Please select a start date';
    }
    if (!formData.endDate) {
      return 'Please select an end date';
    }
    if (!formData.metric) {
      return 'Please select a metric';
    }
    if (formData.startDate > formData.endDate) {
      return 'Start date must be before end date';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (viewMode === 'simple') {
        // Simple view: fetch single metric
        const response = await axios.post<{
          city_results: CityWeatherResult[];
          [key: string]: unknown;
        }>(`${API_BASE_URL}/api/weather/single-city`, {
          city: formData.city.trim(),
          start: formData.startDate,
          end: formData.endDate,
          metric: formData.metric,
        });

        setResults(response.data.city_results);
        setDetailedData(null);
      } else {
        // Detailed view: fetch all metrics
        const response = await axios.post<{
          temperature_data: CityWeatherResult[];
          wind_data: CityWeatherResult[];
          wind_gusts_data: CityWeatherResult[];
          precipitation_data: CityWeatherResult[];
          [key: string]: unknown;
        }>(`${API_BASE_URL}/api/weather/single-city-detailed`, {
          city: formData.city.trim(),
          start: formData.startDate,
          end: formData.endDate,
        });

        // Transform data for charts
        const windData = response.data.wind_data.map((item: CityWeatherResult, idx: number) => ({
          date: item.date,
          windspeed: item.value,
          windgusts: response.data.wind_gusts_data[idx]?.value || null,
        }));

        const precipData = response.data.precipitation_data.map((item: CityWeatherResult) => ({
          date: item.date,
          precipitation: item.value,
        }));

        setResults(response.data.temperature_data);
        setDetailedData({
          wind: windData,
          precipitation: precipData,
        });
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError('An unexpected error occurred');
      }
      setResults([]);
      setDetailedData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="single-city-view">
      <div className="view-header">
        <h1>📍 Single City Time Series</h1>
        <p className="view-subtitle">Analyze weather trends for a specific city over time</p>
      </div>

      <div className="view-content">
        <form className="single-city-form" onSubmit={handleSubmit}>
          <div className="view-mode-toggle">
            <button
              type="button"
              onClick={() => setViewMode('simple')}
              className={`toggle-btn ${viewMode === 'simple' ? 'active' : ''}`}
              disabled={loading}
            >
              📊 Simple View
            </button>
            <button
              type="button"
              onClick={() => setViewMode('detailed')}
              className={`toggle-btn ${viewMode === 'detailed' ? 'active' : ''}`}
              disabled={loading}
            >
              📈 Detailed Analysis
            </button>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <CitySelector
                id="city-input"
                value={formData.city}
                onChange={(city) => handleChange('city', city)}
                disabled={loading}
                label="Város"
              />
            </div>

            <div className="form-group">
              <label htmlFor="start-date">Start Date</label>
              <input
                id="start-date"
                type="date"
                value={formData.startDate}
                onChange={(e) => handleChange('startDate', e.target.value)}
                disabled={loading}
                className="form-input bg-white text-gray-900"
                style={{ color: '#1f2937' }}
              />
            </div>

            <div className="form-group">
              <label htmlFor="end-date">End Date</label>
              <input
                id="end-date"
                type="date"
                value={formData.endDate}
                onChange={(e) => handleChange('endDate', e.target.value)}
                disabled={loading}
                className="form-input bg-white text-gray-900"
                style={{ color: '#1f2937' }}
              />
            </div>
          </div>

          {viewMode === 'simple' && (
            <MetricSelector
              selectedMetric={formData.metric}
              onMetricChange={handleMetricChange}
              disabled={loading}
            />
          )}

          {viewMode === 'detailed' && (
            <div className="detailed-info">
              <p className="info-text">
                Detailed analysis includes temperature, wind (speed & gusts), and precipitation charts
              </p>
            </div>
          )}

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? '⏳ Loading...' : viewMode === 'simple' ? '🔍 Analyze Weather Data' : '📊 Run Detailed Analysis'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {results.length > 0 && viewMode === 'simple' && (
          <div className="results-section">
            <div className="results-header">
              <div className="tab-selector">
                <button
                  className={`tab-btn ${activeTab === 'chart' ? 'active' : ''}`}
                  onClick={() => setActiveTab('chart')}
                >
                  📊 Chart
                </button>
                <button
                  className={`tab-btn ${activeTab === 'map' ? 'active' : ''}`}
                  onClick={() => setActiveTab('map')}
                >
                  🗺️ Map
                </button>
              </div>
              <button
                className="export-csv-btn"
                onClick={handleExportCSV}
                title="Export data to CSV"
              >
                ⬇️ Export CSV
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'chart' && (
                <TimeSeriesChart
                  data={results}
                  metric={formData.metric}
                  metricName={metricInfo.name}
                  metricUnit={metricInfo.unit}
                />
              )}

              {activeTab === 'map' && (
                <MapView
                  data={mapData}
                  metric={formData.metric}
                  unit={metricInfo.unit}
                />
              )}
            </div>
          </div>
        )}

        {results.length > 0 && viewMode === 'detailed' && detailedData && (
          <div className="detailed-results">
            <div className="detailed-results-header">
              <h3>Detailed Analysis Results</h3>
              <button
                className="export-csv-btn"
                onClick={handleExportCSV}
                title="Export temperature data to CSV"
              >
                ⬇️ Export CSV
              </button>
            </div>
            <TimeSeriesChart
              data={results}
              metric="temperature_2m_mean"
              metricName="Mean Temperature"
              metricUnit="°C"
            />
            <WindChart
              data={detailedData.wind}
              city={formData.city}
            />
            <PrecipitationChart
              data={detailedData.precipitation}
              city={formData.city}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default SingleCityView;
