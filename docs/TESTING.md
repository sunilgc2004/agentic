# Testing & Verification Guide

## 1. Running the Automated QA Agent Test Suite

The QA Agent platform includes automated pytest tests verifying all internal engines:
- `test_safety_policy.py`: Sensitive data masking & restricted actions
- `test_locator_engine.py`: Priority hierarchy & self-healing
- `test_test_generator.py`: Smoke, negative, and natural language test generation
- `test_analyzer.py`: Expected vs actual outcome evaluation & confidence threshold
- `test_bug_analyzer.py`: False positive differentiation & severity reasoning
- `test_api.py`: FastAPI REST endpoints and playground app

Run the test suite:
```powershell
cd backend
python -m pytest tests -v
```

---

## 2. End-to-End Autonomous Testing Verification

To run a live autonomous test using the built-in target sandbox:
1. Start the FastAPI backend:
   ```powershell
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```
2. Start the React frontend:
   ```powershell
   cd frontend
   npm run dev
   ```
3. Open your browser to `http://localhost:5173`.
4. Click **Start AI Test** with Mode: `Smoke Testing`.
5. Observe the live progression on the **Live Execution** tab:
   - Application base URL visited
   - Login page detected and authenticated
   - Case Management module explored
   - Case creation submitted and validated
   - Video Conference link generated (observing the intentional simulated API 500 error)
   - Agent 5 triages the defect and assigns `BUG-001` (Severity: High, Category: API)
   - Final audit report generated in HTML and JSON.
