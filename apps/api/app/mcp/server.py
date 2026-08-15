"""
MCP Server — Exposes Agent Hub agents as MCP tools.

Supports:
  - tools/list: Returns all active agents as MCP-compatible tool definitions
  - tools/call: Routes tool calls to the appropriate agent

This can be served via SSE for remote access or stdio for local usage.
"""

import json
import time
from typing import Any

import structlog

from apps.api.app.services.agent_registry import registry

logger = structlog.get_logger(__name__)


def get_mcp_tools() -> list[dict[str, Any]]:
    """
    Generate MCP tool definitions from all registered agents.

    Each agent becomes a tool with:
    - name: agent slug
    - description: agent description
    - inputSchema: agent's JSON schema for input
    """
    tools = []
    for agent in registry.list_active():
        tool = {
            "name": agent.slug,
            "description": f"{agent.description} (v{agent.version})",
            "inputSchema": agent.get_input_schema(),
        }
        tools.append(tool)
    return tools


async def call_mcp_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Execute an MCP tool call by routing to the appropriate agent.

    Returns MCP-formatted response with content array.
    """
    agent = registry.get(tool_name)
    if not agent:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"Tool '{tool_name}' not found. Available tools: {[a.slug for a in registry.list_active()]}",
                }
            ],
        }

    start_time = time.perf_counter()
    try:
        result = await agent.execute(arguments)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2),
                }
            ],
            "_meta": {
                "agent": agent.slug,
                "version": agent.version,
                "latency_ms": latency_ms,
            },
        }
    except Exception as e:
        logger.error("mcp.tool_call_error", tool=tool_name, error=str(e))
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"Error executing '{tool_name}': {str(e)}",
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
