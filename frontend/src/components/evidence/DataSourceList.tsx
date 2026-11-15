import React from 'react';
import { DataSourceReference } from '../../types';
import { ExternalLink } from 'lucide-react';

interface DataSourceListProps {
  sources: DataSourceReference[];
  selectedSourceIds?: string[];
  onToggleSelect?: (sourceId: string) => void;
  readOnly?: boolean;
}

export const DataSourceList: React.FC<DataSourceListProps> = ({
  sources,
  selectedSourceIds = [],
  onToggleSelect,
  readOnly = false,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
      {sources.map((source) => {
        const isSelected = selectedSourceIds.includes(source.id);
        return (
          <div
            key={source.id}
            onClick={() => {
              if (!readOnly && onToggleSelect) {
                onToggleSelect(source.id);
              }
            }}
            style={{
              border: isSelected ? '1px solid var(--color-primary)' : '1px solid var(--color-border)',
              backgroundColor: isSelected ? 'var(--color-primary-subtle)' : 'var(--color-surface)',
              borderRadius: 'var(--radius-sm)',
              padding: 'var(--space-md)',
              cursor: readOnly ? 'default' : 'pointer',
              transition: 'border-color 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {!readOnly && (
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => {}} // Handled by container onClick
                      style={{ cursor: 'pointer' }}
                    />
                  )}
                  <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                    {source.name}
                  </h4>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                  Provider: {source.provider}
                </div>
              </div>
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                style={{
                  color: 'var(--color-primary)',
                  fontSize: '11px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  textDecoration: 'none',
                }}
              >
                Catalog Link <ExternalLink size={12} />
              </a>
            </div>

            <div
              style={{
                marginTop: 'var(--space-sm)',
                paddingTop: 'var(--space-sm)',
                borderTop: '1px solid var(--color-border-subtle)',
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: '8px',
                fontSize: '11px',
              }}
            >
              <div>
                <span style={{ color: 'var(--color-text-muted)' }}>Period: </span>
                <span style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{source.collectionPeriod}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)' }}>Resolution: </span>
                <span style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{source.resolution}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)' }}>DOI: </span>
                <span style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-mono)' }}>{source.doi || 'N/A'}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)' }}>Coverage: </span>
                <span style={{ color: 'var(--color-text-primary)' }}>{source.geographicCoverage}</span>
              </div>
            </div>

            {source.limitations && (
              <div
                style={{
                  marginTop: 'var(--space-xs)',
                  fontSize: '11px',
                  color: 'var(--color-warning)',
                  backgroundColor: 'var(--color-warning-subtle)',
                  padding: '4px 8px',
                  borderRadius: 'var(--radius-xs)',
                }}
              >
                <strong>Scientific limitation:</strong> {source.limitations}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

