import React, { useState } from 'react';
import axios from 'axios';
import apiClient from '../services/apiClient';
import { logger } from '../utils/logger';
import ExtremeRecordsTable from '../components/ExtremeRecordsTable';
import CityAutocomplete from '../components/common/CityAutocomplete';
import {
  ExtremeRecord,
  AnomalyStatus,
  AggregationType,
  DailyWeatherData,
  calculateExtremes,
  detectAnomalies,
  generateTextSummary,
} from '../utils/extremeCalculator/index';
import { CityWeatherResult } from '../types/weather';
import './ExtremeEventsView.css';

interface FormData {
  city: string;
  startDate: string;
  endDate: string;
}

const ExtremeEventsView: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    city: '',
    startDate: '',
    endDate: '',
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [aggregation, setAggregation] = useState<AggregationType>('daily');
  const [records, setRecords] = useState<ExtremeRecord[]>([]);
  const [anomalyStatus, setAnomalyStatus] = useState<AnomalyStatus | null>(null);
  const [summary, setSummary] = useState<string>('');
  const [rawData, setRawData] = useState<DailyWeatherData[]>([]);

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleAggregationChange = (newAggregation: AggregationType) => {
    setAggregation(newAggregation);
    if (rawData.length > 0) {
      const newRecords = calculateExtremes(rawData, newAggregation);
      setRecords(newRecords);
      setSummary(generateTextSummary(newRecords));
    }
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
    if (formData.startDate > formData.endDate) {
      return 'Start date must be before end date';
    }
    return null;
  };

  const fetchAllMetrics = async (): Promise<DailyWeatherData[]> => {
    const metrics = [
      'temperature_2m_max',
      'temperature_2m_min',
      'precipitation_sum',
      'windgusts_10m_max',
    ];

    const results: CityWeatherResult[] = [];

    for (const metric of metrics) {
      try {
        const response = await apiClient.post<{
          city_results: CityWeatherResult[];
        }>('/api/weather/single-city', {
          city: formData.city.trim(),
          start: formData.startDate,
          end: formData.endDate,
          metric,
        });
        results.push(...response.data.city_results);
      } catch (err) {
        logger.warn(`Failed to fetch ${metric}:`, err);
      }
    }

    // Transform to DailyWeatherData
    const dataMap = new Map<string, DailyWeatherData>();
    for (const result of results) {
      const existing = dataMap.get(result.date) || {
        date: result.date,
        temperature_max: null,
        temperature_min: null,
        precipitation: null,
        windspeed: null,
        windgusts: null,
      };

      if (result.metric === 'temperature_2m_max') {
        existing.temperature_max = result.value;
      } else if (result.metric === 'temperature_2m_min') {
        existing.temperature_min = result.value;
      } else if (result.metric === 'precipitation_sum') {
        existing.precipitation = result.value;
      } else if (result.metric === 'windgusts_10m_max') {
        existing.windgusts = result.value;
      } else if (result.metric === 'windspeed_10m_max') {
        existing.windspeed = result.value;
      }

      dataMap.set(result.date, existing);
    }

    return Array.from(dataMap.values()).sort((a, b) => a.date.localeCompare(b.date));
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
      const data = await fetchAllMetrics();

      if (data.length === 0) {
        setError('No data returned from API');
        setRecords([]);
        setAnomalyStatus(null);
        setSummary('');
        setRawData([]);
        return;
      }

      setRawData(data);
      const calculatedRecords = calculateExtremes(data, aggregation);
      setRecords(calculatedRecords);
      setAnomalyStatus(detectAnomalies(data));
      setSummary(generateTextSummary(calculatedRecords));
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError('An unexpected error occurred');
      }
      setRecords([]);
      setAnomalyStatus(null);
      setSummary('');
      setRawData([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusClass = (status: 'normal' | 'warning' | 'danger'): string => {
    switch (status) {
      case 'danger':
        return 'status-danger';
      case 'warning':
        return 'status-warning';
      default:
        return 'status-normal';
    }
  };

  return (
    <div className="extreme-events-view">
      <div className="view-header">
        <h1>Extreme Weather Events</h1>
        <p className="view-subtitle">Analyze weather records and detect anomalies</p>
      </div>

      <div className="view-content">
        <form className="extreme-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <CityAutocomplete
                value={formData.city}
                onChange={(city) => handleChange('city', city)}
                disabled={loading}
                placeholder="Város neve..."
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
                className="form-input"
                style={{ color: '#1f2937', backgroundColor: '#ffffff' }}
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
                className="form-input"
                style={{ color: '#1f2937', backgroundColor: '#ffffff' }}
              />
            </div>
          </div>

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'Analyzing...' : 'Analyze Extreme Events'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {anomalyStatus && (
          <div className="anomaly-panel">
            <h3>Anomaly Detection</h3>
            <div className="anomaly-indicators">
              <div className={`anomaly-indicator ${getStatusClass(anomalyStatus.temperature)}`}>
                <span className="indicator-icon">🌡️</span>
                <span className="indicator-label">Temperature</span>
                <span className="indicator-value">{anomalyStatus.temperatureMessage}</span>
              </div>
              <div className={`anomaly-indicator ${getStatusClass(anomalyStatus.precipitation)}`}>
                <span className="indicator-icon">🌧️</span>
                <span className="indicator-label">Precipitation</span>
                <span className="indicator-value">{anomalyStatus.precipitationMessage}</span>
              </div>
              <div className={`anomaly-indicator ${getStatusClass(anomalyStatus.wind)}`}>
                <span className="indicator-icon">🌪️</span>
                <span className="indicator-label">Wind</span>
                <span className="indicator-value">{anomalyStatus.windMessage}</span>
              </div>
            </div>
          </div>
        )}

        {rawData.length > 0 && (
          <div className="records-section">
            <div className="section-header">
              <h3>Weather Records</h3>
              <div className="aggregation-toggle">
                <button
                  type="button"
                  className={`toggle-btn ${aggregation === 'daily' ? 'active' : ''}`}
                  onClick={() => handleAggregationChange('daily')}
                >
                  Daily
                </button>
                <button
                  type="button"
                  className={`toggle-btn ${aggregation === 'monthly' ? 'active' : ''}`}
                  onClick={() => handleAggregationChange('monthly')}
                >
                  Monthly
                </button>
                <button
                  type="button"
                  className={`toggle-btn ${aggregation === 'yearly' ? 'active' : ''}`}
                  onClick={() => handleAggregationChange('yearly')}
                >
                  Yearly
                </button>
              </div>
            </div>

            <ExtremeRecordsTable records={records} loading={loading} />

            {summary && (
              <div className="summary-panel">
                <h4>Summary</h4>
                <p className="summary-text">{summary}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ExtremeEventsView;
