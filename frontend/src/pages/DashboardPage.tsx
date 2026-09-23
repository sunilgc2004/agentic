import React from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  TrendingUp,
  Clock,
  Bug as BugIcon,
  Play,
  ArrowRight,
} from 'lucide-react';
import { TestRun, Bug } from '../types';
import { StatusBadge } from '../components/common/StatusBadge';

interface DashboardPageProps {
  testRuns: TestRun[];
  bugs: Bug[];
  onStartTest: (mode: string) => void;
  onSelectRun: (runId: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  testRuns,
  bugs,
  onStartTest,
  onSelectRun,
}) => {
  // Aggregate stats across all runs or latest run
  const latestRun = testRuns[0];

  const totalRuns = testRuns.length;
  const totalTests = testRuns.reduce((acc, r) => acc + r.total_tests, 0);
  const totalPassed = testRuns.reduce((acc, r) => acc + r.passed_tests, 0);
  const totalFailed = testRuns.reduce((acc, r) => acc + r.failed_tests, 0);
  const totalBlocked = testRuns.reduce((acc, r) => acc + r.blocked_tests, 0);
  const totalInconclusive = testRuns.reduce((acc, r) => acc + r.inconclusive_tests, 0);
  const avgPassRate =
    totalTests > 0 ? Math.round((totalPassed / totalTests) * 100) : 0;

  const criticalBugs = bugs.filter((b) => b.severity === 'Critical').length;
  const highBugs = bugs.filter((b) => b.severity === 'High').length;
  const mediumBugs = bugs.filter((b) => b.severity === 'Medium').length;
  const lowBugs = bugs.filter((b) => b.severity === 'Low').length;

  return (
    <div className="space-y-6">
      {/* Top Banner / Quick Action */}
      <div className="bg-gradient-to-r from-sky-900/40 via-slate-900 to-slate-900 border border-sky-500/20 rounded-xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Autonomous QA Engineer Console</h2>
          <p className="text-sm text-slate-400 mt-1">
            Playwright-driven autonomous crawler, multi-agent AI verification, self-healing locators, and automated bug reports.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => onStartTest('SMOKE')}
            className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-1.5 shadow"
          >
            <Play size={14} />
            <span>Run Smoke Test</span>
          </button>
          <button
            onClick={() => onStartTest('NEGATIVE')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold rounded-lg"
          >
            Run Negative Test
          </button>
          <button
            onClick={() => onStartTest('FULL_QA')}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg"
          >
            Run Full QA
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Tests Executed</div>
          <div className="text-2xl font-bold text-slate-100 mt-2">{totalTests}</div>
          <div className="text-xs text-slate-500 mt-1">{totalRuns} test runs recorded</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs font-medium text-emerald-400 uppercase tracking-wider flex items-center space-x-1">
            <CheckCircle2 size={14} />
            <span>Passed</span>
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-2">{totalPassed}</div>
          <div className="text-xs text-slate-500 mt-1">{avgPassRate}% average pass rate</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs font-medium text-rose-400 uppercase tracking-wider flex items-center space-x-1">
            <XCircle size={14} />
            <span>Failed</span>
          </div>
          <div className="text-2xl font-bold text-rose-400 mt-2">{totalFailed}</div>
          <div className="text-xs text-slate-500 mt-1">Requires investigation</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs font-medium text-amber-400 uppercase tracking-wider flex items-center space-x-1">
            <AlertTriangle size={14} />
            <span>Blocked</span>
          </div>
          <div className="text-2xl font-bold text-amber-400 mt-2">{totalBlocked}</div>
          <div className="text-xs text-slate-500 mt-1">Safety policy stops</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center space-x-1">
            <HelpCircle size={14} />
            <span>Inconclusive</span>
          </div>
          <div className="text-2xl font-bold text-slate-300 mt-2">{totalInconclusive}</div>
          <div className="text-xs text-slate-500 mt-1">Confidence &lt; 70%</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs font-medium text-rose-400 uppercase tracking-wider flex items-center space-x-1">
            <BugIcon size={14} />
            <span>Open Bugs</span>
          </div>
          <div className="text-2xl font-bold text-rose-300 mt-2">{bugs.length}</div>
          <div className="text-xs text-rose-400 mt-1">{criticalBugs} Critical | {highBugs} High</div>
        </div>
      </div>

      {/* Visual Analytics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pass / Fail Distribution Bar */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center space-x-2">
            <TrendingUp size={16} className="text-sky-400" />
            <span>Overall Test Outcome Breakdown</span>
          </h3>
          {totalTests === 0 ? (
            <div className="text-sm text-slate-500 py-8 text-center">No test execution records yet. Click 'Start AI Test' to begin.</div>
          ) : (
            <div className="space-y-4">
              <div className="h-4 w-full bg-slate-800 rounded-full overflow-hidden flex">
                <div style={{ width: `${(totalPassed / totalTests) * 100}%` }} className="bg-emerald-500" title="Passed" />
                <div style={{ width: `${(totalFailed / totalTests) * 100}%` }} className="bg-rose-500" title="Failed" />
                <div style={{ width: `${(totalBlocked / totalTests) * 100}%` }} className="bg-amber-500" title="Blocked" />
                <div style={{ width: `${(totalInconclusive / totalTests) * 100}%` }} className="bg-slate-600" title="Inconclusive" />
              </div>
              <div className="grid grid-cols-4 gap-2 text-xs text-center">
                <div className="bg-slate-800/40 p-2 rounded">
                  <span className="text-emerald-400 font-bold">{Math.round((totalPassed / totalTests) * 100)}%</span>
                  <div className="text-slate-400">Pass</div>
                </div>
                <div className="bg-slate-800/40 p-2 rounded">
                  <span className="text-rose-400 font-bold">{Math.round((totalFailed / totalTests) * 100)}%</span>
                  <div className="text-slate-400">Fail</div>
                </div>
                <div className="bg-slate-800/40 p-2 rounded">
                  <span className="text-amber-400 font-bold">{Math.round((totalBlocked / totalTests) * 100)}%</span>
                  <div className="text-slate-400">Blocked</div>
                </div>
                <div className="bg-slate-800/40 p-2 rounded">
                  <span className="text-slate-400 font-bold">{Math.round((totalInconclusive / totalTests) * 100)}%</span>
                  <div className="text-slate-400">Inconclusive</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Severity Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center space-x-2">
            <BugIcon size={16} className="text-rose-400" />
            <span>Bug Severity Distribution (Agent 5 Triage)</span>
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-red-950/40 border border-red-900/60 p-3 rounded-lg text-center">
              <div className="text-xl font-bold text-red-400">{criticalBugs}</div>
              <div className="text-xs font-medium text-red-300 mt-1">Critical</div>
              <div className="text-[10px] text-slate-500 mt-0.5">Workflow blocker</div>
            </div>
            <div className="bg-rose-950/40 border border-rose-900/60 p-3 rounded-lg text-center">
              <div className="text-xl font-bold text-rose-400">{highBugs}</div>
              <div className="text-xs font-medium text-rose-300 mt-1">High</div>
              <div className="text-[10px] text-slate-500 mt-0.5">Core feature broken</div>
            </div>
            <div className="bg-amber-950/40 border border-amber-900/60 p-3 rounded-lg text-center">
              <div className="text-xl font-bold text-amber-400">{mediumBugs}</div>
              <div className="text-xs font-medium text-amber-300 mt-1">Medium</div>
              <div className="text-[10px] text-slate-500 mt-0.5">Workaround exists</div>
            </div>
            <div className="bg-emerald-950/40 border border-emerald-900/60 p-3 rounded-lg text-center">
              <div className="text-xl font-bold text-emerald-400">{lowBugs}</div>
              <div className="text-xs font-medium text-emerald-300 mt-1">Low</div>
              <div className="text-[10px] text-slate-500 mt-0.5">Cosmetic / minor</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Test Runs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center">
          <h3 className="text-base font-semibold text-slate-100">Recent AI Execution Sessions</h3>
          <span className="text-xs text-slate-400">{testRuns.length} total sessions</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/50 text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-6 py-3">Run Name</th>
                <th className="px-6 py-3">Mode</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Results (P / F / B)</th>
                <th className="px-6 py-3">Pass Rate</th>
                <th className="px-6 py-3">Duration</th>
                <th className="px-6 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {testRuns.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-500">
                    No execution sessions found. Click 'Start AI Test' to run your first autonomous test.
                  </td>
                </tr>
              ) : (
                testRuns.slice(0, 8).map((run) => (
                  <tr key={run.id} className="hover:bg-slate-800/40 transition">
                    <td className="px-6 py-4 font-medium text-slate-100">{run.name}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                        {run.mode}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={run.status} />
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">
                      <span className="text-emerald-400">{run.passed_tests}P</span> /{' '}
                      <span className="text-rose-400">{run.failed_tests}F</span> /{' '}
                      <span className="text-amber-400">{run.blocked_tests}B</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-xs">{run.pass_percentage}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400 flex items-center space-x-1">
                      <Clock size={12} />
                      <span>{run.duration_seconds}s</span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => onSelectRun(run.id)}
                        className="text-sky-400 hover:text-sky-300 text-xs font-semibold inline-flex items-center space-x-1"
                      >
                        <span>Inspect</span>
                        <ArrowRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
