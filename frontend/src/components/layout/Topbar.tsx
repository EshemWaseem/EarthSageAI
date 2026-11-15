import React from 'react';
import { User as UserIcon, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface TopbarProps {
  currentProject: string;
  activeContext?: string;
}

export const Topbar: React.FC<TopbarProps> = ({
  currentProject = 'Atmospheric & Geospatial Workstation',
  activeContext,
}) => {
  const { user, logout } = useAuth();

  return (
    <header
      style={{
        height: 'var(--topbar-height)',
        backgroundColor: 'var(--color-bg)',
        borderBottom: '1px solid var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 var(--space-lg)',
        flexShrink: 0,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
        <span style={{ color: 'var(--color-text-muted)' }}>Workspace:</span>
        <span style={{ fontWeight: 500, color: 'var(--color-text-primary)' }}>{currentProject}</span>
        {activeContext && (
          <>
            <span style={{ color: 'var(--color-border)' }}>/</span>
            <span style={{ color: 'var(--color-text-secondary)' }}>{activeContext}</span>
          </>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>Coordinates: WGS84 (EPSG:4326)</span>
          <span>•</span>
          <span>MERRA-2 Climatology</span>
        </div>

        {user && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              paddingLeft: '12px',
              borderLeft: '1px solid var(--color-border)',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: 'var(--color-text-primary)',
              }}
            >
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-primary)',
                }}
              >
                <UserIcon size={11} />
              </div>
              <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>
                {user.fullName}
              </span>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '10px' }}>
                ({user.email})
              </span>
            </div>

            <button
              onClick={() => logout()}
              title="Revoke session and sign out"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '11px',
                fontWeight: 500,
                color: 'var(--color-text-secondary)',
                padding: '3px 8px',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-xs)',
                backgroundColor: 'var(--color-surface)',
                cursor: 'pointer',
                transition: 'background-color 0.15s ease',
              }}
            >
              <LogOut size={11} />
              <span>Sign Out</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
