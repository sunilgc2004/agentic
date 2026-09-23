# AI Agent Design & State Machine Specification

## 1. The 10-State Execution Machine

To ensure predictability, prevent infinite loops, and handle retries gracefully, the QA Agent operates through a deterministic State Machine:

```
[IDLE]
  │
  ▼
[DISCOVER] ──(Agent 1 explores DOM & navigation)──>
  │
  ▼
[PLAN] ──(Agent 2 generates structured test cases)──>
  │
  ▼
[VALIDATE PLAN] ──(Verifies preconditions & safety policy)──>
  │
  ▼
[EXECUTE] ──(Agent 3 runs Playwright step with smart locator)──>
  │
  ▼
[OBSERVE] ──(Collects console logs, network errors, screenshot)──>
  │
  ▼
[ANALYZE] ──(Agent 4 evaluates expected vs actual outcome)──>
  │
  ├─── If Failed & retries < MAX_RETRIES ──> [RECOVER] ──> [RETRY] ──> [EXECUTE]
  │
  ▼
[VERIFY] ──(Agent 5 triages bugs, classifies severity, generates report)──>
  │
  ▼
[REPORT] ──(Generates HTML/JSON reports & updates baseline)──>
  │
  ▼
[COMPLETED]
```

---

## 2. Confidence Scoring & Inconclusive Safeguard (Section 33)

Every evaluation made by Agent 4 includes a confidence score $\in [0.0, 1.0]$.
- If the AI evaluates a potential discrepancy but has low certainty ($\text{confidence} < 0.70$), it marks the outcome as **`INCONCLUSIVE`** instead of prematurely claiming a bug.
- This prevents flakiness and alerts the human QA engineer to review the evidence.

---

## 3. False Positive Filtering (Section 42)

Agent 5 actively distinguishes between:
1. **Application Bugs**: Real frontend JavaScript exceptions, functional mismatch against expected criteria, or backend HTTP 500 errors.
2. **Automation Failures**: Locator timeout due to DOM restructuring where self-healing could not resolve. Flagged as `Automation` category, severity `Low`, `is_application_bug = False`.
3. **Environment Failures**: DNS failures, host connection refused (`ERR_CONNECTION_REFUSED`), or 502/503 gateway outages. Flagged as `Environment` category, preventing misleading defect metrics.
4. **Test Data Failures**: Stale test records or collision on unique fields.

---

## 4. Self-Healing Locator Engine (Section 17 & 18)

When a primary selector fails:
1. The locator engine queries the DOM for semantic candidates matching keywords in the target description.
2. Calculates relevance scores across `role`, `aria-label`, `placeholder`, `name`, `id`, and inner text.
3. Filters candidates to only those that are visible, within the viewport, and enabled (`!disabled`).
4. Selects the highest-confidence equivalent element, logs the self-healing event, and retries the action.
