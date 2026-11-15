import React from 'react';
import {
  BarChart3,
  Plus,
  Folder,
  FileText,
  Database,
  Sliders,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

export type NavItemKey =
  | 'overview'
  | 'new-investigation'
  | 'investigations'
  | 'reports'
  | 'data-sources'
  | 'settings';

interface SidebarProps {
  currentTab: NavItemKey;
  onSelectTab: (tab: NavItemKey) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  collapsed,
  onToggleCollapse,
}) => {
  const navItems: { key: NavItemKey; label: string; icon: React.ReactNode }[] = [
    { key: 'overview', label: 'Overview', icon: <BarChart3 size={15} /> },
    { key: 'new-investigation', label: 'New Investigation', icon: <Plus size={15} /> },
    { key: 'investigations', label: 'Investigations', icon: <Folder size={15} /> },
    { key: 'reports', label: 'Saved Reports', icon: <FileText size={15} /> },
    { key: 'data-sources', label: 'Data Sources', icon: <Database size={15} /> },
    { key: 'settings', label: 'Settings', icon: <Sliders size={15} /> },
  ];

  return (
    <aside
      style={{
        width: collapsed ? 'var(--sidebar-width-collapsed)' : 'var(--sidebar-width)',
        backgroundColor: 'var(--color-surface)',
        borderRight: '1px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
        height: '100%',
      }}
    >
      {/* Platform Title */}
      <div
        style={{
          height: 'var(--topbar-height)',
          borderBottom: '1px solid var(--color-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          padding: collapsed ? '0' : '0 var(--space-md)',
        }}
      >
        {!collapsed && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div
              style={{
                width: '8px',
                height: '8px',
                backgroundColor: 'var(--color-primary)',
              }}
            />
            <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--color-text-primary)' }}>
              EarthSage AI
            </span>
            <span style={{ fontSize: '10px', color: 'var(--color-text-muted)', border: '1px solid var(--color-border)', padding: '1px 3px' }}>
              v1.0
            </span>
          </div>
        )}
        <button
          onClick={onToggleCollapse}
          aria-label={collapsed ? 'Expand' : 'Collapse'}
          style={{
            padding: '2px',
            color: 'var(--color-text-secondary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>

      {/* Navigation */}
      <nav style={{ padding: 'var(--space-xs)', flex: 1, overflowY: 'auto' }}>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '1px' }}>
          {navItems.map((item) => {
            const isActive = currentTab === item.key;
            return (
              <li key={item.key}>
                <button
                  onClick={() => onSelectTab(item.key)}
                  title={collapsed ? item.label : undefined}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: collapsed ? '8px 0' : '6px 10px',
                    justifyContent: collapsed ? 'center' : 'flex-start',
                    fontSize: '12px',
                    fontWeight: isActive ? 600 : 400,
                    color: isActive ? 'var(--color-primary)' : 'var(--color-text-primary)',
                    backgroundColor: isActive ? 'var(--color-primary-subtle)' : 'transparent',
                    borderLeft: isActive ? '2px solid var(--color-primary)' : '2px solid transparent',
                    textAlign: 'left',
                  }}
                >
                  <span style={{ color: isActive ? 'var(--color-primary)' : 'var(--color-text-muted)' }}>
                    {item.icon}
                  </span>
                  {!collapsed && <span>{item.label}</span>}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* System Status */}
      <div
        style={{
          padding: collapsed ? '8px 2px' : '8px 12px',
          borderTop: '1px solid var(--color-border)',
          fontSize: '10px',
          color: 'var(--color-text-muted)',
          textAlign: collapsed ? 'center' : 'left',
        }}
      >
        {!collapsed ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <span style={{ width: '5px', height: '5px', backgroundColor: 'var(--color-success)', display: 'inline-block' }} />
              <span style={{ color: 'var(--color-text-secondary)', fontWeight: 500 }}>NASA POWER API Active</span>
            </div>
            {/* <div style={{ marginTop: '2px' }}>PostgreSQL 16 (Port 5439)</div> */}
          </div>
        ) : (
          <span style={{ display: 'inline-block', width: '6px', height: '6px', backgroundColor: 'var(--color-success)' }} />
        )}
      </div>
    </aside>
  );
};
