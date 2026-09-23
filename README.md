# Autonomous AI QA Testing Agent

> **A production-ready, multi-agent AI QA platform that autonomously explores, tests, analyzes, and reports on web applications with minimal human intervention.**

---

## 🌟 Key Features

- **Decoupled 5-Agent Architecture**:
  - **Agent 1 (Explorer)**: Crawls page DOM, extracts routes, buttons, forms, navigation, and workflows.
  - **Agent 2 (Generator)**: Synthesizes structured test cases (Smoke, Functional, Negative, UI, Regression, Exploratory, and Natural Language prompt-based tests).
  - **Agent 3 (Executor)**: Executes steps in Playwright with a **Smart Locator Priority Engine** and **Self-Healing DOM Recovery**.
  - **Agent 4 (Analyzer)**: Validates actual business outcomes against expected criteria (enforces Principle 41 and confidence safeguards).
  - **Agent 5 (Bug Hunter)**: Distinguishes application bugs from automation/environment issues, explains severity reasoning, and generates reproducible bug reports.
- **Pluggable AI Reasoning Layer**:
  - Supports OpenAI (`gpt-4o`, `gpt-4o-mini`), any OpenAI-compatible API (Groq, vLLM, DeepSeek), and local Ollama (`llama3.2`, `qwen2.5`).
  - Includes an out-of-the-box **Smart Heuristic Engine** allowing 100% functionality on day one without external API keys.
- **Credential & Secret Masking Engine**:
  - Automatically redacts passwords, tokens, and secret parameters from logs, screenshots, reports, and AI prompts.
- **Safety Policy & Production Guardrails**:
  - Restricts destructive actions (`delete`, `payments`, `account reset`) in production unless explicitly authorized.
- **Real-Time Live Dashboard**:
  - Built with **React 18 + TypeScript + Vite + Tailwind CSS**.
  - WebSocket streaming for live step-by-step progress, terminal logs, screenshot preview, and human-in-the-loop controls (Pause, Resume, Stop, Approve).
- **Built-in Target QA Playground**:
  - Includes a live local web application (LexArbitrate Portal) featuring authentication, case management, form validation, and testable edge cases so you can test the agent immediately.
- **Audit-Ready Reporting & Regression Deltas**:
  - Standalone HTML reports, JSON schema exports, and regression comparison (Passed $\to$ Failed, Failed $\to$ Passed).
- **Enterprise Ready**:
  - SQLAlchemy (SQLite & PostgreSQL ready), Docker Compose, and GitHub Actions CI/CD pipeline.

---

## 📁 Repository Structure

```
ai-qa-agent/
├── backend/
│   ├── app/
│   │   ├── agents/          # 5 Specialized AI Agents + State Machine + Orchestrator
│   │   ├── api/             # REST Endpoints (Projects, Apps, Runs, Bugs, Reports, Playground)
│   │   ├── browser/         # Playwright Manager, Smart Locators, Evidence, Performance
│   │   ├── core/            # Config, Sensitive Data Masking, Safety Policies, Logging
│   │   ├── database/        # SQLAlchemy Engine, Session, and Base
│   │   ├── models/          # 13 Relational Tables (Projects, Runs, Cases, Bugs, Evidence)
│   │   ├── schemas/         # Pydantic Schemas for Agents & REST DTOs
│   │   ├── services/        # Synthetic Test Data, Regression Differ, Report Generator
│   │   └── main.py          # FastAPI Server Entry Point
│   ├── tests/               # Pytest Suite (17 Unit & Integration Tests)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # Badges, Modals, Navbar, Sidebar
│   │   ├── pages/           # Dashboard, Live Execution, Test Runs, Cases, Bugs, Reports, Playground, Settings
│   │   ├── services/        # REST API & WebSocket Client
│   │   ├── types/           # TypeScript Data Models
│   │   ├── App.tsx          # Root Application
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── docs/                    # Architecture, API, Agent Design, Testing, Deployment Guides
├── .github/workflows/       # GitHub Actions CI/CD Pipeline
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm 9+

### 1. Backend Setup

```powershell
cd backend
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m uvicorn app.main:app --reload --port 8000
```
The FastAPI backend will start at `http://localhost:8000`.
- API Docs: `http://localhost:8000/docs`
- Built-in Target Sandbox: `http://localhost:8000/api/v1/playground`

### 2. Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```
Open your browser to `http://localhost:5173`.

---

## 🧪 Testing the QA Agent

Run the automated test suite verifying all agent engines:

```powershell
cd backend
python -m pytest tests -v
```

All 17 tests verify:
- Credential masking & restricted action policies
- Priority locator building and self-healing recovery
- Smoke, negative, and natural language test generation
- Expected vs actual outcome evaluation
- Bug classification, HTTP 500 triage, and false-positive differentiation
- REST API CRUD and health check endpoints

---

## 🐳 Docker Deployment

To launch the complete containerized stack:

```bash
docker compose up --build -d
```

---

## ⚙️ Configuration & Pluggable LLM Options

Copy `.env.example` to `.env` in `backend/`:

```env
# Pluggable LLM (heuristic, openai, ollama)
LLM_PROVIDER=heuristic

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o

# Ollama Configuration (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Browser Engine (chromium, firefox, webkit)
DEFAULT_BROWSER=chromium
HEADLESS=true
```
