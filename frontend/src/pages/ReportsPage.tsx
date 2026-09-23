import React, { useState, useEffect } from 'react';
import { FileText, Download, Printer, GitCompare, ExternalLink } from 'lucide-react';
import { TestRun } from '../types';
import { api } from '../services/api';

interface ReportsPageProps {
  testRuns: TestRun[];
}

export const ReportsPage: React.FC<ReportsPageProps> = ({ testRuns }) => {
  const [selectedRunId, setSelectedRunId] = useState<string>(testRuns[0]?.id || '');
  const [reportData, setReportData] = useState<any>(null);
  const [regressionData, setRegressionData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'html' | 'regression' | 'json'>('html');

  useEffect(() => {
    if (!selectedRunId && testRuns.length > 0) {
      setSelectedRunId(testRuns[0].id);
    }
  }, [testRuns]);

  useEffect(() => {
    if (!selectedRunId) return;

    api.getReportJson(selectedRunId).then((data) => setReportData(data)).catch(console.error);
    api.getRegressionReport(selectedRunId).then((data) => setRegressionData(data)).catch(console.error);
  }, [selectedRunId]);

  const handleDownloadJson = () => {
    if (!reportData) return;
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `qa_report_${selectedRunId}.json`;
    a.click();
  };

  const handlePrint = () => {
    const iframe = document.getElementById('report-iframe') as HTMLIFrameElement;
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.print();
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Executive QA Reports &amp; Regression Analytics</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Audit-ready HTML reports, JSON schema exports, and historical regression deltas.
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex items-center space-x-3">
          <select
            value={selectedRunId}
            onChange={(e) => setSelectedRunId(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2"
          >
            {testRuns.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name} ({r.mode}) - {r.pass_percentage}%
              </option>
            ))}
          </select>

          <button
            onClick={handleDownloadJson}
            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg flex items-center space-x-1.5 border border-slate-700"
          >
            <Download size={14} />
            <span>JSON</span>
          </button>

          <button
            onClick={handlePrint}
            className="px-3 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-1.5 shadow"
          >
            <Printer size={14} />
            <span>Print / PDF</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 space-x-6 text-sm">
        <button
          onClick={() => setActiveTab('html')}
          className={`pb-3 font-medium transition ${
            activeTab === 'html'
              ? 'text-sky-400 border-b-2 border-sky-400 font-semibold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Executive HTML Report
        </button>
        <button
          onClick={() => setActiveTab('regression')}
          className={`pb-3 font-medium transition flex items-center space-x-1.5 ${
            activeTab === 'regression'
              ? 'text-sky-400 border-b-2 border-sky-400 font-semibold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <GitCompare size={15} />
          <span>Regression Comparison Delta</span>
        </button>
        <button
          onClick={() => setActiveTab('json')}
          className={`pb-3 font-medium transition ${
            activeTab === 'json'
              ? 'text-sky-400 border-b-2 border-sky-400 font-semibold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Raw JSON Schema
        </button>
      </div>

      {/* Content */}
      {activeTab === 'html' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden h-[750px]">
          {selectedRunId ? (
            <iframe
              id="report-iframe"
              src={`/api/v1/reports/${selectedRunId}/html`}
              title="QA HTML Report"
              className="w-full h-full border-0 bg-white"
            />
          ) : (
            <div className="p-12 text-center text-slate-500">Select a test run to view report.</div>
          )}
        </div>
      )}

      {activeTab === 'regression' && (
        <div className="space-y-6">
          {regressionData?.has_baseline ? (
            <>
              {/* Regression Summary Cards */}
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-slate-900 border border-rose-900/60 p-4 rounded-xl text-center">
                  <div className="text-2xl font-bold text-rose-400">{regressionData.summary.newly_failed_count}</div>
                  <div className="text-xs text-rose-300 font-medium mt-1">Newly Failing (Regressions)</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Previously Passed → Now Failed</div>
                </div>

                <div className="bg-slate-900 border border-emerald-900/60 p-4 rounded-xl text-center">
                  <div className="text-2xl font-bold text-emerald-400">{regressionData.summary.fixed_count}</div>
                  <div className="text-xs text-emerald-300 font-medium mt-1">Fixed Tests</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Previously Failed → Now Passed</div>
                </div>

                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
                  <div className="text-2xl font-bold text-slate-200">{regressionData.summary.stable_passed_count}</div>
                  <div className="text-xs text-slate-400 font-medium mt-1">Stable Passed</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Passed → Passed</div>
                </div>

                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
                  <div className="text-2xl font-bold text-slate-200">{regressionData.summary.stable_failed_count}</div>
                  <div className="text-xs text-slate-400 font-medium mt-1">Unchanged Failures</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Failed → Failed</div>
                </div>
              </div>

              {/* Newly Failed Regressions Table */}
              {regressionData.newly_failed.length > 0 && (
                <div className="bg-slate-900 border border-rose-900/40 rounded-xl p-5">
                  <h3 className="text-sm font-semibold text-rose-400 mb-3">⚠️ Critical Regressions Detected</h3>
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-950 text-slate-400 uppercase">
                      <tr>
                        <th className="p-3">Test Case ID</th>
                        <th className="p-3">Baseline Status</th>
                        <th className="p-3">Current Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {regressionData.newly_failed.map((item: any, i: number) => (
                        <tr key={i}>
                          <td className="p-3 font-mono font-semibold text-sky-400">{item.test_case_id}</td>
                          <td className="p-3 text-emerald-400 font-semibold">{item.previous_status}</td>
                          <td className="p-3 text-rose-400 font-semibold">{item.current_status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400 text-sm">
              {regressionData?.message || 'No previous baseline run available for comparison.'}
            </div>
          )}
        </div>
      )}

      {activeTab === 'json' && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 overflow-x-auto">
          <pre className="font-mono text-xs text-slate-300">
            {JSON.stringify(reportData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
