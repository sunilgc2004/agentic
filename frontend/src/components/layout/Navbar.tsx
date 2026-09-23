import React from 'react';
import { Play, ShieldAlert, Cpu } from 'lucide-react';
import { Application } from '../../types';

interface NavbarProps {
  applications: Application[];
  selectedApp: Application | null;
  onSelectApp: (app: Application) => void;
  onQuickStart: () => void;
  isExecuting?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  applications,
  selectedApp,
  onSelectApp,
  onQuickStart,
  isExecuting = false,
}) => {
  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-sky-500/20 border border-sky-500/40 flex items-center justify-center text-sky-400">
          <Cpu size={22} />
        </div>
        <div>
          <span className="font-bold text-slate-100 text-lg tracking-tight">Antigravity AI QA</span>
          <span className="ml-2 text-xs uppercase px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800">
            Autonomous
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Application Selector */}
        <div className="flex items-center space-x-2 text-sm">
          <span className="text-slate-400">Target App:</span>
          <select
            value={selectedApp?.id || ''}
            onChange={(e) => {
              const app = applications.find((a) => a.id === e.target.value);
              if (app) onSelectApp(app);
            }}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-sky-500"
          >
            {applications.map((app) => (
              <option key={app.id} value={app.id}>
                {app.name} ({app.default_environment})
              </option>
            ))}
          </select>
        </div>

        {/* Start AI Test Button */}
        <button
          onClick={onQuickStart}
          disabled={isExecuting}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-sm transition shadow-lg ${
            isExecuting
              ? 'bg-amber-600 text-white animate-pulse'
              : 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-900/30'
          }`}
        >
          <Play size={16} fill="currentColor" />
          <span>{isExecuting ? 'Test in Progress...' : 'Start AI Test'}</span>
        </button>
      </div>
    </header>
  );
};
