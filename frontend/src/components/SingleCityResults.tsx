import React, { useState, useMemo } from 'react';
import TimeSeriesChart from './TimeSeriesChart';
import MapView from './MapView';
import ExportCSVButton from './ExportCSVButton';
import { CityWeatherResult } from '../types/weather';

type ViewTab = 'chart' | 'map';

interface SingleCityResultsProps {
  data: CityWeatherResult[];
  metric: string;
  metricName: string;
  metricUnit: string;
  city: string;
  startDate: string;
  endDate: string;
}

const SingleCityResults: React.FC<SingleCityResultsProps> = ({
  data,
  metric,
  metricName,
  metricUnit,
  city,
  startDate,
  endDate,
}) => {
  const [activeTab, setActiveTab] = useState<ViewTab>('chart');

  // Aggregate time series data to single point for map view
  const mapData = useMemo((): CityWeatherResult[] => {
    if (data.length === 0) return [];
    const first = data[0];
    const validValues = data.map(r => r.value).filter(v => v !== null && !isNaN(v));
    const avgValue = validValues.length > 0
      ? validValues.reduce((sum, v) => sum + v, 0) / validValues.length
      : 0;
    return [{
      ...first,
      value: avgValue,
      date: `${startDate} - ${endDate}`,
    }];
  }, [data, startDate, endDate]);

  return (
    <div className="results-section">
      <div className="results-header">
        <div className="tab-selector">
          <button
            className={`tab-btn ${activeTab === 'chart' ? 'active' : ''}`}
            onClick={() => setActiveTab('chart')}
          >
            📊 Chart
          </button>
          <button
            className={`tab-btn ${activeTab === 'map' ? 'active' : ''}`}
            onClick={() => setActiveTab('map')}
          >
            🗺️ Map
          </button>
        </div>
        <ExportCSVButton
          data={data}
          metric={metric}
          city={city}
          startDate={startDate}
          endDate={endDate}
          title="Export data to CSV"
        />
      </div>

      <div className="tab-content">
        {activeTab === 'chart' && (
          <TimeSeriesChart
            data={data}
            metric={metric}
            metricName={metricName}
            metricUnit={metricUnit}
          />
        )}

        {activeTab === 'map' && (
          <MapView
            data={mapData}
            metric={metric}
            unit={metricUnit}
          />
        )}
      </div>
    </div>
  );
};

export default SingleCityResults;