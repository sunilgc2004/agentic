import React, { useState } from 'react';
import { Play, Plus, Clock, Globe, Laptop, ArrowRight } from 'lucide-react';
import { TestRun, Application } from '../types';
import { StatusBadge } from '../components/common/StatusBadge';
import { Modal } from '../components/common/Modal';

interface TestRunsPageProps {
  testRuns: TestRun[];
  applications: Application[];
  selectedApp: Application | null;
  onStartTestRun: (data: any) => Promise<void>;
  onInspectRun: (runId: string) => void;
}

export const TestRunsPage: React.FC<TestRunsPageProps> = ({
  testRuns,
  applications,
  selectedApp,
  onStartTestRun,
  onInspectRun,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAppId, setSelectedAppId] = useState(selectedApp?.id || '');
  const [mode, setMode] = useState('SMOKE');
  const [environment, setEnvironment] = useState('qa');
  const [browser, setBrowser] = useState('chromium');
  const [headless, setHeadless] = useState(true);
  const [customPrompt, setCustomPrompt] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAppId) return;
    setIsSubmitting(true);
    try {
      await onStartTestRun({
        application_id: selectedAppId,
        mode,
        environment,
        browser,
        headless,
        custom_prompt: customPrompt.trim() || undefined,
      });
      setIsModalOpen(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100">AI Test Execution Sessions</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            History of autonomous exploration, smoke, functional, regression, and negative testing runs.
          </p>
        </div>
        <button
          onClick={() => {
            if (selectedApp) setSelectedAppId(selectedApp.id);
            setIsModalOpen(true);
          }}
          className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-2 shadow"
        >
          <Plus size={16} />
          <span>New AI Test Run</span>
        </button>
      </div>

      {/* Test Runs List */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-950/50 text-slate-400 text-xs uppercase font-medium">
            <tr>
              <th className="px-6 py-3">Session Name</th>
              <th className="px-6 py-3">Test Mode</th>
              <th className="px-6 py-3">Environment</th>
              <th className="px-6 py-3">Browser</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Tally (P / F / B)</th>
              <th className="px-6 py-3">Pass %</th>
              <th className="px-6 py-3">Duration</th>
              <th className="px-6 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-300">
            {testRuns.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-6 py-10 text-center text-slate-500">
                  No execution runs yet. Click 'New AI Test Run' to begin.
                </td>
              </tr>
            ) : (
              testRuns.map((run) => (
                <tr key={run.id} className="hover:bg-slate-800/40 transition">
                  <td className="px-6 py-4 font-medium text-slate-100">{run.name}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                      {run.mode}
                    </span>
                  </td>
                  <td className="px-6 py-4 capitalize text-slate-300">{run.environment}</td>
                  <td className="px-6 py-4 text-xs font-mono text-slate-400 capitalize">{run.browser}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={run.status} />
                  </td>
                  <td className="px-6 py-4 font-mono text-xs">
                    <span className="text-emerald-400 font-semibold">{run.passed_tests}P</span> /{' '}
                    <span className="text-rose-400 font-semibold">{run.failed_tests}F</span> /{' '}
                    <span className="text-amber-400 font-semibold">{run.blocked_tests}B</span>
                  </td>
                  <td className="px-6 py-4 font-semibold text-xs text-slate-200">{run.pass_percentage}%</td>
                  <td className="px-6 py-4 text-xs text-slate-400 flex items-center space-x-1">
                    <Clock size={12} />
                    <span>{run.duration_seconds}s</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => onInspectRun(run.id)}
                      className="text-sky-400 hover:text-sky-300 text-xs font-semibold inline-flex items-center space-x-1"
                    >
                      <span>{run.status === 'RUNNING' ? 'Watch Live' : 'View Report'}</span>
                      <ArrowRight size={14} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* New Test Run Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Configure New Autonomous AI Test Run">
        <form onSubmit={handleSubmit} className="space-y-4 text-sm">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Target Application</label>
            <select
              value={selectedAppId}
              onChange={(e) => setSelectedAppId(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200 text-xs focus:ring-1 focus:ring-sky-500"
              required
            >
              {applications.map((app) => (
                <option key={app.id} value={app.id}>
                  {app.name} ({app.base_url})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Testing Mode (Section 4)</label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200 text-xs focus:ring-1 focus:ring-sky-500"
            >
              <option value="SMOKE">Smoke Testing (Critical Path Workflows)</option>
              <option value="FUNCTIONAL">Functional Testing (Feature Verification)</option>
              <option value="NEGATIVE">Negative Testing (Invalid Inputs, SQL Injection, Boundary)</option>
              <option value="UI">UI &amp; Responsive Layout Testing</option>
              <option value="REGRESSION">Regression Testing (Compare Against Baseline)</option>
              <option value="EXPLORATORY">Exploratory Testing (Autonomous Crawler Budget)</option>
              <option value="FULL_QA">Full QA Comprehensive Suite</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Target Environment</label>
              <select
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200 text-xs"
              >
                <option value="qa">QA</option>
                <option value="local">Local</option>
                <option value="development">Development</option>
                <option value="staging">Staging</option>
                <option value="production">Production (Enforces Safe Mode)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Browser Engine (Section 43)</label>
              <select
                value={browser}
                onChange={(e) => setBrowser(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200 text-xs"
              >
                <option value="chromium">Chromium (Google Chrome)</option>
                <option value="firefox">Firefox</option>
                <option value="webkit">WebKit (Apple Safari)</option>
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-2 pt-2">
            <input
              type="checkbox"
              id="headless"
              checked={headless}
              onChange={(e) => setHeadless(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0"
            />
            <label htmlFor="headless" className="text-xs text-slate-300">
              Run Headless Browser (Uncheck for headed browser observation)
            </label>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Custom Natural Language Goal (Optional)
            </label>
            <input
              type="text"
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder="e.g. 'Verify that a user can create an arbitration case and generate VC link'"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200 text-xs focus:ring-1 focus:ring-sky-500"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-lg text-xs flex items-center space-x-2 shadow"
            >
              <Play size={14} />
              <span>{isSubmitting ? 'Starting Agent...' : 'Launch Autonomous Test'}</span>
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
