/**
 * WindRoseChart - Szélirány és erősség rózsadiagram
 * Polar chart using Plotly.js
 */
import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

// Wind rose direction data structure
export interface WindRoseDirection {
  direction: string;        // N, NNE, NE, etc.
  angle: number;            // Center angle in degrees
  speed_buckets: number[];  // [0-25, 25-50, 50-70, 70-100, 100-120, 120+] counts
}

export interface WindRoseData {
  city: string;
  start: string;
  end: string;
  directions: WindRoseDirection[];
  calms_percentage: number;
  total_observations: number;
  statistics: {
    avg_speed: number;
    max_speed: number;
    data_source: string;
    calms_count: number;
  };
}

interface WindRoseChartProps {
  data: WindRoseData | null;
  loading?: boolean;
  error?: string;
  height?: number;
}

// Speed bucket labels and colors (defined outside component to avoid recreation)
const SPEED_LABELS = ['0-25', '25-50', '50-70', '70-100', '100-120', '120+'];
const SPEED_COLORS = [
  '#9ca3af',  // calm - gray
  '#34d399',  // light - green
  '#fbbf24',  // moderate - yellow
  '#f97316',  // strong - orange
  '#ef4444',  // very strong - red
  '#dc2626',  // extreme - dark red
];

const WindRoseChart: React.FC<WindRoseChartProps> = ({
  data,
  loading = false,
  error = '',
  height = 500
}) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!data || !chartRef.current) return;

    const chartElement = chartRef.current;

    // Prepare data for polar bar chart
    // Each speed bucket becomes a separate trace
    const traces: Plotly.Data[] = [];

    // Get directions in order
    const directions = data.directions;

    for (let i = 0; i < SPEED_LABELS.length; i++) {
      const values = directions.map(d => d.speed_buckets[i]);
      const r = values.map((v, idx) => {
        // Stack the values on top of previous buckets
        let sum = 0;
        for (let j = 0; j <= i; j++) {
          sum += directions[idx].speed_buckets[j];
        }
        return sum;
      });

      traces.push({
        type: 'scatterpolar',
        mode: 'lines',
        r: r,
        theta: directions.map(d => d.angle),
        fill: 'toself',
        name: SPEED_LABELS[i],
        marker: {
          color: SPEED_COLORS[i],
        },
        hovertemplate: `${SPEED_LABELS[i]} km/h: %{r} napok<extra></extra>`,
      });
    }

    const layout: Partial<Plotly.Layout> = {
      title: {
        text: `🌹 Szélrózsa - ${data.city}<br>` +
               `<sub>${data.start} ↔ ${data.end} | ` +
               `Összesen: ${data.total_observations} mérés</sub>`,
        font: { size: 16, color: '#374151' }
      },
      polar: {
        radialaxis: {
          visible: true,
          tickfont: { size: 11, color: '#6b7280' },
          gridcolor: '#e5e7eb',
          linecolor: '#e5e7eb',
        },
        angularaxis: {
          direction: 'clockwise',
          rotation: 90,
          tickmode: 'array',
          tickvals: directions.map(d => d.angle),
          ticktext: directions.map(d => d.direction),
          tickfont: { size: 12, weight: 'bold', color: '#374151' },
          gridcolor: '#e5e7eb',
          linecolor: '#e5e7eb',
        },
        bgcolor: 'rgba(0,0,0,0)',
      },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      showlegend: true,
      legend: {
        x: 1.1,
        y: 1,
        bgcolor: 'rgba(255,255,255,0.8)',
        bordercolor: '#e5e7eb',
        borderwidth: 1,
      },
      margin: { t: 80, r: 150, b: 50, l: 50 },
      annotations: [
        {
          x: 0.5,
          y: -0.15,
          xref: 'paper',
          yref: 'paper',
          text: `<b>Statisztika:</b><br>` +
                 `Átlag: ${data.statistics.avg_speed} km/h | ` +
                 `Max: ${data.statistics.max_speed} km/h<br>` +
                 `Csendes napok: ${data.calms_percentage}%`,
          showarrow: false,
          font: { size: 11, color: '#4b5563' },
          bgcolor: 'rgba(243, 244, 246, 0.8)',
          bordercolor: '#e5e7eb',
          borderwidth: 1,
          borderpad: 5,
        },
      ],
    };

    const config: Partial<Plotly.Config> = {
      responsive: true,
      displayModeBar: false,
    };

    Plotly.newPlot(chartElement, traces, layout, config);

    return () => {
      Plotly.purge(chartElement);
    };
  }, [data]);

  if (loading) {
    return (
      <div className="wind-rose-chart-container" style={{ height: `${height}px` }}>
        <div className="chart-loading">
          <div className="spinner"></div>
          <p>Betöltés...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="wind-rose-chart-container" style={{ height: `${height}px` }}>
        <div className="chart-error">
          <p>❌ {error}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="wind-rose-chart-container" style={{ height: `${height}px` }}>
        <div className="chart-empty">
          <p>🌹 Szélrózsa diagram</p>
          <p className="text-sm text-gray-500">
            Indíts analízist a szélirány és erősség megjelenítéséhez
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="wind-rose-chart-container">
      <div ref={chartRef} style={{ width: '100%', height: `${height}px` }}></div>
    </div>
  );
};

export default WindRoseChart;
