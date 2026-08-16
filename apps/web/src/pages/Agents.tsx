import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "@/lib/api";

interface AgentTool {
  name: string;
  description: string;
  inputSchema: { properties?: Record<string, any> };
}

export default function Agents() {
  const [tools, setTools] = useState<AgentTool[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/mcp/tools")
      .then((res) => setTools(res.data.tools || []))
      .catch(() => setTools([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Nav */}
      <nav className="border-b border-gray-800 px-6 py-4 flex justify-between items-center max-w-6xl mx-auto">
        <Link to="/" className="font-bold text-xl">Agent Hub</Link>
        <div className="flex gap-4 items-center">
          <Link to="/docs" className="text-gray-400 hover:text-white text-sm">Docs</Link>
          <Link to="/register" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium">Get API Key</Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold mb-2">Agent Catalog</h1>
        <p className="text-gray-400 mb-8">Production-ready APIs you can call via REST or MCP.</p>

        {loading ? (
          <p className="text-gray-400">Loading agents...</p>
        ) : tools.length === 0 ? (
          <p className="text-gray-400">No agents available.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {tools.map((tool) => {
              const ops = tool.inputSchema?.properties?.operation;
              const opsCount = ops?.enum?.length || 0;
              return (
                <Link
                  key={tool.name}
                  to={`/agents/${tool.name}`}
                  className="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-blue-500 transition-colors"
                >
                  <h3 className="text-white font-semibold text-lg mb-1">{tool.name}</h3>
                  <p className="text-gray-400 text-sm mb-3">{tool.description}</p>
                  {opsCount > 0 && (
                    <span className="text-xs bg-gray-700 px-2 py-1 rounded text-gray-300">
                      {opsCount} operations
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
