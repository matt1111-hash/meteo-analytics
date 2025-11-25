/**
 * Daily Records Calculation
 */

import {
  ExtremeRecord,
  DailyWeatherData,
  WIND_CATEGORIES,
  categorizeWindGust,
} from './types';

export function calculateDailyRecords(data: DailyWeatherData[]): ExtremeRecord[] {
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
