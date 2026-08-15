"""
Well-known endpoints — AI plugin manifest, llms.txt.

These help AI systems discover and understand Agent Hub.
"""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from apps.api.app.core.config import settings
from apps.api.app.services.agent_registry import registry

router = APIRouter(tags=["Discovery"])


@router.get("/.well-known/ai-plugin.json")
async def ai_plugin_manifest():
    """OpenAI-compatible AI plugin manifest."""
    return {
        "schema_version": "v1",
        "name_for_human": "Agent Hub",
        "name_for_model": "agent_hub",
        "description_for_human": "AI Agent Utility Platform — APIs for calculators, business tools, and more.",
        "description_for_model": "Agent Hub provides utility APIs. Use tools/list to discover available agents, then call them via the execute endpoint.",
        "auth": {
            "type": "service_http",
            "authorization_type": "bearer",
            "verification_tokens": {},
        },
        "api": {
            "type": "openapi",
            "url": "/openapi.json",
        },
        "logo_url": "",
        "contact_email": "support@agent-hub.dev",
        "legal_info_url": "",
    }


@router.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    """
    Plain-text description of Agent Hub for LLMs.

    Following the llms.txt convention for AI-readable service descriptions.
    """
    agents = registry.list_active()
    agent_lines = []
    for a in agents:
        price = "free" if a.price_per_request == 0 else f"₹{a.price_per_request/100:.2f}/req"
        agent_lines.append(f"  - {a.slug}: {a.description} [{price}]")

    agents_block = "\n".join(agent_lines) if agent_lines else "  (none registered yet)"

    return f"""# Agent Hub
> AI Agent Utility Platform

## What is this?
Agent Hub is a platform that provides utility APIs designed for both humans and AI agents.
Each utility is called an "agent" — you send structured input, get structured output.

## Available Agents
{agents_block}

## How to use
1. Get an API key: POST /api/v1/auth/register then POST /api/v1/keys
2. Call an agent: POST /api/v1/agents/{{slug}}/execute with X-API-Key header
3. Or use MCP: POST /mcp with JSON-RPC (tools/list, tools/call)

## Authentication
- Header: X-API-Key: sk_live_...
- Rate limits: Free=100/day, Developer=1000/day, Pro=10000/day

## MCP Integration
Agent Hub supports the Model Context Protocol.
Connect as an MCP server at: /mcp

## Links
- API Docs: /docs
- OpenAPI Spec: /openapi.json
- MCP Tools: /mcp/tools
- Developer Guide: /api/v1/developers/quickstart
"""
