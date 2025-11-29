/**
 * Hungarian cities preset list for CitySelector component
 */

export interface CityOption {
  name: string;
  country: string;
}

export const HUNGARIAN_CITIES: CityOption[] = [
  { name: 'Budapest', country: 'Hungary' },
  { name: 'Debrecen', country: 'Hungary' },
  { name: 'Szeged', country: 'Hungary' },
  { name: 'Miskolc', country: 'Hungary' },
  { name: 'Pécs', country: 'Hungary' },
  { name: 'Győr', country: 'Hungary' },
  { name: 'Nyíregyháza', country: 'Hungary' },
  { name: 'Kecskemét', country: 'Hungary' },
  { name: 'Székesfehérvár', country: 'Hungary' },
  { name: 'Szombathely', country: 'Hungary' },
  { name: 'Szolnok', country: 'Hungary' },
  { name: 'Eger', country: 'Hungary' },
  { name: 'Veszprém', country: 'Hungary' },
  { name: 'Sopron', country: 'Hungary' },
  { name: 'Zalaegerszeg', country: 'Hungary' },
];

export const EUROPEAN_CITIES: CityOption[] = [
  { name: 'Vienna', country: 'Austria' },
  { name: 'Prague', country: 'Czech Republic' },
  { name: 'Bratislava', country: 'Slovakia' },
  { name: 'Zagreb', country: 'Croatia' },
  { name: 'Ljubljana', country: 'Slovenia' },
  { name: 'Berlin', country: 'Germany' },
  { name: 'Munich', country: 'Germany' },
  { name: 'Paris', country: 'France' },
  { name: 'London', country: 'United Kingdom' },
  { name: 'Rome', country: 'Italy' },
];

/** Special value for custom input mode */
export const CUSTOM_CITY_VALUE = '__CUSTOM__';
