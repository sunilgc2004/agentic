from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter()

PLAYGROUND_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Arbitration & Case Management Portal</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; }
        .container { max-width: 1000px; margin: 40px auto; padding: 24px; background: #1e293b; border-radius: 12px; border: 1px solid #334155; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; }
        nav a { color: #94a3b8; text-decoration: none; margin-right: 20px; font-weight: 500; }
        nav a.active, nav a:hover { color: #38bdf8; }
        .btn { padding: 10px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; border: none; font-size: 14px; transition: all 0.2s; }
        .btn-primary { background: #2563eb; color: #fff; }
        .btn-primary:hover { background: #1d4ed8; }
        .btn-danger { background: #dc2626; color: #fff; }
        .btn-secondary { background: #334155; color: #fff; }
        .form-group { margin-bottom: 16px; }
        label { display: block; margin-bottom: 6px; font-size: 14px; color: #94a3b8; }
        input, select { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; }
        .alert { padding: 12px; border-radius: 6px; margin-bottom: 16px; font-size: 14px; display: none; }
        .alert-success { background: #064e3b; color: #6ee7b7; border: 1px solid #059669; }
        .alert-danger { background: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626; }
        table { width: 100%; border-collapse: collapse; margin-top: 16px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }
        th { color: #94a3b8; background: #0f172a; }
        .hidden { display: none !important; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h2 style="margin:0; color:#38bdf8;">LexArbitrate Enterprise Portal</h2>
        <nav id="nav-bar" class="hidden">
            <a href="javascript:void(0)" id="nav-dash" class="active" onclick="showView('dashboard')">Dashboard</a>
            <a href="javascript:void(0)" id="nav-cases" onclick="showView('cases')">Case Management</a>
            <button id="btn-logout" class="btn btn-secondary" style="margin-left:16px;" onclick="logout()">Logout</button>
        </nav>
    </div>

    <!-- 1. LOGIN VIEW -->
    <div id="login-view">
        <h3 style="margin-top:0;">Sign In to Enterprise Workspace</h3>
        <p style="color:#94a3b8;">Default demo credentials: <code>test@example.com</code> / <code>SecurePass123!</code></p>
        <div id="login-error" class="alert alert-danger">Invalid credentials provided. Please check your username and password.</div>
        <form id="login-form" onsubmit="handleLogin(event)">
            <div class="form-group">
                <label for="username">Username / Work Email</label>
                <input id="username" name="username" type="text" placeholder="name@company.com" required />
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input id="password" name="password" type="password" placeholder="••••••••" required />
            </div>
            <button id="btn-login" type="submit" class="btn btn-primary" style="width:100%;">Login</button>
        </form>
    </div>

    <!-- 2. DASHBOARD VIEW -->
    <div id="dashboard-view" class="hidden">
        <div id="dashboard-header">
            <h3>Welcome to Arbitration Dashboard</h3>
            <p style="color:#94a3b8;">Active Cases: <strong>3</strong> | Pending VC Hearings: <strong>1</strong></p>
        </div>
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:16px; margin:24px 0;">
            <div style="background:#0f172a; padding:16px; border-radius:8px;">
                <h4 style="margin:0 0 8px 0; color:#38bdf8;">Total Cases</h4>
                <div style="font-size:24px; font-weight:bold;">124</div>
            </div>
            <div style="background:#0f172a; padding:16px; border-radius:8px;">
                <h4 style="margin:0 0 8px 0; color:#4ade80;">Settlement Rate</h4>
                <div style="font-size:24px; font-weight:bold;">88.4%</div>
            </div>
            <div style="background:#0f172a; padding:16px; border-radius:8px;">
                <h4 style="margin:0 0 8px 0; color:#f59e0b;">Pending Actions</h4>
                <div style="font-size:24px; font-weight:bold;">2</div>
            </div>
        </div>
        <button class="btn btn-primary" onclick="showView('cases')">Open Case Management</button>
    </div>

    <!-- 3. CASE MANAGEMENT VIEW -->
    <div id="cases-view" class="hidden">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
            <h3 style="margin:0;">Active Arbitration Cases</h3>
            <button id="btn-create-case" class="btn btn-primary" onclick="toggleCreateModal(true)">+ Create Case</button>
        </div>

        <div id="case-success-banner" class="alert alert-success">Case record successfully registered in database.</div>

        <table id="cases-table">
            <thead>
                <tr>
                    <th>Case Number</th>
                    <th>Claimant</th>
                    <th>Respondent</th>
                    <th>Dispute Amount</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="cases-tbody">
                <tr>
                    <td>ARB-2026-8812</td>
                    <td>Acme Corp</td>
                    <td>Global Logistics Ltd</td>
                    <td>$125,000</td>
                    <td>
                        <button id="btn-open-case" class="btn btn-secondary" style="padding:4px 8px; font-size:12px;" onclick="selectCase('ARB-2026-8812')">View</button>
                        <button id="btn-generate-vc" class="btn btn-primary" style="padding:4px 8px; font-size:12px;" onclick="triggerGenerateVC('ARB-2026-8812')">Generate VC Link</button>
                    </td>
                </tr>
            </tbody>
        </table>

        <!-- VC Result notification area -->
        <div id="vc-container" style="margin-top:20px; padding:16px; background:#0f172a; border-radius:8px;" class="hidden">
            <h4 style="margin:0 0 8px 0; color:#38bdf8;">Video Conference Hearing Status</h4>
            <div id="vc-link-url" style="color:#4ade80; font-family:monospace;"></div>
            <div id="vc-error-msg" style="color:#ef4444; display:none;">Error 500: Video conference service failed to provision room token.</div>
        </div>
    </div>

    <!-- 4. CREATE CASE MODAL -->
    <div id="create-modal" class="hidden" style="margin-top:24px; padding:20px; background:#0f172a; border-radius:8px; border:1px solid #334155;">
        <h4 style="margin-top:0;">Register New Arbitration Case</h4>
        <div id="modal-error" class="alert alert-danger">Please fill all required fields with valid amounts.</div>
        <form id="create-case-form" onsubmit="submitCase(event)">
            <div class="form-group">
                <label for="claimant_name">Claimant Name *</label>
                <input id="claimant_name" name="claimant_name" type="text" placeholder="e.g. Apex Industrial Solutions" required />
            </div>
            <div class="form-group">
                <label for="respondent_name">Respondent Name *</label>
                <input id="respondent_name" name="respondent_name" type="text" placeholder="e.g. Zenith Tech Partners" required />
            </div>
            <div class="form-group">
                <label for="dispute_amount">Dispute Amount (USD) *</label>
                <input id="dispute_amount" name="dispute_amount" type="number" placeholder="e.g. 50000" required />
            </div>
            <div style="display:flex; gap:12px; margin-top:20px;">
                <button id="btn-submit-case" type="submit" class="btn btn-primary">Submit Case</button>
                <button type="button" class="btn btn-secondary" onclick="toggleCreateModal(false)">Cancel</button>
            </div>
        </form>
    </div>
</div>

<script>
    let isAuthenticated = false;

    function showView(view) {
        document.getElementById('login-view').classList.add('hidden');
        document.getElementById('dashboard-view').classList.add('hidden');
        document.getElementById('cases-view').classList.add('hidden');
        document.getElementById('create-modal').classList.add('hidden');

        if (view === 'login') {
            document.getElementById('login-view').classList.remove('hidden');
            document.getElementById('nav-bar').classList.add('hidden');
        } else if (view === 'dashboard') {
            document.getElementById('dashboard-view').classList.remove('hidden');
            document.getElementById('nav-bar').classList.remove('hidden');
            document.getElementById('nav-dash').classList.add('active');
            document.getElementById('nav-cases').classList.remove('active');
        } else if (view === 'cases') {
            document.getElementById('cases-view').classList.remove('hidden');
            document.getElementById('nav-bar').classList.remove('hidden');
            document.getElementById('nav-cases').classList.add('active');
            document.getElementById('nav-dash').classList.remove('active');
        }
    }

    function handleLogin(e) {
        e.preventDefault();
        const u = document.getElementById('username').value.trim();
        const p = document.getElementById('password').value.trim();
        const err = document.getElementById('login-error');

        // Simple auth check
        if (u === 'test@example.com' && p === 'SecurePass123!') {
            err.style.display = 'none';
            isAuthenticated = true;
            showView('dashboard');
        } else {
            err.style.display = 'block';
        }
    }

    function logout() {
        isAuthenticated = false;
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
        showView('login');
    }

    function toggleCreateModal(open) {
        const modal = document.getElementById('create-modal');
        if (open) modal.classList.remove('hidden');
        else modal.classList.add('hidden');
    }

    function submitCase(e) {
        e.preventDefault();
        const claimant = document.getElementById('claimant_name').value.trim();
        const respondent = document.getElementById('respondent_name').value.trim();
        const amount = parseFloat(document.getElementById('dispute_amount').value);
        const err = document.getElementById('modal-error');

        if (!claimant || !respondent || isNaN(amount) || amount <= 0) {
            err.style.display = 'block';
            return;
        }
        err.style.display = 'none';

        // Add to table
        const tbody = document.getElementById('cases-tbody');
        const caseNum = 'ARB-2026-' + Math.floor(1000 + Math.random() * 9000);
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${caseNum}</td>
            <td>${claimant}</td>
            <td>${respondent}</td>
            <td>$${amount.toLocaleString()}</td>
            <td>
                <button class="btn btn-secondary" style="padding:4px 8px; font-size:12px;">View</button>
                <button class="btn btn-primary" style="padding:4px 8px; font-size:12px;" onclick="triggerGenerateVC('${caseNum}')">Generate VC Link</button>
            </td>
        `;
        tbody.appendChild(tr);

        // Success banner
        toggleCreateModal(false);
        const banner = document.getElementById('case-success-banner');
        banner.style.display = 'block';
        setTimeout(() => { banner.style.display = 'none'; }, 4000);
    }

    function triggerGenerateVC(caseNum) {
        const container = document.getElementById('vc-container');
        const urlBox = document.getElementById('vc-link-url');
        const errBox = document.getElementById('vc-error-msg');
        container.classList.remove('hidden');

        // Intentionally simulate an API failure with HTTP 500 error call to demonstrate AI Bug Analyzer
        fetch('/api/v1/playground/api/cases/vc-token?case=' + caseNum, { method: 'POST' })
            .then(res => {
                if (!res.ok) throw new Error('HTTP ' + res.status);
                return res.json();
            })
            .then(data => {
                urlBox.innerText = data.conference_url;
                urlBox.style.display = 'block';
                errBox.style.display = 'none';
            })
            .catch(e => {
                console.error('VC generation API failed:', e);
                errBox.style.display = 'block';
                urlBox.style.display = 'none';
            });
    }

    function selectCase(id) {
        alert('Opening Case: ' + id);
    }
</script>
</body>
</html>
"""


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def get_playground():
    """Serves the live, fully-interactive test application."""
    return HTMLResponse(content=PLAYGROUND_HTML)


@router.post("/api/cases/vc-token")
async def generate_vc_token(case: str = "ARB-2026-8812"):
    """
    Simulated backend endpoint. Intentionally returns HTTP 500 for demonstration of AI Bug Analysis,
    or returns 200 if configured.
    """
    # Intentional simulated 500 error for case ARB-2026-8812 as per user workflow requirement!
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "message": f"Failed to allocate conference room for {case}"}
    )
