import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MetricsResponse } from '../types/weather';
import './MetricSelector.css';

interface MetricSelectorProps {
  selectedMetric: string;
  onMetricChange: (metric: string) => void;
  disabled?: boolean;
}

const API_BASE_URL = 'http://localhost:8001';

const MetricSelector: React.FC<MetricSelectorProps> = ({
  selectedMetric,
  onMetricChange,
  disabled = false,
}) => {
  const [metrics, setMetrics] = useState<Record<string, { name: string; unit: string; description: string }>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await axios.get<MetricsResponse>(`${API_BASE_URL}/api/weather/metrics`);
        setMetrics(response.data.metrics);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch metrics:', err);
        setError('Failed to load metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="metric-selector">
        <label htmlFor="metric-select">Metric:</label>
        <select id="metric-select" disabled>
          <option>Loading metrics...</option>
        </select>
      </div>
    );
  }

  if (error) {
    return (
      <div className="metric-selector">
        <label htmlFor="metric-select">Metric:</label>
        <select id="metric-select" disabled>
          <option>{error}</option>
        </select>
      </div>
    );
  }

  return (
    <div className="metric-selector">
      <label htmlFor="metric-select">Metric:</label>
      <select
        id="metric-select"
        value={selectedMetric}
        onChange={(e) => onMetricChange(e.target.value)}
        disabled={disabled}
        className="metric-select"
        style={{ color: '#1f2937' }}
      >
        <option value="">-- Select a metric --</option>
        {Object.entries(metrics).map(([key, info]) => (
          <option key={key} value={key} title={info.description}>
            {info.name} ({info.unit})
          </option>
        ))}
      </select>
    </div>
  );
};

export default MetricSelector;
