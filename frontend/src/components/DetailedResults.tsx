import React from 'react';
import TimeSeriesChart from './TimeSeriesChart';
import WindChart from './WindChart';
import PrecipitationChart from './PrecipitationChart';
import ExportCSVButton from './ExportCSVButton';
import { CityWeatherResult } from '../types/weather';

interface WindDataPoint {
  date: string;
  windspeed: number | null;
  windgusts: number | null;
}

interface PrecipitationDataPoint {
  date: string;
  precipitation: number | null;
}

interface DetailedResultsProps {
  temperatureData: CityWeatherResult[];
  windData: CityWeatherResult[];
  windGustsData: CityWeatherResult[];
  precipitationData: CityWeatherResult[];
  city: string;
  startDate: string;
  endDate: string;
}

const DetailedResults: React.FC<DetailedResultsProps> = ({
  temperatureData,
  windData,
  windGustsData,
  precipitationData,
  city,
  startDate,
  endDate,
}) => {
  // Early return if all data arrays are empty
  const hasAnyData = temperatureData?.length > 0 ||
                    windData?.length > 0 ||
                    windGustsData?.length > 0 ||
                    precipitationData?.length > 0;

  if (!hasAnyData) {
    return (
      <div className="detailed-results">
        <div className="detailed-results-header">
          <h3>Detailed Analysis Results</h3>
          <p>No data available for {city} in the selected period.</p>
        </div>
      </div>
    );
  }

  // Convert CityWeatherResult to chart-specific formats
  // Create maps for quick date lookup
  const windGustsMap = new Map(
    windGustsData?.map(item => [item.date, item.value]) || []
  );

  const precipitationMap = new Map(
    precipitationData?.map(item => [item.date, item.value]) || []
  );

  // Merge all data by date for consistent visualization
  const allDates = new Set([
    ...(windData?.map(item => item.date) || []),
    ...(windGustsData?.map(item => item.date) || []),
    ...(precipitationData?.map(item => item.date) || [])
  ]);

  const windChartData: WindDataPoint[] = Array.from(allDates)
    .sort()
    .map(date => {
      const windItem = windData?.find(item => item.date === date);
      const windGustsValue = windGustsMap.get(date);

      return {
        date,
        windspeed: windItem?.value || null,
        windgusts: windGustsValue || null
      };
    });

  const precipitationChartData: PrecipitationDataPoint[] = Array.from(allDates)
    .sort()
    .map(date => ({
      date,
      precipitation: precipitationMap.get(date) || null
    }));

  return (
    <div className="detailed-results">
      <div className="detailed-results-header">
        <h3>Detailed Analysis Results</h3>
        <ExportCSVButton
          data={temperatureData}
          metric="temperature_2m_mean"
          city={city}
          startDate={startDate}
          endDate={endDate}
          title="Export temperature data to CSV"
        />
      </div>

      {temperatureData && temperatureData.length > 0 ? (
        <TimeSeriesChart
          data={temperatureData}
          metric="temperature_2m_mean"
          metricName="Mean Temperature"
          metricUnit="°C"
        />
      ) : (
        <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
          No temperature data available for {city} in selected period.
        </div>
      )}

      {windChartData && windChartData.length > 0 ? (
        <WindChart
          data={windChartData}
          city={city}
        />
      ) : (
        <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
          No wind data available for {city} in selected period.
        </div>
      )}

      {windGustsData && windGustsData.length > 0 ? (
        <TimeSeriesChart
          data={windGustsData}
          metric="windgusts_10m_max"
          metricName="Wind Gusts"
          metricUnit="km/h"
        />
      ) : (
        <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
          No wind gust data available for {city} in selected period.
        </div>
      )}

      {precipitationChartData && precipitationChartData.length > 0 ? (
        <PrecipitationChart
          data={precipitationChartData}
          city={city}
        />
      ) : (
        <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
          No precipitation data available for {city} in selected period.
        </div>
      )}
    </div>
  );
};

export default DetailedResults;