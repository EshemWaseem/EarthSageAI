import React from 'react';
import { InvestigationStatus, FindingClassification } from '../../types';

interface StatusBadgeProps {
  status: InvestigationStatus | FindingClassification;
  type?: 'status' | 'finding';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'status' }) => {
  const getBadgeConfig = () => {
    if (type === 'finding') {
      switch (status) {
        case 'observed':
          return {
            label: 'Observed Fact',
            bg: 'var(--color-primary-subtle)',
            color: 'var(--color-primary)',
            border: 'var(--color-primary-border)',
          };
        case 'statistical':
          return {
            label: 'Statistical Finding',
            bg: 'var(--color-surface)',
            color: 'var(--color-text-primary)',
            border: 'var(--color-border)',
          };
        case 'predicted':
          return {
            label: 'Model Prediction',
            bg: 'var(--color-warning-subtle)',
            color: 'var(--color-warning)',
            border: 'var(--color-warning-border)',
          };
        case 'hypothesis':
        default:
          return {
            label: 'Research Hypothesis',
            bg: 'var(--color-surface)',
            color: 'var(--color-text-secondary)',
            border: 'var(--color-border)',
          };
      }
    }

    switch (status) {
      case 'completed':
        return {
          label: 'Completed',
          bg: 'var(--color-success-subtle)',
          color: 'var(--color-success)',
          border: 'var(--color-success-border)',
        };
      case 'running':
        return {
          label: 'Running',
          bg: 'var(--color-primary-subtle)',
          color: 'var(--color-primary)',
          border: 'var(--color-primary-border)',
        };
      case 'queued':
        return {
          label: 'Queued',
          bg: 'var(--color-warning-subtle)',
          color: 'var(--color-warning)',
          border: 'var(--color-warning-border)',
        };
      case 'failed':
        return {
          label: 'Failed',
          bg: 'var(--color-error-subtle)',
          color: 'var(--color-error)',
          border: 'var(--color-error-border)',
        };
      case 'draft':
      default:
        return {
          label: 'Draft',
          bg: 'var(--color-surface)',
          color: 'var(--color-text-secondary)',
          border: 'var(--color-border)',
        };
    }
  };

  const config = getBadgeConfig();

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        fontSize: '11px',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.04em',
        borderRadius: 'var(--radius-xs)',
        backgroundColor: config.bg,
        color: config.color,
        border: `1px solid ${config.border}`,
      }}
    >
      {config.label}
    </span>
  );
};

