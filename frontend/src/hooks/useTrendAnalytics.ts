/**
 * useTrendAnalytics Hook - Fetch trend analysis data
 */
import { useState } from 'react';
import axios from 'axios';
import {
  fetchTrendAnalysis,
  TrendAnalysisRequest,
  TrendAnalysisResult,
} from '../services/trendService';

interface UseTrendAnalyticsReturn {
  data: TrendAnalysisResult | null;
  loading: boolean;
  error: string | null;
  fetchTrendData: (request: TrendAnalysisRequest) => Promise<void>;
  resetData: () => void;
}

export const useTrendAnalytics = (): UseTrendAnalyticsReturn => {
  const [data, setData] = useState<TrendAnalysisResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTrendData = async (request: TrendAnalysisRequest): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const result = await fetchTrendAnalysis(request);
      setData(result);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError('An unexpected error occurred');
      }
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const resetData = (): void => {
    setData(null);
    setError(null);
  };

  return {
    data,
    loading,
    error,
    fetchTrendData,
    resetData,
  };
};
