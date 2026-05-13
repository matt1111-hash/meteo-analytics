import { useState } from 'react';
import axios from 'axios';
import apiClient from '../services/apiClient';
import { logger } from '../utils/logger';
import { CityWeatherResult } from '../types/weather';

interface MonthlyData {
  [month: string]: number | null;
}

interface YearlyData {
  [year: number]: MonthlyData;
}

interface ChartData {
  month: string;
  [key: string]: string | number | null;
}

interface UseMultiYearWeatherParams {
  city: string;
  years: number[];
  metric: string;
}

export const useMultiYearWeather = () => {
  const [data, setData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMultiYearData = async (params: UseMultiYearWeatherParams): Promise<void> => {
    logger.debug('fetchMultiYearData called with:', params);
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post<{
        city: string;
        metric: string;
        years: Record<string, CityWeatherResult[]>;
      }>('/api/weather/multi-year-batch', {
        city: params.city.trim(),
        years: params.years,
        metric: params.metric,
      });

      const yearlyData: YearlyData = {};
      const englishMonthNames = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
      ];

      Object.entries(response.data.years).forEach(([yearStr, cityResults]) => {
        const year = parseInt(yearStr, 10);
        const monthlyData: MonthlyData = {};
        englishMonthNames.forEach((monthName) => {
          monthlyData[monthName] = null;
        });

        const monthSums: Record<string, number> = {};
        const monthCounts: Record<string, number> = {};

        (cityResults as CityWeatherResult[]).forEach((item) => {
          if (item.date && item.value !== null && !isNaN(item.value)) {
            const date = new Date(item.date);
            const monthIndex = date.getMonth();
            const monthName = englishMonthNames[monthIndex];

            if (!monthSums[monthName]) {
              monthSums[monthName] = 0;
              monthCounts[monthName] = 0;
            }
            monthSums[monthName] += item.value;
            monthCounts[monthName] += 1;
          }
        });

        Object.keys(monthSums).forEach((monthName) => {
          if (monthCounts[monthName] > 0) {
            monthlyData[monthName] = monthSums[monthName] / monthCounts[monthName];
          }
        });

        yearlyData[year] = monthlyData;
      });

      const chartData: ChartData[] = englishMonthNames.map((month) => {
        const dataPoint: ChartData = { month };
        params.years.forEach((year) => {
          const value = yearlyData[year]?.[month];
          dataPoint[year.toString()] = value !== undefined ? value : null;
        });
        return dataPoint;
      });

      setData(chartData);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError('An unexpected error occurred');
      }
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  const resetData = (): void => {
    setData([]);
    setError(null);
  };

  return {
    data,
    loading,
    error,
    fetchMultiYearData,
    resetData,
  };
};
