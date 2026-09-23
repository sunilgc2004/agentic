import React, { useState } from 'react';
import { Globe, Plus, ExternalLink, ShieldCheck } from 'lucide-react';
import { Application, Project } from '../types';
import { api } from '../services/api';
import { Modal } from '../components/common/Modal';

interface ApplicationsPageProps {
  applications: Application[];
  projects: Project[];
  onRefresh: () => void;
  onSelectApp: (app: Application) => void;
}

export const ApplicationsPage: React.FC<ApplicationsPageProps> = ({
  applications,
  projects,
  onRefresh,
  onSelectApp,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [baseUrl, setBaseUrl] = useState('');
  const [description, setDescription] = useState('');
  const [projectId, setProjectId] = useState(projects[0]?.id || '');
  const [env, setEnv] = useState('qa');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createApplication({
      project_id: projectId || projects[0]?.id,
      name,
      base_url: baseUrl,
      description,
      default_environment: env,
      auth_type: username ? 'credentials' : 'none',
      auth_credentials: username ? { username, password } : undefined,
    });
    setIsModalOpen(false);
    setName('');
    setBaseUrl('');
    setDescription('');
    setUsername('');
    setPassword('');
    onRefresh();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Applications Under Test</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Target web applications registered for autonomous exploration and testing.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-2 shadow"
        >
          <Plus size={16} />
          <span>Add Application</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {applications.map((app) => (
          <div
            key={app.id}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-sky-500/40 transition flex flex-col justify-between"
          >
            <div>
              <div className="flex justify-between items-start">
                <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
                  <Globe size={20} />
                </div>
                <span className="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300 border border-slate-700 uppercase font-mono">
                  {app.default_environment}
                </span>
              </div>
              <h3 className="text-base font-semibold text-slate-100 mt-3">{app.name}</h3>
              <p className="text-xs text-slate-400 mt-1 font-mono break-all">{app.base_url}</p>
              {app.description && <p className="text-xs text-slate-400 mt-2 line-clamp-2">{app.description}</p>}
            </div>

            <div className="mt-5 pt-3 border-t border-slate-800 flex justify-between items-center">
              <button
                onClick={() => onSelectApp(app)}
                className="text-sky-400 hover:text-sky-300 text-xs font-semibold"
              >
                Set as Active
              </button>
              <a
                href={app.base_url}
                target="_blank"
                rel="noreferrer"
                className="text-slate-400 hover:text-slate-200 text-xs flex items-center space-x-1"
              >
                <span>Visit URL</span>
                <ExternalLink size={12} />
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Add App Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Register Web Application">
        <form onSubmit={handleCreate} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-400 mb-1">Application Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. LegalTech Case Portal"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-400 mb-1">Target Application URL *</label>
            <input
              type="url"
              required
              placeholder="https://example.com or http://localhost:8000/api/v1/playground"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200 font-mono"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-400 mb-1">Project</label>
              <select
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200"
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-medium text-slate-400 mb-1">Environment</label>
              <select
                value={env}
                onChange={(e) => setEnv(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200"
              >
                <option value="qa">QA</option>
                <option value="staging">Staging</option>
                <option value="production">Production</option>
                <option value="local">Local</option>
              </select>
            </div>
          </div>

          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2">
            <div className="font-semibold text-slate-300">Optional Credentials (Masked &amp; Secure)</div>
            <p className="text-slate-500">Credentials are masked and never exposed to logs, reports, or LLM prompts.</p>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                placeholder="Username / Email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded p-2 text-slate-200"
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded p-2 text-slate-200"
              />
            </div>
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
              Save Application
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
