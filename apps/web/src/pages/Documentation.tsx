import { useEffect, useState } from "react";
import api from "@/lib/api";

interface QuickstartStep {
  step: number;
  title: string;
  description: string;
  example?: Record<string, unknown>;
  config?: Record<string, unknown>;
}

export default function Documentation() {
  const [quickstart, setQuickstart] = useState<QuickstartStep[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/v1/developers/quickstart")
      .then((r) => setQuickstart(r.data.steps || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-3xl font-bold text-white mb-2">Developer Documentation</h1>
      <p className="text-gray-400 mb-8">
        Everything you need to integrate with Agent Hub.
      </p>

      {/* Quick links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        <a href="/docs" target="_blank" className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-blue-500 transition-colors text-center">
          <div className="text-2xl mb-1">📖</div>
          <div className="text-sm text-white font-medium">Swagger</div>
          <div className="text-xs text-gray-400">/docs</div>
        </a>
        <a href="/redoc" target="_blank" className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-blue-500 transition-colors text-center">
          <div className="text-2xl mb-1">📋</div>
          <div className="text-sm text-white font-medium">ReDoc</div>
          <div className="text-xs text-gray-400">/redoc</div>
        </a>
        <a href="/mcp/tools" target="_blank" className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-blue-500 transition-colors text-center">
          <div className="text-2xl mb-1">🔧</div>
          <div className="text-sm text-white font-medium">MCP Tools</div>
          <div className="text-xs text-gray-400">/mcp/tools</div>
        </a>
        <a href="/llms.txt" target="_blank" className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-blue-500 transition-colors text-center">
          <div className="text-2xl mb-1">🤖</div>
          <div className="text-sm text-white font-medium">llms.txt</div>
          <div className="text-xs text-gray-400">/llms.txt</div>
        </a>
      </div>

      {/* Quick Start */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Quick Start</h2>
        {loading ? (
          <p className="text-gray-400">Loading...</p>
        ) : (
          <div className="space-y-6">
            {quickstart.map((s) => (
              <div key={s.step} className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
                  {s.step}
                </div>
                <div className="flex-1">
                  <h3 className="text-white font-medium">{s.title}</h3>
                  <p className="text-gray-400 text-sm mt-1">{s.description}</p>
                  {s.example && (
                    <pre className="mt-2 bg-gray-900 rounded p-3 text-xs text-green-400 overflow-x-auto">
                      {JSON.stringify(s.example, null, 2)}
                    </pre>
                  )}
                  {s.config && (
                    <pre className="mt-2 bg-gray-900 rounded p-3 text-xs text-blue-400 overflow-x-auto">
                      {JSON.stringify(s.config, null, 2)}
                    </pre>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Authentication */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Authentication</h2>
        <div className="space-y-4 text-sm">
          <div>
            <h3 className="text-white font-medium mb-1">API Key (recommended for production)</h3>
            <code className="text-green-400 bg-gray-900 px-2 py-1 rounded">X-API-Key: sk_live_your_key_here</code>
          </div>
          <div>
            <h3 className="text-white font-medium mb-1">Bearer Token (for dashboard)</h3>
            <code className="text-green-400 bg-gray-900 px-2 py-1 rounded">Authorization: Bearer eyJ...</code>
          </div>
        </div>
      </div>

      {/* Rate Limits */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Rate Limits</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b border-gray-700">
              <th className="pb-2">Tier</th>
              <th className="pb-2">Limit</th>
              <th className="pb-2">Price</th>
            </tr>
          </thead>
          <tbody className="text-gray-300">
            <tr className="border-b border-gray-800"><td className="py-2">Free</td><td>100/day</td><td>₹0</td></tr>
            <tr className="border-b border-gray-800"><td className="py-2">Developer</td><td>1,000/day</td><td>₹499/mo</td></tr>
            <tr className="border-b border-gray-800"><td className="py-2">Pro</td><td>10,000/day</td><td>₹1,999/mo</td></tr>
            <tr><td className="py-2">Enterprise</td><td>100,000/day</td><td>Custom</td></tr>
          </tbody>
        </table>
      </div>

      {/* MCP */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-4">MCP Integration</h2>
        <p className="text-gray-400 text-sm mb-3">
          Connect Agent Hub to any MCP-compatible AI assistant (Claude, Kiro, Cursor).
        </p>
        <pre className="bg-gray-900 rounded p-4 text-xs text-blue-400 overflow-x-auto">
{`{
  "mcpServers": {
    "agent-hub": {
      "url": "https://agent-hub-production-70f1.up.railway.app/mcp",
      "transport": "http"
    }
  }
}`}
        </pre>
      </div>
    </div>
  );
}
