import { useEffect, useState } from "react";
import api from "@/lib/api";
import { getStoredToken } from "@/lib/auth";

interface UsageSummary {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  total_cost_paisa: number;
  period: string;
}

interface DailyItem {
  date: string;
  requests: number;
  cost_paisa: number;
}

interface AgentItem {
  agent_slug: string;
  requests: number;
  cost_paisa: number;
}

export default function Usage() {
  const [summary, setSummary] = useState<UsageSummary | null>(null);
  const [daily, setDaily] = useState<DailyItem[]>([]);
  const [byAgent, setByAgent] = useState<AgentItem[]>([]);
  const [loading, setLoading] = useState(true);

  const headers = { Authorization: `Bearer ${getStoredToken()}` };

  useEffect(() => {
    Promise.all([
      api.get("/api/v1/usage", { headers }).then((r) => setSummary(r.data)),
      api.get("/api/v1/usage/daily?days=30", { headers }).then((r) => setDaily(r.data.daily)),
      api.get("/api/v1/usage/by-agent", { headers }).then((r) => setByAgent(r.data.by_agent)),
    ])
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-gray-400">Loading usage data...</div>;

  const maxDaily = Math.max(...daily.map((d) => d.requests), 1);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-6">Usage</h1>

      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-800 rounded-lg p-5 border border-gray-700">
          <p className="text-gray-400 text-sm">Total Requests</p>
          <p className="text-3xl font-bold text-white mt-1">{summary?.total_requests || 0}</p>
          <p className="text-gray-500 text-xs mt-1">{summary?.period || "—"}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-5 border border-gray-700">
          <p className="text-gray-400 text-sm">Successful</p>
          <p className="text-3xl font-bold text-green-400 mt-1">{summary?.successful_requests || 0}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-5 border border-gray-700">
          <p className="text-gray-400 text-sm">Failed</p>
          <p className="text-3xl font-bold text-red-400 mt-1">{summary?.failed_requests || 0}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-5 border border-gray-700">
          <p className="text-gray-400 text-sm">Estimated Cost</p>
          <p className="text-3xl font-bold text-yellow-400 mt-1">
            ₹{((summary?.total_cost_paisa || 0) / 100).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Daily chart (simple CSS bar chart) */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
        <h2 className="text-lg font-semibold text-white mb-4">Daily Requests (last 30 days)</h2>
        {daily.length === 0 ? (
          <p className="text-gray-400 text-sm">No usage data yet.</p>
        ) : (
          <div className="flex items-end gap-1 h-32">
            {daily.map((d) => (
              <div
                key={d.date}
                className="flex-1 bg-blue-500 rounded-t opacity-80 hover:opacity-100 transition-opacity cursor-default relative group"
                style={{ height: `${(d.requests / maxDaily) * 100}%`, minHeight: "2px" }}
                title={`${d.date}: ${d.requests} requests`}
              >
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block bg-gray-700 text-xs text-white px-2 py-1 rounded whitespace-nowrap">
                  {d.date}: {d.requests}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* By Agent */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-lg font-semibold text-white mb-4">By Agent</h2>
        {byAgent.length === 0 ? (
          <p className="text-gray-400 text-sm">No usage data yet.</p>
        ) : (
          <div className="space-y-3">
            {byAgent.map((a) => (
              <div key={a.agent_slug} className="flex items-center justify-between">
                <span className="text-white font-medium">{a.agent_slug}</span>
                <div className="flex items-center gap-4">
                  <span className="text-gray-400 text-sm">{a.requests} calls</span>
                  <span className="text-yellow-400 text-sm">
                    ₹{(a.cost_paisa / 100).toFixed(2)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
