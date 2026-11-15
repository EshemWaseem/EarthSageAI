import React from 'react';
import { SavedReport, Investigation } from '../types';
import { Button } from '../components/common/Button';
import { EmptyState } from '../components/common/EmptyState';
import { Download } from 'lucide-react';
import { apiService } from '../services/apiService';

interface ReportsPageProps {
  reports: SavedReport[];
  investigations: Investigation[];
  onOpenInvestigation: (id: string) => void;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({
  reports,
  investigations,
  onOpenInvestigation,
}) => {
  const getInvestigation = (id: string) => investigations.find((i) => i.id === id);

  const handleDownload = (report: SavedReport) => {
    const downloadUrl = apiService.getDownloadUrl(report.id);
    const link = document.createElement('a');
    link.href = downloadUrl;
    const ext = (report.fileFormat || 'PDF').toLowerCase();
    link.download = `${report.id}.${ext}`;
    link.target = '_blank';
    link.click();
  };

  return (
    <div>
      <div style={{ marginBottom: 'var(--space-lg)' }}>
        <h1 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
          Saved Scientific Technical Reports
        </h1>
        <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
          Audited PDF reports containing full non-parametric methodology, observation counts, and reproducibility metadata.
        </p>
      </div>

      {reports.length === 0 ? (
        <EmptyState
          title="No reports compiled yet"
          description="Reports are generated from completed investigations. Open a finished inquiry and click 'Generate Report'."
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
          {reports.map((report) => {
            const inv = getInvestigation(report.investigationId);
            return (
              <div
                key={report.id}
                style={{
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg)',
                  padding: 'var(--space-md)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div style={{ maxWidth: '80%' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                    <span
                      style={{
                        padding: '1px 4px',
                        backgroundColor: 'var(--color-surface)',
                        border: '1px solid var(--color-border)',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '10px',
                        fontWeight: 600,
                      }}
                    >
                      {report.fileFormat}
                    </span>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      Size: {report.fileSize}
                    </span>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>•</span>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                      Compiled: {new Date(report.generatedAt).toLocaleString()}
                    </span>
                  </div>

                  <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                    {report.title}
                  </h3>

                  <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                    {report.summary}
                  </p>

                  {inv && (
                    <div style={{ marginTop: '4px', fontSize: '11px' }}>
                      <span style={{ color: 'var(--color-text-muted)' }}>Associated Investigation: </span>
                      <button
                        onClick={() => onOpenInvestigation(inv.id)}
                        style={{
                          color: 'var(--color-primary)',
                          textDecoration: 'underline',
                          fontWeight: 500,
                        }}
                      >
                        {inv.title} ({inv.id})
                      </button>
                    </div>
                  )}
                </div>

                <div>
                  <Button variant="secondary" size="sm" onClick={() => handleDownload(report)}>
                    <Download size={13} /> Download {report.fileFormat || 'Report'}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
