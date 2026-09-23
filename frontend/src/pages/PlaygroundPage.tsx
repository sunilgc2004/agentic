import React from 'react';
import { Compass, ExternalLink, ShieldCheck } from 'lucide-react';

export const PlaygroundPage: React.FC = () => {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center bg-slate-900 border border-slate-800 rounded-xl p-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
            <Compass size={20} className="text-sky-400" />
            <span>Target Web Application: LexArbitrate Portal</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            This live enterprise application is hosted locally on <code>http://localhost:8000/api/v1/playground</code> for end-to-end QA testing.
          </p>
        </div>
        <a
          href="http://localhost:8000/api/v1/playground"
          target="_blank"
          rel="noreferrer"
          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg flex items-center space-x-1.5 border border-slate-700"
        >
          <span>Open in New Tab</span>
          <ExternalLink size={14} />
        </a>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden h-[720px]">
        <iframe
          src="http://localhost:8000/api/v1/playground"
          title="Target Application Sandbox"
          className="w-full h-full border-0"
        />
      </div>
    </div>
  );
};
