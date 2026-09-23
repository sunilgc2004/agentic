import React, { useState } from 'react';
import { Bug as BugIcon, Check, AlertOctagon, CheckCircle2, ExternalLink, Image as ImageIcon } from 'lucide-react';
import { Bug } from '../types';
import { api } from '../services/api';
import { StatusBadge } from '../components/common/StatusBadge';
import { Modal } from '../components/common/Modal';

interface BugReportsPageProps {
  bugs: Bug[];
  onRefresh?: () => void;
}

export const BugReportsPage: React.FC<BugReportsPageProps> = ({ bugs, onRefresh }) => {
  const [selectedBug, setSelectedBug] = useState<Bug | null>(null);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');

  const handleUpdateStatus = async (bugId: string, newStatus: 'OPEN' | 'FALSE_POSITIVE' | 'RESOLVED') => {
    await api.updateBugStatus(bugId, { status: newStatus });
    if (onRefresh) onRefresh();
    if (selectedBug && selectedBug.id === bugId) {
      setSelectedBug({ ...selectedBug, status: newStatus });
    }
  };

  const filteredBugs = bugs.filter((b) => {
    if (filterSeverity !== 'ALL' && b.severity !== filterSeverity) return false;
    if (filterStatus !== 'ALL' && b.status !== filterStatus) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100">AI Bug Intelligence &amp; Triage</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Defects identified by Agent 5 with root-cause hypotheses, failure evidence, and severity rationale.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
          <span>{bugs.length} Total Defects</span>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap gap-4 text-xs">
        <div className="flex items-center space-x-2">
          <span className="text-slate-400">Severity:</span>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 rounded px-2.5 py-1"
          >
            <option value="ALL">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-slate-400">Status:</span>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 rounded px-2.5 py-1"
          >
            <option value="ALL">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="FALSE_POSITIVE">False Positive</option>
            <option value="RESOLVED">Resolved</option>
          </select>
        </div>
      </div>

      {/* Bug Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredBugs.length === 0 ? (
          <div className="col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-500">
            No defects found matching current filters.
          </div>
        ) : (
          filteredBugs.map((bug) => (
            <div
              key={bug.id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition flex flex-col justify-between"
            >
              <div>
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold text-sky-400 bg-sky-950/60 px-2 py-0.5 rounded border border-sky-900">
                      {bug.custom_id}
                    </span>
                    <StatusBadge status={bug.severity} type="severity" />
                    <span className="text-xs text-slate-400 px-2 py-0.5 bg-slate-800 rounded border border-slate-700">
                      {bug.category}
                    </span>
                  </div>
                  <span
                    className={`text-xs px-2 py-0.5 rounded font-medium ${
                      bug.status === 'OPEN'
                        ? 'bg-rose-950/60 text-rose-400 border border-rose-900'
                        : bug.status === 'FALSE_POSITIVE'
                        ? 'bg-slate-800 text-slate-400'
                        : 'bg-emerald-950/60 text-emerald-400 border border-emerald-900'
                    }`}
                  >
                    {bug.status}
                  </span>
                </div>

                <h3 className="text-sm font-semibold text-slate-100 mt-2 line-clamp-1">{bug.title}</h3>
                <div className="text-xs text-slate-400 mt-1">Module: {bug.module}</div>

                <div className="mt-3 bg-slate-950 p-3 rounded-lg border border-slate-800/80 text-xs space-y-1.5">
                  <div>
                    <span className="text-slate-500">Observed Fact:</span>{' '}
                    <span className="text-rose-300">{bug.actual_result}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">AI Hypothesis:</span>{' '}
                    <span className="text-slate-300">{bug.root_cause_hypothesis}</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between items-center text-xs">
                <button
                  onClick={() => setSelectedBug(bug)}
                  className="text-sky-400 hover:text-sky-300 font-semibold flex items-center space-x-1"
                >
                  <span>Inspect Full Evidence</span>
                </button>
                <div className="flex space-x-2">
                  {bug.status === 'OPEN' ? (
                    <>
                      <button
                        onClick={() => handleUpdateStatus(bug.id, 'FALSE_POSITIVE')}
                        className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded"
                        title="Mark as false positive"
                      >
                        False Positive
                      </button>
                      <button
                        onClick={() => handleUpdateStatus(bug.id, 'RESOLVED')}
                        className="px-2 py-1 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 rounded"
                      >
                        Resolve
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => handleUpdateStatus(bug.id, 'OPEN')}
                      className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded"
                    >
                      Re-open
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Full Bug Detail Modal */}
      <Modal
        isOpen={!!selectedBug}
        onClose={() => setSelectedBug(null)}
        title={selectedBug ? `[${selectedBug.custom_id}] ${selectedBug.title}` : 'Bug Report'}
        maxWidth="max-w-3xl"
      >
        {selectedBug && (
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950 p-3 rounded-lg border border-slate-800">
              <div>
                <span className="text-slate-500">Severity:</span>
                <div><StatusBadge status={selectedBug.severity} type="severity" /></div>
              </div>
              <div>
                <span className="text-slate-500">Category:</span>
                <div className="font-semibold text-slate-200 mt-0.5">{selectedBug.category}</div>
              </div>
              <div>
                <span className="text-slate-500">Module:</span>
                <div className="font-semibold text-slate-200 mt-0.5">{selectedBug.module}</div>
              </div>
              <div>
                <span className="text-slate-500">Status:</span>
                <div className="font-semibold text-slate-200 mt-0.5">{selectedBug.status}</div>
              </div>
            </div>

            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2">
              <div>
                <strong className="text-slate-300 block mb-0.5">Why this Severity was assigned:</strong>
                <p className="text-slate-400">{selectedBug.severity_reasoning}</p>
              </div>
              <div>
                <strong className="text-slate-300 block mb-0.5">Expected Behavior:</strong>
                <p className="text-emerald-400">{selectedBug.expected_result}</p>
              </div>
              <div>
                <strong className="text-slate-300 block mb-0.5">Actual Behavior:</strong>
                <p className="text-rose-400">{selectedBug.actual_result}</p>
              </div>
            </div>

            <div>
              <strong className="text-slate-200 text-sm block mb-2">Steps to Reproduce</strong>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono space-y-1">
                {selectedBug.steps_to_reproduce.map((step, i) => (
                  <div key={i} className="text-slate-300">{step}</div>
                ))}
              </div>
            </div>

            {selectedBug.evidence && selectedBug.evidence.screenshot && (
              <div>
                <strong className="text-slate-200 text-sm block mb-2">Visual Failure Evidence</strong>
                <div className="border border-slate-800 rounded-lg overflow-hidden bg-black/60 p-2">
                  <img
                    src={`/evidence/${selectedBug.test_run_id}/${selectedBug.evidence.screenshot.split('\\').pop()?.split('/').pop()}`}
                    alt="Bug Screenshot"
                    className="max-h-[300px] mx-auto object-contain"
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};
