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
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
}

export default function AgentDetail() {
  const { slug } = useParams<{ slug: string }>();
  const [doc, setDoc] = useState<AgentDoc | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get(`/api/v1/agents/${slug}/docs`)
      .then((res) => setDoc(res.data))
      .catch((err) => setError(err.response?.data?.error?.message || "Agent not found"))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <div className="p-8 text-gray-400">Loading...</div>;
  if (error) return <div className="p-8 text-red-400">{error}</div>;
  if (!doc) return null;

  return (
    <div className="p-8 max-w-4xl">
      <Link to="/agents" className="text-blue-400 hover:underline text-sm mb-4 block">
        ← Back to Agents
      </Link>

      <div className="flex items-center gap-4 mb-6">
        <h1 className="text-3xl font-bold text-white">{doc.name}</h1>
        <span className="bg-blue-600 text-xs px-2 py-1 rounded">{doc.category}</span>
        <span className="text-gray-400 text-sm">v{doc.version}</span>
      </div>

      <p className="text-gray-300 mb-8">{doc.description}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-3">Input Schema</h2>
          <pre className="text-sm text-gray-300 overflow-auto">
            {JSON.stringify(doc.input_schema, null, 2)}
          </pre>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-3">Output Schema</h2>
          <pre className="text-sm text-gray-300 overflow-auto">
            {JSON.stringify(doc.output_schema, null, 2)}
          </pre>
        </div>
      </div>

      <div className="mt-6 bg-gray-800 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-3">Pricing</h2>
        <p className="text-gray-300">
          {doc.price_per_request === 0
            ? "Free"
            : `₹${(doc.price_per_request / 100).toFixed(2)} per request`}
        </p>
      </div>

      <div className="mt-6 bg-gray-800 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-3">Try It</h2>
        <code className="text-sm text-green-400 block">
          POST /api/v1/agents/{doc.slug}/execute
        </code>
        <pre className="text-sm text-gray-400 mt-2">
{`{
  "input": {
    ${Object.keys(doc.input_schema?.properties || {})
      .map((k) => `"${k}": "..."`)
      .join(",\n    ")}
  }
}`}
        </pre>
      </div>
    </div>
  );
}
