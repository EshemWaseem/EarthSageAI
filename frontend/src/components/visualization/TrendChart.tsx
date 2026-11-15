import React from 'react';
import { ResponsiveContainer, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ComposedChart } from 'recharts';
import { TimeSeriesPoint } from '../../types';

interface TrendChartProps {
  data: TimeSeriesPoint[];
  title?: string;
  yAxisLabel?: string;
  height?: number;
}

export const TrendChart: React.FC<TrendChartProps> = ({
  data,
  title = 'Annual Mean Observed Series & OLS Linear Regression',
  yAxisLabel = 'Mean Value',
  height = 290,
}) => {
  if (!data || data.length === 0) {
    return (
      <div
        style={{
          height: `${height}px`,
          border: '1px solid var(--color-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--color-text-muted)',
          fontSize: '12px',
          backgroundColor: 'var(--color-surface)',
        }}
      >
        No time-series data available. Execute the investigation to generate time-series analysis.
      </div>
    );
  }

  return (
    <div
      style={{
        border: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-bg)',
        padding: 'var(--space-md)',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 'var(--space-sm)',
          paddingBottom: '4px',
          borderBottom: '1px solid var(--color-border-subtle)',
        }}
      >
        <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
          {title}
        </span>
        <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
          Unit: {yAxisLabel}
        </span>
      </div>

      <div style={{ width: '100%', height }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
            <CartesianGrid stroke="#F4F4F5" strokeDasharray="2 2" vertical={false} />
            <XAxis
              dataKey="timestamp"
              stroke="#71717A"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#E4E4E7' }}
            />
            <YAxis
              stroke="#71717A"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#E4E4E7' }}
              domain={['auto', 'auto']}
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <div
                      style={{
                        backgroundColor: '#FFFFFF',
                        border: '1px solid var(--color-border)',
                        padding: '6px 10px',
                        fontSize: '11px',
                        boxShadow: 'none',
                      }}
                    >
                      <div style={{ fontWeight: 600, marginBottom: '2px', color: 'var(--color-text-primary)' }}>
                        Year: {label}
                      </div>
                      {payload.map((entry, idx) => (
                        <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', color: entry.color }}>
                          <span>{entry.name}:</span>
                          <span className="tabular-nums" style={{ fontWeight: 600 }}>
                            {Number(entry.value).toFixed(2)}
                          </span>
                        </div>
                      ))}
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend
              verticalAlign="top"
              align="right"
              iconType="plainline"
              wrapperStyle={{ paddingBottom: '8px', fontSize: '11px' }}
            />
            {/* Real Observed Annual Mean */}
            <Line
              type="linear"
              dataKey="observed"
              name="Annual Mean Observation"
              stroke="#18181B"
              strokeWidth={1.5}
              dot={{ r: 2, fill: '#18181B' }}
              activeDot={{ r: 4 }}
            />
            {/* Real OLS Linear Trend */}
            <Line
              type="linear"
              dataKey="predicted"
              name="OLS Linear Trend Fit"
              stroke="#2563EB"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
