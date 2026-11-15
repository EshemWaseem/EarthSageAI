import React, { useState, useEffect } from 'react';
import { Investigation, DataSourceReference } from '../types';
import { GeographicMap } from '../components/visualization/GeographicMap';
import { TrendChart } from '../components/visualization/TrendChart';
import { ResearchResults } from '../components/research/ResearchResults';
import { DataSourceList } from '../components/evidence/DataSourceList';
import { StatusBadge } from '../components/common/StatusBadge';
import { Button } from '../components/common/Button';
import { apiService } from '../services/apiService';
import {
  Play, Download, ArrowLeft, RefreshCw, AlertCircle, FileSpreadsheet,
  FileText, Activity, GitCompare, Sparkles, CheckCircle2, Info
} from 'lucide-react';
import { ResponsiveContainer, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ComposedChart } from 'recharts';

interface InvestigationPageProps {
  investigation: Investigation;
  allDataSources: DataSourceReference[];
  onBack: () => void;
  onUpdate: (updated: Investigation) => void;
  onReportGenerated?: () => void;
}

type ViewTab = 'trends' | 'anomalies' | 'comparison' | 'ai-synthesis';

export const InvestigationPage: React.FC<InvestigationPageProps> = ({
  investigation,
  allDataSources,
  onBack,
  onUpdate,
  onReportGenerated,
}) => {
  const [activeTab, setActiveTab] = useState<ViewTab>('trends');
  const [isRunning, setIsRunning] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Anomaly state
  const [anomaliesData, setAnomaliesData] = useState<any>(null);
  const [isLoadingAnomalies, setIsLoadingAnomalies] = useState(false);

  // Comparison state
  const [comparisonData, setComparisonData] = useState<any>(null);
  const [isLoadingComparison, setIsLoadingComparison] = useState(false);

  // AI Synthesis state
  const [aiExplanation, setAiExplanation] = useState<any>(null);
  const [isLoadingAi, setIsLoadingAi] = useState(false);

  const selectedSources = allDataSources.filter((s) => investigation.datasetIds.includes(s.id));

  // Load anomalies when switching to anomalies tab
  useEffect(() => {
    if (activeTab === 'anomalies' && !anomaliesData && investigation.status === 'completed') {
      setIsLoadingAnomalies(true);
      apiService.getAnomalies(investigation.id)
        .then(setAnomaliesData)
        .catch((e) => setErrorMsg(`Failed to load anomalies: ${e.message}`))
        .finally(() => setIsLoadingAnomalies(false));
    }
  }, [activeTab, investigation.id, investigation.status, anomaliesData]);

  // Load comparison when switching to comparison tab
  useEffect(() => {
    if (activeTab === 'comparison' && !comparisonData && investigation.status === 'completed') {
      setIsLoadingComparison(true);
      apiService.getVariableComparison(investigation.id, 'T2M', 'PRECTOTCORR')
        .then(setComparisonData)
        .catch((e) => setErrorMsg(`Failed to load variable comparison: ${e.message}`))
        .finally(() => setIsLoadingComparison(false));
    }
  }, [activeTab, investigation.id, investigation.status, comparisonData]);

  const handleRunInvestigation = async () => {
    try {
      setIsRunning(true);
      setErrorMsg(null);
      const updated = await apiService.runInvestigation(investigation.id);
      onUpdate(updated);
      setAnomaliesData(null);
      setComparisonData(null);
      setAiExplanation(null);
    } catch (e: any) {
      setErrorMsg(e.message || 'Analytical execution failed.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleExportReport = async (format: 'PDF' | 'CSV') => {
    try {
      setIsExporting(true);
      const rep = await apiService.generateReport(investigation.id, format);
      if (onReportGenerated) onReportGenerated();
      // Directly trigger browser download
      const downloadUrl = apiService.getDownloadUrl(rep.id);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${rep.id}.${format.toLowerCase()}`;
      link.target = '_blank';
      link.click();
    } catch (e: any) {
      alert(`Report export failed: ${e.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  const handleGenerateAiExplanation = async () => {
    try {
      setIsLoadingAi(true);
      setErrorMsg(null);
      const explanation = await apiService.explainFindingsWithAi(investigation.id);
      setAiExplanation(explanation);
    } catch (e: any) {
      setErrorMsg(`AI Synthesis failed: ${e.message}`);
    } finally {
      setIsLoadingAi(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
      {/* Top Action Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button
          onClick={onBack}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '12px',
            color: 'var(--color-text-secondary)',
            background: 'none',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          <ArrowLeft size={14} /> Back to Directory
        </button>

        <div style={{ display: 'flex', gap: '6px' }}>
          {investigation.status !== 'completed' && (
            <Button
              variant="primary"
              size="sm"
              onClick={handleRunInvestigation}
              isLoading={isRunning}
            >
              <Play size={13} /> Execute Pipeline (NASA POWER + Mann-Kendall)
            </Button>
          )}

          {investigation.status === 'completed' && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRunInvestigation}
                isLoading={isRunning}
              >
                <RefreshCw size={13} /> Re-run Calculations
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => handleExportReport('CSV')}
                isLoading={isExporting}
              >
                <FileSpreadsheet size={13} /> Export Dataset (CSV)
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => handleExportReport('PDF')}
                isLoading={isExporting}
              >
                <FileText size={13} /> Generate Report (PDF)
              </Button>
            </>
          )}
        </div>
      </div>

      {errorMsg && (
        <div
          style={{
            padding: '8px 12px',
            backgroundColor: 'var(--color-error-subtle)',
            border: '1px solid var(--color-error-border)',
            color: 'var(--color-error)',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '12px',
          }}
        >
          <AlertCircle size={14} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Investigation Metadata Header Card */}
      <div
        style={{
          border: '1px solid var(--color-border)',
          backgroundColor: 'var(--color-surface)',
          padding: 'var(--space-md)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <StatusBadge status={investigation.status} />
          <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--color-text-muted)' }}>
            {investigation.id}
          </span>
          <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>•</span>
          <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
            Updated: {new Date(investigation.updatedAt).toLocaleDateString()}
          </span>
          <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>•</span>
          <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
            Window: {investigation.temporalRange.start.substring(0, 4)}–{investigation.temporalRange.end.substring(0, 4)} (30 Years)
          </span>
        </div>

        <h1 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '8px' }}>
          {investigation.title}
        </h1>

        <div style={{ marginBottom: '6px' }}>
          <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--color-text-muted)', fontWeight: 600 }}>
            Research Question
          </div>
          <div style={{ fontSize: '13px', color: 'var(--color-text-primary)', marginTop: '2px' }}>
            {investigation.researchQuestion}
          </div>
        </div>

        {investigation.hypothesis && (
          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--color-text-muted)', fontWeight: 600 }}>
              Working Hypothesis
            </div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
              {investigation.hypothesis}
            </div>
          </div>
        )}
      </div>

      {/* Scientific Analysis View Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--color-border)', gap: '4px' }}>
        {[
          { id: 'trends', label: '1. Climate Trend Explorer', icon: Activity },
          { id: 'anomalies', label: '2. Anomaly Detection', icon: AlertCircle },
          { id: 'comparison', label: '3. Variable Comparison', icon: GitCompare },
          { id: 'ai-synthesis', label: '4. AI Research Assistant', icon: Sparkles }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as ViewTab)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                fontSize: '12px',
                fontWeight: isActive ? 600 : 500,
                color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                backgroundColor: isActive ? 'var(--color-bg)' : 'transparent',
                border: '1px solid',
                borderColor: isActive ? 'var(--color-border) var(--color-border) var(--color-bg) var(--color-border)' : 'transparent',
                marginBottom: '-1px',
                cursor: 'pointer'
              }}
            >
              <Icon size={13} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: CLIMATE TREND EXPLORER */}
      {activeTab === 'trends' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          {/* Visualizations Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
            <GeographicMap
              location={investigation.primaryLocation}
              spatialExtent={investigation.spatialExtent}
              title={`Coordinate Point: ${investigation.primaryLocation.name}`}
              height="280px"
            />

            <TrendChart
              data={investigation.timeSeriesData}
              title="Annual Mean Observed Series vs. OLS Linear Trend"
              yAxisLabel="Annual Mean"
              height={240}
            />
          </div>

          {/* Empirical Findings & Statistical Parameters */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <h2 style={{ fontSize: '14px', fontWeight: 600 }}>
                Empirical Findings & Non-Parametric Statistics
              </h2>
              <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                {investigation.findings.length} parameter(s) evaluated
              </span>
            </div>
            <ResearchResults
              findings={investigation.findings}
              dataSources={allDataSources}
            />
          </div>
        </div>
      )}

      {/* TAB 2: ANOMALY DETECTION */}
      {activeTab === 'anomalies' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <div style={{ padding: '8px 12px', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', fontSize: '11px', color: 'var(--color-text-secondary)' }}>
            <strong>Methodology & Scientific Caveat:</strong> Standardized monthly departures are calculated as 
            <em> Z = (Observed - Calendar Month Mean) / Standard Deviation</em> relative to the 1991–2020 climatological baseline. 
            Statistical outliers (Z ≥ 2.0σ) represent mathematical departures and do not confirm ground disaster events without auxiliary ground verification.
          </div>

          {isLoadingAnomalies && (
            <div style={{ padding: 'var(--space-xl)', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '12px' }}>
              Detecting climatological monthly anomalies...
            </div>
          )}

          {!isLoadingAnomalies && anomaliesData && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
              {Object.entries(anomaliesData.anomalies || {}).map(([paramKey, pData]: [string, any]) => (
                <div key={paramKey} style={{ border: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg)' }}>
                  <div style={{ padding: '8px 12px', backgroundColor: 'var(--color-surface)', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 600, fontSize: '12px' }}>
                      {paramKey} — Detected Climatological Departures ({pData.anomaly_count} events / {pData.total_observations} months)
                    </span>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      Threshold: |Z| ≥ {pData.z_threshold_used}σ
                    </span>
                  </div>

                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '11px' }}>
                    <thead>
                      <tr style={{ backgroundColor: 'var(--color-surface)', textAlign: 'left' }}>
                        <th style={{ padding: '6px 10px', borderBottom: '1px solid var(--color-border)' }}>Date</th>
                        <th style={{ padding: '6px 10px', borderBottom: '1px solid var(--color-border)' }}>Observed</th>
                        <th style={{ padding: '6px 10px', borderBottom: '1px solid var(--color-border)' }}>Clim Mean</th>
                        <th style={{ padding: '6px 10px', borderBottom: '1px solid var(--color-border)' }}>Departure</th>
                        <th style={{ padding: '6px 10px', borderBottom: '1px solid var(--color-border)' }}>Z-Score</th>
                        <th style={{ padding: '6px 10px', borderBottom: '1px solid var(--color-border)' }}>Severity</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(pData.detected_anomalies || []).map((an: any, idx: number) => (
                        <tr key={idx} style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
                          <td style={{ padding: '6px 10px', fontFamily: 'var(--font-mono)' }}>{an.date}</td>
                          <td style={{ padding: '6px 10px' }}>{an.observed_value} {an.units}</td>
                          <td style={{ padding: '6px 10px', color: 'var(--color-text-muted)' }}>{an.climatological_mean}</td>
                          <td style={{ padding: '6px 10px', color: an.departure > 0 ? '#B91C1C' : '#1D4ED8' }}>
                            {an.departure > 0 ? `+${an.departure}` : an.departure}
                          </td>
                          <td style={{ padding: '6px 10px', fontWeight: 600 }}>{an.standardized_z_score}σ</td>
                          <td style={{ padding: '6px 10px' }}>
                            <span style={{
                              padding: '1px 5px',
                              borderRadius: '2px',
                              fontSize: '10px',
                              textTransform: 'uppercase',
                              fontWeight: 600,
                              backgroundColor: an.severity === 'extreme' ? '#FEE2E2' : '#FEF3C7',
                              color: an.severity === 'extreme' ? '#991B1B' : '#92400E'
                            }}>
                              {an.severity}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: VARIABLE COMPARISON */}
      {activeTab === 'comparison' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <div style={{ padding: '8px 12px', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', fontSize: '11px', color: 'var(--color-text-secondary)' }}>
            <strong>Scientific Principle:</strong> Variables are transformed to dimensionless Z-scores 
            <em> Z = (X - μ) / σ</em> to enable valid multi-parameter visual comparison without artificial dual-axis distortion.
            <strong> CORRELATION DOES NOT IMPLY CAUSATION.</strong>
          </div>

          {isLoadingComparison && (
            <div style={{ padding: 'var(--space-xl)', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '12px' }}>
              Computing variable co-variation and correlations...
            </div>
          )}

          {!isLoadingComparison && comparisonData && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
              {/* Correlation Summary Stats */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-sm)' }}>
                <div style={{ border: '1px solid var(--color-border)', padding: '10px 14px', backgroundColor: 'var(--color-bg)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Non-Parametric Spearman Rank Correlation</div>
                  <div style={{ fontSize: '18px', fontWeight: 600, marginTop: '2px' }}>
                    ρ = {comparisonData.comparison?.spearman_rank_correlation?.coefficient_rho}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                    p-value: {comparisonData.comparison?.spearman_rank_correlation?.p_value} ({comparisonData.comparison?.sample_size} concurrent months)
                  </div>
                </div>

                <div style={{ border: '1px solid var(--color-border)', padding: '10px 14px', backgroundColor: 'var(--color-bg)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Parametric Pearson Correlation</div>
                  <div style={{ fontSize: '18px', fontWeight: 600, marginTop: '2px' }}>
                    r = {comparisonData.comparison?.pearson_correlation?.coefficient_r}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                    p-value: {comparisonData.comparison?.pearson_correlation?.p_value} (Linear co-variation)
                  </div>
                </div>
              </div>

              {/* Normalized Overlay Chart */}
              <div style={{ border: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg)', padding: 'var(--space-md)' }}>
                <div style={{ fontSize: '12px', fontWeight: 600, marginBottom: '8px' }}>
                  Standardized Monthly Co-Variation (Z-Scores: T2M vs. PRECTOTCORR)
                </div>
                <div style={{ width: '100%', height: '280px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={comparisonData.comparison?.comparison_series?.slice(0, 120) || []} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
                      <CartesianGrid stroke="#F4F4F5" strokeDasharray="2 2" vertical={false} />
                      <XAxis dataKey="timestamp" stroke="#71717A" fontSize={10} tickLine={false} />
                      <YAxis stroke="#71717A" fontSize={10} tickLine={false} domain={[-3, 4]} />
                      <Tooltip />
                      <Legend verticalAlign="top" align="right" wrapperStyle={{ fontSize: '11px' }} />
                      <Line type="monotone" dataKey="norm_a" name="Temperature (T2M Z-Score)" stroke="#B91C1C" dot={false} strokeWidth={1.5} />
                      <Line type="monotone" dataKey="norm_b" name="Precipitation (PRECTOTCORR Z-Score)" stroke="#2563EB" dot={false} strokeWidth={1.5} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
                <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '4px', textAlign: 'center' }}>
                  Showing first 120 monthly observations for readability. Full 360-month dataset evaluated in correlation statistics.
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: AI RESEARCH ASSISTANT SYNTHESIS */}
      {activeTab === 'ai-synthesis' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600 }}>Gemini Climatological Narrative Interpretation</div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                Translates validated non-parametric outputs into scientific prose with clear limitation disclosures.
              </div>
            </div>
            <Button
              variant="primary"
              size="sm"
              onClick={handleGenerateAiExplanation}
              isLoading={isLoadingAi}
            >
              <Sparkles size={13} /> Synthesize Narrative
            </Button>
          </div>

          {aiExplanation && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
              <div style={{
                padding: '8px 12px',
                backgroundColor: aiExplanation.is_ai_generated ? '#f0fdf4' : '#f9fafb',
                border: `1px solid ${aiExplanation.is_ai_generated ? '#bbf7d0' : '#e5e7eb'}`,
                fontSize: '11px',
                color: aiExplanation.is_ai_generated ? '#166534' : '#4b5563',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '8px',
                borderRadius: 'var(--radius-xs)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Info size={14} />
                  <span>{aiExplanation.disclaimer || 'Scientific Interpretation (Advisory Only). Derived from backend statistics.'}</span>
                </div>
                {aiExplanation.is_ai_generated && (
                  <span style={{ fontSize: '10px', fontWeight: 600, padding: '1px 6px', backgroundColor: '#dcfce7', borderRadius: '3px', color: '#15803d' }}>
                    {aiExplanation.ai_model || 'Gemini'}
                  </span>
                )}
              </div>

              {/* Plain Language Summary */}
              <div style={{ border: '1px solid var(--color-border)', padding: '12px 14px', backgroundColor: 'var(--color-bg)' }}>
                <h3 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '6px', color: 'var(--color-text-primary)' }}>
                  Executive Scientific Summary
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                  {aiExplanation.plain_language_summary}
                </p>
              </div>

              {/* Statistical Deep Dive */}
              <div style={{ border: '1px solid var(--color-border)', padding: '12px 14px', backgroundColor: 'var(--color-bg)' }}>
                <h3 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '6px', color: 'var(--color-text-primary)' }}>
                  Statistical Parameter Interpretation
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                  {aiExplanation.statistical_deep_dive}
                </p>
              </div>

              {/* Physical Mechanisms */}
              <div style={{ border: '1px solid var(--color-border)', padding: '12px 14px', backgroundColor: 'var(--color-bg)' }}>
                <h3 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '6px', color: 'var(--color-text-primary)' }}>
                  Coupled Earth System Dynamics & Physical Mechanisms
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                  {aiExplanation.physical_mechanisms}
                </p>
              </div>

              {/* Limitations & Follow-ups */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-sm)' }}>
                <div style={{ border: '1px solid var(--color-border)', padding: '10px 12px', backgroundColor: 'var(--color-surface)' }}>
                  <h4 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>
                    Observational Scope & Limitations
                  </h4>
                  <p style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
                    {aiExplanation.scientific_limitations}
                  </p>
                </div>

                <div style={{ border: '1px solid var(--color-border)', padding: '10px 12px', backgroundColor: 'var(--color-surface)' }}>
                  <h4 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>
                    Recommended Follow-Up Investigations
                  </h4>
                  <ul style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '4px', paddingLeft: '14px', lineHeight: 1.4 }}>
                    {(aiExplanation.recommended_follow_ups || []).map((rec: string, i: number) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {!aiExplanation && !isLoadingAi && (
            <div style={{ padding: 'var(--space-xl)', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '12px', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)' }}>
              Click 'Synthesize Narrative' to produce an advisory scientific explanation of the verified mathematical results.
            </div>
          )}
        </div>
      )}

      {/* Data Sources and Constraints */}
      <div>
        <h2 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
          Observational Data Sources & Known Characteristics
        </h2>
        <DataSourceList
          sources={selectedSources}
          readOnly={true}
        />
      </div>
    </div>
  );
};
