import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { CityWeatherResult, MetricsResponse } from '../types/weather';
import MetricSelector from '../components/MetricSelector';
import HeatmapChart from '../components/HeatmapChart';
import './HeatmapView.css';

// Quick preset city lists for heatmap
const HUNGARIAN_PRESET = 'Budapest, Debrecen, Szeged, Miskolc, Pécs, Győr';
const EUROPEAN_PRESET = 'Vienna, Prague, Bratislava, Zagreb, Berlin';

// Calculate dynamic default dates
const getDefaultDates = () => {
  const today = new Date();
  const thirtyDaysAgo = new Date(today);
  thirtyDaysAgo.setDate(today.getDate() - 30);
  return {
    start: thirtyDaysAgo.toISOString().split('T')[0],
    end: today.toISOString().split('T')[0],
  };
};

const HeatmapView: React.FC = () => {
  const defaultDates = getDefaultDates();
  const [cities, setCities] = useState<string>('Budapest, London, Paris, Berlin, Rome');
  const [startDate, setStartDate] = useState<string>(defaultDates.start);
  const [endDate, setEndDate] = useState<string>(defaultDates.end);
  const [selectedMetric, setSelectedMetric] = useState<string>('temperature_2m_max');
  const [metricUnit, setMetricUnit] = useState<string>('°C');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [heatmapData, setHeatmapData] = useState<CityWeatherResult[]>([]);
  const [metrics, setMetrics] = useState<Record<string, { name: string; unit: string; description: string }>>({});

  // Fetch metrics metadata on mount
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get<MetricsResponse>('http://localhost:8001/api/weather/metrics');
        setMetrics(response.data.metrics);
      } catch (err) {
        console.error('Failed to fetch metrics:', err);
      }
    };
    fetchMetrics();
  }, []);

  // Update unit when metric changes
  useEffect(() => {
    if (metrics[selectedMetric]) {
      setMetricUnit(metrics[selectedMetric].unit);
    }
  }, [selectedMetric, metrics]);

  const handleMetricChange = (metric: string) => {
    setSelectedMetric(metric);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setHeatmapData([]);

    try {
      const cityList = cities
        .split(',')
        .map(c => c.trim())
        .filter(c => c.length > 0);

      if (cityList.length === 0) {
        setError('Please enter at least one city');
        setLoading(false);
        return;
      }

      const response = await axios.post(
        'http://localhost:8001/api/weather/multi-city?aggregate=false',
        {
          cities: cityList,
          date_range: {
            start: startDate,
            end: endDate,
          },
          metric: selectedMetric,
        }
      );

      if (response.data && response.data.city_results) {
        setHeatmapData(response.data.city_results);
      } else {
        setError('No data returned from API');
      }
    } catch (err: any) {
      console.error('Heatmap fetch error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to fetch heatmap data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="heatmap-view">
      <h1>Weather Heatmap Analysis</h1>
      <p className="view-description">
        Visualize weather patterns across multiple cities and dates in a color-coded table format.
      </p>

      <form onSubmit={handleSubmit} className="heatmap-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="cities">Városok (vesszővel elválasztva)</label>
            <div className="preset-buttons">
              <button
                type="button"
                onClick={() => setCities(HUNGARIAN_PRESET)}
                className="preset-btn"
              >
                Magyar városok
              </button>
              <button
                type="button"
                onClick={() => setCities(EUROPEAN_PRESET)}
                className="preset-btn"
              >
                Európai városok
              </button>
              <button
                type="button"
                onClick={() => setCities(`${HUNGARIAN_PRESET}, ${EUROPEAN_PRESET}`)}
                className="preset-btn"
              >
                Mind
              </button>
            </div>
            <textarea
              id="cities"
              value={cities}
              onChange={(e) => setCities(e.target.value)}
              placeholder="Budapest, London, Paris, Berlin, Rome"
              rows={3}
              required
              style={{ color: '#000000', backgroundColor: '#ffffff' }}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="startDate">Start Date</label>
            <input
              type="date"
              id="startDate"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
              style={{ color: '#000000', backgroundColor: '#ffffff' }}
            />
          </div>

          <div className="form-group">
            <label htmlFor="endDate">End Date</label>
            <input
              type="date"
              id="endDate"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              required
              style={{ color: '#000000', backgroundColor: '#ffffff' }}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Weather Metric</label>
            <MetricSelector
              selectedMetric={selectedMetric}
              onMetricChange={handleMetricChange}
            />
          </div>
        </div>

        <button type="submit" disabled={loading} className="submit-button">
          {loading ? 'Generating Heatmap...' : 'Generate Heatmap'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {heatmapData.length > 0 && (
        <HeatmapChart
          data={heatmapData}
          metric={selectedMetric}
          unit={metricUnit}
        />
      )}

      {!loading && !error && heatmapData.length === 0 && (
        <div className="empty-state">
          <p>Enter cities and date range above, then click "Generate Heatmap" to visualize weather patterns.</p>
        </div>
      )}
    </div>
  );
};

export default HeatmapView;
