import { useEffect, useState } from "react";
import api from "@/lib/api";
import { getStoredToken } from "@/lib/auth";

interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string;
}

export default function ApiKeys() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [newKeyName, setNewKeyName] = useState("");
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const headers = { Authorization: `Bearer ${getStoredToken()}` };

  const fetchKeys = () => {
    api.get("/api/v1/keys", { headers })
      .then((res) => setKeys(res.data.keys))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(fetchKeys, []);

  const createKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;
    setCreating(true);
    try {
      const res = await api.post("/api/v1/keys", { name: newKeyName }, { headers });
      setCreatedKey(res.data.key);
      setNewKeyName("");
      fetchKeys();
    } catch {
      alert("Failed to create key");
    } finally {
      setCreating(false);
    }
  };

  const revokeKey = async (id: string) => {
    if (!confirm("Revoke this key? This cannot be undone.")) return;
    await api.delete(`/api/v1/keys/${id}`, { headers });
    fetchKeys();
  };

  const copyKey = () => {
    if (createdKey) navigator.clipboard.writeText(createdKey);
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-6">API Keys</h1>

      {/* Created key modal */}
      {createdKey && (
        <div className="bg-green-900/30 border border-green-700 rounded-lg p-4 mb-6">
          <p className="text-green-300 text-sm font-medium mb-2">
            🔑 Your new API key (copy it now — it won't be shown again):
          </p>
          <div className="flex items-center gap-2">
            <code className="bg-gray-800 px-3 py-2 rounded text-green-400 text-sm flex-1 overflow-x-auto">
              {createdKey}
            </code>
            <button
              onClick={copyKey}
              className="px-3 py-2 bg-green-700 hover:bg-green-600 text-white text-sm rounded"
            >
              Copy
            </button>
            <button
              onClick={() => setCreatedKey(null)}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Create form */}
      <form onSubmit={createKey} className="flex gap-3 mb-6">
        <input
          type="text"
          value={newKeyName}
          onChange={(e) => setNewKeyName(e.target.value)}
          placeholder="Key name (e.g., Production)"
          className="flex-1 px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          disabled={creating}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white font-medium rounded"
        >
          {creating ? "Creating..." : "Create Key"}
        </button>
      </form>

      {/* Keys table */}
      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : keys.length === 0 ? (
        <p className="text-gray-400">No API keys yet. Create one above.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-700">
                <th className="pb-3 pr-4">Name</th>
                <th className="pb-3 pr-4">Key</th>
                <th className="pb-3 pr-4">Status</th>
                <th className="pb-3 pr-4">Last Used</th>
                <th className="pb-3 pr-4">Created</th>
                <th className="pb-3"></th>
              </tr>
            </thead>
            <tbody>
              {keys.map((key) => (
                <tr key={key.id} className="border-b border-gray-800">
                  <td className="py-3 pr-4 text-white">{key.name}</td>
                  <td className="py-3 pr-4">
                    <code className="text-gray-400">{key.key_prefix}...****</code>
                  </td>
                  <td className="py-3 pr-4">
                    <span className={`px-2 py-0.5 rounded text-xs ${key.is_active ? "bg-green-900 text-green-300" : "bg-red-900 text-red-300"}`}>
                      {key.is_active ? "Active" : "Revoked"}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-gray-400">
                    {key.last_used_at ? new Date(key.last_used_at).toLocaleDateString() : "Never"}
                  </td>
                  <td className="py-3 pr-4 text-gray-400">
                    {new Date(key.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-3">
                    {key.is_active && (
                      <button
                        onClick={() => revokeKey(key.id)}
                        className="text-red-400 hover:text-red-300 text-xs"
                      >
                        Revoke
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
