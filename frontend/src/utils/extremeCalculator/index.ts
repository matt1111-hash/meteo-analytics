/**
 * Extreme Weather Calculator - Main entry point
 * Re-exports all types and functions
 */

// Imports first (alphabetical order)
import { calculateDailyRecords } from './dailyRecords';
import { calculateMonthlyRecords } from './monthlyRecords';
import { AggregationType, DailyWeatherData, ExtremeRecord } from './types';
import { calculateYearlyRecords } from './yearlyRecords';

// Re-export types
export type {
  AggregationType,
  AnomalyStatus,
  DailyWeatherData,
  ExtremeRecord,
  MonthlyAggregate,
  YearlyAggregate,
} from './types';

// Re-export constants and utility functions
export {
  categorizeWindGust,
  detectAnomalies,
  generateTextSummary,
  WIND_CATEGORIES,
  WIND_THRESHOLDS,
} from './types';

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
