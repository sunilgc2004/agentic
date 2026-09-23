# REST & WebSocket API Specification

Base URL: `http://localhost:8000/api/v1`

---

## 1. Projects API

### `POST /projects`
Create a new project workspace.
```json
{
  "name": "LegalTech Platform",
  "description": "Enterprise arbitration portal testing"
}
```

### `GET /projects`
List all projects.

---

## 2. Applications API

### `POST /applications`
Register a web application for autonomous testing.
```json
{
  "project_id": "uuid-...",
  "name": "Arbitration Portal",
  "base_url": "http://localhost:8000/api/v1/playground",
  "default_environment": "qa",
  "auth_type": "credentials",
  "auth_credentials": {
    "username": "test@example.com",
    "password": "SecurePass123!"
  }
}
```

### `GET /applications`
List registered applications. Filter by `?project_id=...`.

---

## 3. Test Runs API

### `POST /test-runs`
Launch an autonomous AI testing run in the background.
```json
{
  "application_id": "uuid-...",
  "mode": "SMOKE", // SMOKE, FUNCTIONAL, REGRESSION, UI, NEGATIVE, EXPLORATORY, FULL_QA
  "environment": "qa",
  "browser": "chromium", // chromium, firefox, webkit
  "headless": true,
  "custom_prompt": "Verify case creation and video conference link generation"
}
```

### `GET /test-runs/{id}`
Retrieve test run progress, tally metrics, step results, bugs, and logs.

### `POST /test-runs/{id}/control`
Apply human-in-the-loop controls.
```json
{
  "action": "pause" // "pause", "resume", "stop"
}
```

---

## 4. Test Cases API

### `GET /test-cases`
List test cases. Filter by `?application_id=...&module=...&priority=...`.

### `POST /test-cases/natural-language`
Generate structured test cases from natural language instructions.
```json
{
  "application_id": "uuid-...",
  "prompt": "Verify user can create an arbitration case with valid claimant and respondent."
}
```

### `PUT /test-cases/{id}`
Update an existing test case.

### `DELETE /test-cases/{id}`
Delete a test case.

---

## 5. Bug Reports API

### `GET /bugs`
List triaged bugs. Filter by `?severity=Critical&status=OPEN`.

### `PATCH /bugs/{id}`
Update bug status (e.g. `FALSE_POSITIVE`, `RESOLVED`, `OPEN`).
```json
{
  "status": "FALSE_POSITIVE"
}
```

---

## 6. Reports API

### `GET /reports/{run_id}`
Returns machine-readable JSON schema report.

### `GET /reports/{run_id}/html`
Returns downloadable standalone HTML report with embedded styles and charts.

### `GET /reports/{run_id}/regression`
Returns regression delta comparing current run against previous baseline.

---

## 7. Real-Time WebSocket API

### `ws://localhost:8000/ws/execution/{run_id}`
Streams live events:
- `state_transition`: State machine stage updates (DISCOVER, PLAN, EXECUTE, etc.)
- `test_started`: Active test case notification
- `step_update`: Live step completion, locator recovery info, and screenshot path
- `test_completed`: Test outcome (PASS, FAIL, BLOCKED, INCONCLUSIVE)
- `bug_detected`: Real-time bug alert
- `run_completed`: Executive summary and final report notification
- Incoming client commands: Send `{"action": "pause"}` or `{"action": "resume"}` or `{"action": "stop"}`.
