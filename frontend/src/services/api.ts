import {
  Project,
  Application,
  TestCase,
  TestSuite,
  TestRun,
  TestResult,
  Bug,
  ExecutionLog,
  AgentSettings
} from '../types';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`API Error ${res.status}: ${errorBody}`);
  }
  return res.json();
}

export const api = {
  // Projects
  getProjects: () => fetchJson<Project[]>('/projects'),
  createProject: (data: { name: string; description?: string }) =>
    fetchJson<Project>('/projects', { method: 'POST', body: JSON.stringify(data) }),

  // Applications
  getApplications: (projectId?: string) =>
    fetchJson<Application[]>(`/applications${projectId ? `?project_id=${projectId}` : ''}`),
  createApplication: (data: any) =>
    fetchJson<Application>('/applications', { method: 'POST', body: JSON.stringify(data) }),

  // Test Cases
  getTestCases: (appId?: string) =>
    fetchJson<TestCase[]>(`/test-cases${appId ? `?application_id=${appId}` : ''}`),
  createTestCase: (data: any) =>
    fetchJson<TestCase>('/test-cases', { method: 'POST', body: JSON.stringify(data) }),
  updateTestCase: (id: string, data: any) =>
    fetchJson<TestCase>(`/test-cases/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTestCase: (id: string) =>
    fetchJson<{ status: string; id: string }>(`/test-cases/${id}`, { method: 'DELETE' }),
  generateFromNaturalLanguage: (data: { application_id: string; prompt: string; module?: string; priority?: string }) =>
    fetchJson<TestCase>('/test-cases/natural-language', { method: 'POST', body: JSON.stringify(data) }),

  // Test Suites
  getTestSuites: (projectId?: string) =>
    fetchJson<TestSuite[]>(`/test-suites${projectId ? `?project_id=${projectId}` : ''}`),
  createTestSuite: (data: any) =>
    fetchJson<TestSuite>('/test-suites', { method: 'POST', body: JSON.stringify(data) }),

  // Test Runs
  getTestRuns: (appId?: string) =>
    fetchJson<TestRun[]>(`/test-runs${appId ? `?application_id=${appId}` : ''}`),
  getTestRunDetail: (id: string) =>
    fetchJson<{ run: TestRun; results: TestResult[]; bugs: Bug[]; logs: ExecutionLog[] }>(`/test-runs/${id}`),
  startTestRun: (data: {
    application_id: string;
    name?: string;
    mode: string;
    environment?: string;
    browser?: string;
    headless?: boolean;
    credentials?: any;
    custom_prompt?: string;
  }) => fetchJson<TestRun>('/test-runs', { method: 'POST', body: JSON.stringify(data) }),
  controlTestRun: (runId: string, action: 'pause' | 'resume' | 'stop') =>
    fetchJson<{ status: string; message: string }>(`/test-runs/${runId}/control`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    }),

  // Bugs
  getBugs: (runId?: string, severity?: string, status?: string) => {
    const params = new URLSearchParams();
    if (runId) params.append('test_run_id', runId);
    if (severity) params.append('severity', severity);
    if (status) params.append('status', status);
    return fetchJson<Bug[]>(`/bugs?${params.toString()}`);
  },
  getBugDetail: (id: string) => fetchJson<Bug>(`/bugs/${id}`),
  updateBugStatus: (id: string, data: { status?: string; severity?: string; priority?: string }) =>
    fetchJson<Bug>(`/bugs/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  // Reports
  getReportJson: (runId: string) => fetchJson<any>(`/reports/${runId}`),
  getRegressionReport: (runId: string) => fetchJson<any>(`/reports/${runId}/regression`),

  // Settings
  getSettings: () => fetchJson<AgentSettings>('/settings'),
  updateSettings: (data: Partial<AgentSettings>) =>
    fetchJson<{ status: string; settings: AgentSettings }>('/settings', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
