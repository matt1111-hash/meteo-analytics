import React, { useState, useEffect } from 'react';
import RecordCard from './RecordCard';
import TemperatureHeatmap from './TemperatureHeatmap';
import apiClient from '../../services/apiClient';
import { logger } from '../../utils/logger';
import './TemperatureTab.css';

interface TemperatureData {
  date: string;
  value: number;
  location?: string;
}

interface TemperatureStats {
  max: { value: number; date: string };
  min: { value: number; date: string };
  avg: number;
  count: number;
}

interface TemperatureTabProps {
  city: string;
  startDate: string;
  endDate: string;
}

const TemperatureTab: React.FC<TemperatureTabProps> = ({ city, startDate, endDate }) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [temperatureData, setTemperatureData] = useState<TemperatureData[]>([]);
  const [stats, setStats] = useState<TemperatureStats | null>(null);

  const calculateStats = (data: TemperatureData[]): TemperatureStats => {
    if (!data || data.length === 0) {
      return {
        max: { value: 0, date: '-' },
        min: { value: 0, date: '-' },
        avg: 0,
        count: 0,
      };
    }

    const values = data.map((d) => d.value).filter((v) => v !== null && v !== undefined);
    const max = Math.max(...values);
    const min = Math.min(...values);
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;

    const maxEntry = data.find((d) => d.value === max);
    const minEntry = data.find((d) => d.value === min);

    return {
      max: { value: max, date: maxEntry?.date || '-' },
      min: { value: min, date: minEntry?.date || '-' },
      avg: Math.round(avg * 10) / 10,
      count: values.length,
    };
  };

  const fetchTemperatureData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post('/api/weather/single-city-detailed', {
        city,
        start: startDate,
        end: endDate,
      });

      const data = response.data;

      if (data.temperature_data && Array.isArray(data.temperature_data)) {
        const processedData: TemperatureData[] = data.temperature_data
          .filter(
            (item: Record<string, unknown>) => item.value !== null && item.value !== undefined,
          )
          .map((item: Record<string, unknown>) => ({
            date: item.date as string,
            value: item.value as number,
            location: (item.city_name as string) || city,
          }));

        setTemperatureData(processedData);
        setStats(calculateStats(processedData));
      } else {
        throw new Error('Invalid temperature data format received');
      }
    } catch (err) {
      logger.error('Temperature fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch temperature data');
      setTemperatureData([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemperatureData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [city, startDate, endDate]);

  const handleRetry = () => {
    fetchTemperatureData();
  };

  if (loading) {
    return (
      <div className="temperature-tab loading">
        <div className="loading-spinner"></div>
        <p>Loading temperature data for {city}...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="temperature-tab error">
        <div className="error-icon">⚠️</div>
        <h3>Failed to load temperature data</h3>
        <p>{error}</p>
        <button onClick={handleRetry} className="retry-button">
          🔄 Try Again
        </button>
      </div>
    );
  }

  if (!stats || stats.count === 0) {
    return (
      <div className="temperature-tab empty">
        <div className="empty-icon">🌡️</div>
        <h3>No temperature data available</h3>
        <p>No temperature records found for {city} in the selected period.</p>
      </div>
    );
  }

  return (
    <div className="temperature-tab">
      <div className="tab-header">
        <h3>🌡️ Temperature Analysis</h3>
        <p className="period-info">
          {city} • {startDate} to {endDate} • {stats.count} days
        </p>
      </div>

      <div className="stats-grid">
        <RecordCard
          icon="🔥"
          title="Maximum Temperature"
          value={stats.max.value}
          date={stats.max.date}
          unit="°C"
          className="danger"
        />

        <RecordCard
          icon="❄️"
          title="Minimum Temperature"
          value={stats.min.value}
          date={stats.min.date}
          unit="°C"
          className="info"
        />

        <RecordCard
          icon="🌡️"
          title="Average Temperature"
          value={stats.avg}
          unit="°C"
          className="success"
        />

        <RecordCard
          icon="📊"
          title="Data Points"
          value={stats.count}
          unit="days"
          className="highlight"
        />
      </div>

      <div className="data-summary">
        <h4>Temperature Range</h4>
        <div className="range-bar">
          <div className="range-min">{stats.min.value}°C</div>
          <div className="range-track">
            <div
              className="range-fill"
              style={{
                width: `${((stats.avg - stats.min.value) / (stats.max.value - stats.min.value)) * 100}%`,
              }}
            ></div>
          </div>
          <div className="range-max">{stats.max.value}°C</div>
        </div>
      </div>

      {/* 🌡️ Temperature Heatmap - Qt funkcionalitás implementálása */}
      <div className="heatmap-section">
        <h4>📅 Daily Temperature Heatmap</h4>
        <p className="heatmap-description">
          365-day calendar view showing daily temperature variations. Each rectangle represents one
          day, colored by temperature.
        </p>
        <TemperatureHeatmap data={temperatureData} width={1000} height={400} />
      </div>
    </div>
  );
};

export default TemperatureTab;
