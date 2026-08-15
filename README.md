# Agent Hub

An AI Agent Utility Platform — build once, deploy, let AI agents discover and pay for usage.

## Vision

A platform hosting micro-SaaS API tools (agents) that are accessible to both humans and AI agents via REST APIs and MCP (Model Context Protocol).

**Revenue model:** Per-API-call pricing (₹0.05–₹5 per request) + subscription tiers.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 (async) |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Infrastructure | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | Railway (backend), Vercel (frontend) |

## Quick Start

```bash
# 1. Clone and configure
git clone <repo-url>
cd agent-hub
cp .env.example .env

# 2. Start all services
docker compose up

# 3. Access
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
# Health:    http://localhost:8000/health
```

## Project Structure

```
agent-hub/
│
├── apps/
│   ├── api/              # FastAPI backend
│   │   ├── app/
│   │   │   ├── core/    # Config, DB, logging, security
│   │   │   ├── api/v1/  # API routes
│   │   │   ├── models/  # SQLAlchemy ORM models
│   │   │   ├── schemas/ # Pydantic schemas
│   │   │   ├── services/# Business logic
│   │   │   └── middleware/
│   │   ├── tests/
│   │   └── alembic/
│   │
│   └── web/              # React + TypeScript frontend
│       └── src/
│
├── agents/               # Agent implementations
├── packages/shared/      # Shared utilities
├── docker/               # Dockerfiles
├── docs/                 # Documentation
├── .github/workflows/    # CI/CD
├── docker-compose.yml
└── .env.example
```

## Roadmap

| Epic | Description | Status |
|------|-------------|--------|
| 1 | Agent Hub Foundation | 🔲 |
| 2 | Agent Registry + API Gateway | 🔲 |
| 3 | Authentication + Usage Metering | 🔲 |
| 4 | MCP + Developer Portal | 🔲 |
| 5 | First Revenue Agents | 🔲 |
| 6 | Billing & Payments | 🔲 |
| 7 | Job Intelligence Agent | 🔲 |
| 8 | Business Intelligence Agent | 🔲 |
| 9 | AI Visibility Agent | 🔲 |
| 10 | Agent Marketplace | 🔲 |
| 11 | Developer Publishing | 🔲 |
| 12 | Growth + Distribution | 🔲 |

## Revenue Agents (Planned)

| Agent | Category | Price/Request |
|-------|----------|---------------|
| GST Calculator | Finance | ₹0.10 |
| Salary Calculator | Finance | ₹0.20 |
| EMI Calculator | Finance | ₹0.05 |
| SIP/CAGR Calculator | Finance | ₹0.10 |
| Profit Margin Calculator | Business | ₹0.10 |
| Job Intelligence | Career | ₹1.00 |
| Company Research | Data | ₹2.00 |
| AI Visibility Monitor | SaaS | ₹5.00 |

## Development

```bash
# Backend only
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend only
cd apps/web
npm install
npm run dev

# Tests
cd apps/api
pytest

# Docker
docker compose up --build
```

## License

MIT
