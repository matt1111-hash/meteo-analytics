import React from 'react';
import { CityWeatherResult } from '../types/weather';

interface ExportCSVButtonProps {
  data: CityWeatherResult[];
  metric: string;
  city: string;
  startDate: string;
  endDate: string;
  title?: string;
}

const ExportCSVButton: React.FC<ExportCSVButtonProps> = ({
  data,
  metric,
  city,
  startDate,
  endDate,
  title = 'Export data to CSV',
}) => {
  const handleExportCSV = (): void => {
    if (data.length === 0) return;

    // Build CSV content
    const headers = ['date', 'metric', 'value', 'city'];
    const rows = data.map((r) => [
      r.date,
      metric,
      r.value?.toString() ?? '',
      city,
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    // Filename: {city}_{metric}_{startDate}_{endDate}.csv
    const sanitizedCity = city.replace(/[^a-zA-Z0-9]/g, '_');
    const filename = `${sanitizedCity}_${metric}_${startDate}_${endDate}.csv`;

    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <button
      className="export-csv-btn"
      onClick={handleExportCSV}
      title={title}
      disabled={data.length === 0}
    >
      ⬇️ Export CSV
    </button>
  );
};

export default ExportCSVButton;
