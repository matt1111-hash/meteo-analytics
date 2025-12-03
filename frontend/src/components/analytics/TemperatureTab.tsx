import React, { useState, useEffect } from 'react';
import RecordCard from './RecordCard';
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
  city?: string;
  startDate?: string;
  endDate?: string;
}

const TemperatureTab: React.FC<TemperatureTabProps> = ({
  city = 'Budapest',
  startDate = '2023-01-01',
  endDate = '2023-12-31'
}) => {
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
        count: 0
      };
    }

    const values = data.map(d => d.value).filter(v => v !== null && v !== undefined);
    const max = Math.max(...values);
    const min = Math.min(...values);
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;

    const maxEntry = data.find(d => d.value === max);
    const minEntry = data.find(d => d.value === min);

    return {
      max: { value: max, date: maxEntry?.date || '-' },
      min: { value: min, date: minEntry?.date || '-' },
      avg: Math.round(avg * 10) / 10,
      count: values.length
    };
  };

  const fetchTemperatureData = async () => {
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

      if (data.temperature_data && Array.isArray(data.temperature_data)) {
        const processedData: TemperatureData[] = data.temperature_data
          .filter((item: any) => item.value !== null && item.value !== undefined)
          .map((item: any) => ({
            date: item.date,
            value: item.value,
            location: item.location || city
          }));

        setTemperatureData(processedData);
        setStats(calculateStats(processedData));
      } else {
        throw new Error('Invalid temperature data format received');
      }

    } catch (err) {
      console.error('Temperature fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch temperature data');
      setTemperatureData([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemperatureData();
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
                width: `${((stats.avg - stats.min.value) / (stats.max.value - stats.min.value)) * 100}%`
              }}
            ></div>
          </div>
          <div className="range-max">{stats.max.value}°C</div>
        </div>
      </div>
    </div>
  );
};

export default TemperatureTab;