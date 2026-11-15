import { DataSourceReference, Investigation, SavedReport } from '../types';
import { authService } from './authService';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8020';

async function authedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const headers = new Headers(options.headers || {});
  const token = authService.getAccessToken();
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const mergedOptions: RequestInit = {
    ...options,
    headers,
    credentials: 'include',
  };

  let res = await fetch(url, mergedOptions);

  // Silent automatic token refresh on 401 Unauthorized (unless it's an auth route)
  if (res.status === 401 && !url.includes('/api/auth/')) {
    const newToken = await authService.refreshToken();
    if (newToken) {
      headers.set('Authorization', `Bearer ${newToken}`);
      res = await fetch(url, {
        ...options,
        headers,
        credentials: 'include',
      });
    }
  }

  return res;
}

export const apiService = {
  // Data Sources Catalog
  async getDataSources(): Promise<DataSourceReference[]> {
    try {
      const res = await authedFetch(`${API_BASE_URL}/api/v1/datasets`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('Backend datasets API fallback:', e);
      return [];
    }
  },

  // Investigations List
  async getInvestigations(): Promise<Investigation[]> {
    const res = await authedFetch(`${API_BASE_URL}/api/v1/investigations`);
    if (!res.ok) throw new Error(`Failed to load investigations: HTTP ${res.status}`);
    return await res.json();
  },

  // Single Investigation Detail
  async getInvestigationById(id: string): Promise<Investigation | null> {
    const res = await authedFetch(`${API_BASE_URL}/api/v1/investigations/${id}`);
    if (!res.ok) {
      if (res.status === 404) return null;
      throw new Error(`Failed to load investigation: HTTP ${res.status}`);
    }
    return await res.json();
  },

  // Create Investigation
  async createInvestigation(payload: {
    title: string;
    researchQuestion: string;
    hypothesis?: string;
    primaryLocation: { lat: number; lng: number; name: string; region: string; country: string };
    temporalRange: { start: string; end: string };
    datasetIds: string[];
    parameters?: string[];
  }): Promise<Investigation> {
    const startYear = parseInt(payload.temporalRange.start.substring(0, 4), 10) || 1991;
    const endYear = parseInt(payload.temporalRange.end.substring(0, 4), 10) || 2020;

    const body = {
      title: payload.title,
      research_question: payload.researchQuestion,
      hypothesis: payload.hypothesis || null,
      location_name: payload.primaryLocation.name,
      region: payload.primaryLocation.region,
      country: payload.primaryLocation.country,
      latitude: payload.primaryLocation.lat,
      longitude: payload.primaryLocation.lng,
      start_year: startYear,
      end_year: endYear,
      parameters: payload.parameters || ['T2M', 'PRECTOTCORR']
    };

    const res = await authedFetch(`${API_BASE_URL}/api/v1/investigations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Creation failed' }));
      throw new Error(err.detail || `Server error HTTP ${res.status}`);
    }

    return await res.json();
  },

  // Execute Analytical Pipeline (NASA POWER fetch + Mann-Kendall + Sen's slope + DB commit)
  async runInvestigation(id: string): Promise<Investigation> {
    const res = await authedFetch(`${API_BASE_URL}/api/v1/investigations/${id}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Execution failed' }));
      throw new Error(err.detail || `Server error HTTP ${res.status}`);
    }

    return await res.json();
  },

  // Saved Reports
  async getReports(): Promise<SavedReport[]> {
    try {
      const res = await authedFetch(`${API_BASE_URL}/api/v1/reports`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('Backend reports API fallback:', e);
      return [];
    }
  },

  async generateReport(investigationId: string, format: 'PDF' | 'CSV' | 'GeoJSON'): Promise<SavedReport> {
    const res = await authedFetch(`${API_BASE_URL}/api/v1/reports`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        investigation_id: investigationId,
        file_format: format
      })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Report generation failed' }));
      throw new Error(err.detail || `Server error HTTP ${res.status}`);
    }

    return await res.json();
  },

  getDownloadUrl(reportId: string): string {
    return `${API_BASE_URL}/api/v1/reports/${reportId}/download`;
  },

  // Gemini AI Research Assistant
  async getAiStatus(): Promise<{ available: boolean; provider: string; model?: string; message: string }> {
    try {
      const res = await authedFetch(`${API_BASE_URL}/api/v1/ai/status`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      return { available: false, provider: 'none', message: 'AI service unreachable.' };
    }
  },

  async planWithAi(researchQuestion: string): Promise<any> {
    const res = await authedFetch(`${API_BASE_URL}/api/v1/ai/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ research_question: researchQuestion }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'AI planning failed' }));
      throw new Error(err.detail || `Server error HTTP ${res.status}`);
    }
    return await res.json();
  },

  async explainFindingsWithAi(invId: string): Promise<any> {
    const res = await authedFetch(`${API_BASE_URL}/api/v1/ai/explain/${invId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'AI explanation failed' }));
      throw new Error(err.detail || `Server error HTTP ${res.status}`);
    }
    return await res.json();
  },

  // Anomaly Detection
  async getAnomalies(invId: string): Promise<any> {
    const res = await authedFetch(`${API_BASE_URL}/api/v1/analysis/investigations/${invId}/anomalies`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch anomalies' }));
      throw new Error(err.detail || `Server error HTTP ${res.status}`);
    }
    return await res.json();
  },

  // Variable Comparison
  async getVariableComparison(invId: string, paramA = 'T2M', paramB = 'PRECTOTCORR'): Promise<any> {
    const res = await authedFetch(
      `${API_BASE_URL}/api/v1/analysis/investigations/${invId}/compare?param_a=${paramA}&param_b=${paramB}`
    );
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch comparison' }));
      throw new Error(err.detail || `Server error HTTP ${res.status}`);
    }
    return await res.json();
  }
};
