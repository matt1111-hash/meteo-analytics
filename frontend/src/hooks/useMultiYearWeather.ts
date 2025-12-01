import { useState } from 'react';
import axios from 'axios';
import { CityWeatherResult } from '../types/weather';

const API_BASE_URL = 'http://localhost:8001';

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
    console.log('Debug: fetchMultiYearData called with:', params);
    setLoading(true);
    setError(null);

    try {
      // Initialize yearly data structure
      const yearlyData: YearlyData = {};

      // Fetch data for each year
      const yearPromises = params.years.map(async (year) => {
        try {
          const response = await axios.post<{
            city_results: CityWeatherResult[];
            [key: string]: unknown;
          }>(`${API_BASE_URL}/api/weather/single-city`, {
            city: params.city.trim(),
            start: `${year}-01-01`,
            end: `${year}-12-31`,
            metric: params.metric,
          });

          return { year, data: response.data.city_results };
        } catch (err) {
          console.error(`Error fetching data for year ${year}:`, err);
          return { year, data: [] as CityWeatherResult[] };
        }
      });

      const yearResults = await Promise.all(yearPromises);

      // Process data into monthly aggregates
      yearResults.forEach(({ year, data }) => {
        const monthlyData: MonthlyData = {};

        // Use consistent English month names
        const englishMonthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

        // Initialize all months with null
        englishMonthNames.forEach(monthName => {
          monthlyData[monthName] = null;
        });

        // Initialize month sums and counts
        const monthSums: Record<string, number> = {};
        const monthCounts: Record<string, number> = {};

        // Aggregate data by month (using English month names)
        data.forEach((item) => {
          if (item.date && item.value !== null && !isNaN(item.value)) {
            const date = new Date(item.date);
            const monthIndex = date.getMonth(); // 0-11
            const monthName = englishMonthNames[monthIndex];

            if (!monthSums[monthName]) {
              monthSums[monthName] = 0;
              monthCounts[monthName] = 0;
            }
            monthSums[monthName] += item.value;
            monthCounts[monthName] += 1;
          }
        });

        console.log(`Debug: Year ${year} month counts:`, monthCounts);

        // Calculate averages
        Object.keys(monthSums).forEach((monthName) => {
          if (monthCounts[monthName] > 0) {
            monthlyData[monthName] = monthSums[monthName] / monthCounts[monthName];
          }
        });

        yearlyData[year] = monthlyData;
      });

      // Transform to chart data format - only show months that have data
      const allMonths = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ];

      // Check which months actually have data in the current year
      let months = allMonths;

      if (params.years.includes(new Date().getFullYear())) {
        // Find the latest month with actual data
        let latestMonthWithIndex = -1;

        Object.keys(yearlyData).forEach(year => {
          if (parseInt(year) === new Date().getFullYear()) {
            const yearData = yearlyData[parseInt(year)];
            allMonths.forEach((month, index) => {
              if (yearData[month] !== null && yearData[month] !== undefined) {
                latestMonthWithIndex = index;
              }
            });
          }
        });

        // Only show months up to the latest month with actual data
        if (latestMonthWithIndex >= 0) {
          months = allMonths.slice(0, latestMonthWithIndex + 1);
        }
      }

      const chartData: ChartData[] = months.map((month) => {
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