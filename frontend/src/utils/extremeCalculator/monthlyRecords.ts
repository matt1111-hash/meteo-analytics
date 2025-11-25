/**
 * Monthly Records Calculation
 */

import {
  ExtremeRecord,
  DailyWeatherData,
  MonthlyAggregate,
  WIND_CATEGORIES,
  categorizeWindGust,
} from './types';

export function calculateMonthlyRecords(data: DailyWeatherData[]): ExtremeRecord[] {
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
