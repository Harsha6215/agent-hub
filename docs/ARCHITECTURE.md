# Architecture

## Overview

Agent Hub is an AI Agent Utility Platform built as a monorepo with the following services:

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Web Dashboard│  │  API Client  │  │  AI Agent    │  │
│  │  (React)     │  │  (curl/SDK)  │  │  (MCP/REST)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │  FastAPI Backend                                   │ │
│  │  • Auth (JWT + API Keys)                           │ │
│  │  • Rate Limiting (Redis)                           │ │
│  │  • Request Routing                                 │ │
│  │  • Usage Metering                                  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Agent Registry                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │GST Agent │ │Salary    │ │EMI Agent │ │Job Agent │  │
│  │          │ │Agent     │ │          │ │          │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Data Layer                            │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │  PostgreSQL   │  │    Redis     │                    │
│  │  (primary DB) │  │  (cache/RL)  │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

## Key Decisions

1. **Monorepo** — keeps all services in one repo for easier development
2. **FastAPI** — async, auto-generates OpenAPI docs, fast development
3. **PostgreSQL** — robust, JSONB for flexible agent configs
4. **Redis** — rate limiting and caching without complex infrastructure
5. **BaseAgent pattern** — adding new agents is just implementing an interface
6. **Per-request pricing** — simple, measurable, scalable revenue model

## Data Flow

```
Request → Gateway → Auth → Rate Limit → Agent Execute → Usage Record → Response
```

## Security Layers

1. API Key validation (SHA-256 hash comparison)
2. JWT for dashboard access
3. Rate limiting per user tier
4. Input validation (Pydantic schemas per agent)
5. CORS restriction
