import React, { useState, useEffect } from 'react';
import RecordCard from './RecordCard';
import WindHeatmap from './WindHeatmap';
import apiClient from '../../services/apiClient';
import { logger } from '../../utils/logger';
import './WindTab.css';
import './WindHeatmap.css';

interface WindData {
  date: string;
  value: number;
  location?: string;
}

interface WindStats {
  max: { value: number; date: string };
  avg: number;
  min: { value: number; date: string };
  strongWindDays: number; // >39 km/h (Beaufort 6+)
  calmDays: number; // <=6 km/h (Beaufort 0-2)
  count: number;
}

interface WindTabProps {
  city: string;
  startDate: string;
  endDate: string;
}

const WindTab: React.FC<WindTabProps> = ({ city, startDate, endDate }) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [windData, setWindData] = useState<WindData[]>([]);
  const [stats, setStats] = useState<WindStats | null>(null);

  const calculateStats = (data: WindData[]): WindStats => {
    if (!data || data.length === 0) {
      return {
        max: { value: 0, date: '-' },
        avg: 0,
        min: { value: 0, date: '-' },
        strongWindDays: 0,
        calmDays: 0,
        count: 0,
      };
    }

    const values = data.map((d) => d.value).filter((v) => v !== null && v !== undefined);
    const max = Math.max(...values);
    const min = Math.min(...values);
    const total = values.reduce((sum, val) => sum + val, 0);
    const avg = total / values.length;

    // Count days with strong wind (>39 km/h - Beaufort 6+) and calm days (<=6 km/h - Beaufort 0-2)
    const strongWindDays = values.filter((v) => v > 39).length; // Beaufort 6+
    const calmDays = values.filter((v) => v <= 6).length; // Beaufort 0-2

    const maxEntry = data.find((d) => d.value === max);
    const minEntry = data.find((d) => d.value === min);

    return {
      max: { value: Math.round(max * 10) / 10, date: maxEntry?.date || '-' },
      avg: Math.round(avg * 10) / 10,
      min: { value: Math.round(min * 10) / 10, date: minEntry?.date || '-' },
      strongWindDays,
      calmDays,
      count: values.length,
    };
  };

  const fetchWindData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post('/api/weather/single-city-detailed', {
        city,
        start: startDate,
        end: endDate,
      });

      const data = response.data;

      // API paraméter: windspeed_10m_max (Qt verzióval egyező)
      if (data.wind_data && Array.isArray(data.wind_data)) {
        const processedData: WindData[] = data.wind_data
          .filter((item: any) => item.value !== null && item.value !== undefined)
          .map((item: any) => ({
            date: item.date,
            value: item.value,
            location: item.city_name || city,
          }));

        setWindData(processedData);
        setStats(calculateStats(processedData));
      } else {
        throw new Error('Invalid wind data format received');
      }
    } catch (err) {
      logger.error('Wind fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch wind data');
      setWindData([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWindData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [city, startDate, endDate]);

  const handleRetry = () => {
    fetchWindData();
  };

  if (loading) {
    return (
      <div className="wind-tab loading">
        <div className="loading-spinner"></div>
        <p>Loading wind data for {city}...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="wind-tab error">
        <div className="error-icon">⚠️</div>
        <h3>Failed to load wind data</h3>
        <p>{error}</p>
        <button onClick={handleRetry} className="retry-button">
          🔄 Try Again
        </button>
      </div>
    );
  }

  if (!stats || stats.count === 0) {
    return (
      <div className="wind-tab empty">
        <div className="empty-icon">💨</div>
        <h3>No wind data available</h3>
        <p>No wind speed records found for {city} in the selected period.</p>
      </div>
    );
  }

  return (
    <div className="wind-tab">
      <div className="tab-header">
        <h3>💨 Wind Speed Analysis</h3>
        <p className="period-info">
          {city} • {startDate} to {endDate} • {stats.count} days
        </p>
      </div>

      <div className="stats-grid">
        <RecordCard
          icon="💨"
          title="Maximum Wind"
          value={stats.max.value}
          date={stats.max.date}
          unit="km/h"
          className="danger"
        />

        <RecordCard icon="📊" title="Average Wind" value={stats.avg} unit="km/h" className="info" />

        <RecordCard
          icon="🍃"
          title="Minimum Wind"
          value={stats.min.value}
          date={stats.min.date}
          unit="km/h"
          className="success"
        />

        <RecordCard
          icon="🌪️"
          title="Strong Wind Days"
          value={stats.strongWindDays}
          date={`${stats.calmDays} calm days`}
          unit="days"
          className="warning"
        />
      </div>

      {/* 💨 Qt kompatibilis Beaufort heatmap vizualizáció */}
      <div className="heatmap-section">
        <h4>📊 Daily Wind Speed Heatmap (Beaufort Scale)</h4>
        <WindHeatmap data={windData} width={1000} height={400} />
      </div>

      <div className="wind-summary">
        <h4>Wind Speed Distribution</h4>
        <div className="distribution-bar">
          <div
            className="calm-section"
            style={{ width: `${(stats.calmDays / stats.count) * 100}%` }}
          >
            <span className="section-label">🍃 {stats.calmDays} calm</span>
          </div>
          <div
            className="moderate-section"
            style={{
              width: `${((stats.count - stats.strongWindDays - stats.calmDays) / stats.count) * 100}%`,
            }}
          >
            <span className="section-label">
              💨 {stats.count - stats.strongWindDays - stats.calmDays} moderate
            </span>
          </div>
          <div
            className="strong-section"
            style={{ width: `${(stats.strongWindDays / stats.count) * 100}%` }}
          >
            <span className="section-label">🌪️ {stats.strongWindDays} strong</span>
          </div>
        </div>
        <div className="distribution-legend">
          <div className="legend-item">
            <div className="legend-color calm-color"></div>
            <span>Calm days (0-6 km/h)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color moderate-color"></div>
            <span>Moderate days (7-39 km/h)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color strong-color"></div>
            <span>Strong wind days (40+ km/h)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WindTab;
