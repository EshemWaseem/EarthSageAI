import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { AppLayout } from './components/layout/AppLayout';
import { NavItemKey } from './components/layout/Sidebar';
import { OverviewPage } from './pages/OverviewPage';
import { NewInvestigationPage } from './pages/NewInvestigationPage';
import { InvestigationPage } from './pages/InvestigationPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';
import { DataSourceList } from './components/evidence/DataSourceList';
import { Investigation, DataSourceReference, SavedReport } from './types';
import { apiService } from './services/apiService';

const WorkstationMain: React.FC = () => {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [authView, setAuthView] = useState<'login' | 'signup'>(() =>
    typeof window !== 'undefined' && window.location.pathname === '/signup' ? 'signup' : 'login'
  );

  const [currentTab, setCurrentTab] = useState<NavItemKey>('overview');
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [dataSources, setDataSources] = useState<DataSourceReference[]>([]);
  const [reports, setReports] = useState<SavedReport[]>([]);
  const [selectedInvestigationId, setSelectedInvestigationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setFetchError(null);
      const [invs, sources, reps] = await Promise.all([
        apiService.getInvestigations(),
        apiService.getDataSources(),
        apiService.getReports(),
      ]);
      setInvestigations(invs);
      setDataSources(sources);
      setReports(reps);
    } catch (e: any) {
      console.error('Failed to load application data:', e);
      setFetchError(e.message || 'Error communicating with backend API.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated]);

  // Loading state during silent session restoration
  if (authLoading) {
    return (
      <div
        style={{
          height: '100vh',
          width: '100vw',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'var(--color-surface)',
          fontFamily: 'var(--font-family)',
        }}
      >
        <div
          style={{
            width: '28px',
            height: '28px',
            border: '2px solid var(--color-border)',
            borderTop: '2px solid var(--color-primary)',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
            marginBottom: '16px',
          }}
        />
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
        <div
          style={{
            fontSize: '11px',
            fontWeight: 600,
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
            color: 'var(--color-text-muted)',
          }}
        >
          Restoring Verified Research Session...
        </div>
      </div>
    );
  }

  // Unauthenticated view: Login or Signup
  if (!isAuthenticated) {
    if (authView === 'signup') {
      return <SignupPage onSwitchToLogin={() => setAuthView('login')} />;
    }
    return <LoginPage onSwitchToSignup={() => setAuthView('signup')} />;
  }

  // Authenticated Scientific Workstation
  const activeInvestigation = investigations.find((i) => i.id === selectedInvestigationId);

  const handleOpenInvestigation = (id: string) => {
    setSelectedInvestigationId(id);
    setCurrentTab('investigations');
  };

  const handleInvestigationUpdated = (updated: Investigation) => {
    setInvestigations((prev) =>
      prev.map((item) => (item.id === updated.id ? updated : item))
    );
  };

  const handleInvestigationCreated = (newInv: Investigation) => {
    setInvestigations((prev) => [newInv, ...prev]);
    setSelectedInvestigationId(newInv.id);
    setCurrentTab('investigations');
  };

  const getActiveContext = () => {
    if (currentTab === 'investigations' && activeInvestigation) {
      return activeInvestigation.title;
    }
    if (currentTab === 'new-investigation') {
      return 'New Investigation';
    }
    if (currentTab === 'reports') {
      return 'Saved Reports';
    }
    if (currentTab === 'data-sources') {
      return 'Data Sources Catalog';
    }
    if (currentTab === 'settings') {
      return 'Configuration';
    }
    return undefined;
  };

  return (
    <AppLayout
      currentTab={currentTab}
      onSelectTab={(tab) => {
        setCurrentTab(tab);
      }}
      activeContext={getActiveContext()}
    >
      {fetchError && (
        <div
          style={{
            padding: '8px 12px',
            backgroundColor: 'var(--color-error-subtle)',
            border: '1px solid var(--color-error-border)',
            color: 'var(--color-error)',
            marginBottom: 'var(--space-md)',
            fontSize: '12px',
          }}
        >
          Backend connection error: {fetchError} (Confirm backend container on port 8020 is accessible).
        </div>
      )}

      {isLoading ? (
        <div
          style={{
            padding: 'var(--space-3xl)',
            textAlign: 'center',
            color: 'var(--color-text-muted)',
            fontSize: '12px',
          }}
        >
          Loading research workstation records...
        </div>
      ) : (
        <>
          {currentTab === 'overview' && (
            <OverviewPage
              investigations={investigations}
              dataSources={dataSources}
              onSelectInvestigation={handleOpenInvestigation}
              onNewInvestigation={() => setCurrentTab('new-investigation')}
              onViewReports={() => setCurrentTab('reports')}
            />
          )}

          {currentTab === 'new-investigation' && (
            <NewInvestigationPage
              dataSources={dataSources}
              onCreated={handleInvestigationCreated}
              onCancel={() => setCurrentTab('overview')}
            />
          )}

          {currentTab === 'investigations' && (
            <>
              {activeInvestigation ? (
                <InvestigationPage
                  investigation={activeInvestigation}
                  allDataSources={dataSources}
                  onBack={() => setCurrentTab('overview')}
                  onUpdate={handleInvestigationUpdated}
                  onReportGenerated={loadData}
                />
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                  <h1 style={{ fontSize: '16px', fontWeight: 600 }}>Investigations Directory</h1>
                  <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                    Select an inquiry from the list below to review its analytical results:
                  </p>
                  {investigations.length === 0 ? (
                    <div
                      style={{
                        padding: 'var(--space-lg)',
                        border: '1px solid var(--color-border)',
                        color: 'var(--color-text-muted)',
                        fontSize: '12px',
                        textAlign: 'center',
                        backgroundColor: 'var(--color-surface)',
                      }}
                    >
                      No investigations recorded yet. Click 'New Investigation' to initiate one.
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
                      {investigations.map((inv) => (
                        <div
                          key={inv.id}
                          onClick={() => handleOpenInvestigation(inv.id)}
                          style={{
                            padding: '10px 12px',
                            border: '1px solid var(--color-border)',
                            backgroundColor: 'var(--color-bg)',
                            cursor: 'pointer',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                          }}
                        >
                          <div>
                            <div style={{ fontWeight: 600, fontSize: '13px' }}>{inv.title}</div>
                            <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                              {inv.researchQuestion}
                            </div>
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                            {inv.primaryLocation.name} • {inv.temporalRange.start.substring(0, 4)}–{inv.temporalRange.end.substring(0, 4)}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {currentTab === 'reports' && (
            <ReportsPage
              reports={reports}
              investigations={investigations}
              onOpenInvestigation={handleOpenInvestigation}
            />
          )}

          {currentTab === 'data-sources' && (
            <div>
              <div style={{ marginBottom: 'var(--space-lg)' }}>
                <h1 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                  Connected Data Sources Catalog
                </h1>
                <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                  Peer-reviewed satellite observations, atmospheric reanalysis models, and surface sensors.
                </p>
              </div>

              <DataSourceList sources={dataSources} readOnly={true} />
            </div>
          )}

          {currentTab === 'settings' && <SettingsPage />}
        </>
      )}
    </AppLayout>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <WorkstationMain />
    </AuthProvider>
  );
};

export default App;
