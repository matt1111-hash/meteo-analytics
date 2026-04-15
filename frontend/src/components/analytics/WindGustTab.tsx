import React, { useState, useEffect } from 'react';
import RecordCard from './RecordCard';
import WindGustHeatmap from './WindGustHeatmap';
import { logger } from '../../utils/logger';
import './WindGustTab.css';
import './WindGustHeatmap.css';

interface WindGustData {
  date: string;
  value: number;
  location?: string;
}

interface WindGustStats {
  max: { value: number; date: string };
  avg: number;
  strongGusts: number;
  extremeGusts: number;
  count: number;
}

interface WindGustTabProps {
  city: string;
  startDate: string;
  endDate: string;
}

const WindGustTab: React.FC<WindGustTabProps> = ({
  city,
  startDate,
  endDate
}) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [windGustData, setWindGustData] = useState<WindGustData[]>([]);
  const [stats, setStats] = useState<WindGustStats | null>(null);

  const calculateStats = (data: WindGustData[]): WindGustStats => {
    if (!data || data.length === 0) {
      return {
        max: { value: 0, date: '-' },
        avg: 0,
        strongGusts: 0,
        extremeGusts: 0,
        count: 0
      };
    }

    const values = data.map(d => d.value).filter(v => v !== null && v !== undefined);
    const max = Math.max(...values);
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;

    // Wind gust thresholds (stronger than regular wind)
    const STRONG_THRESHOLD = 54; // km/h - strong gusts (15 m/s * 3.6)
    const EXTREME_THRESHOLD = 90; // km/h - extreme gusts (25 m/s * 3.6)

    // Count strong and extreme gust days
    const strongGusts = values.filter(v => v >= STRONG_THRESHOLD && v < EXTREME_THRESHOLD).length;
    const extremeGusts = values.filter(v => v >= EXTREME_THRESHOLD).length;

    const maxEntry = data.find(d => d.value === max);

    return {
      max: { value: max, date: maxEntry?.date || '-' },
      avg: Math.round(avg * 10) / 10,
      strongGusts,
      extremeGusts,
      count: values.length
    };
  };

  const fetchWindGustData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/weather/single-city-detailed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          city,
          start: startDate,
          end: endDate
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // 🚨 API PARAMÉTER JAVÍTÁS: wind_gusts_10m_max → wind_gusts_max (Qt verzióval egyező)
      if (data.wind_gusts_data && Array.isArray(data.wind_gusts_data)) {
        const processedData: WindGustData[] = data.wind_gusts_data
          .filter((item: any) => item.value !== null && item.value !== undefined)
          .map((item: any) => ({
            date: item.date,
            value: item.value, // Keep as km/h
            location: item.city_name || city
          }));

        setWindGustData(processedData);
        setStats(calculateStats(processedData));
      } else {
        throw new Error('Invalid wind gust data format received');
      }

    } catch (err) {
      logger.error('Wind gust fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch wind gust data');
      setWindGustData([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWindGustData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [city, startDate, endDate]);

  const handleRetry = () => {
    fetchWindGustData();
  };

  if (loading) {
    return (
      <div className="wind-gust-tab loading">
        <div className="loading-spinner"></div>
        <p>Loading wind gust data for {city}...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="wind-gust-tab error">
        <div className="error-icon">⚠️</div>
        <h3>Failed to load wind gust data</h3>
        <p>{error}</p>
        <button onClick={handleRetry} className="retry-button">
          🔄 Try Again
        </button>
      </div>
    );
  }

  if (!stats || stats.count === 0) {
    return (
      <div className="wind-gust-tab empty">
        <div className="empty-icon">🌪️</div>
        <h3>No wind gust data available</h3>
        <p>No wind gust records found for {city} in the selected period.</p>
      </div>
    );
  }

  return (
    <div className="wind-gust-tab">
      <div className="tab-header">
        <h3>🌪️ Wind Gust Analysis</h3>
        <p className="period-info">
          {city} • {startDate} to {endDate} • {stats.count} days
        </p>
      </div>

      <div className="stats-grid">
        <RecordCard
          icon="⛈️"
          title="Maximum Gust"
          value={stats.max.value}
          date={stats.max.date}
          unit="km/h"
          className="danger"
        />

        <RecordCard
          icon="🌪️"
          title="Average Gust"
          value={stats.avg}
          unit="km/h"
          className="warning"
        />

        <RecordCard
          icon="💨"
          title="Strong Gusts"
          value={stats.strongGusts}
          date="54-89.6 km/h"
          unit="days"
          className="info"
        />

        <RecordCard
          icon="🔥"
          title="Extreme Gusts"
          value={stats.extremeGusts}
          date="≥90 km/h"
          unit="days"
          className="highlight"
        />
      </div>

      {/* 🌪️ Qt kompatibilis Beaufort heatmap vizualizáció */}
      <div className="heatmap-section">
        <h4>📊 Daily Wind Gust Heatmap (Beaufort Scale)</h4>
        <WindGustHeatmap
          data={windGustData}
          width={1000}
          height={400}
        />
      </div>

      <div className="gust-summary">
        <h4>Gust Distribution</h4>
        <div className="gust-bars">
          <div className="gust-bar-item strong">
            <div className="bar-label">
              <span className="bar-icon">💨</span>
              <span className="bar-text">Strong (15-24.9 m/s)</span>
            </div>
            <div className="bar-container">
              <div
                className="bar-fill strong-fill"
                style={{ width: `${(stats.strongGusts / stats.count) * 100}%` }}
              ></div>
            </div>
            <span className="bar-count">{stats.strongGusts}</span>
          </div>

          <div className="gust-bar-item extreme">
            <div className="bar-label">
              <span className="bar-icon">🔥</span>
              <span className="bar-text">Extreme (≥25 m/s)</span>
            </div>
            <div className="bar-container">
              <div
                className="bar-fill extreme-fill"
                style={{ width: `${(stats.extremeGusts / stats.count) * 100}%` }}
              ></div>
            </div>
            <span className="bar-count">{stats.extremeGusts}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WindGustTab;
