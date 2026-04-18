import React, { useState, useMemo, useCallback } from 'react';
import './DataTablePanel.css';

export interface WeatherTableRow {
  date: string;
  temperature_max: number | null;
  temperature_min: number | null;
  temperature_mean: number | null;
  precipitation: number | null;
  windspeed: number | null;
  windgusts: number | null;
  humidity: number | null;
}

export interface DataTablePanelProps {
  data: WeatherTableRow[];
  loading?: boolean;
}

type SortDirection = 'asc' | 'desc' | null;
type SortColumn = keyof WeatherTableRow | null;

const ITEMS_PER_PAGE_OPTIONS = [10, 25, 50, 100];

const formatValue = (value: number | null, unit: string): string => {
  if (value === null || value === undefined) return '-';
  return `${value.toFixed(1)} ${unit}`;
};

const DataTablePanel: React.FC<DataTablePanelProps> = ({ data, loading = false }) => {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage, setItemsPerPage] = useState<number>(25);
  const [sortColumn, setSortColumn] = useState<SortColumn>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = useCallback(
    (column: keyof WeatherTableRow) => {
      if (sortColumn === column) {
        if (sortDirection === 'asc') {
          setSortDirection('desc');
        } else if (sortDirection === 'desc') {
          setSortDirection(null);
          setSortColumn(null);
        } else {
          setSortDirection('asc');
        }
      } else {
        setSortColumn(column);
        setSortDirection('asc');
      }
    },
    [sortColumn, sortDirection],
  );

  const sortedData = useMemo(() => {
    if (!sortColumn || !sortDirection) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];

      if (aVal === null && bVal === null) return 0;
      if (aVal === null) return 1;
      if (bVal === null) return -1;

      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, sortColumn, sortDirection]);

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedData.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedData, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(data.length / itemsPerPage);

  const handleItemsPerPageChange = (newItemsPerPage: number) => {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1);
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(Math.max(1, Math.min(newPage, totalPages)));
  };

  const getSortIcon = (column: keyof WeatherTableRow): string => {
    if (sortColumn !== column) return '↕';
    if (sortDirection === 'asc') return '↑';
    if (sortDirection === 'desc') return '↓';
    return '↕';
  };

  const getHeaderClass = (column: keyof WeatherTableRow): string => {
    const base = 'sortable';
    if (sortColumn === column) {
      return sortDirection ? `${base} active ${sortDirection}` : base;
    }
    return base;
  };

  if (loading) {
    return (
      <div className="data-table-panel">
        <div className="table-loading">
          <div className="loading-spinner" />
          <span>Loading data...</span>
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="data-table-panel">
        <div className="table-empty">
          <span className="empty-icon">📋</span>
          <span>No data available</span>
        </div>
      </div>
    );
  }

  return (
    <div className="data-table-panel">
      <div className="table-controls">
        <div className="rows-per-page">
          <label htmlFor="rows-per-page">Rows per page:</label>
          <select
            id="rows-per-page"
            value={itemsPerPage}
            onChange={(e) => handleItemsPerPageChange(Number(e.target.value))}
            className="rows-select"
          >
            {ITEMS_PER_PAGE_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </div>
        <div className="table-info">
          Showing {(currentPage - 1) * itemsPerPage + 1} -{' '}
          {Math.min(currentPage * itemsPerPage, data.length)} of {data.length}
        </div>
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th className={getHeaderClass('date')} onClick={() => handleSort('date')}>
                Date {getSortIcon('date')}
              </th>
              <th
                className={getHeaderClass('temperature_max')}
                onClick={() => handleSort('temperature_max')}
              >
                Max Temp {getSortIcon('temperature_max')}
              </th>
              <th
                className={getHeaderClass('temperature_min')}
                onClick={() => handleSort('temperature_min')}
              >
                Min Temp {getSortIcon('temperature_min')}
              </th>
              <th
                className={getHeaderClass('temperature_mean')}
                onClick={() => handleSort('temperature_mean')}
              >
                Avg Temp {getSortIcon('temperature_mean')}
              </th>
              <th
                className={getHeaderClass('precipitation')}
                onClick={() => handleSort('precipitation')}
              >
                Precipitation {getSortIcon('precipitation')}
              </th>
              <th className={getHeaderClass('windspeed')} onClick={() => handleSort('windspeed')}>
                Wind Speed {getSortIcon('windspeed')}
              </th>
              <th className={getHeaderClass('windgusts')} onClick={() => handleSort('windgusts')}>
                Wind Gusts {getSortIcon('windgusts')}
              </th>
              <th className={getHeaderClass('humidity')} onClick={() => handleSort('humidity')}>
                Humidity {getSortIcon('humidity')}
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, idx) => (
              <tr key={`${row.date}-${idx}`}>
                <td className="date-cell">{row.date}</td>
                <td
                  className={
                    row.temperature_max !== null && row.temperature_max > 30
                      ? 'hot'
                      : row.temperature_max !== null && row.temperature_max < 0
                        ? 'cold'
                        : ''
                  }
                >
                  {formatValue(row.temperature_max, '°C')}
                </td>
                <td>{formatValue(row.temperature_min, '°C')}</td>
                <td>{formatValue(row.temperature_mean, '°C')}</td>
                <td>{formatValue(row.precipitation, 'mm')}</td>
                <td>{formatValue(row.windspeed, 'km/h')}</td>
                <td className={row.windgusts !== null && row.windgusts > 50 ? 'windy' : ''}>
                  {formatValue(row.windgusts, 'km/h')}
                </td>
                <td>{formatValue(row.humidity, '%')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pagination-controls">
        <button
          type="button"
          onClick={() => handlePageChange(1)}
          disabled={currentPage === 1}
          className="page-btn"
        >
          ««
        </button>
        <button
          type="button"
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="page-btn"
        >
          «
        </button>
        <span className="page-info">
          Page {currentPage} of {totalPages}
        </span>
        <button
          type="button"
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="page-btn"
        >
          »
        </button>
        <button
          type="button"
          onClick={() => handlePageChange(totalPages)}
          disabled={currentPage === totalPages}
          className="page-btn"
        >
          »»
        </button>
      </div>
    </div>
  );
};

export default DataTablePanel;
