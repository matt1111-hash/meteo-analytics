/**
 * Hungarian Counties GeoJSON - Simplified boundaries
 *
 * This is a simplified version of Hungarian county boundaries for Leaflet display.
 * Coordinates are in [lon, lat] format (GeoJSON standard).
 *
 * Source: Simplified from official Hungarian county boundaries
 */

export interface HungaryCountyFeature {
  type: 'Feature';
  properties: {
    name: string;
    nameHu: string;
    region: string;
    population: number;
    areaKm2: number;
  };
  geometry: {
    type: 'Polygon';
    coordinates: number[][][];
  };
}

export interface HungaryCountiesGeoJSON {
  type: 'FeatureCollection';
  features: HungaryCountyFeature[];
}

/**
 * Simplified Hungarian county boundaries GeoJSON
 * Each county has simplified polygon coordinates for efficient rendering
 */
export const HUNGARY_COUNTIES_GEOJSON: HungaryCountiesGeoJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: {
        name: 'Budapest',
        nameHu: 'Budapest',
        region: 'Közép-Magyarország',
        population: 1752000,
        areaKm2: 525,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [19.15, 47.55],
            [19.2, 47.55],
            [19.22, 47.5],
            [19.2, 47.47],
            [19.15, 47.47],
            [19.12, 47.5],
            [19.15, 47.55],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Pest',
        nameHu: 'Pest',
        region: 'Közép-Magyarország',
        population: 1290000,
        areaKm2: 6393,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [19.12, 47.5],
            [19.15, 47.55],
            [19.22, 47.5],
            [19.45, 47.55],
            [19.65, 47.75],
            [19.85, 47.85],
            [20.0, 47.8],
            [20.05, 47.6],
            [19.9, 47.45],
            [19.7, 47.35],
            [19.5, 47.3],
            [19.3, 47.35],
            [19.12, 47.5],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Fejér',
        nameHu: 'Fejér',
        region: 'Közép-Dunántúl',
        population: 421000,
        areaKm2: 4359,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [18.4, 47.25],
            [18.65, 47.25],
            [18.8, 47.35],
            [18.95, 47.4],
            [19.15, 47.45],
            [19.3, 47.35],
            [19.3, 47.2],
            [19.1, 47.15],
            [18.85, 47.1],
            [18.55, 47.15],
            [18.4, 47.25],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Komárom-Esztergom',
        nameHu: 'Komárom-Esztergom',
        region: 'Közép-Dunántúl',
        population: 299000,
        areaKm2: 2265,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [18.05, 47.6],
            [18.3, 47.65],
            [18.55, 47.7],
            [18.7, 47.6],
            [18.65, 47.45],
            [18.45, 47.35],
            [18.2, 47.4],
            [18.05, 47.6],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Veszprém',
        nameHu: 'Veszprém',
        region: 'Közép-Dunántúl',
        population: 342000,
        areaKm2: 4613,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [17.55, 47.15],
            [17.8, 47.2],
            [18.1, 47.3],
            [18.4, 47.25],
            [18.55, 47.15],
            [18.45, 46.95],
            [18.2, 46.85],
            [17.9, 46.9],
            [17.6, 47.0],
            [17.55, 47.15],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Győr-Moson-Sopron',
        nameHu: 'Győr-Moson-Sopron',
        region: 'Nyugat-Dunántúl',
        population: 465000,
        areaKm2: 4089,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [16.8, 47.7],
            [17.2, 47.75],
            [17.55, 47.65],
            [18.05, 47.6],
            [18.2, 47.4],
            [18.0, 47.3],
            [17.65, 47.25],
            [17.3, 47.35],
            [16.95, 47.5],
            [16.8, 47.7],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Vas',
        nameHu: 'Vas',
        region: 'Nyugat-Dunántúl',
        population: 244000,
        areaKm2: 3357,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [16.4, 47.0],
            [16.8, 47.0],
            [17.05, 47.15],
            [17.3, 47.35],
            [16.95, 47.5],
            [16.7, 47.45],
            [16.45, 47.3],
            [16.4, 47.0],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Zala',
        nameHu: 'Zala',
        region: 'Nyugat-Dunántúl',
        population: 268000,
        areaKm2: 3844,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [16.45, 46.6],
            [16.85, 46.55],
            [17.1, 46.65],
            [17.3, 46.85],
            [17.5, 46.95],
            [17.45, 47.15],
            [17.05, 47.15],
            [16.8, 47.0],
            [16.45, 46.85],
            [16.45, 46.6],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Baranya',
        nameHu: 'Baranya',
        region: 'Dél-Dunántúl',
        population: 376000,
        areaKm2: 4430,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [18.0, 45.85],
            [18.35, 45.8],
            [18.6, 45.95],
            [18.8, 46.15],
            [18.85, 46.45],
            [18.65, 46.6],
            [18.45, 46.65],
            [18.15, 46.55],
            [17.95, 46.35],
            [18.0, 45.85],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Somogy',
        nameHu: 'Somogy',
        region: 'Dél-Dunántúl',
        population: 310000,
        areaKm2: 6036,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [17.45, 46.65],
            [17.5, 46.95],
            [17.7, 47.1],
            [17.9, 46.9],
            [18.2, 46.85],
            [18.45, 46.95],
            [18.45, 47.15],
            [18.2, 47.2],
            [17.9, 47.0],
            [17.7, 46.8],
            [17.45, 46.65],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Tolna',
        nameHu: 'Tolna',
        region: 'Dél-Dunántúl',
        population: 213000,
        areaKm2: 3703,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [18.45, 46.35],
            [18.65, 46.4],
            [18.85, 46.45],
            [18.9, 46.75],
            [18.75, 46.95],
            [18.45, 46.95],
            [18.35, 46.7],
            [18.45, 46.35],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Bács-Kiskun',
        nameHu: 'Bács-Kiskun',
        region: 'Dél-Alföld',
        population: 509000,
        areaKm2: 8445,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [19.1, 46.6],
            [19.5, 46.5],
            [19.9, 46.45],
            [20.3, 46.55],
            [20.5, 46.85],
            [20.35, 47.15],
            [20.05, 47.3],
            [19.7, 47.35],
            [19.5, 47.3],
            [19.3, 47.2],
            [19.1, 46.95],
            [19.1, 46.6],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Békés',
        nameHu: 'Békés',
        region: 'Dél-Alföld',
        population: 350000,
        areaKm2: 5630,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [20.35, 46.55],
            [20.9, 46.5],
            [21.3, 46.55],
            [21.45, 46.75],
            [21.35, 47.0],
            [21.1, 47.15],
            [20.75, 47.2],
            [20.5, 47.15],
            [20.35, 46.85],
            [20.35, 46.55],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Csongrád-Csanád',
        nameHu: 'Csongrád-Csanád',
        region: 'Dél-Alföld',
        population: 406000,
        areaKm2: 4263,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [20.05, 46.15],
            [20.5, 46.1],
            [20.95, 46.2],
            [21.2, 46.4],
            [21.3, 46.55],
            [20.9, 46.5],
            [20.5, 46.55],
            [20.3, 46.55],
            [20.05, 46.4],
            [20.05, 46.15],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Jász-Nagykun-Szolnok',
        nameHu: 'Jász-Nagykun-Szolnok',
        region: 'Észak-Alföld',
        population: 374000,
        areaKm2: 5582,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [20.05, 47.3],
            [20.35, 47.15],
            [20.5, 47.15],
            [20.75, 47.2],
            [20.9, 47.45],
            [20.8, 47.7],
            [20.55, 47.85],
            [20.25, 47.8],
            [20.0, 47.6],
            [20.05, 47.3],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Hajdú-Bihar',
        nameHu: 'Hajdú-Bihar',
        region: 'Észak-Alföld',
        population: 527000,
        areaKm2: 6211,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [21.1, 47.15],
            [21.45, 47.1],
            [21.9, 47.15],
            [22.2, 47.3],
            [22.3, 47.55],
            [22.15, 47.8],
            [21.85, 47.9],
            [21.5, 47.85],
            [21.2, 47.75],
            [21.1, 47.5],
            [21.1, 47.15],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Szabolcs-Szatmár-Bereg',
        nameHu: 'Szabolcs-Szatmár-Bereg',
        region: 'Észak-Alföld',
        population: 549000,
        areaKm2: 5936,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [22.15, 47.8],
            [22.45, 47.75],
            [22.8, 47.85],
            [22.7, 48.15],
            [22.4, 48.35],
            [22.0, 48.4],
            [21.75, 48.3],
            [21.7, 48.0],
            [21.85, 47.9],
            [22.15, 47.8],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Nógrád',
        nameHu: 'Nógrád',
        region: 'Észak-Magyarország',
        population: 194000,
        areaKm2: 2544,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [19.45, 47.95],
            [19.85, 47.9],
            [20.1, 48.0],
            [20.15, 48.2],
            [19.9, 48.35],
            [19.55, 48.3],
            [19.35, 48.15],
            [19.45, 47.95],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Heves',
        nameHu: 'Heves',
        region: 'Észak-Magyarország',
        population: 295000,
        areaKm2: 3637,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [20.0, 47.6],
            [20.25, 47.8],
            [20.55, 47.85],
            [20.6, 48.1],
            [20.4, 48.3],
            [20.0, 48.35],
            [19.8, 48.2],
            [19.85, 47.9],
            [20.0, 47.6],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        name: 'Borsod-Abaúj-Zemplén',
        nameHu: 'Borsod-Abaúj-Zemplén',
        region: 'Észak-Magyarország',
        population: 668000,
        areaKm2: 7247,
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [20.0, 48.35],
            [20.4, 48.3],
            [20.85, 48.35],
            [21.25, 48.45],
            [21.65, 48.6],
            [21.75, 48.9],
            [21.45, 49.1],
            [20.95, 49.15],
            [20.55, 49.05],
            [20.2, 48.85],
            [19.95, 48.7],
            [19.8, 48.55],
            [20.0, 48.35],
          ],
        ],
      },
    },
  ],
};

/**
 * Get county center point for zooming
 */
export function getCountyCenter(countyName: string): [number, number] | null {
  const feature = HUNGARY_COUNTIES_GEOJSON.features.find((f) => f.properties.name === countyName);
  if (!feature) return null;

  const coords = feature.geometry.coordinates[0];
  const lon = coords.reduce((sum, c) => sum + c[0], 0) / coords.length;
  const lat = coords.reduce((sum, c) => sum + c[1], 0) / coords.length;

  return [lat, lon];
}

/**
 * Get Hungary center point
 */
export const HUNGARY_CENTER: [number, number] = [47.25, 19.15];

/**
 * Default zoom levels
 */
export const DEFAULT_ZOOM = 7;
export const COUNTY_ZOOM = 9;
