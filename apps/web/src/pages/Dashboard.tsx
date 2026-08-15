export default function Dashboard() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard label="Total Agents" value="0" icon="🤖" />
        <StatCard label="API Calls Today" value="0" icon="📡" />
        <StatCard label="Estimated Revenue" value="₹0.00" icon="💰" />
      </div>
      <div className="mt-8 p-6 bg-gray-900 rounded-xl border border-gray-800">
        <h2 className="text-lg font-semibold mb-2">Getting Started</h2>
        <p className="text-gray-400 text-sm">
          Welcome to Agent Hub. Start by registering your first agent, then
          create an API key to begin receiving requests.
        </p>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <div className="p-6 bg-gray-900 rounded-xl border border-gray-800">
      <div className="flex items-center justify-between">
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-2xl font-bold mt-3">{value}</p>
      <p className="text-sm text-gray-400 mt-1">{label}</p>
    </div>
  );
}
