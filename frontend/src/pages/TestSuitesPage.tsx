import React, { useState, useEffect } from 'react';
import { Layers, Plus, Play } from 'lucide-react';
import { TestSuite, Project } from '../types';
import { api } from '../services/api';
import { Modal } from '../components/common/Modal';

interface TestSuitesPageProps {
  projects: Project[];
  onStartSuiteRun?: (suiteId: string) => void;
}

export const TestSuitesPage: React.FC<TestSuitesPageProps> = ({ projects, onStartSuiteRun }) => {
  const [suites, setSuites] = useState<TestSuite[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [suiteType, setSuiteType] = useState('smoke');
  const [projectId, setProjectId] = useState(projects[0]?.id || '');

  useEffect(() => {
    api.getTestSuites().then(setSuites).catch(console.error);
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const created = await api.createTestSuite({
      project_id: projectId || projects[0]?.id,
      name,
      description,
      suite_type: suiteType,
    });
    setSuites([...suites, created]);
    setIsModalOpen(false);
    setName('');
    setDescription('');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Test Suites Management</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Organized groupings of test cases (Smoke, Functional, Regression, and Custom modules).
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-2 shadow"
        >
          <Plus size={16} />
          <span>Create Suite</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {suites.length === 0 ? (
          <div className="col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-500">
            No test suites configured. Click 'Create Suite' or run an autonomous test to auto-generate.
          </div>
        ) : (
          suites.map((s) => (
            <div key={s.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start">
                  <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
                    <Layers size={20} />
                  </div>
                  <span className="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300 border border-slate-700 uppercase font-mono">
                    {s.suite_type}
                  </span>
                </div>
                <h3 className="text-base font-semibold text-slate-100 mt-3">{s.name}</h3>
                <p className="text-xs text-slate-400 mt-1">{s.description || 'Custom autonomous test suite.'}</p>
              </div>
              <div className="mt-5 pt-3 border-t border-slate-800 flex justify-end">
                <button
                  onClick={() => onStartSuiteRun && onStartSuiteRun(s.id)}
                  className="px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded flex items-center space-x-1.5"
                >
                  <Play size={12} />
                  <span>Execute Suite</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create Test Suite">
        <form onSubmit={handleCreate} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-400 mb-1">Suite Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. Critical Path Smoke Suite"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200"
            />
          </div>
          <div>
            <label className="block font-medium text-slate-400 mb-1">Suite Type</label>
            <select
              value={suiteType}
              onChange={(e) => setSuiteType(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200"
            >
              <option value="smoke">Smoke Suite</option>
              <option value="functional">Functional Suite</option>
              <option value="regression">Regression Suite</option>
              <option value="negative">Negative Suite</option>
              <option value="exploratory">Exploratory Suite</option>
            </select>
          </div>
          <div>
            <label className="block font-medium text-slate-400 mb-1">Description</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200"
            />
          </div>
          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-lg shadow"
            >
              Save Suite
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
