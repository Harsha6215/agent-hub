export default function Documentation() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Documentation</h1>
      <div className="prose prose-invert max-w-none">
        <div className="p-6 bg-gray-900 rounded-xl border border-gray-800">
          <h2 className="text-lg font-semibold mb-4">Quick Start</h2>
          <ol className="list-decimal list-inside space-y-2 text-sm text-gray-300">
            <li>Create an account and generate an API key</li>
            <li>Browse the Agent Catalog to find a useful agent</li>
            <li>Call the agent via the API gateway</li>
            <li>Monitor your usage in the dashboard</li>
          </ol>

          <h3 className="text-md font-semibold mt-6 mb-2">Example API Call</h3>
          <pre className="p-4 bg-gray-950 rounded-lg text-xs overflow-x-auto">
{`curl -X POST https://api.agenthub.dev/api/v1/agents/gst-calculator/execute \\
  -H "Authorization: Bearer sk_live_your_key_here" \\
  -H "Content-Type: application/json" \\
  -d '{"amount": 100000, "gst_rate": 18}'`}
          </pre>
        </div>
      </div>
    </div>
  );
}
