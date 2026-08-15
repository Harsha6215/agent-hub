"""
MCP Server — Exposes Agent Hub agents as MCP tools.

IMPORTANT: tools/call goes through the shared executor.
This ensures auth, rate limiting, and usage recording apply equally
to MCP and REST calls. No free backdoor.

Discovery (tools/list) remains public.
"""

import json
from typing import Any

import structlog

from apps.api.app.services.agent_registry import registry
from apps.api.app.services.executor import execute_agent, ExecutionResult

logger = structlog.get_logger(__name__)


def get_mcp_tools() -> list[dict[str, Any]]:
    """
    Generate MCP tool definitions from all registered agents.
    This is public — no authentication required for discovery.
    """
    tools = []
    for agent in registry.list_active():
        tool = {
            "name": agent.slug,
            "description": f"{agent.description} (v{agent.version}, ₹{agent.price_per_request/100:.2f}/req)",
            "inputSchema": agent.get_input_schema(),
        }
        tools.append(tool)
    return tools


async def call_mcp_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Execute an MCP tool call through the shared executor.

    Goes through: auth → rate limit → execute → usage recording.
    Same path as REST. No bypassing.

    Optional: pass `_api_key` in arguments for authenticated calls.
    """
    # Extract optional API key from arguments (MCP clients can pass it)
    api_key = arguments.pop("_api_key", None)

    try:
        result: ExecutionResult = await execute_agent(
            slug=tool_name,
            input_data=arguments,
            api_key=api_key,
        )

        if result.success:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result.data, ensure_ascii=False, indent=2),
                    }
                ],
                "_meta": {
                    "agent": result.agent,
                    "version": result.version,
                    "latency_ms": result.latency_ms,
                    "request_id": result.request_id,
                    "cost_paisa": registry.get(tool_name).price_per_request if registry.get(tool_name) else 0,
                },
            }
        else:
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": result.error or "Unknown error",
                    }
                ],
            }

    except Exception as e:
        error_type = type(e).__name__
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"{error_type}: {str(e)}",
                }
            ],
        }


def get_server_info() -> dict[str, Any]:
    """MCP server metadata."""
    return {
        "name": "agent-hub",
        "version": "0.1.0",
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {"listChanged": False},
        },
    }
