/**
 * Yearly Records Calculation
 */

import {
  ExtremeRecord,
  DailyWeatherData,
  YearlyAggregate,
  WIND_CATEGORIES,
  categorizeWindGust,
} from './types';

export function calculateYearlyRecords(data: DailyWeatherData[]): ExtremeRecord[] {
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
      existing.tempMax =
        existing.tempMax !== null
          ? Math.max(existing.tempMax, d.temperature_max)
          : d.temperature_max;
      existing.tempSum += d.temperature_max;
      existing.tempCount++;
    }
    if (d.temperature_min !== null) {
      existing.tempMin =
        existing.tempMin !== null
          ? Math.min(existing.tempMin, d.temperature_min)
          : d.temperature_min;
    }
    if (d.precipitation !== null) {
      existing.precipSum += d.precipitation;
    }
    const windVal = d.windgusts ?? d.windspeed;
    if (windVal !== null) {
      existing.windMax = existing.windMax !== null ? Math.max(existing.windMax, windVal) : windVal;
    }
    yearlyMap.set(year, existing);
  }

  const years = Array.from(yearlyMap.values());

  // Hottest year (max temperature)
  const validTempMax = years.filter((y) => y.tempMax !== null);
  if (validTempMax.length > 0) {
    const hottest = validTempMax.reduce((max, y) => (y.tempMax! > max.tempMax! ? y : max));
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
    const coldest = validTempMin.reduce((min, y) => (y.tempMin! < min.tempMin! ? y : min));
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
    const wettest = years.reduce((max, y) => (y.precipSum > max.precipSum ? y : max));
    const driest = years.reduce((min, y) => (y.precipSum < min.precipSum ? y : min));
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
    const windiest = validWind.reduce((max, y) => (y.windMax! > max.windMax! ? y : max));
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
