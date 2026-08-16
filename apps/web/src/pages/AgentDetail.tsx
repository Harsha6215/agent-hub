import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "@/lib/api";

interface AgentDoc {
  name: string;
  slug: string;
  version: string;
  description: string;
  category: string;
  price_per_request: number;
  input_schema: { properties?: Record<string, any>; required?: string[] };
  output_schema: Record<string, unknown>;
}

export default function AgentDetail() {
  const { slug } = useParams<{ slug: string }>();
  const [doc, setDoc] = useState<AgentDoc | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Try-it state
  const [tryInput, setTryInput] = useState<Record<string, string>>({});
  const [tryResult, setTryResult] = useState<any>(null);
  const [trying, setTrying] = useState(false);
  const [tryError, setTryError] = useState<string | null>(null);

  // Feedback state
  const [feedbackSent, setFeedbackSent] = useState(false);

  useEffect(() => {
    api.get(`/api/v1/agents/${slug}/docs`)
      .then((res) => {
        setDoc(res.data);
        // Pre-fill operation if enum exists
        const ops = res.data.input_schema?.properties?.operation;
        if (ops?.enum?.[0]) {
          setTryInput({ operation: ops.enum[0] });
        }
      })
      .catch((err) => setError(err.response?.data?.error?.message || "Agent not found"))
      .finally(() => setLoading(false));
  }, [slug]);

  const handleTry = async () => {
    setTrying(true);
    setTryError(null);
    setTryResult(null);
    try {
      const res = await api.post(`/api/v1/agents/${slug}/execute`, { input: tryInput });
      setTryResult(res.data);
    } catch (err: any) {
      setTryError(err.response?.data?.error?.message || "Execution failed");
    } finally {
      setTrying(false);
    }
  };

  if (loading) return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-gray-400">Loading...</div>;
  if (error) return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-red-400">{error}</div>;
  if (!doc) return null;

  const properties = doc.input_schema?.properties || {};
  const operations = properties.operation?.enum || [];
  const price = doc.price_per_request === 0 ? "Free" : `₹${(doc.price_per_request / 100).toFixed(2)}`;

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Nav */}
      <nav className="border-b border-gray-800 px-6 py-4 flex justify-between items-center max-w-6xl mx-auto">
        <Link to="/" className="font-bold text-xl">Agent Hub</Link>
        <div className="flex gap-4 items-center">
          <Link to="/agents" className="text-gray-400 hover:text-white text-sm">Agents</Link>
          <Link to="/register" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium">Get API Key</Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-8">
        <Link to="/agents" className="text-blue-400 hover:underline text-sm mb-4 block">← All Agents</Link>

        {/* Header */}
        <div className="flex items-center gap-4 mb-2">
          <h1 className="text-3xl font-bold">{doc.name}</h1>
          <span className="bg-blue-600/20 text-blue-400 text-xs px-2 py-1 rounded">{doc.category}</span>
          <span className="text-gray-500 text-sm">v{doc.version}</span>
        </div>
        <p className="text-gray-400 mb-2">{doc.description}</p>
        <p className="text-blue-400 font-medium mb-8">{price} / request</p>

        {/* Try It In Browser */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">🧪 Try It</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {/* Operation selector */}
            {operations.length > 0 && (
              <div>
                <label className="block text-sm text-gray-400 mb-1">operation</label>
                <select
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                  value={tryInput.operation || ""}
                  onChange={(e) => setTryInput({ ...tryInput, operation: e.target.value })}
                  aria-label="Operation"
                >
                  {operations.map((op: string) => (
                    <option key={op} value={op}>{op}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Other fields */}
            {Object.entries(properties)
              .filter(([key]) => key !== "operation")
              .filter(([, schema]: [string, any]) => schema.type === "string")
              .map(([key, schema]: [string, any]) => (
                <div key={key}>
                  <label className="block text-sm text-gray-400 mb-1">
                    {key} {schema.description && <span className="text-gray-600">— {schema.description}</span>}
                  </label>
                  <input
                    type="text"
                    className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500"
                    placeholder={schema.description || key}
                    value={tryInput[key] || ""}
                    onChange={(e) => setTryInput({ ...tryInput, [key]: e.target.value })}
                  />
                </div>
              ))}
          </div>

          <button
            onClick={handleTry}
            disabled={trying}
            className="bg-green-600 hover:bg-green-700 disabled:bg-green-800 px-6 py-2 rounded font-medium"
          >
            {trying ? "Calculating..." : "Calculate →"}
          </button>

          {/* Result */}
          {tryResult && (
            <div className="mt-4 bg-gray-900 rounded p-4">
              <div className="text-xs text-gray-500 mb-2">Result ({tryResult.latency_ms}ms)</div>
              <pre className="text-sm text-green-400 overflow-x-auto">
                {JSON.stringify(tryResult.data, null, 2)}
              </pre>
            </div>
          )}
          {tryError && (
            <div className="mt-4 bg-red-900/30 border border-red-700 rounded p-3 text-red-300 text-sm">
              {tryError}
            </div>
          )}
        </div>

        {/* API Equivalent */}
        {tryResult && (
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-8">
            <h3 className="text-lg font-semibold mb-3">API Equivalent</h3>
            <pre className="text-sm text-blue-400 overflow-x-auto bg-gray-900 rounded p-4">
{`curl -X POST /api/v1/agents/${slug}/execute \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: sk_live_YOUR_KEY" \\
  -d '${JSON.stringify({ input: tryInput })}'`}
            </pre>
          </div>
        )}

        {/* Code Examples */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">Integration</h2>
          <div className="space-y-4">
            <div>
              <div className="text-xs text-gray-500 mb-1">REST</div>
              <code className="text-sm text-green-400">POST /api/v1/agents/{doc.slug}/execute</code>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">MCP</div>
              <code className="text-sm text-blue-400">tools/call → name: "{doc.slug}"</code>
            </div>
          </div>
        </div>

        {/* Feedback */}
        {!feedbackSent ? (
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex items-center justify-between">
            <span className="text-gray-400 text-sm">Was this agent useful?</span>
            <div className="flex gap-2">
              <button onClick={() => setFeedbackSent(true)} className="text-2xl hover:scale-110 transition-transform" aria-label="Thumbs up">👍</button>
              <button onClick={() => setFeedbackSent(true)} className="text-2xl hover:scale-110 transition-transform" aria-label="Thumbs down">👎</button>
            </div>
          </div>
        ) : (
          <div className="bg-green-900/20 border border-green-700 rounded-lg p-4 text-center text-green-300 text-sm">
            Thanks for the feedback!
          </div>
        )}
      </div>
    </div>
  );
}
