# System Architecture & Technical Specifications

## 1. High-Level Architecture Overview

The Autonomous AI QA Testing Agent platform decouples automated testing into specialized micro-agents coordinated by a deterministic finite state machine, backed by Playwright for browser interaction and multi-provider LLMs for semantic reasoning.

```
       +-------------------------------------------------------+
       |               React + TS + Tailwind UI                |
       |  (Live Execution, Dashboard, Bug Triage, Reports)     |
       +-------------------------------------------------------+
                                  |  ^ (REST + WebSockets)
                                  v  |
       +-------------------------------------------------------+
       |                 FastAPI Orchestrator                  |
       +-------------------------------------------------------+
                                  |
                                  v
+------------------------------------------------------------------------+
|                         AI Agent State Machine                         |
|                                                                        |
|  DISCOVER -> PLAN -> VALIDATE -> EXECUTE -> OBSERVE -> ANALYZE -> ... |
|                                                                        |
|  [Agent 1: Explorer]    -> Crawls DOM, maps forms, links, buttons      |
|  [Agent 2: Generator]   -> Synthesizes Smoke, Negative, UI tests       |
|  [Agent 3: Executor]    -> Playwright actions + Smart Locator Engine   |
|  [Agent 4: Analyzer]    -> Expected vs Actual verification             |
|  [Agent 5: Bug Triage]  -> Severity, root-cause & false-positive check |
+------------------------------------------------------------------------+
              |                                          |
              v                                          v
+-----------------------------+            +-----------------------------+
|    Playwright Automation    |            |   Database & Evidence Store |
|  - Chromium, Firefox, WebKit|            |  - SQLite / PostgreSQL      |
|  - Self-Healing Locators    |            |  - Screenshots, DOM, HAR    |
|  - Network & Console Hooks  |            |  - HTML & JSON Reports      |
+-----------------------------+            +-----------------------------+
```

---

## 2. Multi-Agent Role Segregation

Unlike conventional monolithic AI QA scripts with single prompt chains, this platform divides responsibilities into 5 specialized agents:

### Agent 1: Application Explorer (`explorer.py`)
- Injects a DOM discovery bundle extracting visible interactive elements, form structures, navigation links, and tables.
- Identifies logical business flows (e.g. Authentication, Case Creation, Document Generation).
- Outputs structured `PageMapSchema`.

### Agent 2: Test Case Generator (`test_generator.py`)
- Consumes `PageMapSchema` and user-configured testing mode (Smoke, Functional, Negative, UI, Regression, Exploratory, Full QA).
- Generates structured test cases with preconditions, actionable steps, synthetic test data, priority, and expected business outcomes.
- Supports **Natural Language Test Creation** allowing human testers to write plain English requirements that are automatically converted into executable Playwright steps.

### Agent 3: Browser Execution Agent (`executor.py`)
- Executes test steps sequentially in Playwright.
- Employs **Smart Locator Engine** with priority fallback:
  `data-testid` > accessibility role & name > `aria-label` > label > name > placeholder > visible text > CSS > XPath.
- Implements **Self-Healing Locator Recovery**: If an element selector fails, scans the DOM for semantic and contextual equivalence, verifies visibility, logs locator healing, and retries.
- Enforces the **Safety Policy Engine** (`SAFE_ACTIONS` vs `RESTRICTED_ACTIONS`). Destructive actions (e.g. deletion) are halted in Production/Safe Mode for human authorization.

### Agent 4: Expected vs Actual Analyzer (`analyzer.py`)
- Assesses outcome against **QA Principle 41**: *Never assume a test passed simply because a click had no error.*
- Verifies actual state change: URL transition, success notice visibility, DOM mutations, and API status codes.
- Computes confidence score (0.0 to 1.0). If confidence < 0.70, marks outcome as `INCONCLUSIVE` (Section 33).

### Agent 5: Bug Analyzer & Severity Engine (`bug_analyzer.py`)
- Triages failed tests against browser console errors, network 4xx/5xx requests, and DOM state.
- **Filters False Positives (Section 42)**: Distinguishes between `APPLICATION_BUG`, `AUTOMATION_FAILURE` (locator shift), and `ENVIRONMENT_FAILURE` (network down).
- Assigns severity (`Critical`, `High`, `Medium`, `Low`) with transparent reasoning.
- Produces reproducible bug reports (`BUG-001`, steps to reproduce, screenshot link, network traces).

---

## 3. Storage & Relational Data Model

Implemented using SQLAlchemy with support for both SQLite (local development) and PostgreSQL (production):
- **User & Project**: Multi-tenant workspace partitioning.
- **Application & Environment**: Target URL, credentials (masked with `***MASKED***`), environment safety configuration.
- **TestSuite & TestCase**: Structured test repository, tagging, and versioning.
- **TestRun & TestResult**: Execution sessions, duration, metrics, step-by-step traces, confidence ratings.
- **Bug**: Triaged defects with reproducible markdown steps and evidence links.
- **ExecutionLog & ApiLog**: Comprehensive telemetry logs for auditability.
- **Screenshot & BrowserSession**: Visual proof and session token storage.
