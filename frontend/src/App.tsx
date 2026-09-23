import React, { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { LiveExecutionPage } from './pages/LiveExecutionPage';
import { TestRunsPage } from './pages/TestRunsPage';
import { TestCasesPage } from './pages/TestCasesPage';
import { TestSuitesPage } from './pages/TestSuitesPage';
import { BugReportsPage } from './pages/BugReportsPage';
import { ReportsPage } from './pages/ReportsPage';
import { PlaygroundPage } from './pages/PlaygroundPage';
import { ApplicationsPage } from './pages/ApplicationsPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { SettingsPage } from './pages/SettingsPage';

import { api } from './services/api';
import { Project, Application, TestRun, Bug } from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [projects, setProjects] = useState<Project[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [bugs, setBugs] = useState<Bug[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [projs, apps, runs, bugList] = await Promise.all([
        api.getProjects(),
        api.getApplications(),
        api.getTestRuns(),
        api.getBugs(),
      ]);

      setProjects(projs);
      setApplications(apps);
      if (apps.length > 0 && !selectedApp) {
        setSelectedApp(apps[0]);
      }
      setTestRuns(runs);
      setBugs(bugList);

      // Check if any run is currently RUNNING
      const running = runs.find((r) => r.status === 'RUNNING' || r.status === 'PENDING');
      if (running) {
        setActiveRunId(running.id);
      }
    } catch (e) {
      console.error('Failed to load initial workspace data', e);
    }
  };

  const handleStartTestRun = async (config: {
    application_id?: string;
    mode: string;
    environment?: string;
    browser?: string;
    headless?: boolean;
    custom_prompt?: string;
  }) => {
    const appId = config.application_id || selectedApp?.id;
    if (!appId) {
      alert('Please select or add an application first.');
      return;
    }

    try {
      const newRun = await api.startTestRun({
        application_id: appId,
        mode: config.mode,
        environment: config.environment || 'qa',
        browser: config.browser || 'chromium',
        headless: config.headless !== false,
        custom_prompt: config.custom_prompt,
      });

      setTestRuns([newRun, ...testRuns]);
      setActiveRunId(newRun.id);
      setCurrentTab('live');
    } catch (e: any) {
      alert(`Failed to start test run: ${e.message}`);
    }
  };

  const handleInspectRun = (runId: string) => {
    const run = testRuns.find((r) => r.id === runId);
    if (run && (run.status === 'RUNNING' || run.status === 'PENDING')) {
      setActiveRunId(runId);
      setCurrentTab('live');
    } else {
      setActiveRunId(runId);
      setCurrentTab('reports');
    }
  };

  const isExecuting = testRuns.some((r) => r.id === activeRunId && (r.status === 'RUNNING' || r.status === 'PENDING'));

  return (
    <div className="min-h-screen bg-[#090e1f] text-slate-100 flex flex-col font-sans">
      <Navbar
        applications={applications}
        selectedApp={selectedApp}
        onSelectApp={setSelectedApp}
        onQuickStart={() => handleStartTestRun({ mode: 'SMOKE' })}
        isExecuting={isExecuting}
      />

      <div className="flex flex-1">
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          activeRunId={isExecuting ? activeRunId : null}
        />

        <main className="flex-1 p-8 overflow-y-auto max-w-7xl mx-auto w-full">
          {currentTab === 'dashboard' && (
            <DashboardPage
              testRuns={testRuns}
              bugs={bugs}
              onStartTest={(mode) => handleStartTestRun({ mode })}
              onSelectRun={handleInspectRun}
            />
          )}

          {currentTab === 'live' && (
            <LiveExecutionPage
              runId={activeRunId || testRuns[0]?.id || null}
              onRunCompleted={() => {
                loadInitialData();
              }}
            />
          )}

          {currentTab === 'test-runs' && (
            <TestRunsPage
              testRuns={testRuns}
              applications={applications}
              selectedApp={selectedApp}
              onStartTestRun={handleStartTestRun}
              onInspectRun={handleInspectRun}
            />
          )}

          {currentTab === 'test-cases' && (
            <TestCasesPage selectedApp={selectedApp} />
          )}

          {currentTab === 'test-suites' && (
            <TestSuitesPage
              projects={projects}
              onStartSuiteRun={() => handleStartTestRun({ mode: 'SMOKE' })}
            />
          )}

          {currentTab === 'bugs' && (
            <BugReportsPage
              bugs={bugs}
              onRefresh={() => api.getBugs().then(setBugs)}
            />
          )}

          {currentTab === 'reports' && (
            <ReportsPage testRuns={testRuns} />
          )}

          {currentTab === 'playground' && <PlaygroundPage />}

          {currentTab === 'applications' && (
            <ApplicationsPage
              applications={applications}
              projects={projects}
              onRefresh={loadInitialData}
              onSelectApp={(app) => {
                setSelectedApp(app);
                setCurrentTab('dashboard');
              }}
            />
          )}

          {currentTab === 'projects' && (
            <ProjectsPage projects={projects} onRefresh={loadInitialData} />
          )}

          {currentTab === 'settings' && <SettingsPage />}
        </main>
      </div>
    </div>
  );
};

export default App;
