# Autonomous AI QA Testing Agent - Git Push & Deployment Guide

This document provides step-by-step instructions to push your codebase to Git (GitHub / GitLab) and deploy the Autonomous AI QA Testing Agent platform to staging and production environments.

---

## 1. Push to GitHub / GitLab

The repository is already initialized on branch `main` with `.gitignore` properly configured.

### Step 1.1: Create an Empty Repository on GitHub or GitLab
1. Go to **[GitHub](https://github.com/new)** (or GitLab).
2. Set Repository Name: `ai-qa-agent` (or your preferred name).
3. Choose **Private** or **Public**.
4. **Do NOT** check "Add a README file", ".gitignore", or "license" (we already have them).
5. Click **Create repository**.

### Step 1.2: Add Remote and Push
Open PowerShell or your terminal in the project directory:
```powershell
# Navigate to the project directory if not already there
cd C:\Users\sunil\.gemini\antigravity\scratch\ai-qa-agent

# Link your GitHub repository (replace with your actual repo URL)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/ai-qa-agent.git

# Set default branch to main and push
git push -u origin main
```

*(If you use GitLab, replace the URL with `https://gitlab.com/<username>/ai-qa-agent.git`)*

---

## 2. Deployment Architecture Overview

```
                      +-----------------------------+
                      |   Reverse Proxy (Nginx)     |
                      |   Port 80 / 443 (SSL/TLS)   |
                      +--------------+--------------+
                                     |
               +---------------------+---------------------+
               |                                           |
      HTTP / WebSocket                             Static Assets
      /api/* and /ws/*                             /*
               |                                           |
+--------------v---------------+            +--------------v---------------+
|    FastAPI QA Agent Engine   |            |    React / Vite Web UI       |
|    Port 8000 (Internal)      |            |    Port 5173 (or Nginx dist) |
|    + Headless Playwright     |            +------------------------------+
+--------------+---------------+
               |
  +------------v------------+
  |  Data Volume / Database |
  |  - SQLite or PostgreSQL |
  |  - Evidence Screenshots |
  |  - HTML/JSON Reports    |
  +-------------------------+
```

---

## 3. Deployment Option A: Cloud VM via Docker Compose (Recommended)

Ideal for **AWS EC2, DigitalOcean Droplet, Hetzner, Linode, or any Ubuntu/Debian server**.

### Step 3.1: Server Prerequisites
Ensure your VM has Docker and Docker Compose installed:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

### Step 3.2: Clone and Configure
On your cloud server:
```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/ai-qa-agent.git
cd ai-qa-agent

# Create environment configuration
cp backend/.env.example backend/.env
```

Edit `backend/.env` to configure your LLM provider and production settings:
```env
LLM_PROVIDER=openai  # or heuristic / anthropic
OPENAI_API_KEY=sk-proj-your-api-key-here
HEADLESS=true
DEFAULT_BROWSER=chromium
CONFIDENCE_THRESHOLD=0.70
```

### Step 3.3: Launch with Docker Compose
```bash
docker compose up --build -d
```

Verify services are running:
```bash
docker compose ps
docker compose logs -f
```

The application is now live:
- **Frontend Dashboard**: `http://<YOUR_SERVER_IP>:5173`
- **Backend REST API**: `http://<YOUR_SERVER_IP>:8000`
- **API Swagger Docs**: `http://<YOUR_SERVER_IP>:8000/docs`

---

## 4. Production Domain & Free SSL Setup (Nginx + Let's Encrypt)

To serve the app over `https://qa.yourdomain.com`:

### Step 4.1: Nginx Configuration
Create `/etc/nginx/sites-available/ai-qa`:
```nginx
server {
    server_name qa.yourdomain.com;

    # Frontend UI
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend REST API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket Live Execution Stream
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

Enable site and install SSL certificate:
```bash
sudo ln -s /etc/nginx/sites-available/ai-qa /etc/nginx/sites-enabled/
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d qa.yourdomain.com
```

---

## 5. Deployment Option B: Managed Container Platforms

### Render / Railway / Fly.io
1. Connect your GitHub repository.
2. Select **Dockerfile** as the build method.
3. Configure Environment Variables:
   - `OPENAI_API_KEY`: `sk-...`
   - `LLM_PROVIDER`: `openai`
   - `HEADLESS`: `true`
4. Attach a persistent volume mounted at `/app/backend/data` to retain test history and evidence screenshots across deploys.

### Google Cloud Run / AWS ECS / Azure Container Apps
1. Build and push image:
   ```bash
   docker build -t your-registry/ai-qa-agent:latest .
   docker push your-registry/ai-qa-agent:latest
   ```
2. Set Memory to minimum **2 GB** (to comfortably run Chromium headless browser).
3. Set CPU to minimum **1 vCPU** (2 vCPUs recommended for concurrent test runs).
4. For Google Cloud Run, enable **WebSockets session affinity**.

---

## 6. Enterprise Database: PostgreSQL Setup

For team and multi-worker deployments, switch from SQLite to PostgreSQL:

In `backend/.env` or Docker environment:
```env
DATABASE_URL=postgresql://qa_user:secure_password@postgres_host:5432/qa_agent_db
```

SQLAlchemy automatically provisions all tables (`projects`, `applications`, `test_runs`, `bugs`, `evidence`, etc.) on initial startup.

---

## 7. Production Safe Mode & Security Guardrails

When testing staging or production apps (`environment = "production"`):
- The **Safety Policy Engine** blocks destructive actions automatically (`delete`, `remove`, `drop`, `purchase`, `reset password`).
- When a restricted action is reached, execution pauses and prompts for human approval over the live WebSocket feed.
- Credentials and tokens are automatically masked in all execution logs (`***MASKED***`).

---

## 8. CI/CD Automated Testing (GitHub Actions)

The repository includes a ready-to-use GitHub Actions workflow located at `.github/workflows/ai-qa.yml`:
- Runs unit & integration tests on pull requests.
- Installs Playwright Chromium.
- Executes automated smoke tests against target web apps.
- Uploads HTML/JSON test reports and screenshot evidence as GitHub build artifacts.
