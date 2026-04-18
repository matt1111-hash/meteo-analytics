import React, { useState } from 'react';
import axios from 'axios';
import apiClient from '../services/apiClient';
import WeatherForm from '../components/WeatherForm';
import WeatherResults from '../components/WeatherResults';
import MetricSelector from '../components/MetricSelector';
import MultiCityChart from '../components/MultiCityChart';
import HeatmapChart from '../components/HeatmapChart';
import MapView from '../components/MapView';
import { WeatherAnalysisRequest, WeatherAnalysisResponse } from '../types/weather';
import './MultiCityView.css';

type ViewTab = 'chart' | 'heatmap' | 'map';

const MultiCityView: React.FC = () => {
  const [results, setResults] = useState<WeatherAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<string>('temperature_2m_max');
  const [aggregate, setAggregate] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<ViewTab>('chart');

  const handleMetricChange = (metric: string) => {
    setSelectedMetric(metric);
  };

  const getMetricDisplayInfo = (metric: string) => {
    const metricInfo: Record<string, { name: string; unit: string }> = {
      temperature_2m_max: { name: 'Maximum Temperature', unit: '°C' },
      temperature_2m_min: { name: 'Minimum Temperature', unit: '°C' },
      temperature_2m_mean: { name: 'Mean Temperature', unit: '°C' },
      precipitation_sum: { name: 'Precipitation', unit: 'mm' },
      windspeed_10m_max: { name: 'Wind Speed', unit: 'km/h' },
      windgusts_10m_max: { name: 'Wind Gusts', unit: 'km/h' },
      temperature_range: { name: 'Temperature Range', unit: '°C' },
    };
    return metricInfo[metric] || { name: metric, unit: '' };
  };

  const handleAggregateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAggregate(e.target.checked);
  };

  const handleSubmit = async (request: WeatherAnalysisRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post<WeatherAnalysisResponse>(
        `/api/weather/multi-city?aggregate=${aggregate}`,
        {
          cities: request.cities,
          date_range: request.date_range,
          metric: selectedMetric,
        },
      );

      setResults(response.data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError('An unexpected error occurred');
      }
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="multi-city-view">
      <div className="view-header">
        <h1>🌍 Multi-City Comparison</h1>
        <p className="view-subtitle">Compare weather data across multiple cities</p>
      </div>

      <div className="view-content">
        <div className="form-section">
          <div className="options-section">
            <MetricSelector
              selectedMetric={selectedMetric}
              onMetricChange={handleMetricChange}
              disabled={loading}
            />

            <div className="aggregate-control">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={aggregate}
                  onChange={handleAggregateChange}
                  disabled={loading}
                />
                <span>Aggregate multi-day data per city</span>
              </label>
              <p className="control-hint">
                {aggregate
                  ? 'Shows one aggregated value per city'
                  : 'Shows daily breakdown for each city'}
              </p>
            </div>
          </div>

          <WeatherForm onSubmit={handleSubmit} loading={loading} />
        </div>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {results && (
          <div className="results-section">
            <div className="tab-selector">
              <button
                className={`tab-btn ${activeTab === 'chart' ? 'active' : ''}`}
                onClick={() => setActiveTab('chart')}
              >
                📊 Chart
              </button>
              <button
                className={`tab-btn ${activeTab === 'heatmap' ? 'active' : ''}`}
                onClick={() => setActiveTab('heatmap')}
              >
                🔥 Heatmap
              </button>
              <button
                className={`tab-btn ${activeTab === 'map' ? 'active' : ''}`}
                onClick={() => setActiveTab('map')}
              >
                🗺️ Map
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'chart' && (
                <MultiCityChart
                  data={results.city_results}
                  aggregate={aggregate}
                  metricName={getMetricDisplayInfo(selectedMetric).name}
                  metricUnit={getMetricDisplayInfo(selectedMetric).unit}
                />
              )}

              {activeTab === 'heatmap' && (
                <HeatmapChart
                  data={results.city_results}
                  metric={selectedMetric}
                  unit={getMetricDisplayInfo(selectedMetric).unit}
                />
              )}

              {activeTab === 'map' && (
                <MapView
                  data={results.city_results}
                  metric={selectedMetric}
                  unit={getMetricDisplayInfo(selectedMetric).unit}
                />
              )}
            </div>

            <WeatherResults data={results} />
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiCityView;
