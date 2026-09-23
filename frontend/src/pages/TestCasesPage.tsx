import React, { useState, useEffect } from 'react';
import { Plus, Sparkles, Filter, Trash2, CheckCircle2, Eye, Play } from 'lucide-react';
import { TestCase, Application } from '../types';
import { api } from '../services/api';
import { StatusBadge } from '../components/common/StatusBadge';
import { Modal } from '../components/common/Modal';

interface TestCasesPageProps {
  selectedApp: Application | null;
  onRunSingleTest?: (testCase: TestCase) => void;
}

export const TestCasesPage: React.FC<TestCasesPageProps> = ({ selectedApp, onRunSingleTest }) => {
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterModule, setFilterModule] = useState('ALL');
  const [filterType, setFilterType] = useState('ALL');

  // Modals
  const [isNLModalOpen, setIsNLModalOpen] = useState(false);
  const [nlPrompt, setNlPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedTestCase, setSelectedTestCase] = useState<TestCase | null>(null);

  useEffect(() => {
    loadTestCases();
  }, [selectedApp]);

  const loadTestCases = async () => {
    setIsLoading(true);
    try {
      const data = await api.getTestCases(selectedApp?.id);
      setTestCases(data);
    } catch (e) {
      console.error('Failed to load test cases', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateFromNL = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedApp || !nlPrompt.trim()) return;
    setIsGenerating(true);
    try {
      const newCase = await api.generateFromNaturalLanguage({
        application_id: selectedApp.id,
        prompt: nlPrompt.trim(),
      });
      setTestCases([newCase, ...testCases]);
      setIsNLModalOpen(false);
      setNlPrompt('');
    } catch (e) {
      console.error('Failed to generate from natural language', e);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this test case?')) return;
    await api.deleteTestCase(id);
    setTestCases(testCases.filter((tc) => tc.id !== id));
  };

  // Modules list
  const modules = Array.from(new Set(testCases.map((tc) => tc.module)));

  const filteredCases = testCases.filter((tc) => {
    if (filterModule !== 'ALL' && tc.module !== filterModule) return false;
    if (filterType !== 'ALL' && tc.test_type !== filterType) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Test Case Repository</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Structured test suites generated autonomously by Agent 2 or authored via Natural Language.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsNLModalOpen(true)}
            className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-1.5 shadow"
          >
            <Sparkles size={15} />
            <span>AI Natural Language Creator</span>
          </button>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center gap-4 text-xs">
        <div className="flex items-center space-x-2">
          <Filter size={14} className="text-slate-400" />
          <span className="text-slate-400">Module:</span>
          <select
            value={filterModule}
            onChange={(e) => setFilterModule(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 rounded px-2.5 py-1"
          >
            <option value="ALL">All Modules</option>
            {modules.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-slate-400">Type:</span>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 rounded px-2.5 py-1"
          >
            <option value="ALL">All Types</option>
            <option value="Smoke">Smoke</option>
            <option value="Functional">Functional</option>
            <option value="Negative">Negative</option>
            <option value="UI">UI</option>
            <option value="Custom">Custom</option>
          </select>
        </div>

        <div className="ml-auto text-slate-400 font-mono">
          Showing {filteredCases.length} of {testCases.length} test cases
        </div>
      </div>

      {/* Test Cases Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-950/50 text-slate-400 text-xs uppercase font-medium">
            <tr>
              <th className="px-6 py-3">Test ID</th>
              <th className="px-6 py-3">Module</th>
              <th className="px-6 py-3">Scenario</th>
              <th className="px-6 py-3">Steps</th>
              <th className="px-6 py-3">Type</th>
              <th className="px-6 py-3">Priority</th>
              <th className="px-6 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-300">
            {isLoading ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-slate-500">
                  Loading test repository...
                </td>
              </tr>
            ) : filteredCases.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-slate-500">
                  No test cases found matching filters.
                </td>
              </tr>
            ) : (
              filteredCases.map((tc) => (
                <tr key={tc.id} className="hover:bg-slate-800/40 transition">
                  <td className="px-6 py-4 font-mono font-semibold text-xs text-sky-400">{tc.custom_id}</td>
                  <td className="px-6 py-4 font-medium text-slate-200 text-xs">{tc.module}</td>
                  <td className="px-6 py-4 text-slate-300 max-w-md truncate text-xs">{tc.scenario}</td>
                  <td className="px-6 py-4 font-mono text-xs text-slate-400">{tc.steps.length} steps</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300 border border-slate-700">
                      {tc.test_type}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={tc.priority} type="priority" />
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button
                      onClick={() => setSelectedTestCase(tc)}
                      className="p-1 text-slate-400 hover:text-sky-400 transition"
                      title="Inspect steps"
                    >
                      <Eye size={16} />
                    </button>
                    <button
                      onClick={() => handleDelete(tc.id)}
                      className="p-1 text-slate-400 hover:text-rose-400 transition"
                      title="Delete test case"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Natural Language Creation Modal (Section 25) */}
      <Modal isOpen={isNLModalOpen} onClose={() => setIsNLModalOpen(false)} title="Natural Language Test Case Creator">
        <form onSubmit={handleGenerateFromNL} className="space-y-4">
          <p className="text-xs text-slate-400">
            Enter a plain English description of what you want to verify. Agent 2 will automatically generate preconditions, test data, locators, Playwright steps, and expected assertions.
          </p>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Testing Objective</label>
            <textarea
              rows={4}
              value={nlPrompt}
              onChange={(e) => setNlPrompt(e.target.value)}
              placeholder="e.g. 'Verify that a user can create a new arbitration case using valid claimant and respondent details and confirm that the case appears in the table.'"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-slate-200 text-xs focus:ring-1 focus:ring-sky-500"
              required
            />
          </div>
          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={() => setIsNLModalOpen(false)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isGenerating}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg text-xs flex items-center space-x-1.5 shadow"
            >
              <Sparkles size={14} />
              <span>{isGenerating ? 'AI Synthesizing Test Steps...' : 'Generate Test Case'}</span>
            </button>
          </div>
        </form>
      </Modal>

      {/* Test Case Detail Modal */}
      <Modal
        isOpen={!!selectedTestCase}
        onClose={() => setSelectedTestCase(null)}
        title={selectedTestCase ? `[${selectedTestCase.custom_id}] ${selectedTestCase.scenario}` : 'Test Details'}
        maxWidth="max-w-3xl"
      >
        {selectedTestCase && (
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-4 bg-slate-950 p-3 rounded-lg border border-slate-800">
              <div>
                <span className="text-slate-500">Module:</span> <strong className="text-slate-200">{selectedTestCase.module}</strong>
              </div>
              <div>
                <span className="text-slate-500">Feature:</span> <strong className="text-slate-200">{selectedTestCase.feature}</strong>
              </div>
              <div>
                <span className="text-slate-500">Priority:</span> <strong className="text-slate-200">{selectedTestCase.priority}</strong>
              </div>
              <div>
                <span className="text-slate-500">Expected Result:</span> <strong className="text-emerald-400">{selectedTestCase.expected_result}</strong>
              </div>
            </div>

            <h4 className="font-semibold text-slate-200 text-sm">Automated Execution Steps</h4>
            <div className="space-y-2">
              {selectedTestCase.steps.map((s, i) => (
                <div key={i} className="p-2.5 bg-slate-800/50 border border-slate-700 rounded flex justify-between items-center">
                  <div>
                    <span className="font-bold text-sky-400 mr-2">Step {s.step_number}:</span>
                    <span className="font-mono bg-slate-900 px-1.5 py-0.5 rounded mr-2 text-slate-300">{s.action}</span>
                    <span className="text-slate-200">{s.target_description}</span>
                    {s.value && <span className="text-amber-300 ml-2 font-mono">val="{s.value}"</span>}
                  </div>
                  {s.selector && <code className="text-[10px] text-slate-400">{s.selector}</code>}
                </div>
              ))}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
