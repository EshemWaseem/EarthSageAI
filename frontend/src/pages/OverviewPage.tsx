import React from 'react';
import { Investigation, DataSourceReference } from '../types';
import { StatusBadge } from '../components/common/StatusBadge';
import { Button } from '../components/common/Button';
import { EmptyState } from '../components/common/EmptyState';
import { ArrowRight, Plus } from 'lucide-react';

interface OverviewPageProps {
  investigations: Investigation[];
  dataSources: DataSourceReference[];
  onSelectInvestigation: (id: string) => void;
  onNewInvestigation: () => void;
  onViewReports: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  investigations,
  dataSources,
  onSelectInvestigation,
  onNewInvestigation,
}) => {
  const completedCount = investigations.filter((i) => i.status === 'completed').length;
  const runningCount = investigations.filter((i) => i.status === 'running').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
            Research Overview & Investigation Register
          </h1>
          <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            Empirical planetary records and peer-reviewable meteorological evaluations.
          </p>
        </div>
        <Button variant="primary" size="sm" onClick={onNewInvestigation}>
          <Plus size={14} /> New Investigation
        </Button>
      </div>

      {/* Summary Row */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 'var(--space-sm)',
        }}
      >
        <div style={{ border: '1px solid var(--color-border)', padding: '10px 14px', backgroundColor: 'var(--color-surface)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Registered Inquiries</div>
          <div className="tabular-nums" style={{ fontSize: '20px', fontWeight: 600, marginTop: '2px' }}>
            {investigations.length}
          </div>
        </div>
        <div style={{ border: '1px solid var(--color-border)', padding: '10px 14px', backgroundColor: 'var(--color-surface)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Active Pipelines</div>
          <div className="tabular-nums" style={{ fontSize: '20px', fontWeight: 600, marginTop: '2px' }}>
            {runningCount}
          </div>
        </div>
        <div style={{ border: '1px solid var(--color-border)', padding: '10px 14px', backgroundColor: 'var(--color-surface)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Completed Studies</div>
          <div className="tabular-nums" style={{ fontSize: '20px', fontWeight: 600, marginTop: '2px', color: 'var(--color-success)' }}>
            {completedCount}
          </div>
        </div>
        <div style={{ border: '1px solid var(--color-border)', padding: '10px 14px', backgroundColor: 'var(--color-surface)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Connected Feeds</div>
          <div className="tabular-nums" style={{ fontSize: '20px', fontWeight: 600, marginTop: '2px' }}>
            {dataSources.length}
          </div>
        </div>
      </div>

      {/* Investigations Table */}
      <section>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <h2 style={{ fontSize: '14px', fontWeight: 600 }}>Recorded Inquiries</h2>
          <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
            {investigations.length} record(s) persisted in database
          </span>
        </div>

        {investigations.length === 0 ? (
          <EmptyState
            title="No investigations registered"
            description="No scientific inquiries have been submitted yet. Start by defining a research question and coordinates."
            actionLabel="Start New Investigation"
            onAction={onNewInvestigation}
          />
        ) : (
          <div style={{ border: '1px solid var(--color-border)' }}>
            <table>
              <thead>
                <tr style={{ backgroundColor: 'var(--color-surface)' }}>
                  <th style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)' }}>ID</th>
                  <th style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)' }}>Title & Research Inquiry</th>
                  <th style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)' }}>Location / Coordinates</th>
                  <th style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)' }}>Status</th>
                  <th style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)' }}>Window</th>
                  <th style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {investigations.map((inv) => (
                  <tr
                    key={inv.id}
                    style={{ backgroundColor: 'var(--color-bg)', cursor: 'pointer' }}
                    onClick={() => onSelectInvestigation(inv.id)}
                  >
                    <td className="tabular-nums" style={{ padding: '8px 12px', fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--color-text-muted)' }}>
                      {inv.id}
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <div style={{ fontWeight: 600, fontSize: '12px' }}>{inv.title}</div>
                      <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '1px' }}>
                        {inv.researchQuestion}
                      </div>
                    </td>
                    <td style={{ padding: '8px 12px', fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                      {inv.primaryLocation.name} ({inv.primaryLocation.lat}°, {inv.primaryLocation.lng}°)
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <StatusBadge status={inv.status} />
                    </td>
                    <td className="tabular-nums" style={{ padding: '8px 12px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      {inv.temporalRange.start.substring(0, 4)}–{inv.temporalRange.end.substring(0, 4)}
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <span style={{ color: 'var(--color-primary)', fontSize: '11px', fontWeight: 500, display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                        Open <ArrowRight size={11} />
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};
