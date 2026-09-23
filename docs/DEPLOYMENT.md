# Production Deployment & Infrastructure Guide

## 1. Docker Compose Deployment (Recommended)

The easiest way to run the full stack in production is using Docker Compose:

```bash
docker compose up --build -d
```

Services started:
- `backend`: FastAPI server running on port 8000 with Playwright Chromium installed.
- `frontend`: React + Vite application running on port 5173.
- `qa_data`: Persistent volume for SQLite database, evidence screenshots, and generated reports.

---

## 2. Production PostgreSQL Database Configuration

For multi-worker enterprise deployments, configure PostgreSQL in `.env` or Docker environment:

```env
DATABASE_URL=postgresql://qa_user:secure_password@postgres_host:5432/qa_agent_db
```

SQLAlchemy models will automatically connect and create required schemas.

---

## 3. Production Safe Mode & Authorization

In production environments (`environment = "production"`), the Safety Policy Engine blocks destructive actions:
- `delete`, `remove`, `drop`, `purge`
- `payment`, `purchase`
- `send email`, `send sms`
- `reset password`, `change settings`

When a restricted action is reached, execution pauses and emits an approval request to the dashboard over WebSockets.
