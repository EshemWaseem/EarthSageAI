import React, { useState, useEffect } from 'react';
import { DataSourceReference, Investigation } from '../types';
import { Button } from '../components/common/Button';
import { DataSourceList } from '../components/evidence/DataSourceList';
import { apiService } from '../services/apiService';
import { Compass, Calendar, BookOpen, AlertCircle, CheckCircle2, Sparkles, HelpCircle } from 'lucide-react';

interface NewInvestigationPageProps {
  dataSources: DataSourceReference[];
  onCreated: (inv: Investigation) => void;
  onCancel: () => void;
}

export const NewInvestigationPage: React.FC<NewInvestigationPageProps> = ({
  dataSources,
  onCreated,
  onCancel,
}) => {
  const [title, setTitle] = useState('Lahore Climatological Normal Analysis (1991–2020)');
  const [researchQuestion, setResearchQuestion] = useState(
    'Has surface air temperature (T2M) and precipitation flux (PRECTOTCORR) exhibited significant multi-decadal trends over Lahore, Pakistan?'
  );
  const [hypothesis, setHypothesis] = useState(
    'Precipitation intensity has increased during monsoon seasons while mean temperatures exhibit shifting seasonal variance.'
  );

  // Location inputs (Lahore default, fully editable for other global stations)
  const [locName, setLocName] = useState('Lahore');
  const [locRegion, setLocRegion] = useState('Punjab');
  const [locCountry, setLocCountry] = useState('Pakistan');
  const [lat, setLat] = useState('31.5497');
  const [lng, setLng] = useState('74.3436');

  // Temporal range
  const [startDate, setStartDate] = useState('1991-01-01');
  const [endDate, setEndDate] = useState('2020-12-31');

  // Parameters
  const [selectedParams, setSelectedParams] = useState<string[]>(['T2M', 'PRECTOTCORR']);
  const [paramJustifications, setParamJustifications] = useState<Record<string, string>>({});

  // Selected datasets
  const [selectedDatasetIds, setSelectedDatasetIds] = useState<string[]>([
    'nasa-power-merra2',
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [isAiPlanning, setIsAiPlanning] = useState(false);
  const [aiStatus, setAiStatus] = useState<{ available: boolean; provider: string; model?: string; message: string } | null>(null);
  const [aiNotice, setAiNotice] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    apiService.getAiStatus().then(setAiStatus).catch(() => {});
  }, []);

  const handlePlanWithAi = async () => {
    if (!researchQuestion.trim()) {
      setValidationError('Please enter a research inquiry first.');
      return;
    }
    try {
      setIsAiPlanning(true);
      setValidationError(null);
      const plan = await apiService.planWithAi(researchQuestion);
      if (plan.title) setTitle(plan.title);
      if (plan.research_question) setResearchQuestion(plan.research_question);
      if (plan.hypothesis) setHypothesis(plan.hypothesis);
      if (plan.location_name) setLocName(plan.location_name);
      if (plan.country) setLocCountry(plan.country);
      if (plan.latitude !== undefined) setLat(String(plan.latitude));
      if (plan.longitude !== undefined) setLng(String(plan.longitude));
      if (plan.start_year) setStartDate(`${plan.start_year}-01-01`);
      if (plan.end_year) setEndDate(`${plan.end_year}-12-31`);
      if (plan.parameters && Array.isArray(plan.parameters)) setSelectedParams(plan.parameters);
      if (plan.parameter_justifications) setParamJustifications(plan.parameter_justifications);

      setAiNotice(
        plan.is_ai_generated
          ? `Plan formulated by Google Gemini (${plan.ai_model || 'Gemini'}). Parameters and hypotheses populated.`
          : `Plan formulated by EarthSage deterministic research planner (Gemini offline).`
      );
    } catch (e: any) {
      setValidationError(`AI Planning failed: ${e.message}`);
    } finally {
      setIsAiPlanning(false);
    }
  };

  const toggleDataset = (id: string) => {
    if (selectedDatasetIds.includes(id)) {
      setSelectedDatasetIds(selectedDatasetIds.filter((item) => item !== id));
    } else {
      setSelectedDatasetIds([...selectedDatasetIds, id]);
    }
  };

  const toggleParam = (param: string) => {
    if (selectedParams.includes(param)) {
      if (selectedParams.length > 1) {
        setSelectedParams(selectedParams.filter((p) => p !== param));
      }
    } else {
      setSelectedParams([...selectedParams, param]);
    }
  };

  const setPresetLocation = (name: string, region: string, country: string, latVal: string, lngVal: string) => {
    setLocName(name);
    setLocRegion(region);
    setLocCountry(country);
    setLat(latVal);
    setLng(lngVal);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!title.trim()) {
      setValidationError('Investigation title is required.');
      return;
    }
    if (!researchQuestion.trim()) {
      setValidationError('A clear scientific research question is required.');
      return;
    }

    const parsedLat = parseFloat(lat);
    const parsedLng = parseFloat(lng);
    if (isNaN(parsedLat) || isNaN(parsedLng)) {
      setValidationError('Valid numerical coordinates are required.');
      return;
    }

    try {
      setIsLoading(true);
      const newInv = await apiService.createInvestigation({
        title,
        researchQuestion,
        hypothesis: hypothesis.trim() || undefined,
        primaryLocation: {
          lat: parsedLat,
          lng: parsedLng,
          name: locName,
          region: locRegion,
          country: locCountry,
        },
        temporalRange: {
          start: startDate,
          end: endDate,
        },
        datasetIds: selectedDatasetIds,
        parameters: selectedParams,
      });

      onCreated(newInv);
    } catch (err: any) {
      setValidationError(err.message || 'Failed to submit investigation.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto' }}>
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <h1 style={{ fontSize: '22px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
          Initiate Scientific Investigation
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
          Define an empirical inquiry, set coordinate bounds, and retrieve verified NASA POWER / MERRA-2 meteorological data.
        </p>
      </div>

      {validationError && (
        <div
          style={{
            padding: '10px 14px',
            backgroundColor: 'var(--color-error-subtle)',
            border: '1px solid var(--color-error-border)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--color-error)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '13px',
            marginBottom: 'var(--space-lg)',
          }}
        >
          <AlertCircle size={16} />
          <span>{validationError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
        {/* Research Question & Identification */}
        <section
          style={{
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--color-bg)',
            padding: 'var(--space-lg)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-md)' }}>
            <BookOpen size={16} style={{ color: 'var(--color-primary)' }} />
            <h2 style={{ fontSize: '15px', fontWeight: 600 }}>Scientific Inquiry</h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, marginBottom: '4px' }}>
                Investigation Title *
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                  fontSize: '13px',
                }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <label style={{ fontSize: '12px', fontWeight: 500 }}>
                  Research Question *
                </label>
                <button
                  type="button"
                  onClick={handlePlanWithAi}
                  disabled={isAiPlanning}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '11px',
                    padding: '2px 8px',
                    border: '1px solid var(--color-border)',
                    backgroundColor: 'var(--color-surface)',
                    color: 'var(--color-primary)',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  <Sparkles size={12} />
                  {isAiPlanning ? 'Formulating Plan...' : 'Plan with AI Assistant'}
                </button>
              </div>
              <textarea
                value={researchQuestion}
                onChange={(e) => setResearchQuestion(e.target.value)}
                rows={3}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                  fontSize: '13px',
                  resize: 'vertical',
                }}
              />
              {aiNotice && (
                <div style={{ marginTop: '6px', fontSize: '11px', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <CheckCircle2 size={12} />
                  <span>{aiNotice}</span>
                </div>
              )}
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, marginBottom: '4px' }}>
                Working Hypothesis (Optional)
              </label>
              <input
                type="text"
                value={hypothesis}
                onChange={(e) => setHypothesis(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                  fontSize: '13px',
                }}
              />
            </div>
          </div>
        </section>

        {/* Spatial and Temporal Scope */}
        <section
          style={{
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--color-bg)',
            padding: 'var(--space-lg)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Compass size={16} style={{ color: 'var(--color-primary)' }} />
              <h2 style={{ fontSize: '15px', fontWeight: 600 }}>Geographic Point & Observation Bounds</h2>
            </div>
            {/* Rapid Preset Stations */}
            <div style={{ display: 'flex', gap: '6px' }}>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setPresetLocation('Lahore', 'Punjab', 'Pakistan', '31.5497', '74.3436')}
              >
                Lahore (Test)
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setPresetLocation('Geneva / Alps', 'Geneva', 'Switzerland', '46.2044', '6.1432')}
              >
                Geneva
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setPresetLocation('Nairobi Basin', 'Nairobi', 'Kenya', '-1.2921', '36.8219')}
              >
                Nairobi
              </Button>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, marginBottom: '4px' }}>
                Location / Site Name
              </label>
              <input
                type="text"
                value={locName}
                onChange={(e) => setLocName(e.target.value)}
                style={{
                  width: '100%',
                  padding: '6px 10px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, marginBottom: '4px' }}>
                Country
              </label>
              <input
                type="text"
                value={locCountry}
                onChange={(e) => setLocCountry(e.target.value)}
                style={{
                  width: '100%',
                  padding: '6px 10px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, marginBottom: '4px' }}>
                Latitude (WGS84)
              </label>
              <input
                type="text"
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                className="tabular-nums"
                style={{
                  width: '100%',
                  padding: '6px 10px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, marginBottom: '4px' }}>
                Longitude (WGS84)
              </label>
              <input
                type="text"
                value={lng}
                onChange={(e) => setLng(e.target.value)}
                className="tabular-nums"
                style={{
                  width: '100%',
                  padding: '6px 10px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                }}
              />
            </div>
          </div>

          <div style={{ marginTop: 'var(--space-md)', paddingTop: 'var(--space-md)', borderTop: '1px solid var(--color-border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <Calendar size={14} style={{ color: 'var(--color-text-secondary)' }} />
              <span style={{ fontSize: '12px', fontWeight: 500 }}>Temporal Window (NASA POWER Baseline 1981–Present):</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
              <div>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--color-text-muted)', marginBottom: '2px' }}>
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '6px 10px',
                    borderRadius: 'var(--radius-xs)',
                    border: '1px solid var(--color-border)',
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--color-text-muted)', marginBottom: '2px' }}>
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '6px 10px',
                    borderRadius: 'var(--radius-xs)',
                    border: '1px solid var(--color-border)',
                  }}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Meteorological Parameters to Retrieve and Analyze */}
        <section
          style={{
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--color-bg)',
            padding: 'var(--space-lg)',
          }}
        >
          <div style={{ marginBottom: 'var(--space-md)' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 600 }}>NASA POWER / MERRA-2 Variables</h2>
            <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
              Select variables to retrieve and subject to Mann-Kendall and Sen's slope analysis.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-sm)' }}>
            {[
              { id: 'T2M', name: 'T2M (Temperature at 2m)', unit: '°C', desc: 'Mean monthly air temperature estimate' },
              { id: 'PRECTOTCORR', name: 'PRECTOTCORR (Precipitation)', unit: 'mm/day', desc: 'Bias-corrected precipitation flux' },
              { id: 'T2M_MAX', name: 'T2M_MAX (Max Temperature)', unit: '°C', desc: 'Monthly maximum of daily maximum' },
              { id: 'T2M_MIN', name: 'T2M_MIN (Min Temperature)', unit: '°C', desc: 'Monthly minimum of daily minimum' }
            ].map((param) => {
              const active = selectedParams.includes(param.id);
              return (
                <div
                  key={param.id}
                  onClick={() => toggleParam(param.id)}
                  style={{
                    padding: '10px 14px',
                    border: active ? '1px solid var(--color-primary)' : '1px solid var(--color-border)',
                    backgroundColor: active ? 'var(--color-primary-subtle)' : 'var(--color-surface)',
                    borderRadius: 'var(--radius-xs)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '10px',
                  }}
                >
                  <input
                    type="checkbox"
                    checked={active}
                    onChange={() => { }}
                    style={{ marginTop: '2px', cursor: 'pointer' }}
                  />
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                      {param.name}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                      {param.desc} ({param.unit})
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {Object.keys(paramJustifications).length > 0 && (
            <div style={{ marginTop: 'var(--space-md)', padding: '10px 12px', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', fontSize: '11px' }}>
              <div style={{ fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '4px' }}>
                Scientific Variable Justifications (Research Assistant):
              </div>
              {Object.entries(paramJustifications).map(([p, just]) => (
                <div key={p} style={{ marginTop: '2px', color: 'var(--color-text-secondary)' }}>
                  <strong>{p}:</strong> {just}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Selected Data Sources */}
        <section
          style={{
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--color-bg)',
            padding: 'var(--space-lg)',
          }}
        >
          <div style={{ marginBottom: 'var(--space-md)' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 600 }}>Observational Data Provider</h2>
          </div>

          <DataSourceList
            sources={dataSources}
            selectedSourceIds={selectedDatasetIds}
            onToggleSelect={toggleDataset}
          />
        </section>

        {/* Action Controls */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" isLoading={isLoading}>
            Create Investigation Workspace
          </Button>
        </div>
      </form>
    </div>
  );
};
