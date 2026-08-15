"""
MCP HTTP endpoints — SSE transport for remote MCP access.

Provides JSON-RPC style endpoints that MCP clients can connect to:
  POST /mcp — handles all MCP JSON-RPC requests
  GET /mcp/sse — Server-Sent Events stream (for MCP SSE transport)
"""

from typing import Any

import structlog
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from apps.api.app.mcp.server import call_mcp_tool, get_mcp_tools, get_server_info

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/mcp", tags=["MCP"])


@router.post("")
async def mcp_jsonrpc(request: Request):
    """
    MCP JSON-RPC endpoint.

    Handles:
    - initialize → server info + capabilities
    - tools/list → list all available tools
    - tools/call → execute a tool
    """
    body = await request.json()
    method = body.get("method", "")
    params = body.get("params", {})
    request_id = body.get("id")

    logger.info("mcp.request", method=method, id=request_id)

    if method == "initialize":
        result = get_server_info()
    elif method == "tools/list":
        result = {"tools": get_mcp_tools()}
    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        result = await call_mcp_tool(tool_name, arguments)
    elif method == "ping":
        result = {}
    else:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }
        )

    return JSONResponse(
        content={
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }
    )


@router.get("/tools")
async def list_mcp_tools():
    """List all available MCP tools (convenience endpoint)."""
    return {"tools": get_mcp_tools(), "count": len(get_mcp_tools())}
