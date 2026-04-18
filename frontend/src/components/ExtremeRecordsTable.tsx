import React from 'react';
import { ExtremeRecord } from '../utils/extremeCalculator/index';
import './ExtremeRecordsTable.css';

interface ExtremeRecordsTableProps {
  records: ExtremeRecord[];
  loading?: boolean;
}

const getCategoryIcon = (category: string): string => {
  switch (category.toLowerCase()) {
    case 'temperature':
      return '🌡️';
    case 'precipitation':
      return '🌧️';
    case 'wind':
      return '🌪️';
    default:
      return '📊';
  }
};

const getRecordIcon = (recordType: string): string => {
  const lower = recordType.toLowerCase();
  if (lower.includes('hottest') || lower.includes('warmest')) return '🔥';
  if (lower.includes('coldest')) return '🧊';
  if (lower.includes('wettest')) return '💧';
  if (lower.includes('driest') || lower.includes('dry')) return '🏜️';
  if (lower.includes('wind') || lower.includes('gust')) return '🚨';
  if (lower.includes('range')) return '📊';
  if (lower.includes('total')) return '📈';
  return '🏆';
};

const ExtremeRecordsTable: React.FC<ExtremeRecordsTableProps> = ({ records, loading }) => {
  if (loading) {
    return (
      <div className="extreme-records-table-container">
        <div className="loading-state">Loading records...</div>
      </div>
    );
  }

  if (records.length === 0) {
    return (
      <div className="extreme-records-table-container">
        <div className="empty-state">
          No extreme records available. Submit a query to analyze weather data.
        </div>
      </div>
    );
  }

  return (
    <div className="extreme-records-table-container">
      <table className="extreme-records-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Record Type</th>
            <th>Value</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {records.map((record, index) => (
            <tr key={`${record.category}-${record.recordType}-${index}`} className="record-row">
              <td className="category-cell">
                <span className="category-icon">{getCategoryIcon(record.category)}</span>
                <span className="category-text">{record.category}</span>
              </td>
              <td className="record-type-cell">
                <span className="record-icon">{getRecordIcon(record.recordType)}</span>
                <span className="record-text">{record.recordType}</span>
              </td>
              <td className="value-cell">
                <span className="value-text">{record.value}</span>
              </td>
              <td className="date-cell">
                <span className="date-text">{record.date}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ExtremeRecordsTable;
