/**
 * Extreme Weather Calculator - Main entry point
 * Re-exports all types and functions
 */

// Re-export types
export type {
  ExtremeRecord,
  DailyWeatherData,
  AnomalyStatus,
  AggregationType,
  MonthlyAggregate,
  YearlyAggregate,
} from './types';

// Re-export constants and utility functions
export {
  WIND_THRESHOLDS,
  WIND_CATEGORIES,
  categorizeWindGust,
  detectAnomalies,
  generateTextSummary,
} from './types';

// Import calculation functions
import { calculateDailyRecords } from './dailyRecords';
import { calculateMonthlyRecords } from './monthlyRecords';
import { calculateYearlyRecords } from './yearlyRecords';
import { DailyWeatherData, AggregationType, ExtremeRecord } from './types';

// Re-export individual calculators
export { calculateDailyRecords } from './dailyRecords';
export { calculateMonthlyRecords } from './monthlyRecords';
export { calculateYearlyRecords } from './yearlyRecords';

/**
 * Main calculation function - delegates to appropriate calculator
 */
export function calculateExtremes(
  data: DailyWeatherData[],
  aggregation: AggregationType = 'daily'
): ExtremeRecord[] {
  if (data.length === 0) return [];

  switch (aggregation) {
    case 'monthly':
      return calculateMonthlyRecords(data);
    case 'yearly':
      return calculateYearlyRecords(data);
    case 'daily':
    default:
      return calculateDailyRecords(data);
  }
}
