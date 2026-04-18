/**
 * Extreme Weather Calculator - Type definitions and constants
 */

// ============================================================================
// TYPES
// ============================================================================

export interface ExtremeRecord {
  category: string;
  recordType: string;
  value: string;
  date: string;
  rawValue: number;
}

export interface DailyWeatherData {
  date: string;
  temperature_max: number | null;
  temperature_min: number | null;
  precipitation: number | null;
  windspeed: number | null;
  windgusts: number | null;
}

export interface AnomalyStatus {
  temperature: 'normal' | 'warning' | 'danger';
  precipitation: 'normal' | 'warning' | 'danger';
  wind: 'normal' | 'warning' | 'danger';
  temperatureMessage: string;
  precipitationMessage: string;
  windMessage: string;
}

export type AggregationType = 'daily' | 'monthly' | 'yearly';

export interface MonthlyAggregate {
  yearMonth: string;
  tempMax: number | null;
  tempMin: number | null;
  precipSum: number;
  windMax: number | null;
  count: number;
}

export interface YearlyAggregate {
  year: string;
  tempMax: number | null;
  tempMin: number | null;
  tempSum: number;
  tempCount: number;
  precipSum: number;
  windMax: number | null;
}

// ============================================================================
// WIND CATEGORIES (from Python WindGustsConstants)
// ============================================================================

export const WIND_THRESHOLDS = {
  NORMAL: 40,
  STRONG: 60,
  EXTREME: 90,
  HURRICANE: 120,
} as const;

export const WIND_CATEGORIES: Record<string, string> = {
  normal: 'Normal',
  strong: 'Strong',
  extreme: 'Extreme',
  hurricane: 'Hurricane',
};

export function categorizeWindGust(speed: number): string {
  if (speed >= WIND_THRESHOLDS.HURRICANE) return 'hurricane';
  if (speed >= WIND_THRESHOLDS.EXTREME) return 'extreme';
  if (speed >= WIND_THRESHOLDS.STRONG) return 'strong';
  return 'normal';
}

// ============================================================================
// ANOMALY DETECTION
// ============================================================================

export function detectAnomalies(data: DailyWeatherData[]): AnomalyStatus {
  const status: AnomalyStatus = {
    temperature: 'normal',
    precipitation: 'normal',
    wind: 'normal',
    temperatureMessage: 'Normal',
    precipitationMessage: 'Normal',
    windMessage: 'Normal',
  };

  if (data.length === 0) return status;

  // Temperature anomaly detection
  const temps = data
    .filter((d) => d.temperature_max !== null)
    .map((d) => d.temperature_max as number);

  if (temps.length > 0) {
    const maxTemp = Math.max(...temps);
    const minTemp = Math.min(...temps);

    if (maxTemp >= 40 || minTemp <= -20) {
      status.temperature = 'danger';
      status.temperatureMessage =
        maxTemp >= 40
          ? `Extreme heat: ${maxTemp.toFixed(1)}°C`
          : `Extreme cold: ${minTemp.toFixed(1)}°C`;
    } else if (maxTemp >= 35 || minTemp <= -10) {
      status.temperature = 'warning';
      status.temperatureMessage =
        maxTemp >= 35
          ? `High temperature: ${maxTemp.toFixed(1)}°C`
          : `Low temperature: ${minTemp.toFixed(1)}°C`;
    }
  }

  // Precipitation anomaly detection
  const precips = data
    .filter((d) => d.precipitation !== null)
    .map((d) => d.precipitation as number);

  if (precips.length > 0) {
    const maxPrecip = Math.max(...precips);
    const totalPrecip = precips.reduce((sum, p) => sum + p, 0);

    if (maxPrecip >= 50 || totalPrecip >= 200) {
      status.precipitation = 'danger';
      status.precipitationMessage = `Heavy rain: ${maxPrecip.toFixed(1)}mm/day`;
    } else if (maxPrecip >= 25 || totalPrecip >= 100) {
      status.precipitation = 'warning';
      status.precipitationMessage = `Moderate rain: ${maxPrecip.toFixed(1)}mm/day`;
    }
  }

  // Wind anomaly detection
  const winds = data
    .filter((d) => d.windgusts !== null || d.windspeed !== null)
    .map((d) => (d.windgusts ?? d.windspeed) as number);

  if (winds.length > 0) {
    const maxWind = Math.max(...winds);
    const category = categorizeWindGust(maxWind);

    if (category === 'hurricane' || category === 'extreme') {
      status.wind = 'danger';
      status.windMessage = `${WIND_CATEGORIES[category]}: ${maxWind.toFixed(1)}km/h`;
    } else if (category === 'strong') {
      status.wind = 'warning';
      status.windMessage = `Strong wind: ${maxWind.toFixed(1)}km/h`;
    }
  }

  return status;
}

// ============================================================================
// TEXT SUMMARY GENERATOR
// ============================================================================

export function generateTextSummary(records: ExtremeRecord[]): string {
  if (records.length === 0) return 'No data available for analysis.';

  const tempRecords = records.filter((r) => r.category === 'Temperature');
  const precipRecords = records.filter((r) => r.category === 'Precipitation');
  const windRecords = records.filter((r) => r.category === 'Wind');

  const lines: string[] = [];

  if (tempRecords.length > 0) {
    const hottest = tempRecords.find((r) => r.recordType.includes('Hottest'));
    const coldest = tempRecords.find((r) => r.recordType.includes('Coldest'));
    if (hottest && coldest) {
      lines.push(`Temperature: ${hottest.value} (max) to ${coldest.value} (min)`);
    }
  }

  if (precipRecords.length > 0) {
    const total = precipRecords.find((r) => r.recordType.includes('Total'));
    const wettest = precipRecords.find((r) => r.recordType.includes('Wettest'));
    if (total) {
      lines.push(`Precipitation: ${total.value} total`);
    } else if (wettest) {
      lines.push(`Precipitation: ${wettest.value} peak`);
    }
  }

  if (windRecords.length > 0) {
    const windiest = windRecords[0];
    lines.push(`Wind: ${windiest.value} max`);
  }

  return lines.join(' | ');
}
