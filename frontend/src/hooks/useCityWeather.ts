import { useState } from 'react';
import axios from 'axios';
import apiClient from '../services/apiClient';
import { logger } from '../utils/logger';
import { CityWeatherResult, DetailedData } from '../types/weather';

interface UseCityWeatherParams {
  city: string;
  startDate: string;
  endDate: string;
  metric: string;
  viewMode: 'simple' | 'detailed';
}

export const useCityWeather = () => {
  const [results, setResults] = useState<CityWeatherResult[]>([]);
  const [detailedData, setDetailedData] = useState<DetailedData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWeatherData = async (params: UseCityWeatherParams): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      if (params.viewMode === 'simple') {
        // Simple view: fetch single metric
        const response = await apiClient.post<{
          city_results: CityWeatherResult[];
          [key: string]: unknown;
        }>('/api/weather/single-city', {
          city: params.city.trim(),
          start: params.startDate,
          end: params.endDate,
          metric: params.metric,
        });

        setResults(response.data.city_results);
        setDetailedData(null);
      } else {
        // Detailed view: fetch all metrics
        const response = await apiClient.post<{
          temperature_data: CityWeatherResult[];
          wind_data: CityWeatherResult[];
          wind_gusts_data: CityWeatherResult[];
          precipitation_data: CityWeatherResult[];
          [key: string]: unknown;
        }>('/api/weather/single-city-detailed', {
          city: params.city.trim(),
          start: params.startDate,
          end: params.endDate,
        });

        // Validate response structure
        const apiData = response.data;
        const temperatureData = apiData.temperature_data || [];
        const windData = apiData.wind_data || [];
        const windGustsData = apiData.wind_gusts_data || [];
        const precipitationData = apiData.precipitation_data || [];

        // Set results based on temperature data (for render condition)
        setResults(temperatureData);

        // Set detailed data with validated structure
        const detailedDataToSet: DetailedData = {
          temperature_data: temperatureData,
          wind_data: windData,
          wind_gusts_data: windGustsData,
          precipitation_data: precipitationData,
        };

        setDetailedData(detailedDataToSet);
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.message;
        setError(`API Error: ${errorMessage}`);
        logger.error('API request failed:', err.response?.status);
      } else {
        setError('An unexpected error occurred');
        logger.error('Unexpected error:', err);
      }
      // Don't reset detailedData on error - preserve existing data
      setResults([]);
      // setDetailedData(null); // REMOVED: Don't reset on error
    } finally {
      setLoading(false);
    }
  };

  const resetData = (): void => {
    setResults([]);
    setDetailedData(null);
    setError(null);
  };

  return {
    results,
    detailedData,
    loading,
    error,
    fetchWeatherData,
    resetData,
  };
};
