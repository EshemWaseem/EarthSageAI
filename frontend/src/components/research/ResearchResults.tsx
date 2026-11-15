import React from 'react';
import { ScientificFinding, DataSourceReference } from '../../types';
import { StatusBadge } from '../common/StatusBadge';

interface ResearchResultsProps {
  findings: ScientificFinding[];
  dataSources: DataSourceReference[];
}

export const ResearchResults: React.FC<ResearchResultsProps> = ({
  findings,
  dataSources,
}) => {
  if (!findings || findings.length === 0) {
    return (
      <div
        style={{
          padding: 'var(--space-lg)',
          border: '1px solid var(--color-border)',
          textAlign: 'center',
          color: 'var(--color-text-muted)',
          fontSize: '12px',
          backgroundColor: 'var(--color-surface)',
        }}
      >
        No empirical statistical results calculated yet. Execute the investigation pipeline.
      </div>
    );
  }

  const getSourceById = (id: string) => dataSources.find((s) => s.id === id);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
      {findings.map((finding) => (
        <div
          key={finding.id}
          style={{
            border: '1px solid var(--color-border)',
            backgroundColor: 'var(--color-bg)',
            padding: 'var(--space-md)',
          }}
        >
          {/* Finding Header */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
              marginBottom: '6px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <StatusBadge status={finding.classification} type="finding" />
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                {finding.title}
              </h3>
            </div>
            {finding.confidenceScore !== undefined && (
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                Confidence: {(finding.confidenceScore * 100).toFixed(0)}%
              </div>
            )}
          </div>

          {/* Finding Summary */}
          <p
            style={{
              fontSize: '12px',
              color: 'var(--color-text-secondary)',
              lineHeight: 1.45,
              marginBottom: 'var(--space-sm)',
            }}
          >
            {finding.summary}
          </p>

          {/* Tabular Measurements */}
          {finding.measurements && finding.measurements.length > 0 && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: '8px',
                marginBottom: 'var(--space-sm)',
              }}
            >
              {finding.measurements.map((m) => (
                <div
                  key={m.id}
                  style={{
                    border: '1px solid var(--color-border)',
                    padding: '6px 8px',
                    backgroundColor: 'var(--color-surface)',
                  }}
                >
                  <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                    {m.label}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px', marginTop: '1px' }}>
                    <span className="tabular-nums" style={{ fontSize: '15px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                      {m.value}
                    </span>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                      {m.unit}
                    </span>
                  </div>
                  {m.uncertainty && (
                    <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '1px' }}>
                      {m.uncertainty}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Traceable Data Sources */}
          <div
            style={{
              borderTop: '1px solid var(--color-border-subtle)',
              paddingTop: '6px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '11px',
              color: 'var(--color-text-muted)',
            }}
          >
            <span>Source citation:</span>
            {finding.evidenceReferences.map((refId) => {
              const src = getSourceById(refId);
              return (
                <span
                  key={refId}
                  style={{
                    color: 'var(--color-text-primary)',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                  }}
                >
                  {src ? src.name : refId}
                </span>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};
