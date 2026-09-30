# Staging & Production Deployment Guide

This guide details how to deploy and manage the Autonomous AI QA Testing Agent across **Staging (`stage`)** and **Production (`prod`)** environments.

---

## 1. Staging vs Production: Key Differences

| Feature | Staging (`stage`) | Production (`prod`) |
| :--- | :--- | :--- |
| **Purpose** | Internal QA, exploratory testing, new feature validation | Continuous monitoring, regression tests, smoke checks |
| **Target Apps Tested** | Staging / dev builds (e.g. `https://stage-app.domain.com`) | Live production web applications (e.g. `https://app.domain.com`) |
| **Safety Mode** | **Permissive (`is_safe_mode = False`)** | **Strict Safe Mode (`is_safe_mode = True`)** |
| **Destructive Actions** | Allowed for form testing and validation | **Blocked / Pauses for Human Approval via WebSockets** |
| **Database** | SQLite or Staging PostgreSQL | Managed PostgreSQL 16 with persistent volume |
| **AI Confidence** | Standard (`0.70`) | High precision (`0.85`) |
| **Ports (Default)** | Backend `8080`, Frontend `5174` | Backend `8000`, Frontend `5173` |
| **Git Branch** | `staging` | `main` |

---

## 2. Git Branching Strategy (Git Flow)

To keep environments isolated and manageable:

```
feature/xxx  ──>  develop/staging  ──>  main (Production)
                        │                     │
                        ▼                     ▼
                Deploys to Staging     Deploys to Production
```

- **Staging Branch**: Push your new features or bug fixes to `staging` to test against staging instances.
- **Production Branch**: When tests pass on Staging, open a Pull Request to merge into `main` for production release.

---

## 3. Staging Deployment (`stage`)

### Step 3.1: Configure Staging Environment
Copy the staging template:
```bash
cp .env.staging.example .env.staging
```
Edit `.env.staging` with your staging settings:
```env
ENVIRONMENT=staging
DATABASE_URL=sqlite:///./data/qa_agent_staging.db
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-staging-api-key
HEADLESS=true
CONFIDENCE_THRESHOLD=0.70
```

### Step 3.2: Spin Up Staging Stack
```bash
docker compose -f docker-compose.staging.yml up --build -d
```

- **Staging Web UI**: `http://<SERVER_IP>:5174`
- **Staging Backend API**: `http://<SERVER_IP>:8080/docs`

---

## 4. Production Deployment (`prod`)

Production uses a dedicated PostgreSQL 16 database, strict safety rules, and production build serving.

### Step 4.1: Configure Production Environment
Copy the production template:
```bash
cp .env.prod.example .env.prod
```
Edit `.env.prod`:
```env
ENVIRONMENT=production
POSTGRES_USER=qa_admin
POSTGRES_PASSWORD=SetAStrongRandomPasswordHere!
POSTGRES_DB=qa_prod
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-production-api-key
HEADLESS=true
CONFIDENCE_THRESHOLD=0.85
BACKEND_CORS_ORIGINS=["https://qa.yourdomain.com"]
```

### Step 4.2: Spin Up Production Stack
```bash
docker compose -f docker-compose.prod.yml up --build -d
```

This starts:
1. `ai-qa-postgres-prod`: PostgreSQL 16 database with health check.
2. `ai-qa-backend-prod`: FastAPI server connected to Postgres with strict Safe Mode enabled.
3. `ai-qa-frontend-prod`: Production-optimized Vite build.

Verify containers:
```bash
docker compose -f docker-compose.prod.yml ps
```

- **Production Web UI**: `http://<SERVER_IP>:5173`
- **Production Backend API**: `http://<SERVER_IP>:8000/docs`

---

## 5. Production Safe Mode & Guardrails

When testing live production web applications, the **Safety Policy Engine** (`backend/app/core/safety_policy.py`) automatically intercepts potentially dangerous operations:

- **Restricted Actions**: `delete`, `remove`, `drop`, `purge`, `payment`, `purchase`, `send email`, `send sms`, `reset password`, `change settings`.
- **Behavior**:
  - The agent automatically halts execution.
  - An approval modal appears in the live execution dashboard.
  - The tester can review the action and click **"Approve"** or **"Skip Step"**.
- **Credential Masking**: All authentication tokens and passwords entered during test runs are masked (`***MASKED***`) across logs, screenshots, and reports.

---

## 6. Production Domain & Nginx SSL Setup

To serve Staging and Production under custom domains with free Let's Encrypt SSL:

```nginx
# Production: https://qa.yourdomain.com
server {
    server_name qa.yourdomain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
    }

    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_read_timeout 86400s;
    }
}

# Staging: https://stage-qa.yourdomain.com
server {
    server_name stage-qa.yourdomain.com;

    location / {
        proxy_pass http://localhost:5174;
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://localhost:8080/api/;
        proxy_set_header Host $host;
    }

    location /ws/ {
        proxy_pass http://localhost:8080/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_read_timeout 86400s;
    }
}
```

Enable SSL with Certbot:
```bash
sudo certbot --nginx -d qa.yourdomain.com -d stage-qa.yourdomain.com
```

---

## 7. Useful Operational Commands

| Task | Command |
| :--- | :--- |
| **View Staging Logs** | `docker compose -f docker-compose.staging.yml logs -f` |
| **View Production Logs** | `docker compose -f docker-compose.prod.yml logs -f` |
| **Stop Staging** | `docker compose -f docker-compose.staging.yml down` |
| **Stop Production** | `docker compose -f docker-compose.prod.yml down` |
| **Backup Production DB** | `docker exec -t ai-qa-postgres-prod pg_dump -U qa_admin qa_prod > backup_$(date +%Y%m%d).sql` |
| **Restore Production DB** | `cat backup.sql \| docker exec -i ai-qa-postgres-prod psql -U qa_admin -d qa_prod` |
