import React, { useState, useEffect } from 'react';
import RecordCard from './RecordCard';
import './WindTab.css';

interface WindData {
  date: string;
  value: number;
  location?: string;
}

interface WindStats {
  avg: number;
  max: { value: number; date: string };
  calmDays: number;
  windyDays: number;
  count: number;
}

interface WindTabProps {
  city: string;
  startDate: string;
  endDate: string;
}

const WindTab: React.FC<WindTabProps> = ({
  city,
  startDate,
  endDate
}) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<WindStats | null>(null);

  const calculateStats = (data: WindData[]): WindStats => {
    if (!data || data.length === 0) {
      return {
        avg: 0,
        max: { value: 0, date: '-' },
        calmDays: 0,
        windyDays: 0,
        count: 0
      };
    }

    const values = data.map(d => d.value).filter(v => v !== null && v !== undefined);
    const max = Math.max(...values);
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;

    // Define wind thresholds
    const CALM_THRESHOLD = 11; // km/h - light breeze (3 m/s * 3.6)
    const WINDY_THRESHOLD = 36; // km/h - strong breeze (10 m/s * 3.6)

    // Count calm days (avg wind < 11 km/h) and windy days (avg wind > 36 km/h)
    const calmDays = values.filter(v => v < CALM_THRESHOLD).length;
    const windyDays = values.filter(v => v > WINDY_THRESHOLD).length;

    const maxEntry = data.find(d => d.value === max);

    return {
      avg: Math.round(avg * 10) / 10,
      max: { value: max, date: maxEntry?.date || '-' },
      calmDays,
      windyDays,
      count: values.length
    };
  };

  const fetchWindData = async () => {
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

      if (data.wind_data && Array.isArray(data.wind_data)) {
        const processedData: WindData[] = data.wind_data
          .filter((item: any) => item.value !== null && item.value !== undefined)
          .map((item: any) => ({
            date: item.date,
            value: item.value, // Keep as km/h
            location: item.city_name || city
          }));

        setStats(calculateStats(processedData));
      } else {
        throw new Error('Invalid wind data format received');
      }

    } catch (err) {
      console.error('Wind fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch wind data');
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
        <p>No wind records found for {city} in the selected period.</p>
      </div>
    );
  }

  return (
    <div className="wind-tab">
      <div className="tab-header">
        <h3>💨 Wind Analysis</h3>
        <p className="period-info">
          {city} • {startDate} to {endDate} • {stats.count} days
        </p>
      </div>

      <div className="stats-grid">
        <RecordCard
          icon="💪"
          title="Maximum Wind"
          value={stats.max.value}
          date={stats.max.date}
          unit="km/h"
          className="danger"
        />

        <RecordCard
          icon="🌪️"
          title="Average Wind"
          value={stats.avg}
          unit="km/h"
          className="success"
        />

        <RecordCard
          icon="🍃"
          title="Calm Days"
          value={stats.calmDays}
          date="Wind &lt; 3 km/h"
          unit="days"
          className="info"
        />

        <RecordCard
          icon="🌬️"
          title="Windy Days"
          value={stats.windyDays}
          date="Wind &gt; 10 km/h"
          unit="days"
          className="warning"
        />
      </div>

      <div className="wind-summary">
        <h4>Wind Distribution</h4>
        <div className="wind-scale">
          <div className="scale-item calm">
            <span className="scale-icon">🍃</span>
            <span className="scale-label">Calm (&lt;3 m/s)</span>
            <span className="scale-count">{stats.calmDays}</span>
          </div>
          <div className="scale-item moderate">
            <span className="scale-icon">🌤️</span>
            <span className="scale-label">Moderate (3-10 m/s)</span>
            <span className="scale-count">{stats.count - stats.calmDays - stats.windyDays}</span>
          </div>
          <div className="scale-item windy">
            <span className="scale-icon">🌬️</span>
            <span className="scale-label">Windy (&gt;10 m/s)</span>
            <span className="scale-count">{stats.windyDays}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WindTab;