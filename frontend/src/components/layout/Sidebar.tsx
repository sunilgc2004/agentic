import React from 'react';
import {
  LayoutDashboard,
  FolderKanban,
  Globe,
  CheckSquare,
  Layers,
  PlayCircle,
  Activity,
  Bug,
  FileText,
  Compass,
  Settings as SettingsIcon,
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  activeRunId?: string | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, activeRunId }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'live', label: 'Live Execution', icon: Activity, badge: activeRunId ? 'Active' : undefined },
    { id: 'test-runs', label: 'Test Runs', icon: PlayCircle },
    { id: 'test-cases', label: 'Test Cases', icon: CheckSquare },
    { id: 'test-suites', label: 'Test Suites', icon: Layers },
    { id: 'bugs', label: 'Bug Reports', icon: Bug },
    { id: 'reports', label: 'QA Reports', icon: FileText },
    { id: 'playground', label: 'Target Playground', icon: Compass },
    { id: 'applications', label: 'Applications', icon: Globe },
    { id: 'projects', label: 'Projects', icon: FolderKanban },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 bg-slate-900/60 border-r border-slate-800 p-4 flex flex-col justify-between h-[calc(100vh-4rem)] sticky top-16">
      <nav className="space-y-1">
        <div className="px-3 pb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Testing Operations
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition ${
                isActive
                  ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon size={18} className={isActive ? 'text-sky-400' : 'text-slate-400'} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="px-1.5 py-0.5 text-xs rounded bg-amber-500/20 text-amber-300 animate-pulse font-semibold">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="p-3 bg-slate-800/40 border border-slate-800 rounded-lg text-xs text-slate-400">
        <div className="font-semibold text-slate-300">Playwright Autonomous</div>
        <div className="mt-1 flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>Engine Online (Chromium)</span>
        </div>
      </div>
    </aside>
  );
};
