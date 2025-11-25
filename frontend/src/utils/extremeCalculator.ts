/**
 * Extreme Weather Calculator - TypeScript utility
 * Calculates weather records from daily time series data
 */

import { CityWeatherResult } from '../types/weather';

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

// ============================================================================
// WIND CATEGORIES (from Python WindGustsConstants)
// ============================================================================

const WIND_THRESHOLDS = {
  NORMAL: 40,
  STRONG: 60,
  EXTREME: 90,
  HURRICANE: 120,
};

const WIND_CATEGORIES: Record<string, string> = {
  normal: 'Normal',
  strong: 'Strong',
  extreme: 'Extreme',
  hurricane: 'Hurricane',
};

function categorizeWindGust(speed: number): string {
  if (speed >= WIND_THRESHOLDS.HURRICANE) return 'hurricane';
  if (speed >= WIND_THRESHOLDS.EXTREME) return 'extreme';
  if (speed >= WIND_THRESHOLDS.STRONG) return 'strong';
  return 'normal';
}

// ============================================================================
// DATA TRANSFORMATION
// ============================================================================

export function transformApiData(results: CityWeatherResult[]): DailyWeatherData[] {
  const dataMap = new Map<string, DailyWeatherData>();

  for (const result of results) {
    const existing = dataMap.get(result.date) || {
      date: result.date,
      temperature_max: null,
      temperature_min: null,
      precipitation: null,
      windspeed: null,
      windgusts: null,
    };

    const metric = result.metric;
    const value = result.value;

    if (metric === 'temperature_2m_max') {
      existing.temperature_max = value;
    } else if (metric === 'temperature_2m_min') {
      existing.temperature_min = value;
    } else if (metric === 'temperature_2m_mean') {
      existing.temperature_max = existing.temperature_max ?? value;
      existing.temperature_min = existing.temperature_min ?? value;
    } else if (metric === 'precipitation_sum') {
      existing.precipitation = value;
    } else if (metric === 'windspeed_10m_max') {
      existing.windspeed = value;
    } else if (metric === 'windgusts_10m_max') {
      existing.windgusts = value;
    }

    dataMap.set(result.date, existing);
  }

  return Array.from(dataMap.values()).sort((a, b) => a.date.localeCompare(b.date));
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
      status.temperatureMessage = maxTemp >= 40
        ? `Extreme heat: ${maxTemp.toFixed(1)}°C`
        : `Extreme cold: ${minTemp.toFixed(1)}°C`;
    } else if (maxTemp >= 35 || minTemp <= -10) {
      status.temperature = 'warning';
      status.temperatureMessage = maxTemp >= 35
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
// DAILY RECORDS CALCULATION
// ============================================================================

function calculateDailyRecords(data: DailyWeatherData[]): ExtremeRecord[] {
  const records: ExtremeRecord[] = [];

  // Temperature records
  const validTempMax = data.filter((d) => d.temperature_max !== null);
  const validTempMin = data.filter((d) => d.temperature_min !== null);

  if (validTempMax.length > 0) {
    const hottest = validTempMax.reduce((max, d) =>
      (d.temperature_max! > max.temperature_max!) ? d : max
    );
    records.push({
      category: 'Temperature',
      recordType: 'Hottest Day',
      value: `${hottest.temperature_max!.toFixed(1)}°C`,
      date: hottest.date,
      rawValue: hottest.temperature_max!,
    });
  }

  if (validTempMin.length > 0) {
    const coldest = validTempMin.reduce((min, d) =>
      (d.temperature_min! < min.temperature_min!) ? d : min
    );
    records.push({
      category: 'Temperature',
      recordType: 'Coldest Day',
      value: `${coldest.temperature_min!.toFixed(1)}°C`,
      date: coldest.date,
      rawValue: coldest.temperature_min!,
    });
  }

  // Temperature range
  const validRanges = data.filter(
    (d) => d.temperature_max !== null && d.temperature_min !== null
  );
  if (validRanges.length > 0) {
    const maxRange = validRanges.reduce((max, d) => {
      const range = d.temperature_max! - d.temperature_min!;
      const maxRangeValue = max.temperature_max! - max.temperature_min!;
      return range > maxRangeValue ? d : max;
    });
    const rangeValue = maxRange.temperature_max! - maxRange.temperature_min!;
    records.push({
      category: 'Temperature',
      recordType: 'Largest Daily Range',
      value: `${rangeValue.toFixed(1)}°C`,
      date: maxRange.date,
      rawValue: rangeValue,
    });
  }

  // Precipitation records
  const validPrecip = data.filter((d) => d.precipitation !== null);
  if (validPrecip.length > 0) {
    const wettest = validPrecip.reduce((max, d) =>
      (d.precipitation! > max.precipitation!) ? d : max
    );
    records.push({
      category: 'Precipitation',
      recordType: 'Wettest Day',
      value: `${wettest.precipitation!.toFixed(1)}mm`,
      date: wettest.date,
      rawValue: wettest.precipitation!,
    });

    const totalPrecip = validPrecip.reduce((sum, d) => sum + d.precipitation!, 0);
    const dryDays = validPrecip.filter((d) => d.precipitation! <= 0.1).length;
    records.push({
      category: 'Precipitation',
      recordType: 'Total Precipitation',
      value: `${totalPrecip.toFixed(1)}mm`,
      date: `${validPrecip.length} days`,
      rawValue: totalPrecip,
    });
    records.push({
      category: 'Precipitation',
      recordType: 'Dry Days',
      value: `${dryDays} days`,
      date: '-',
      rawValue: dryDays,
    });
  }

  // Wind records
  const validWind = data.filter((d) => d.windgusts !== null || d.windspeed !== null);
  if (validWind.length > 0) {
    const windiest = validWind.reduce((max, d) => {
      const windVal = d.windgusts ?? d.windspeed ?? 0;
      const maxWindVal = max.windgusts ?? max.windspeed ?? 0;
      return windVal > maxWindVal ? d : max;
    });
    const maxWindValue = windiest.windgusts ?? windiest.windspeed ?? 0;
    const category = categorizeWindGust(maxWindValue);
    records.push({
      category: 'Wind',
      recordType: `Strongest Gust (${WIND_CATEGORIES[category]})`,
      value: `${maxWindValue.toFixed(1)}km/h`,
      date: windiest.date,
      rawValue: maxWindValue,
    });
  }

  return records;
}

// ============================================================================
// MONTHLY RECORDS CALCULATION
// ============================================================================

interface MonthlyAggregate {
  yearMonth: string;
  tempMax: number | null;
  tempMin: number | null;
  precipSum: number;
  windMax: number | null;
  count: number;
}

function calculateMonthlyRecords(data: DailyWeatherData[]): ExtremeRecord[] {
  const records: ExtremeRecord[] = [];
  const monthlyMap = new Map<string, MonthlyAggregate>();

  for (const d of data) {
    const yearMonth = d.date.substring(0, 7); // "2025-11"
    const existing = monthlyMap.get(yearMonth) || {
      yearMonth,
      tempMax: null,
      tempMin: null,
      precipSum: 0,
      windMax: null,
      count: 0,
    };

    if (d.temperature_max !== null) {
      existing.tempMax = existing.tempMax !== null
        ? Math.max(existing.tempMax, d.temperature_max)
        : d.temperature_max;
    }
    if (d.temperature_min !== null) {
      existing.tempMin = existing.tempMin !== null
        ? Math.min(existing.tempMin, d.temperature_min)
        : d.temperature_min;
    }
    if (d.precipitation !== null) {
      existing.precipSum += d.precipitation;
    }
    const windVal = d.windgusts ?? d.windspeed;
    if (windVal !== null) {
      existing.windMax = existing.windMax !== null
        ? Math.max(existing.windMax, windVal)
        : windVal;
    }
    existing.count++;
    monthlyMap.set(yearMonth, existing);
  }

  const months = Array.from(monthlyMap.values());

  // Hottest month
  const validTempMax = months.filter((m) => m.tempMax !== null);
  if (validTempMax.length > 0) {
    const hottest = validTempMax.reduce((max, m) =>
      m.tempMax! > max.tempMax! ? m : max
    );
    records.push({
      category: 'Temperature',
      recordType: 'Hottest Month',
      value: `${hottest.tempMax!.toFixed(1)}°C`,
      date: hottest.yearMonth,
      rawValue: hottest.tempMax!,
    });
  }

  // Coldest month
  const validTempMin = months.filter((m) => m.tempMin !== null);
  if (validTempMin.length > 0) {
    const coldest = validTempMin.reduce((min, m) =>
      m.tempMin! < min.tempMin! ? m : min
    );
    records.push({
      category: 'Temperature',
      recordType: 'Coldest Month',
      value: `${coldest.tempMin!.toFixed(1)}°C`,
      date: coldest.yearMonth,
      rawValue: coldest.tempMin!,
    });
  }

  // Wettest/Driest month
  if (months.length > 0) {
    const wettest = months.reduce((max, m) =>
      m.precipSum > max.precipSum ? m : max
    );
    const driest = months.reduce((min, m) =>
      m.precipSum < min.precipSum ? m : min
    );
    records.push({
      category: 'Precipitation',
      recordType: 'Wettest Month',
      value: `${wettest.precipSum.toFixed(1)}mm`,
      date: wettest.yearMonth,
      rawValue: wettest.precipSum,
    });
    records.push({
      category: 'Precipitation',
      recordType: 'Driest Month',
      value: `${driest.precipSum.toFixed(1)}mm`,
      date: driest.yearMonth,
      rawValue: driest.precipSum,
    });
  }

  // Windiest month
  const validWind = months.filter((m) => m.windMax !== null);
  if (validWind.length > 0) {
    const windiest = validWind.reduce((max, m) =>
      m.windMax! > max.windMax! ? m : max
    );
    const category = categorizeWindGust(windiest.windMax!);
    records.push({
      category: 'Wind',
      recordType: `Windiest Month (${WIND_CATEGORIES[category]})`,
      value: `${windiest.windMax!.toFixed(1)}km/h`,
      date: windiest.yearMonth,
      rawValue: windiest.windMax!,
    });
  }

  return records;
}

// ============================================================================
// YEARLY RECORDS CALCULATION
// ============================================================================

interface YearlyAggregate {
  year: string;
  tempMax: number | null;
  tempMin: number | null;
  tempSum: number;
  tempCount: number;
  precipSum: number;
  windMax: number | null;
}

function calculateYearlyRecords(data: DailyWeatherData[]): ExtremeRecord[] {
  const records: ExtremeRecord[] = [];
  const yearlyMap = new Map<string, YearlyAggregate>();

  for (const d of data) {
    const year = d.date.substring(0, 4); // "2025"
    const existing = yearlyMap.get(year) || {
      year,
      tempMax: null,
      tempMin: null,
      tempSum: 0,
      tempCount: 0,
      precipSum: 0,
      windMax: null,
    };

    if (d.temperature_max !== null) {
      existing.tempMax = existing.tempMax !== null
        ? Math.max(existing.tempMax, d.temperature_max)
        : d.temperature_max;
      existing.tempSum += d.temperature_max;
      existing.tempCount++;
    }
    if (d.temperature_min !== null) {
      existing.tempMin = existing.tempMin !== null
        ? Math.min(existing.tempMin, d.temperature_min)
        : d.temperature_min;
    }
    if (d.precipitation !== null) {
      existing.precipSum += d.precipitation;
    }
    const windVal = d.windgusts ?? d.windspeed;
    if (windVal !== null) {
      existing.windMax = existing.windMax !== null
        ? Math.max(existing.windMax, windVal)
        : windVal;
    }
    yearlyMap.set(year, existing);
  }

  const years = Array.from(yearlyMap.values());

  // Hottest year (max temperature)
  const validTempMax = years.filter((y) => y.tempMax !== null);
  if (validTempMax.length > 0) {
    const hottest = validTempMax.reduce((max, y) =>
      y.tempMax! > max.tempMax! ? y : max
    );
    records.push({
      category: 'Temperature',
      recordType: 'Hottest Year',
      value: `${hottest.tempMax!.toFixed(1)}°C`,
      date: hottest.year,
      rawValue: hottest.tempMax!,
    });

    // Warmest average year
    const withAvg = validTempMax.filter((y) => y.tempCount > 0);
    if (withAvg.length > 0) {
      const warmestAvg = withAvg.reduce((max, y) => {
        const avg = y.tempSum / y.tempCount;
        const maxAvg = max.tempSum / max.tempCount;
        return avg > maxAvg ? y : max;
      });
      const avgTemp = warmestAvg.tempSum / warmestAvg.tempCount;
      records.push({
        category: 'Temperature',
        recordType: 'Warmest Average Year',
        value: `${avgTemp.toFixed(1)}°C`,
        date: warmestAvg.year,
        rawValue: avgTemp,
      });
    }
  }

  // Coldest year
  const validTempMin = years.filter((y) => y.tempMin !== null);
  if (validTempMin.length > 0) {
    const coldest = validTempMin.reduce((min, y) =>
      y.tempMin! < min.tempMin! ? y : min
    );
    records.push({
      category: 'Temperature',
      recordType: 'Coldest Year',
      value: `${coldest.tempMin!.toFixed(1)}°C`,
      date: coldest.year,
      rawValue: coldest.tempMin!,
    });
  }

  // Wettest/Driest year
  if (years.length > 0) {
    const wettest = years.reduce((max, y) =>
      y.precipSum > max.precipSum ? y : max
    );
    const driest = years.reduce((min, y) =>
      y.precipSum < min.precipSum ? y : min
    );
    records.push({
      category: 'Precipitation',
      recordType: 'Wettest Year',
      value: `${wettest.precipSum.toFixed(0)}mm`,
      date: wettest.year,
      rawValue: wettest.precipSum,
    });
    records.push({
      category: 'Precipitation',
      recordType: 'Driest Year',
      value: `${driest.precipSum.toFixed(0)}mm`,
      date: driest.year,
      rawValue: driest.precipSum,
    });
  }

  // Windiest year
  const validWind = years.filter((y) => y.windMax !== null);
  if (validWind.length > 0) {
    const windiest = validWind.reduce((max, y) =>
      y.windMax! > max.windMax! ? y : max
    );
    const category = categorizeWindGust(windiest.windMax!);
    records.push({
      category: 'Wind',
      recordType: `Windiest Year (${WIND_CATEGORIES[category]})`,
      value: `${windiest.windMax!.toFixed(1)}km/h`,
      date: windiest.year,
      rawValue: windiest.windMax!,
    });
  }

  return records;
}

// ============================================================================
// MAIN EXPORT FUNCTION
// ============================================================================

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
