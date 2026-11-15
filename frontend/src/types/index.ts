export type InvestigationStatus = 
  | 'draft'
  | 'queued'
  | 'running'
  | 'completed'
  | 'failed';

export type FindingClassification = 
  | 'observed'
  | 'statistical'
  | 'predicted'
  | 'hypothesis';

export interface GeoLocation {
  lat: number;
  lng: number;
  name: string;
  region: string;
  country: string;
}

export interface DataSourceReference {
  id: string;
  name: string;
  provider: string;
  collectionPeriod: string;
  geographicCoverage: string;
  resolution: string;
  url: string;
  doi?: string;
  retrievalTimestamp: string;
  limitations: string;
}

export interface MetricMeasurement {
  id: string;
  label: string;
  value: number | string;
  unit: string;
  uncertainty?: string;
  type: 'observed' | 'statistical' | 'model';
}

export interface TimeSeriesPoint {
  timestamp: string;
  observed?: number | null;
  predicted?: number | null;
  uncertaintyLower?: number | null;
  uncertaintyUpper?: number | null;
}

export interface ScientificFinding {
  id: string;
  title: string;
  classification: FindingClassification;
  summary: string;
  confidenceScore?: number; // Optional, only if statistically calculated
  evidenceReferences: string[]; // DataSourceReference IDs
  measurements?: MetricMeasurement[];
}

export interface Investigation {
  id: string;
  userId?: string | null;
  title: string;
  researchQuestion: string;
  hypothesis?: string;
  status: InvestigationStatus;
  createdAt: string;
  updatedAt: string;
  primaryLocation: GeoLocation;
  spatialExtent: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
  temporalRange: {
    start: string;
    end: string;
  };
  datasetIds: string[];
  findings: ScientificFinding[];
  timeSeriesData: TimeSeriesPoint[];
  reportAvailable: boolean;
  notes?: string;
}

export interface SavedReport {
  id: string;
  investigationId: string;
  title: string;
  author: string;
  generatedAt: string;
  fileFormat: 'PDF' | 'CSV' | 'GeoJSON';
  fileSize: string;
  summary: string;
}

export interface User {
  id: string;
  fullName: string;
  email: string;
  isActive: boolean;
  createdAt: string;
}

export interface AuthResponse {
  accessToken: string;
  tokenType: string;
  user: User;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface SignupPayload {
  fullName: string;
  email: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}


