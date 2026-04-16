/**
 * Trend Service - Climate trend analysis API
 */
import apiClient from './apiClient';

// =============================================================================
// TYPES
// =============================================================================

/**
 * Weather metrics available for trend analysis
 */
export type TrendMetric =
  | 'temperature_2m_max'
  | 'temperature_2m_min'
  | 'temperature_2m_mean'
  | 'precipitation_sum'
  | 'windspeed_10m_max'
  | 'windgusts_10m_max'
  | 'temperature_range';

/**
 * Request body for trend analysis
 */
export interface TrendAnalysisRequest {
  location: string;
  metric: TrendMetric;
  time_periods?: number[];
  start_date?: string;
  end_date?: string;
}

/**
 * Single time period trend result
 */
export interface TrendPeriodResult {
  time_period: number;
  years: number[];
  slope: number;
  slope_per_decade: number;
  r_squared: number;
  p_value: number;
  trend_direction: 'increasing' | 'decreasing' | 'stable';
  confidence_interval: [number, number];
  significance: 'highly_significant' | 'significant' | 'moderately_significant' | 'not_significant';
  yearly_means: number[];
  yearly_dates: string[];
  intercept: number;
  std_error: number;
  sample_size: number;
}

/**
 * Complete trend analysis result
 */
export interface TrendAnalysisResult {
  location_name: string;
  metric: string;
  periods: TrendPeriodResult[];
  execution_time: number;
  total_data_points: number;
  date_range: [string, string];
  data_quality_score: number;
  completeness_ratio: number;
  created_at: string;
  summary: {
    total_periods: number;
    trend_directions: {
      increasing: number;
      decreasing: number;
      stable: number;
    };
    avg_r_squared: number;
    significant_periods: number;
    location_name: string;
    metric: string;
  };
}

// =============================================================================
// API FUNCTIONS
// =============================================================================

/**
 * Calculate climate trend for a location

 * @param request - Trend analysis request
 * @returns Trend analysis result with statistics for each time period
 *
 * Example:
 * ```ts
 * const result = await fetchTrendAnalysis({
 *   location: "Budapest",
 *   metric: "temperature_2m_max",
 *   time_periods: [5, 10, 25, 55]
 * });
 * ```
 */
export const fetchTrendAnalysis = async (
  request: TrendAnalysisRequest
): Promise<TrendAnalysisResult> => {
  const response = await apiClient.post<TrendAnalysisResult>(
    '/api/analytics/trend',
    request
  );
  return response.data;
};

// =============================================================================
// CONSTANTS
// =============================================================================

/**
 * Available time periods for trend analysis (years)
 */
export const TIME_PERIODS = [5, 10, 25, 55] as const;

/**
 * Metric display names (Hungarian)
 */
export const METRIC_LABELS: Record<TrendMetric, string> = {
  temperature_2m_max: 'Maximum hőmérséklet',
  temperature_2m_min: 'Minimum hőmérséklet',
  temperature_2m_mean: 'Átlag hőmérséklet',
  precipitation_sum: 'Csapadékmennyiség',
  windspeed_10m_max: 'Szélsebesség',
  windgusts_10m_max: 'Széllökések',
  temperature_range: 'Hőmérséklet ingadozás',
};

/**
 * Metric units
 */
export const METRIC_UNITS: Record<TrendMetric, string> = {
  temperature_2m_max: '°C',
  temperature_2m_min: '°C',
  temperature_2m_mean: '°C',
  precipitation_sum: 'mm',
  windspeed_10m_max: 'km/h',
  windgusts_10m_max: 'km/h',
  temperature_range: '°C',
};

/**
 * Trend direction labels (Hungarian)
 */
export const TREND_DIRECTION_LABELS: Record<TrendPeriodResult['trend_direction'], string> = {
  increasing: 'Növekvő',
  decreasing: 'Csökkenő',
  stable: 'Stabil',
};

/**
 * Significance labels (Hungarian)
 */
export const SIGNIFICANCE_LABELS: Record<TrendPeriodResult['significance'], string> = {
  highly_significant: 'Nagyon szignifikáns',
  significant: 'Szignifikáns',
  moderately_significant: 'Mérsékelten szignifikáns',
  not_significant: 'Nem szignifikáns',
};
