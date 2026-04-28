import React, { useState, useEffect } from 'react';
import RecordCard from './RecordCard';
import PrecipitationHeatmap from './PrecipitationHeatmap';
import apiClient from '../../services/apiClient';
import { logger } from '../../utils/logger';
import './PrecipitationTab.css';
import './PrecipitationHeatmap.css';

interface PrecipitationData {
  date: string;
  value: number;
  location?: string;
}

interface PrecipitationStats {
  total: { value: number; days: number };
  max: { value: number; date: string };
  avg: number;
  rainyDays: number;
  dryDays: number;
  count: number;
}

interface PrecipitationTabProps {
  city: string;
  startDate: string;
  endDate: string;
}

const PrecipitationTab: React.FC<PrecipitationTabProps> = ({ city, startDate, endDate }) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [precipitationData, setPrecipitationData] = useState<PrecipitationData[]>([]);
  const [stats, setStats] = useState<PrecipitationStats | null>(null);

  const calculateStats = (data: PrecipitationData[]): PrecipitationStats => {
    if (!data || data.length === 0) {
      return {
        total: { value: 0, days: 0 },
        max: { value: 0, date: '-' },
        avg: 0,
        rainyDays: 0,
        dryDays: 0,
        count: 0,
      };
    }

    const values = data.map((d) => d.value).filter((v) => v !== null && v !== undefined);
    const max = Math.max(...values);
    const total = values.reduce((sum, val) => sum + val, 0);
    const avg = total / values.length;

    // Count days with precipitation (> 0mm) and dry days (0mm)
    const rainyDays = values.filter((v) => v > 0).length;
    const dryDays = values.filter((v) => v === 0).length;

    const maxEntry = data.find((d) => d.value === max);

    return {
      total: { value: Math.round(total * 10) / 10, days: rainyDays },
      max: { value: max, date: maxEntry?.date || '-' },
      avg: Math.round(avg * 10) / 10,
      rainyDays,
      dryDays,
      count: values.length,
    };
  };

  const fetchPrecipitationData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post('/api/weather/single-city-detailed', {
        city,
        start: startDate,
        end: endDate,
      });

      const data = response.data;

      if (data.precipitation_data && Array.isArray(data.precipitation_data)) {
        const processedData: PrecipitationData[] = data.precipitation_data
          .filter(
            (item: Record<string, unknown>) => item.value !== null && item.value !== undefined,
          )
          .map((item: Record<string, unknown>) => ({
            date: item.date as string,
            value: item.value as number,
            location: (item.city_name as string) || city,
          }));

        setPrecipitationData(processedData);
        setStats(calculateStats(processedData));
      } else {
        throw new Error('Invalid precipitation data format received');
      }
    } catch (err) {
      logger.error('Precipitation fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch precipitation data');
      setPrecipitationData([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrecipitationData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [city, startDate, endDate]);

  const handleRetry = () => {
    fetchPrecipitationData();
  };

  if (loading) {
    return (
      <div className="precipitation-tab loading">
        <div className="loading-spinner"></div>
        <p>Loading precipitation data for {city}...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="precipitation-tab error">
        <div className="error-icon">⚠️</div>
        <h3>Failed to load precipitation data</h3>
        <p>{error}</p>
        <button onClick={handleRetry} className="retry-button">
          🔄 Try Again
        </button>
      </div>
    );
  }

  if (!stats || stats.count === 0) {
    return (
      <div className="precipitation-tab empty">
        <div className="empty-icon">🌧️</div>
        <h3>No precipitation data available</h3>
        <p>No precipitation records found for {city} in the selected period.</p>
      </div>
    );
  }

  return (
    <div className="precipitation-tab">
      <div className="tab-header">
        <h3>🌧️ Precipitation Analysis</h3>
        <p className="period-info">
          {city} • {startDate} to {endDate} • {stats.count} days
        </p>
      </div>

      <div className="stats-grid">
        <RecordCard
          icon="💧"
          title="Total Precipitation"
          value={stats.total.value}
          date={`Over ${stats.total.days} rainy days`}
          unit="mm"
          className="info"
        />

        <RecordCard
          icon="🌊"
          title="Maximum Daily"
          value={stats.max.value}
          date={stats.max.date}
          unit="mm"
          className="danger"
        />

        <RecordCard
          icon="🌧️"
          title="Average Daily"
          value={stats.avg}
          unit="mm"
          className="success"
        />

        <RecordCard
          icon="📊"
          title="Rainy Days"
          value={stats.rainyDays}
          date={`${stats.dryDays} dry days`}
          unit="days"
          className="highlight"
        />
      </div>

      {/* 🌧️ Qt kompatibilis heatmap vizualizáció */}
      <div className="heatmap-section">
        <h4>📊 Daily Precipitation Heatmap</h4>
        <PrecipitationHeatmap data={precipitationData} width={1000} height={400} />
      </div>

      <div className="data-summary">
        <h4>Precipitation Distribution</h4>
        <div className="distribution-bar">
          <div
            className="rainy-section"
            style={{ width: `${(stats.rainyDays / stats.count) * 100}%` }}
          >
            <span className="section-label">🌧️ {stats.rainyDays} days</span>
          </div>
          <div className="dry-section" style={{ width: `${(stats.dryDays / stats.count) * 100}%` }}>
            <span className="section-label">☀️ {stats.dryDays} days</span>
          </div>
        </div>
        <div className="distribution-legend">
          <div className="legend-item">
            <div className="legend-color rainy-color"></div>
            <span>Rainy days (&gt;0mm)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color dry-color"></div>
            <span>Dry days (0mm)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrecipitationTab;
