import React, { useState } from 'react';
import axios from 'axios';
import './AnomalyPanel.css';

const API_BASE_URL = 'http://localhost:8001';

interface AnomalyThresholds {
  temp_hot?: number;
  temp_cold?: number;
  precip_high?: number;
  precip_low?: number;
  wind_normal?: number;
  wind_strong?: number;
  wind_extreme?: number;
  wind_hurricane?: number;
}

interface ClimateAnomaly {
  location_name: string;
  date: string;
  parameter: string;
  measured_value: number;
  category: string;
  severity: 'success' | 'warning' | 'error';
  message: string;
  threshold: number;
  details: string;
}

interface AnomalyResponse {
  city: string;
  date_range: {
    start: string;
    end: string;
  };
  anomalies: {
    temperature: ClimateAnomaly | null;
    precipitation: ClimateAnomaly | null;
    wind: ClimateAnomaly | null;
  };
  thresholds_used: AnomalyThresholds;
}

interface AnomalyPanelProps {
  city: string;
  startDate: string;
  endDate: string;
  thresholds?: AnomalyThresholds;
}

const AnomalyPanel: React.FC<AnomalyPanelProps> = ({
  city,
  startDate,
  endDate,
  thresholds,
}) => {
  const [data, setData] = useState<AnomalyResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const detectAnomalies = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post<AnomalyResponse>(
        `${API_BASE_URL}/api/weather/anomalies`,
        {
          city,
          start: startDate,
          end: endDate,
          thresholds: thresholds || undefined,
        }
      );

      setData(response.data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError('An unexpected error occurred');
      }
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityClass = (severity: string): string => {
    switch (severity) {
      case 'error':
        return 'severity-error';
      case 'warning':
        return 'severity-warning';
      case 'success':
        return 'severity-success';
      default:
        return 'severity-info';
    }
  };

  const getSeverityIcon = (severity: string): string => {
    switch (severity) {
      case 'error':
        return '🚨';
      case 'warning':
        return '⚠️';
      case 'success':
        return '✅';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div className="anomaly-panel">
      <div className="panel-header">
        <h3>🔍 Anomaly Detection</h3>
        <p className="panel-subtitle">
          Detect unusual weather patterns for {city}
        </p>
      </div>

      <button
        onClick={detectAnomalies}
        disabled={loading}
        className="detect-button"
      >
        {loading ? '🔄 Detecting...' : '🔍 Detect Anomalies'}
      </button>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {data && (
        <div className="anomaly-results">
          <div className="results-header">
            <h4>Results for {data.city}</h4>
            <p className="date-range">
              {data.date_range.start} to {data.date_range.end}
            </p>
          </div>

          <div className="anomaly-cards">
            {Object.entries(data.anomalies).map(([key, anomaly]) => {
              if (!anomaly) {
                return (
                  <div key={key} className="anomaly-card severity-success">
                    <div className="card-header">
                      <span className="severity-icon">✅</span>
                      <h5>{key.charAt(0).toUpperCase() + key.slice(1)}</h5>
                    </div>
                    <p className="card-message">No anomalies detected</p>
                  </div>
                );
              }

              return (
                <div
                  key={key}
                  className={`anomaly-card ${getSeverityClass(anomaly.severity)}`}
                >
                  <div className="card-header">
                    <span className="severity-icon">
                      {getSeverityIcon(anomaly.severity)}
                    </span>
                    <h5>{anomaly.parameter.charAt(0).toUpperCase() + anomaly.parameter.slice(1)}</h5>
                  </div>

                  <div className="card-body">
                    <p className="card-message">{anomaly.message}</p>
                    <div className="card-details">
                      <div className="detail-row">
                        <span className="detail-label">Value:</span>
                        <span className="detail-value">
                          {anomaly.measured_value !== null ? anomaly.measured_value.toFixed(1) : 'N/A'}
                        </span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Threshold:</span>
                        <span className="detail-value">
                          {anomaly.threshold !== null ? anomaly.threshold.toFixed(1) : 'N/A'}
                        </span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Category:</span>
                        <span className="detail-value">{anomaly.category}</span>
                      </div>
                    </div>
                    <p className="card-note">{anomaly.details}</p>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="thresholds-info">
            <h5>Thresholds Used</h5>
            <div className="threshold-grid">
              {Object.entries(data.thresholds_used).map(([key, value]) => (
                <div key={key} className="threshold-item">
                  <span className="threshold-key">
                    {key.replace(/_/g, ' ')}:
                  </span>
                  <span className="threshold-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnomalyPanel;
