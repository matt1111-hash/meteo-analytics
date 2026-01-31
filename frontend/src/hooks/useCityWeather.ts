import { useState } from 'react';
import axios from 'axios';
import { CityWeatherResult, DetailedData } from '../types/weather';

const API_BASE_URL = 'http://localhost:8001';

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
        const response = await axios.post<{
          city_results: CityWeatherResult[];
          [key: string]: unknown;
        }>(`${API_BASE_URL}/api/weather/single-city`, {
          city: params.city.trim(),
          start: params.startDate,
          end: params.endDate,
          metric: params.metric,
        });

        setResults(response.data.city_results);
        setDetailedData(null);
      } else {
        // Detailed view: fetch all metrics
        console.log('DEBUG: Fetching detailed data for', params.city, params.startDate, params.endDate);

        const response = await axios.post<{
          temperature_data: CityWeatherResult[];
          wind_data: CityWeatherResult[];
          wind_gusts_data: CityWeatherResult[];
          precipitation_data: CityWeatherResult[];
          [key: string]: unknown;
        }>(`${API_BASE_URL}/api/weather/single-city-detailed`, {
          city: params.city.trim(),
          start: params.startDate,
          end: params.endDate,
        });

        console.log('DEBUG: API Response keys:', Object.keys(response.data));
        console.log('DEBUG: temperature_data length:', response.data.temperature_data?.length);
        console.log('DEBUG: wind_data length:', response.data.wind_data?.length);
        console.log('DEBUG: wind_gusts_data length:', response.data.wind_gusts_data?.length);
        console.log('DEBUG: precipitation_data length:', response.data.precipitation_data?.length);

        // Validate response structure
        const apiData = response.data;
        const temperatureData = apiData.temperature_data || [];
        const windData = apiData.wind_data || [];
        const windGustsData = apiData.wind_gusts_data || [];
        const precipitationData = apiData.precipitation_data || [];

        console.log('DEBUG: Validated data lengths:');
        console.log('  - temperature_data:', temperatureData.length);
        console.log('  - wind_data:', windData.length);
        console.log('  - wind_gusts_data:', windGustsData.length);
        console.log('  - precipitation_data:', precipitationData.length);

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
        console.log('DEBUG: DetailedData set complete with', Object.keys(detailedDataToSet).length, 'metric types');
        
        // 🔍 DEBUG: Wind gust data details
        console.log('🔍 DEBUG: Wind gust data in API response:', {
          length: windGustsData.length,
          sample: windGustsData.slice(0, 3),
          values: windGustsData.map(item => item.value).slice(0, 5)
        });
      }
    } catch (err) {
      console.log('ERROR: Fetch failed:', err);
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
        console.log('ERROR: Axios error - response status:', err.response?.status);
        console.log('ERROR: Axios error - response data:', err.response?.data);
      } else {
        setError('An unexpected error occurred');
        console.log('ERROR: Non-axios error:', err);
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