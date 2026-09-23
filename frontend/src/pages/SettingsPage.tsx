import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Save, Key, Cpu, Globe, Check } from 'lucide-react';
import { api } from '../services/api';
import { AgentSettings } from '../types';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<AgentSettings | null>(null);
  const [llmProvider, setLlmProvider] = useState('heuristic');
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [openaiBaseUrl, setOpenaiBaseUrl] = useState('https://api.openai.com/v1');
  const [openaiModel, setOpenaiModel] = useState('gpt-4o');
  const [ollamaBaseUrl, setOllamaBaseUrl] = useState('http://localhost:11434');
  const [ollamaModel, setOllamaModel] = useState('llama3.2');
  const [defaultBrowser, setDefaultBrowser] = useState('chromium');
  const [headless, setHeadless] = useState(true);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.70);

  const [savedSuccess, setSavedSuccess] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    api.getSettings().then((data) => {
      setSettings(data);
      setLlmProvider(data.llm_provider);
      setOpenaiBaseUrl(data.openai_base_url || 'https://api.openai.com/v1');
      setOpenaiModel(data.openai_model || 'gpt-4o');
      setOllamaBaseUrl(data.ollama_base_url || 'http://localhost:11434');
      setOllamaModel(data.ollama_model || 'llama3.2');
      setDefaultBrowser(data.default_browser || 'chromium');
      setHeadless(data.headless);
      setConfidenceThreshold(data.confidence_threshold || 0.70);
    });
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await api.updateSettings({
        llm_provider: llmProvider,
        openai_api_key: openaiApiKey || undefined,
        openai_base_url: openaiBaseUrl,
        openai_model: openaiModel,
        ollama_base_url: ollamaBaseUrl,
        ollama_model: ollamaModel,
        default_browser: defaultBrowser,
        headless,
        confidence_threshold: confidenceThreshold,
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (e) {
      console.error('Failed to update settings', e);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100">AI Engine &amp; Automation Settings</h2>
        <p className="text-sm text-slate-400 mt-0.5">
          Configure pluggable LLMs, browser execution options, locator thresholds, and safety policies.
        </p>
      </div>

      {savedSuccess && (
        <div className="bg-emerald-950/60 border border-emerald-800 text-emerald-300 p-3 rounded-xl text-xs flex items-center space-x-2">
          <Check size={16} />
          <span>Settings saved successfully. Changes applied to active agents.</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* 1. LLM Provider */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center space-x-2 text-sm font-semibold text-slate-200 border-b border-slate-800 pb-3">
            <Cpu size={16} className="text-sky-400" />
            <span>AI Reasoning Layer (Section 2)</span>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Active AI Provider</label>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-slate-200 rounded-lg p-2.5 text-xs focus:ring-1 focus:ring-sky-500"
            >
              <option value="heuristic">Built-in Smart Heuristic Engine (Immediate Out-of-the-Box QA)</option>
              <option value="openai">OpenAI / OpenAI-Compatible Endpoint (GPT-4o, Groq, DeepSeek, vLLM)</option>
              <option value="ollama">Local Ollama Model Daemon (llama3.2, mistral, qwen2.5)</option>
            </select>
          </div>

          {llmProvider === 'openai' && (
            <div className="space-y-3 pt-2">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">OpenAI API Key</label>
                <input
                  type="password"
                  placeholder="sk-proj-..."
                  value={openaiApiKey}
                  onChange={(e) => setOpenaiApiKey(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-slate-200 rounded-lg p-2.5 text-xs font-mono"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Base URL</label>
                  <input
                    type="text"
                    value={openaiBaseUrl}
                    onChange={(e) => setOpenaiBaseUrl(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-slate-200 rounded-lg p-2.5 text-xs font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Model Name</label>
                  <input
                    type="text"
                    value={openaiModel}
                    onChange={(e) => setOpenaiModel(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-slate-200 rounded-lg p-2.5 text-xs font-mono"
                  />
                </div>
              </div>
            </div>
          )}

          {llmProvider === 'ollama' && (
            <div className="grid grid-cols-2 gap-3 pt-2">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Ollama Base URL</label>
                <input
                  type="text"
                  value={ollamaBaseUrl}
                  onChange={(e) => setOllamaBaseUrl(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-slate-200 rounded-lg p-2.5 text-xs font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Model Name</label>
                <input
                  type="text"
                  value={ollamaModel}
                  onChange={(e) => setOllamaModel(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-slate-200 rounded-lg p-2.5 text-xs font-mono"
                />
              </div>
            </div>
          )}
        </div>

        {/* 2. Playwright Browser & Confidence */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center space-x-2 text-sm font-semibold text-slate-200 border-b border-slate-800 pb-3">
            <Globe size={16} className="text-sky-400" />
            <span>Browser Automation &amp; Confidence Thresholds</span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Default Browser (Section 43)</label>
              <select
                value={defaultBrowser}
                onChange={(e) => setDefaultBrowser(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-slate-200 rounded-lg p-2.5 text-xs"
              >
                <option value="chromium">Chromium</option>
                <option value="firefox">Firefox</option>
                <option value="webkit">WebKit</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">
                AI Confidence Threshold: {Math.round(confidenceThreshold * 100)}% (Section 33)
              </label>
              <input
                type="range"
                min="0.5"
                max="0.95"
                step="0.05"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                className="w-full accent-sky-500 mt-2"
              />
              <span className="text-[11px] text-slate-500">
                Outcomes with confidence below this threshold are marked INCONCLUSIVE.
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-2 pt-2">
            <input
              type="checkbox"
              id="settings-headless"
              checked={headless}
              onChange={(e) => setHeadless(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-sky-500"
            />
            <label htmlFor="settings-headless" className="text-xs text-slate-300">
              Run Playwright in Headless Mode by Default
            </label>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSaving}
            className="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-lg text-xs flex items-center space-x-2 shadow"
          >
            <Save size={14} />
            <span>{isSaving ? 'Saving...' : 'Save Configuration'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
