import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "@/lib/api";

interface Agent {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  category: string;
  version: string;
  price_per_request: number;
  total_executions: number;
}

export default function Agents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState<string>("");

  useEffect(() => {
    const params = category ? { category } : {};
    api
      .get("/api/v1/agents", { params })
      .then((res) => setAgents(res.data.agents))
      .catch(() => setAgents([]))
      .finally(() => setLoading(false));
  }, [category]);

  const categories = [...new Set(agents.map((a) => a.category))];

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Agent Catalog</h1>
        <select
          className="bg-gray-800 text-gray-300 rounded px-3 py-2 text-sm border border-gray-600"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          aria-label="Filter by category"
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <p className="text-gray-400">Loading agents...</p>
      ) : agents.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">No agents available yet.</p>
          <p className="text-gray-500 text-sm mt-2">
            Agents will appear here once registered.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <Link
              key={agent.id}
              to={`/agents/${agent.slug}`}
              className="bg-gray-800 rounded-lg p-5 hover:bg-gray-700 transition-colors border border-gray-700"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-white font-semibold">{agent.name}</h3>
                <span className="text-xs bg-blue-600 px-2 py-0.5 rounded">
                  {agent.category}
                </span>
              </div>
              <p className="text-gray-400 text-sm mb-3 line-clamp-2">
                {agent.description || "No description"}
              </p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>v{agent.version}</span>
                <span>
                  {agent.price_per_request === 0
                    ? "Free"
                    : `₹${(agent.price_per_request / 100).toFixed(2)}/req`}
                </span>
                <span>{agent.total_executions} runs</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
