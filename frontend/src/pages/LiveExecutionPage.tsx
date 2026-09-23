import React, { useState, useEffect, useRef } from 'react';
import {
  Activity,
  Pause,
  Play,
  Square,
  CheckCircle,
  XCircle,
  Clock,
  Terminal,
  Camera,
  Cpu,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { ExecutionWebSocket } from '../services/websocket';
import { api } from '../services/api';
import { StatusBadge } from '../components/common/StatusBadge';

interface LiveExecutionPageProps {
  runId: string | null;
  onRunCompleted?: () => void;
}

export const LiveExecutionPage: React.FC<LiveExecutionPageProps> = ({ runId, onRunCompleted }) => {
  const [runDetails, setRunDetails] = useState<any>(null);
  const [currentState, setCurrentState] = useState<string>('INITIALIZING');
  const [currentTest, setCurrentTest] = useState<any>(null);
  const [steps, setSteps] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [screenshotUrl, setScreenshotUrl] = useState<string | null>(null);
  const logContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!runId) return;

    // Fetch initial run detail
    api.getTestRunDetail(runId).then((res) => {
      setRunDetails(res.run);
      if (res.run) {
        setCurrentState(res.run.status);
      }
      if (res.results && res.results.length > 0) {
        const lastResult = res.results[res.results.length - 1];
        setSteps(lastResult.step_results || []);
      }
      setLogs(res.logs || []);
    });

    // Connect WebSocket
    const ws = new ExecutionWebSocket(runId, (msg) => {
      if (msg.event === 'state_transition') {
        setCurrentState(msg.data.state);
        addLog(`State changed to ${msg.data.state}: ${msg.data.message || ''}`);
      } else if (msg.event === 'test_started') {
        setCurrentTest(msg.data);
        setSteps([]);
        addLog(`Started Test [${msg.data.test_id}]: ${msg.data.scenario}`);
      } else if (msg.event === 'step_update') {
        setSteps((prev) => [...prev, msg.data.step]);
        if (msg.data.step.screenshot_path) {
          // Convert absolute to static route
          const filename = msg.data.step.screenshot_path.split('\\').pop()?.split('/').pop();
          setScreenshotUrl(`/evidence/${runId}/${filename}`);
        }
        addLog(`Step ${msg.data.step.step_number} [${msg.data.step.action} on ${msg.data.step.target}]: ${msg.data.step.status} (${msg.data.step.duration_ms}ms)`);
      } else if (msg.event === 'test_completed') {
        addLog(`Finished Test [${msg.data.test_id}] with outcome: ${msg.data.status} (confidence: ${msg.data.confidence})`);
      } else if (msg.event === 'bug_detected') {
        addLog(`[BUG DETECTED] ${msg.data.bug_id}: ${msg.data.title} (${msg.data.severity})`, 'error');
      } else if (msg.event === 'run_completed') {
        setCurrentState('COMPLETED');
        addLog(`Autonomous QA run completed successfully! Pass rate: ${msg.data.pass_percentage}%`);
        if (onRunCompleted) onRunCompleted();
      } else if (msg.event === 'run_failed') {
        setCurrentState('FAILED');
        addLog(`Run failed: ${msg.data?.error || msg.data?.message || 'Execution error'}`, 'error');
        if (onRunCompleted) onRunCompleted();
      } else if (msg.event === 'paused') {
        setIsPaused(true);
        addLog(`Execution paused by user command.`, 'warning');
      } else if (msg.event === 'resumed') {
        setIsPaused(false);
        addLog(`Execution resumed.`, 'info');
      } else if (msg.event === 'stopped') {
        setCurrentState('STOPPED');
        addLog(`Execution terminated by user command.`, 'warning');
        if (onRunCompleted) onRunCompleted();
      }
    });

    return () => {
      ws.close();
    };
  }, [runId]);

  const addLog = (text: string, level: 'info' | 'error' | 'warning' = 'info') => {
    setLogs((prev) => [
      ...prev,
      {
        timestamp: new Date().toLocaleTimeString(),
        text,
        level,
      },
    ]);
  };

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  const handleControl = async (action: 'pause' | 'resume' | 'stop') => {
    if (!runId) return;
    await api.controlTestRun(runId, action);
    if (action === 'pause') setIsPaused(true);
    if (action === 'resume') setIsPaused(false);
  };

  if (!runId) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
        <Activity size={48} className="mx-auto text-slate-600 mb-4" />
        <h3 className="text-lg font-semibold text-slate-200">No Active Execution Session</h3>
        <p className="text-sm text-slate-400 mt-1">
          Select an ongoing run from 'Test Runs' or click 'Start AI Test' to launch an autonomous agent.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header bar with controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <span className="w-3 h-3 rounded-full bg-emerald-500 animate-ping"></span>
            <h2 className="text-lg font-bold text-slate-100">Live Autonomous Execution</h2>
            <StatusBadge status={currentState} />
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Session ID: {runId} | State Machine: {currentState}
          </p>
        </div>

        {/* Human-in-the-Loop Action Controls (Section 34) */}
        <div className="flex items-center space-x-2">
          {isPaused ? (
            <button
              onClick={() => handleControl('resume')}
              className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-1.5 transition"
            >
              <Play size={14} />
              <span>Resume</span>
            </button>
          ) : (
            <button
              onClick={() => handleControl('pause')}
              className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-1.5 transition"
            >
              <Pause size={14} />
              <span>Pause</span>
            </button>
          )}

          <button
            onClick={() => handleControl('stop')}
            className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-1.5 transition"
          >
            <Square size={14} />
            <span>Stop Run</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Step-by-Step Action Progression (Section 23) */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-semibold text-slate-200">Current Test Case Progression</h3>
                <p className="text-xs text-slate-400">
                  {currentTest
                    ? `[${currentTest.test_id}] ${currentTest.scenario}`
                    : 'Initializing autonomous browser session...'}
                </p>
              </div>
              {currentTest && (
                <span className="text-xs text-sky-400 font-mono">
                  Test {currentTest.index} of {currentTest.total}
                </span>
              )}
            </div>

            {/* Steps List */}
            <div className="space-y-3">
              {steps.length === 0 ? (
                <div className="text-xs text-slate-500 py-6 text-center">
                  Waiting for Playwright browser actions...
                </div>
              ) : (
                steps.map((step, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg border flex items-start justify-between text-xs ${
                      step.status === 'SUCCESS'
                        ? 'bg-emerald-950/20 border-emerald-900/60 text-slate-200'
                        : step.status === 'FAILED'
                        ? 'bg-rose-950/20 border-rose-900/60 text-slate-200'
                        : 'bg-slate-800/40 border-slate-700/60 text-slate-300'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="mt-0.5">
                        {step.status === 'SUCCESS' ? (
                          <CheckCircle size={16} className="text-emerald-400" />
                        ) : step.status === 'FAILED' ? (
                          <XCircle size={16} className="text-rose-400" />
                        ) : (
                          <Clock size={16} className="text-amber-400" />
                        )}
                      </div>
                      <div>
                        <div className="font-semibold text-slate-100">
                          Step {step.step_number}: {step.action.toUpperCase()} - {step.target}
                        </div>
                        {step.error && (
                          <div className="text-rose-400 mt-1 font-mono text-[11px] bg-black/40 p-1.5 rounded">
                            {step.error}
                          </div>
                        )}
                        {step.recovered_selector && (
                          <div className="text-sky-400 mt-1 text-[11px]">
                            ⚡ Self-healed locator: <code>{step.recovered_selector}</code>
                          </div>
                        )}
                      </div>
                    </div>
                    <span className="font-mono text-slate-400">{step.duration_ms}ms</span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Screenshot Evidence View */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center space-x-2">
              <Camera size={16} className="text-sky-400" />
              <span>Real-Time Browser Evidence & Snapshot</span>
            </h3>
            {screenshotUrl ? (
              <div className="border border-slate-800 rounded-lg overflow-hidden bg-black/50">
                <img
                  src={screenshotUrl}
                  alt="Live Browser Snapshot"
                  className="w-full max-h-[380px] object-contain mx-auto"
                />
              </div>
            ) : (
              <div className="h-44 border border-dashed border-slate-800 rounded-lg flex flex-col items-center justify-center text-slate-500 text-xs">
                <Camera size={24} className="mb-2 text-slate-600" />
                <span>Snapshots will render dynamically upon step execution and failures.</span>
              </div>
            )}
          </div>
        </div>

        {/* Right Col: Live Terminal & Telemetry Stream */}
        <div className="space-y-6">
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col h-[600px]">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
              <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
                <Terminal size={14} className="text-sky-400" />
                <span>AI Execution Telemetry Log</span>
              </div>
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            </div>

            <div
              ref={logContainerRef}
              className="flex-1 overflow-y-auto font-mono text-[11px] space-y-1 text-slate-300 pr-1"
            >
              {logs.map((l, i) => (
                <div
                  key={i}
                  className={`leading-relaxed ${
                    l.level === 'error'
                      ? 'text-rose-400'
                      : l.level === 'warning'
                      ? 'text-amber-300'
                      : 'text-slate-300'
                  }`}
                >
                  <span className="text-slate-500">[{l.timestamp || l.created_at?.slice(11, 19)}]</span>{' '}
                  <span>{l.text || `${l.agent}: ${l.action} ${l.target} -> ${l.result}`}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
