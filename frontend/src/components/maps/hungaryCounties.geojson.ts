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
        areaKm2: 525
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [19.15, 47.55], [19.20, 47.55], [19.22, 47.50], [19.20, 47.47],
          [19.15, 47.47], [19.12, 47.50], [19.15, 47.55]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Pest',
        nameHu: 'Pest',
        region: 'Közép-Magyarország',
        population: 1290000,
        areaKm2: 6393
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [19.12, 47.50], [19.15, 47.55], [19.22, 47.50], [19.45, 47.55],
          [19.65, 47.75], [19.85, 47.85], [20.00, 47.80], [20.05, 47.60],
          [19.90, 47.45], [19.70, 47.35], [19.50, 47.30], [19.30, 47.35],
          [19.12, 47.50]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Fejér',
        nameHu: 'Fejér',
        region: 'Közép-Dunántúl',
        population: 421000,
        areaKm2: 4359
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [18.40, 47.25], [18.65, 47.25], [18.80, 47.35], [18.95, 47.40],
          [19.15, 47.45], [19.30, 47.35], [19.30, 47.20], [19.10, 47.15],
          [18.85, 47.10], [18.55, 47.15], [18.40, 47.25]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Komárom-Esztergom',
        nameHu: 'Komárom-Esztergom',
        region: 'Közép-Dunántúl',
        population: 299000,
        areaKm2: 2265
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [18.05, 47.60], [18.30, 47.65], [18.55, 47.70], [18.70, 47.60],
          [18.65, 47.45], [18.45, 47.35], [18.20, 47.40], [18.05, 47.60]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Veszprém',
        nameHu: 'Veszprém',
        region: 'Közép-Dunántúl',
        population: 342000,
        areaKm2: 4613
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [17.55, 47.15], [17.80, 47.20], [18.10, 47.30], [18.40, 47.25],
          [18.55, 47.15], [18.45, 46.95], [18.20, 46.85], [17.90, 46.90],
          [17.60, 47.00], [17.55, 47.15]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Győr-Moson-Sopron',
        nameHu: 'Győr-Moson-Sopron',
        region: 'Nyugat-Dunántúl',
        population: 465000,
        areaKm2: 4089
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [16.80, 47.70], [17.20, 47.75], [17.55, 47.65], [18.05, 47.60],
          [18.20, 47.40], [18.00, 47.30], [17.65, 47.25], [17.30, 47.35],
          [16.95, 47.50], [16.80, 47.70]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Vas',
        nameHu: 'Vas',
        region: 'Nyugat-Dunántúl',
        population: 244000,
        areaKm2: 3357
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [16.40, 47.00], [16.80, 47.00], [17.05, 47.15], [17.30, 47.35],
          [16.95, 47.50], [16.70, 47.45], [16.45, 47.30], [16.40, 47.00]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Zala',
        nameHu: 'Zala',
        region: 'Nyugat-Dunántúl',
        population: 268000,
        areaKm2: 3844
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [16.45, 46.60], [16.85, 46.55], [17.10, 46.65], [17.30, 46.85],
          [17.50, 46.95], [17.45, 47.15], [17.05, 47.15], [16.80, 47.00],
          [16.45, 46.85], [16.45, 46.60]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Baranya',
        nameHu: 'Baranya',
        region: 'Dél-Dunántúl',
        population: 376000,
        areaKm2: 4430
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [18.00, 45.85], [18.35, 45.80], [18.60, 45.95], [18.80, 46.15],
          [18.85, 46.45], [18.65, 46.60], [18.45, 46.65], [18.15, 46.55],
          [17.95, 46.35], [18.00, 45.85]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Somogy',
        nameHu: 'Somogy',
        region: 'Dél-Dunántúl',
        population: 310000,
        areaKm2: 6036
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [17.45, 46.65], [17.50, 46.95], [17.70, 47.10], [17.90, 46.90],
          [18.20, 46.85], [18.45, 46.95], [18.45, 47.15], [18.20, 47.20],
          [17.90, 47.00], [17.70, 46.80], [17.45, 46.65]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Tolna',
        nameHu: 'Tolna',
        region: 'Dél-Dunántúl',
        population: 213000,
        areaKm2: 3703
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [18.45, 46.35], [18.65, 46.40], [18.85, 46.45], [18.90, 46.75],
          [18.75, 46.95], [18.45, 46.95], [18.35, 46.70], [18.45, 46.35]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Bács-Kiskun',
        nameHu: 'Bács-Kiskun',
        region: 'Dél-Alföld',
        population: 509000,
        areaKm2: 8445
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [19.10, 46.60], [19.50, 46.50], [19.90, 46.45], [20.30, 46.55],
          [20.50, 46.85], [20.35, 47.15], [20.05, 47.30], [19.70, 47.35],
          [19.50, 47.30], [19.30, 47.20], [19.10, 46.95], [19.10, 46.60]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Békés',
        nameHu: 'Békés',
        region: 'Dél-Alföld',
        population: 350000,
        areaKm2: 5630
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [20.35, 46.55], [20.90, 46.50], [21.30, 46.55], [21.45, 46.75],
          [21.35, 47.00], [21.10, 47.15], [20.75, 47.20], [20.50, 47.15],
          [20.35, 46.85], [20.35, 46.55]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Csongrád-Csanád',
        nameHu: 'Csongrád-Csanád',
        region: 'Dél-Alföld',
        population: 406000,
        areaKm2: 4263
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [20.05, 46.15], [20.50, 46.10], [20.95, 46.20], [21.20, 46.40],
          [21.30, 46.55], [20.90, 46.50], [20.50, 46.55], [20.30, 46.55],
          [20.05, 46.40], [20.05, 46.15]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Jász-Nagykun-Szolnok',
        nameHu: 'Jász-Nagykun-Szolnok',
        region: 'Észak-Alföld',
        population: 374000,
        areaKm2: 5582
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [20.05, 47.30], [20.35, 47.15], [20.50, 47.15], [20.75, 47.20],
          [20.90, 47.45], [20.80, 47.70], [20.55, 47.85], [20.25, 47.80],
          [20.00, 47.60], [20.05, 47.30]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Hajdú-Bihar',
        nameHu: 'Hajdú-Bihar',
        region: 'Észak-Alföld',
        population: 527000,
        areaKm2: 6211
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [21.10, 47.15], [21.45, 47.10], [21.90, 47.15], [22.20, 47.30],
          [22.30, 47.55], [22.15, 47.80], [21.85, 47.90], [21.50, 47.85],
          [21.20, 47.75], [21.10, 47.50], [21.10, 47.15]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Szabolcs-Szatmár-Bereg',
        nameHu: 'Szabolcs-Szatmár-Bereg',
        region: 'Észak-Alföld',
        population: 549000,
        areaKm2: 5936
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [22.15, 47.80], [22.45, 47.75], [22.80, 47.85], [22.70, 48.15],
          [22.40, 48.35], [22.00, 48.40], [21.75, 48.30], [21.70, 48.00],
          [21.85, 47.90], [22.15, 47.80]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Nógrád',
        nameHu: 'Nógrád',
        region: 'Észak-Magyarország',
        population: 194000,
        areaKm2: 2544
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [19.45, 47.95], [19.85, 47.90], [20.10, 48.00], [20.15, 48.20],
          [19.90, 48.35], [19.55, 48.30], [19.35, 48.15], [19.45, 47.95]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Heves',
        nameHu: 'Heves',
        region: 'Észak-Magyarország',
        population: 295000,
        areaKm2: 3637
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [20.00, 47.60], [20.25, 47.80], [20.55, 47.85], [20.60, 48.10],
          [20.40, 48.30], [20.00, 48.35], [19.80, 48.20], [19.85, 47.90],
          [20.00, 47.60]
        ]]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Borsod-Abaúj-Zemplén',
        nameHu: 'Borsod-Abaúj-Zemplén',
        region: 'Észak-Magyarország',
        population: 668000,
        areaKm2: 7247
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [20.00, 48.35], [20.40, 48.30], [20.85, 48.35], [21.25, 48.45],
          [21.65, 48.60], [21.75, 48.90], [21.45, 49.10], [20.95, 49.15],
          [20.55, 49.05], [20.20, 48.85], [19.95, 48.70], [19.80, 48.55],
          [20.00, 48.35]
        ]]
      }
    }
  ]
};

/**
 * Get county center point for zooming
 */
export function getCountyCenter(countyName: string): [number, number] | null {
  const feature = HUNGARY_COUNTIES_GEOJSON.features.find(
    f => f.properties.name === countyName
  );
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
