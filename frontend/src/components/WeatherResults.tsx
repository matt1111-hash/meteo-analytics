import React from 'react';
import { WeatherAnalysisResponse } from '../types/weather';
import './WeatherResults.css';

interface WeatherResultsProps {
  data: WeatherAnalysisResponse | null;
}

const WeatherResults: React.FC<WeatherResultsProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="results-empty">
        <p>No results yet. Submit the form above to analyze weather data.</p>
      </div>
    );
  }

  const { question, city_results, execution_time, total_cities_found, statistics } = data;

  const formatDate = (dateString: string): string => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  const getMetricUnit = (metric: string): string => {
    const units: Record<string, string> = {
      temperature_2m_max: '°C',
      temperature_2m_min: '°C',
      temperature_2m_mean: '°C',
      precipitation_sum: 'mm',
      windspeed_10m_max: 'km/h',
      windgusts_10m_max: 'km/h',
    };
    return units[metric] || '';
  };

  const getMetricDisplayName = (metric: string): string => {
    const names: Record<string, string> = {
      temperature_2m_max: 'Maximum Temperature',
      temperature_2m_min: 'Minimum Temperature',
      temperature_2m_mean: 'Mean Temperature',
      precipitation_sum: 'Precipitation',
      windspeed_10m_max: 'Wind Speed',
      windgusts_10m_max: 'Wind Gusts',
      temperature_range: 'Temperature Range',
    };
    return names[metric] || metric.replace(/_/g, ' ');
  };

  const cityNames = city_results
    .map((r) => r.city_name)
    .filter((name, index, arr) => arr.indexOf(name) === index)
    .slice(0, 5)
    .join(', ');

  const displayTitle = city_results.length > 5
    ? `${cityNames} and ${city_results.length - 5} more`
    : cityNames;

  return (
    <div className="weather-results">
      <div className="results-header">
        <h2>{displayTitle}</h2>
        <p className="question-meta">
          {getMetricDisplayName(question.metric)} • {city_results.length} {city_results.length === 1 ? 'city' : 'cities'}
        </p>
      </div>

      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-label">Cities Analyzed</div>
          <div className="card-value">{city_results.length}</div>
          <div className="card-subtitle">of {total_cities_found} found</div>
        </div>

        <div className="summary-card">
          <div className="card-label">Execution Time</div>
          <div className="card-value">{execution_time.toFixed(2)}s</div>
          <div className="card-subtitle">API response</div>
        </div>

        {statistics.mean !== undefined && (
          <div className="summary-card">
            <div className="card-label">Average</div>
            <div className="card-value">
              {statistics.mean.toFixed(1)}
              {getMetricUnit(question.metric)}
            </div>
            <div className="card-subtitle">
              Range: {statistics.min?.toFixed(1)} - {statistics.max?.toFixed(1)}
            </div>
          </div>
        )}
      </div>

      <div className="results-table-container">
        <table className="results-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>City</th>
              <th>Country</th>
              <th>Value</th>
              <th>Date</th>
              <th>Quality</th>
            </tr>
          </thead>
          <tbody>
            {city_results.map((result, index) => (
              <tr key={`${result.city_name}-${index}`}>
                <td className="rank-cell">{result.rank || index + 1}</td>
                <td className="city-cell">
                  <div className="city-name">{result.city_name}</div>
                  <div className="city-coords">
                    {result.latitude.toFixed(2)}°, {result.longitude.toFixed(2)}°
                  </div>
                </td>
                <td>
                  <span className="country-badge">{result.country_code}</span>
                </td>
                <td className="value-cell">
                  <strong>{result.value.toFixed(1)}</strong>
                  {getMetricUnit(result.metric)}
                </td>
                <td className="date-cell">{formatDate(result.date)}</td>
                <td className="quality-cell">
                  <div className="quality-bar">
                    <div
                      className="quality-fill"
                      style={{ width: `${result.quality_score * 100}%` }}
                    />
                  </div>
                  <span className="quality-text">
                    {(result.quality_score * 100).toFixed(0)}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {city_results.length === 0 && (
        <div className="no-results">
          <p>No city results available for this query.</p>
        </div>
      )}
    </div>
  );
};

export default WeatherResults;
