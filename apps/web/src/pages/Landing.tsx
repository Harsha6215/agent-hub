import { Link } from "react-router-dom";

export default function Landing() {
  const agents = [
    { slug: "business-calculator", name: "Business Calculator", emoji: "💰", ops: "Profit • Margin • Markup • Break-even • Discount", price: "₹0.10" },
    { slug: "gst-calculator", name: "GST Calculator", emoji: "🧾", ops: "Forward GST • Reverse GST • Invoice Total", price: "₹0.10" },
    { slug: "emi-calculator", name: "EMI Calculator", emoji: "🏦", ops: "EMI • Amortization • Eligibility • Prepayment", price: "₹0.15" },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Nav */}
      <nav className="border-b border-gray-800 px-6 py-4 flex justify-between items-center max-w-6xl mx-auto">
        <span className="font-bold text-xl">Agent Hub</span>
        <div className="flex gap-4 items-center">
          <Link to="/agents" className="text-gray-400 hover:text-white text-sm">Agents</Link>
          <Link to="/docs" className="text-gray-400 hover:text-white text-sm">Docs</Link>
          <Link to="/login" className="text-gray-400 hover:text-white text-sm">Sign In</Link>
          <Link to="/register" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium">
            Get Free API Key
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 pt-20 pb-16 text-center">
        <h1 className="text-5xl font-bold mb-4 leading-tight">
          Production-ready APIs<br/>for AI agents.
        </h1>
        <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
          Give your AI capabilities without building every utility yourself.
          Call via REST or MCP. Pay per request.
        </p>
        <div className="flex gap-4 justify-center">
          <Link to="/register" className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-medium text-lg">
            Get Free API Key
          </Link>
          <Link to="/agents" className="border border-gray-600 hover:border-gray-400 px-6 py-3 rounded-lg font-medium text-lg">
            Browse Agents
          </Link>
        </div>
      </section>

      {/* Agent Cards */}
      <section className="max-w-4xl mx-auto px-6 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {agents.map((a) => (
            <Link key={a.slug} to={`/agents/${a.slug}`} className="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-blue-500 transition-colors">
              <div className="text-3xl mb-3">{a.emoji}</div>
              <h3 className="text-white font-semibold mb-1">{a.name}</h3>
              <p className="text-gray-400 text-sm mb-3">{a.ops}</p>
              <span className="text-blue-400 text-sm font-medium">{a.price} / request</span>
            </Link>
          ))}
        </div>
      </section>

      {/* Code Example */}
      <section className="max-w-4xl mx-auto px-6 pb-16">
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-400 text-sm">One API call away</span>
            <span className="text-xs bg-gray-700 px-2 py-1 rounded text-gray-300">Works with: REST • MCP • OpenAPI</span>
          </div>
          <pre className="text-sm text-green-400 overflow-x-auto">
{`curl -X POST https://your-domain.com/api/v1/agents/gst-calculator/execute \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: sk_live_your_key_here" \\
  -d '{"input": {"operation": "calculate_gst", "amount": "1000", "gst_rate": "18"}}'`}
          </pre>
          <pre className="text-sm text-gray-400 mt-3">
{`→ {"gst_amount": "180.00", "total_amount": "1180.00", "cgst": "90.00", "sgst": "90.00"}`}
          </pre>
        </div>
      </section>

      {/* MCP Section */}
      <section className="max-w-4xl mx-auto px-6 pb-20">
        <h2 className="text-2xl font-bold text-center mb-6">Works with AI Assistants</h2>
        <p className="text-center text-gray-400 mb-6">Connect Agent Hub as an MCP server. Your AI can discover and call agents automatically.</p>
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 max-w-lg mx-auto">
          <pre className="text-sm text-blue-400">
{`{
  "mcpServers": {
    "agent-hub": {
      "url": "https://your-domain.com/mcp"
    }
  }
}`}
          </pre>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 text-center text-gray-500 text-sm">
        Agent Hub — AI Agent Utility Platform
      </footer>
    </div>
  );
}
