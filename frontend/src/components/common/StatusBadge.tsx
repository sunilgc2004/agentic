import React from 'react';

interface StatusBadgeProps {
  status: string;
  type?: 'status' | 'severity' | 'priority';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'status' }) => {
  const s = status.toUpperCase();

  let bg = 'bg-slate-800 text-slate-300 border-slate-700';

  if (type === 'status') {
    if (s === 'PASS' || s === 'SUCCESS' || s === 'COMPLETED') {
      bg = 'bg-emerald-950 text-emerald-400 border-emerald-800';
    } else if (s === 'FAIL' || s === 'FAILED') {
      bg = 'bg-rose-950 text-rose-400 border-rose-800';
    } else if (s === 'BLOCKED') {
      bg = 'bg-amber-950 text-amber-400 border-amber-800';
    } else if (s === 'INCONCLUSIVE') {
      bg = 'bg-slate-800 text-slate-400 border-slate-700';
    } else if (s === 'RUNNING') {
      bg = 'bg-sky-950 text-sky-400 border-sky-800 animate-pulse';
    } else if (s === 'PAUSED') {
      bg = 'bg-yellow-950 text-yellow-400 border-yellow-800';
    }
  } else if (type === 'severity') {
    if (s === 'CRITICAL') {
      bg = 'bg-red-950 text-red-300 border-red-800 font-bold';
    } else if (s === 'HIGH') {
      bg = 'bg-rose-950 text-rose-400 border-rose-800';
    } else if (s === 'MEDIUM') {
      bg = 'bg-amber-950 text-amber-400 border-amber-800';
    } else if (s === 'LOW') {
      bg = 'bg-emerald-950 text-emerald-400 border-emerald-800';
    }
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${bg}`}>
      {status}
    </span>
  );
};
