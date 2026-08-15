"""
Developer Portal endpoints — documentation, quickstart, SDK examples.
"""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from apps.api.app.core.config import settings
from apps.api.app.services.agent_registry import registry

router = APIRouter(prefix="/developers", tags=["Developers"])


@router.get("/quickstart")
async def quickstart():
    """Getting started guide for developers."""
    return {
        "title": "Agent Hub — Quick Start",
        "steps": [
            {
                "step": 1,
                "title": "Register",
                "description": "Create an account at /api/v1/auth/register",
                "example": {
                    "method": "POST",
                    "url": "/api/v1/auth/register",
                    "body": {"email": "you@example.com", "password": "your-password"},
                },
            },
            {
                "step": 2,
                "title": "Create an API Key",
                "description": "Generate an API key for authentication",
                "example": {
                    "method": "POST",
                    "url": "/api/v1/keys",
                    "headers": {"Authorization": "Bearer <your-jwt-token>"},
                    "body": {"name": "My App"},
                },
            },
            {
                "step": 3,
                "title": "Execute an Agent",
                "description": "Call any agent through the gateway",
                "example": {
                    "method": "POST",
                    "url": "/api/v1/agents/hello/execute",
                    "headers": {"X-API-Key": "sk_live_..."},
                    "body": {"input": {"name": "World"}},
                },
            },
            {
                "step": 4,
                "title": "MCP Integration (optional)",
                "description": "Connect Agent Hub as an MCP server for AI assistants",
                "config": {
                    "mcpServers": {
                        "agent-hub": {
                            "url": "http://localhost:8000/mcp",
                            "transport": "http",
                        }
                    }
                },
            },
        ],
        "links": {
            "docs": "/docs",
            "openapi": "/openapi.json",
            "agents": "/api/v1/agents",
            "mcp_tools": "/mcp/tools",
        },
    }


@router.get("/agents")
async def all_agent_docs():
    """Combined documentation for all available agents."""
    agents = registry.list_active()
    return {
        "agents": [agent.get_documentation() for agent in agents],
        "total": len(agents),
    }


@router.get("/examples/{slug}")
async def agent_examples(slug: str):
    """Code examples for a specific agent."""
    agent = registry.get(slug)
    if not agent:
        return {"error": f"Agent '{slug}' not found"}

    base_url = "http://localhost:8000"
    return {
        "agent": slug,
        "examples": {
            "curl": f"""curl -X POST {base_url}/api/v1/agents/{slug}/execute \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: sk_live_YOUR_KEY" \\
  -d '{{"input": {{}}}}'""",
            "python": f"""import httpx

response = httpx.post(
    "{base_url}/api/v1/agents/{slug}/execute",
    headers={{"X-API-Key": "sk_live_YOUR_KEY"}},
    json={{"input": {{}}}},
)
print(response.json())""",
            "javascript": f"""const response = await fetch("{base_url}/api/v1/agents/{slug}/execute", {{
  method: "POST",
  headers: {{
    "Content-Type": "application/json",
    "X-API-Key": "sk_live_YOUR_KEY",
  }},
  body: JSON.stringify({{ input: {{}} }}),
}});
const data = await response.json();
console.log(data);""",
        },
    }


@router.get("/rate-limits")
async def rate_limits_info():
    """Rate limit information by tier."""
    return {
        "tiers": {
            "free": {"limit": 100, "period": "day", "price": "₹0"},
            "developer": {"limit": 1000, "period": "day", "price": "₹499/mo"},
            "pro": {"limit": 10000, "period": "day", "price": "₹1999/mo"},
            "enterprise": {"limit": 100000, "period": "day", "price": "Custom"},
        },
        "headers": {
            "X-RateLimit-Limit": "Maximum requests per period",
            "X-RateLimit-Remaining": "Requests remaining",
            "X-RateLimit-Reset": "Seconds until reset",
            "Retry-After": "Seconds to wait (on 429)",
        },
    }
