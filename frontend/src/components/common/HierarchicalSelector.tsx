import React, { useState, useEffect } from 'react';
import {
  getHungarianRegions,
  getHungarianCounties,
  getHungarianSettlements,
  HungarianSettlement,
  RegionsResponse,
  CountiesResponse,
  SettlementsResponse,
} from '../../services/hungaryService';
import { logger } from '../../utils/logger';
import './HierarchicalSelector.css';

// =============================================================================
// TYPES
// =============================================================================

export interface HierarchicalSelection {
  region?: string;
  county?: string;
  settlement?: string;
}

export interface SelectedLocation {
  region?: string;
  county?: string;
  settlement: string;
  coordinates?: {
    lat: number;
    lon: number;
  };
  population?: number;
}

interface HierarchicalSelectorProps {
  onLocationSelect: (location: SelectedLocation) => void;
  disabled?: boolean;
  className?: string;
  initialRegion?: string;
  initialCounty?: string;
  initialSettlement?: string;
}

// =============================================================================
// REGION TO COUNTIES MAPPING
// =============================================================================

const REGION_COUNTY_MAP: Record<string, string[]> = {
  'Közép-Magyarország': ['Budapest', 'Pest'],
  'Közép-Dunántúl': ['Fejér', 'Komárom-Esztergom', 'Veszprém'],
  'Nyugat-Dunántúl': ['Győr-Moson-Sopron', 'Vas', 'Zala'],
  'Dél-Dunántúl': ['Baranya', 'Somogy', 'Tolna'],
  'Észak-Magyarország': ['Borsod-Abaúj-Zemplén', 'Heves', 'Nógrád'],
  'Észak-Alföld': ['Hajdú-Bihar', 'Jász-Nagykun-Szolnok', 'Szabolcs-Szatmár-Bereg'],
  'Dél-Alföld': ['Bács-Kiskun', 'Békés', 'Csongrád-Csanád'],
};

// =============================================================================
// COMPONENT
// =============================================================================

const HierarchicalSelector: React.FC<HierarchicalSelectorProps> = ({
  onLocationSelect,
  disabled = false,
  className = '',
  initialRegion,
  initialCounty,
  initialSettlement,
}) => {
  // State for each level
  const [selectedRegion, setSelectedRegion] = useState<string | undefined>(initialRegion);
  const [selectedCounty, setSelectedCounty] = useState<string | undefined>(initialCounty);
  const [selectedSettlement, setSelectedSettlement] = useState<string | undefined>(initialSettlement);

  // Data state
  const [regions, setRegions] = useState<string[]>([]);
  const [counties, setCounties] = useState<string[]>([]);
  const [settlements, setSettlements] = useState<HungarianSettlement[]>([]);

  // Loading states
  const [loadingRegions, setLoadingRegions] = useState(false);
  const [loadingCounties, setLoadingCounties] = useState(false);
  const [loadingSettlements, setLoadingSettlements] = useState(false);

  // Error states
  const [regionError, setRegionError] = useState<string | null>(null);
  const [countyError, setCountyError] = useState<string | null>(null);
  const [settlementError, setSettlementError] = useState<string | null>(null);

  // =============================================================================
  // DATA FETCHING
  // =============================================================================

  // Fetch regions on mount
  useEffect(() => {
    const fetchRegions = async () => {
      setLoadingRegions(true);
      setRegionError(null);
      try {
        const data: RegionsResponse = await getHungarianRegions();
        setRegions(data.regions);
      } catch (err) {
        logger.error('Error fetching regions:', err);
        setRegionError('Nem sikerült betölteni a régiókat');
      } finally {
        setLoadingRegions(false);
      }
    };

    fetchRegions();
  }, []);

  // Fetch counties when region changes
  useEffect(() => {
    if (!selectedRegion) {
      setCounties([]);
      setSelectedCounty(undefined);
      setSelectedSettlement(undefined);
      setSettlements([]);
      return;
    }

    const fetchCounties = async () => {
      setLoadingCounties(true);
      setCountyError(null);
      try {
        const data: CountiesResponse = await getHungarianCounties();
        const regionCounties = REGION_COUNTY_MAP[selectedRegion] || [];
        const filteredCounties = data.counties.filter((county) =>
          regionCounties.includes(county)
        );
        setCounties(filteredCounties);
      } catch (err) {
        logger.error('Error fetching counties:', err);
        setCountyError('Nem sikerült betölteni a megyéket');
      } finally {
        setLoadingCounties(false);
      }
    };

    fetchCounties();
  }, [selectedRegion]);

  // Fetch settlements when county changes
  useEffect(() => {
    if (!selectedCounty) {
      setSettlements([]);
      setSelectedSettlement(undefined);
      return;
    }

    const fetchSettlements = async () => {
      setLoadingSettlements(true);
      setSettlementError(null);
      try {
        const data: SettlementsResponse = await getHungarianSettlements({
          county: selectedCounty,
          limit: 500,
        });
        setSettlements(data.settlements);
      } catch (err) {
        logger.error('Error fetching settlements:', err);
        setSettlementError('Nem sikerült betölteni a településeket');
      } finally {
        setLoadingSettlements(false);
      }
    };

    fetchSettlements();
  }, [selectedCounty]);

  // =============================================================================
  // HANDLERS
  // =============================================================================

  const handleRegionChange = (region: string) => {
    setSelectedRegion(region);
    setSelectedCounty(undefined);
    setSelectedSettlement(undefined);
  };

  const handleCountyChange = (county: string) => {
    setSelectedCounty(county);
    setSelectedSettlement(undefined);
  };

  const handleSettlementChange = (settlementName: string) => {
    setSelectedSettlement(settlementName);

    const settlement = settlements.find((s) => s.name === settlementName);
    if (settlement) {
      onLocationSelect({
        region: selectedRegion,
        county: selectedCounty,
        settlement: settlement.name,
        coordinates: settlement.coordinates || undefined,
        population: settlement.population || undefined,
      });
    }
  };

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const renderSelect = (
    label: string,
    value: string | undefined,
    onChange: (val: string) => void,
    options: string[],
    loading: boolean,
    error: string | null,
    disabled: boolean,
    id: string
  ) => (
    <div className="hierarchical-select-wrapper">
      <label htmlFor={id} className="hierarchical-label">
        {label}
      </label>
      <div className="hierarchical-select-container">
        <select
          id={id}
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled || loading}
          className="hierarchical-select"
        >
          <option value="">-- Válassz --</option>
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        {loading && (
          <div className="hierarchical-spinner" aria-hidden="true">
            <div className="spinner-small"></div>
          </div>
        )}
      </div>
      {error && <div className="hierarchical-error">{error}</div>}
    </div>
  );

  // =============================================================================
  // RENDER
  // =============================================================================

  return (
    <div className={`hierarchical-selector ${className}`}>
      <div className="hierarchical-header">
        <h3 className="hierarchical-title">Magyarországi településválasztó</h3>
        <p className="hierarchical-subtitle">
          Válassz régiót, majd megyét és végül települést
        </p>
      </div>

      <div className="hierarchical-levels">
        {/* Region */}
        {renderSelect(
          'Régió',
          selectedRegion,
          handleRegionChange,
          regions,
          loadingRegions,
          regionError,
          disabled,
          'hierarchical-region'
        )}

        {/* County */}
        {renderSelect(
          'Megye',
          selectedCounty,
          handleCountyChange,
          counties,
          loadingCounties,
          countyError,
          disabled || !selectedRegion,
          'hierarchical-county'
        )}

        {/* Settlement */}
        {renderSelect(
          'Település',
          selectedSettlement,
          handleSettlementChange,
          settlements.map((s) => s.name),
          loadingSettlements,
          settlementError,
          disabled || !selectedCounty,
          'hierarchical-settlement'
        )}
      </div>

      {/* Selected info */}
      {selectedSettlement && (
        <div className="hierarchical-selected">
          <div className="hierarchical-selected-info">
            <span className="hierarchical-selected-label">Kiválasztva:</span>
            <span className="hierarchical-selected-value">
              {selectedSettlement}
              {selectedCounty && `, ${selectedCounty}`}
              {selectedRegion && ` (${selectedRegion})`}
            </span>
          </div>
          {settlements.find((s) => s.name === selectedSettlement)?.population && (
            <div className="hierarchical-selected-details">
              Lakosság:{' '}
              {settlements
                .find((s) => s.name === selectedSettlement)
                ?.population?.toLocaleString()}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default HierarchicalSelector;
