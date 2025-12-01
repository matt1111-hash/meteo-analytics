import { useState } from 'react';
import axios from 'axios';
import { CityWeatherResult } from '../types/weather';

const API_BASE_URL = 'http://localhost:8001';

interface DetailedData {
  wind: Array<{ date: string; windspeed: number | null; windgusts: number | null }>;
  precipitation: Array<{ date: string; precipitation: number | null }>;
}

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

        // Transform data for charts
        const windData = response.data.wind_data.map((item: CityWeatherResult, idx: number) => ({
          date: item.date,
          windspeed: item.value,
          windgusts: response.data.wind_gusts_data[idx]?.value || null,
        }));

        const precipData = response.data.precipitation_data.map((item: CityWeatherResult) => ({
          date: item.date,
          precipitation: item.value,
        }));

        setResults(response.data.temperature_data);
        setDetailedData({
          wind: windData,
          precipitation: precipData,
        });
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError('An unexpected error occurred');
      }
      setResults([]);
      setDetailedData(null);
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