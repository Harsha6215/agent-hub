# MCP Setup — Connecting Agent Hub to AI Assistants

Agent Hub implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
so AI assistants can discover and call agents as tools.

## Endpoint

```
POST https://agent-hub-production-70f1.up.railway.app/mcp
```

## Supported Methods

| Method | Description |
|--------|-------------|
| `initialize` | Returns server info and capabilities |
| `tools/list` | Lists all available agents as MCP tools |
| `tools/call` | Executes an agent tool |
| `ping` | Health check |

## Example: tools/list

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "hello",
        "description": "A simple greeting agent. Send a name, get a personalized hello back. (v1.0.0)",
        "inputSchema": {
          "type": "object",
          "properties": {
            "name": {"type": "string", "description": "Name to greet"},
            "language": {"type": "string", "enum": ["en", "hi", "es", "fr"]}
          },
          "required": ["name"]
        }
      }
    ]
  }
}
```

## Example: tools/call

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "hello",
    "arguments": {
      "name": "Harsh",
      "language": "hi"
    }
  }
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"greeting\": \"नमस्ते, Harsh! Agent Hub में आपका स्वागत है।\",\n  \"agent\": \"hello\",\n  \"version\": \"1.0.0\"\n}"
      }
    ]
  }
}
```

## Configuration for AI Clients

### Kiro / VS Code MCP

Add to your `.kiro/settings/mcp.json` or workspace config:

```json
{
  "mcpServers": {
    "agent-hub": {
      "url": "https://agent-hub-production-70f1.up.railway.app/mcp",
      "transport": "http"
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agent-hub": {
      "command": "curl",
      "args": ["-X", "POST", "https://agent-hub-production-70f1.up.railway.app/mcp"]
    }
  }
}
```

### Convenience Endpoint

List all tools without JSON-RPC:
```
GET https://agent-hub-production-70f1.up.railway.app/mcp/tools
```

## Discovery

- **llms.txt**: `GET /llms.txt` — plain text service description
- **AI Plugin**: `GET /.well-known/ai-plugin.json` — OpenAI plugin format
- **OpenAPI**: `GET /openapi.json` — full API specification
