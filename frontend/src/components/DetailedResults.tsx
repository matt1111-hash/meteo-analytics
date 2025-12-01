import React from 'react';
import TimeSeriesChart from './TimeSeriesChart';
import WindChart from './WindChart';
import PrecipitationChart from './PrecipitationChart';
import ExportCSVButton from './ExportCSVButton';
import { CityWeatherResult } from '../types/weather';

interface DetailedData {
  wind: Array<{ date: string; windspeed: number | null; windgusts: number | null }>;
  precipitation: Array<{ date: string; precipitation: number | null }>;
}

interface DetailedResultsProps {
  temperatureData: CityWeatherResult[];
  detailedData: DetailedData;
  city: string;
  startDate: string;
  endDate: string;
}

const DetailedResults: React.FC<DetailedResultsProps> = ({
  temperatureData,
  detailedData,
  city,
  startDate,
  endDate,
}) => {
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
      <TimeSeriesChart
        data={temperatureData}
        metric="temperature_2m_mean"
        metricName="Mean Temperature"
        metricUnit="°C"
      />
      <WindChart
        data={detailedData.wind}
        city={city}
      />
      <PrecipitationChart
        data={detailedData.precipitation}
        city={city}
      />
    </div>
  );
};

export default DetailedResults;