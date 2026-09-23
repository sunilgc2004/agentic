import React, { useState } from 'react';
import { FolderKanban, Plus } from 'lucide-react';
import { Project } from '../types';
import { api } from '../services/api';
import { Modal } from '../components/common/Modal';

interface ProjectsPageProps {
  projects: Project[];
  onRefresh: () => void;
}

export const ProjectsPage: React.FC<ProjectsPageProps> = ({ projects, onRefresh }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createProject({ name, description });
    setIsModalOpen(false);
    setName('');
    setDescription('');
    onRefresh();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100">QA Projects &amp; Workspaces</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Logical containers for enterprise web applications, test suites, and audit trails.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-2 shadow"
        >
          <Plus size={16} />
          <span>New Project</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {projects.map((p) => (
          <div key={p.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
              <FolderKanban size={20} />
            </div>
            <h3 className="text-base font-semibold text-slate-100">{p.name}</h3>
            <p className="text-xs text-slate-400 line-clamp-2">{p.description || 'No description provided.'}</p>
            <div className="pt-2 text-[11px] text-slate-500">Created: {new Date(p.created_at).toLocaleDateString()}</div>
          </div>
        ))}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create QA Project">
        <form onSubmit={handleCreate} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-400 mb-1">Project Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. LegalTech Platform"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200"
            />
          </div>
          <div>
            <label className="block font-medium text-slate-400 mb-1">Description</label>
            <textarea
              rows={3}
              placeholder="Brief summary of systems tested under this workspace"
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
              Create Project
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
